from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate

from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import RegisterSerializer, UserDashboardSerializer, UpdateProfileSerializer
from api.classes.models import Class
from api.classes.serializers import ClassSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Register berhasil",
                "user": {
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                    "birth_date": user.birth_date
                }

            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if email is None or password is None:
            return Response({"error": "Email dan password diperlukan"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=email, password=password)

        if not user:
            return Response({"error": "Email atau password salah"}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Login berhasil",
            "user": {
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "is_verified": user.is_verified
            },
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # 1. Data User & Joined Classes
        user_serializer = UserDashboardSerializer(user, context={'request': request})
        
        # 2. Recommended Classes (Kelas yang BELUM diikuti user)
        # Ambil 5 kelas acak/terbaru yang user tidak ada di dalamnya
        recommended_classes = Class.objects.exclude(students=user).order_by('?')[:5]
        recommended_serializer = ClassSerializer(recommended_classes, many=True, context={'request': request})

        return Response({
            "user": user_serializer.data,
            "recommended_classes": recommended_serializer.data
        }, status=status.HTTP_200_OK)

class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser) # To handle file uploads

    def get(self, request):
         return Response(UserDashboardSerializer(request.user, context={'request': request}).data)

    def patch(self, request):
        user = request.user
        serializer = UpdateProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Return updated user data similar to dashboard or login
            return Response(UserDashboardSerializer(user, context={'request': request}).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TeacherDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'teacher':
             return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)
        
        user = request.user
        # Stats
        active_classes = Class.objects.filter(teacher=user).count()
        # Students count: Sum of students in all classes taught by this teacher
        # distinct() is important because a student can be in multiple classes
        total_students = User.objects.filter(joined_classes__teacher=user, role='student').distinct().count()
        
        # Pending Assignments (For now mock or simple logic)
        # Using Quiz attempts that need grading or just quiz count?
        # Let's say "Assignments" = Quizzes created by teacher
        from api.quizzes.models import Quiz
        assignments_pending = Quiz.objects.filter(created_by=user).count()

        return Response({
            "activeClasses": active_classes,
            "totalStudents": total_students,
            "assignmentsPending": assignments_pending
        })

class SystemAnnouncementListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from .models import SystemAnnouncement
        from .serializers import SystemAnnouncementSerializer
        from django.db.models import Q
        
        user_role = request.user.role

        # Filter announcements: 
        # target_role='all' OR target_role=user_role
        announcements = SystemAnnouncement.objects.filter(
            Q(target_role='all') | Q(target_role=user_role),
            is_active=True
        ).order_by('-created_at')

        serializer = SystemAnnouncementSerializer(announcements, many=True)
        return Response(serializer.data)

    def post(self, request):
        from .serializers import SystemAnnouncementSerializer
        if request.user.role != 'admin':
             return Response({"detail": "Not authorized. Only admin can create system announcements."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = SystemAnnouncementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
