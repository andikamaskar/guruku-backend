from rest_framework import serializers
from .models import Material, MaterialProgress

class MaterialSerializer(serializers.ModelSerializer):
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = Material
        fields = ['id', 'class_obj', 'title', 'content', 'video_file', 'file', 'created_at', 'is_completed']
        read_only_fields = ['id', 'created_at', 'class_obj']

    def get_is_completed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            try:
                progress = MaterialProgress.objects.get(student=user, material=obj)
                return progress.is_completed
            except MaterialProgress.DoesNotExist:
                return False
        return False

class MaterialProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialProgress
        fields = ['id', 'student', 'material', 'is_completed', 'last_accessed']
        read_only_fields = ['id', 'student', 'material', 'last_accessed']
