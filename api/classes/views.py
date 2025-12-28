from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Class
from .serializers import ClassSerializer, AnnouncementSerializer
from django.shortcuts import get_object_or_404


class ClassListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Check if we want all classes (for recommendations) or just joined ones
        mode = request.query_params.get('mode', 'joined') # 'joined' or 'all'
        
        if request.user.role == 'teacher':
            classes = Class.objects.filter(teacher=request.user)
        else:
            # Student logic
            if mode == 'all':
                # Filter by grade if student has a profile
                classes = Class.objects.all()
                try:
                    if hasattr(request.user, 'student_profile') and request.user.student_profile.grade:
                        classes = classes.filter(grade=request.user.student_profile.grade)
                except Exception as e:
                    # Fallback if profile access fails
                    pass
                
                # Exclude joined classes from "all/recommended" list if needed, 
                # or just return all and let frontend filter. 
                # For now, let's return all matching grade.
            else:
                # Default: joined classes
                classes = request.user.joined_classes.all()

        serializer = ClassSerializer(classes, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        if request.user.role != 'teacher':
            return Response({"error": "Hanya guru yang dapat membuat kelas."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ClassSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(teacher=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClassJoinView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        invite_code = request.data.get("invite_code")
        if not invite_code:
            return Response({"error": "Kode undangan diperlukan."}, status=status.HTTP_400_BAD_REQUEST)

        class_obj = get_object_or_404(Class, invite_code=invite_code)
        if request.user.role != 'student':
            return Response({"error": "Hanya siswa yang dapat bergabung dengan kelas."}, status=status.HTTP_403_FORBIDDEN)

        class_obj.students.add(request.user)
        return Response({"message": f"Berhasil bergabung ke kelas {class_obj.name}"}, status=status.HTTP_200_OK)


class ClassDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(Class, pk=pk)

    def get(self, request, pk):
        class_obj = self.get_object(pk)
        serializer = ClassSerializer(class_obj, context={'request': request})
        return Response(serializer.data)

    def patch(self, request, pk):
        class_obj = self.get_object(pk)
        if class_obj.teacher != request.user:
             return Response({"error": "Hanya guru pemilik kelas yang dapat mengedit."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ClassSerializer(class_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        class_obj = self.get_object(pk)
        if class_obj.teacher != request.user:
             return Response({"error": "Hanya guru pemilik kelas yang dapat menghapus."}, status=status.HTTP_403_FORBIDDEN)
        
        class_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ClassStudentsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        class_obj = get_object_or_404(Class, pk=pk)
        
        # Allow Teacher (Owner) OR Student (Member)
        is_teacher = class_obj.teacher == request.user
        is_student = class_obj.students.filter(id=request.user.id).exists()

        if not (is_teacher or is_student):
             return Response({"error": "Anda tidak memiliki akses ke kelas ini."}, status=status.HTTP_403_FORBIDDEN)

        students = class_obj.students.all()
        data = []
        for student in students:
            # Construct full URL for profile picture
            avatar_url = None
            if student.profile_picture:
                avatar_url = request.build_absolute_uri(student.profile_picture.url)
            
            data.append({
                'id': student.id,
                'full_name': student.full_name,
                'email': student.email,
                'avatar': avatar_url
            })
        return Response(data)


class ClassAnnouncementListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        class_obj = get_object_or_404(Class, pk=pk)
        announcements = class_obj.announcements.all()
        serializer = AnnouncementSerializer(announcements, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        class_obj = get_object_or_404(Class, pk=pk)
        if class_obj.teacher != request.user:
            return Response({"error": "Hanya guru pemilik kelas yang dapat membuat pengumuman."}, status=status.HTTP_403_FORBIDDEN)

        serializer = AnnouncementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(teacher=request.user, class_obj=class_obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClassLeaveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        class_obj = get_object_or_404(Class, pk=pk)
        if request.user.role != 'student':
             return Response({"error": "Hanya siswa yang dapat keluar dari kelas."}, status=status.HTTP_403_FORBIDDEN)

        if request.user in class_obj.students.all():
            class_obj.students.remove(request.user)
            return Response({"message": "Berhasil keluar dari kelas."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Anda belum bergabung di kelas ini."}, status=status.HTTP_400_BAD_REQUEST)
