from rest_framework import serializers
from .models import Class, Announcement
from api.users.models import User  # pastikan sesuai path user kamu

class ClassSerializer(serializers.ModelSerializer):
    teacher_name = serializers.ReadOnlyField(source='teacher.full_name')
    students_count = serializers.SerializerMethodField()
    is_joined = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Class
        fields = ['id', 'name', 'description', 'grade', 'teacher', 'teacher_name', 'students_count', 'progress', 'is_joined', 'invite_code', 'created_at']
        read_only_fields = ['teacher', 'invite_code', 'created_at']

    def get_students_count(self, obj):
        return obj.students.count()

    def get_progress(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated or request.user.role != 'student':
            return 0
        
        total_materials = obj.materials.count()
        if total_materials == 0:
            return 0
            
        completed_count = 0
        # This approach might be N+1 if not careful, but for a simple list usually okay.
        # Ideally we prefetch related.
        # Let's count how many materials in this class are completed by the user.
        from api.materials.models import Material
        
        # We can query MaterialProgress directly
        from api.materials.models import MaterialProgress
        completed_count = MaterialProgress.objects.filter(
            student=request.user,
            material__class_obj=obj,
            is_completed=True
        ).count()
        
        return int((completed_count / total_materials) * 100)

    def get_is_joined(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated or request.user.role != 'student':
            return False
        return obj.students.filter(id=request.user.id).exists()


class AnnouncementSerializer(serializers.ModelSerializer):
    teacher_name = serializers.ReadOnlyField(source='teacher.full_name')

    class Meta:
        model = Announcement
        fields = ['id', 'class_obj', 'teacher', 'teacher_name', 'content', 'created_at']
        read_only_fields = ['id', 'teacher', 'class_obj', 'created_at']

