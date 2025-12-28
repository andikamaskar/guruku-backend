
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Quiz, QuizAttempt 
from .serializers import QuizAdminSerializer, QuizDetailSerializer, QuizAttemptSerializer
from .gemini_utils import generate_quiz_from_file
from rest_framework.parsers import MultiPartParser, FormParser
import tempfile
import os

class IsTeacherOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        user_role = getattr(request.user, 'role', None)
        if user_role in ['admin', 'teacher']:
            return True
        
        return False

class QuizManageViewSet(viewsets.ModelViewSet):
    serializer_class = QuizAdminSerializer
    permission_classes = [IsTeacherOrAdmin]

    def get_queryset(self):
        user = self.request.user
        user_role = getattr(user, 'role', None)

        if user_role == 'admin' or user.is_superuser:
            return Quiz.objects.all()
        elif user_role == 'teacher':
            return Quiz.objects.filter(created_by=user)
            
        return Quiz.objects.none()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser]) 
    def generate_from_file(self, request):
        if 'file' not in request.FILES:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        uploaded_file = request.FILES['file']
        num_questions = int(request.data.get('num_questions', 5))
        
        # Save to temp file because genai needs a path
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp:
            for chunk in uploaded_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name
            
        try:
            # Determine mime type (basic check or rely on file extension)
            mime_type = uploaded_file.content_type or 'application/pdf'
            
            questions = generate_quiz_from_file(tmp_path, mime_type, num_questions)
            
            return Response(questions, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    @action(detail=True, methods=['get'])
    def attempts(self, request, pk=None):
        quiz = self.get_object()
        attempts = QuizAttempt.objects.filter(quiz=quiz).order_by('-submitted_at')
        serializer = QuizAttemptSerializer(attempts, many=True)
        return Response(serializer.data)

class QuizStudentViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        user = self.request.user
        # Filter quizzes where the class has the user in its students list
        return Quiz.objects.filter(class_obj__students=user, is_active=True).distinct()
    serializer_class = QuizDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'], serializer_class=QuizAttemptSerializer)
    def submit(self, request, pk=None):
        quiz = self.get_object()
        serializer = QuizAttemptSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save(quiz=quiz)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def history(self, request):
        attempts = QuizAttempt.objects.filter(user=request.user).order_by('-submitted_at')
        data = [{
            "quiz_title": a.quiz.title,
            "score": a.score,
            "submitted_at": a.submitted_at
        } for a in attempts]
        return Response(data)