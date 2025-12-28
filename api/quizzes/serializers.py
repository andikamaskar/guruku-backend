from rest_framework import serializers
from django.db import transaction
from .models import Quiz, Question, QuizAttempt, UserAnswer
from api.classes.models import Class

class QuestionAdminSerializer(serializers.ModelSerializer):
    options = serializers.ListField(
        child=serializers.CharField(), 
        min_length=2, 
        help_text="Masukkan minimal 2 pilihan"
    )

    class Meta:
        model = Question
        fields = ['id', 'text', 'order', 'points', 'options', 'answer']

    def validate(self, data):
        """Validasi: Kunci jawaban harus ada di dalam daftar options"""
        options = data.get('options', [])
        answer = data.get('answer', '')
        
        if answer not in options:
            raise serializers.ValidationError(
                f"Jawaban '{answer}' tidak ditemukan di dalam pilihan options yang tersedia."
            )
        return data

class QuizAdminSerializer(serializers.ModelSerializer):
    questions = QuestionAdminSerializer(many=True)
    class_id = serializers.PrimaryKeyRelatedField(
        queryset=Class.objects.all(), source='class_obj', write_only=True
    )
    class_name = serializers.CharField(source='class_obj.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Quiz
        fields = [
            'id', 'exam_id', 'title', 'description', 
            'class_id', 'class_name', 
            'duration_minutes', 'deadline', 'is_active', 
            'total_questions', 'max_score', 'max_attempts',
            'questions', 
            'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'total_questions']

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        user = self.context['request'].user
        
        with transaction.atomic():
            quiz = Quiz.objects.create(**validated_data)
            for q_data in questions_data:
                Question.objects.create(quiz=quiz, **q_data)
            
            quiz.total_questions = quiz.questions.count()
            # Hitung max_score dari total points pertanyaan
            total_points = sum(q.points for q in quiz.questions.all())
            quiz.max_score = total_points
            quiz.save()
            
        return quiz

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        # Update class_id (mapped to class_obj in validated_data)
        instance.class_obj = validated_data.get('class_obj', instance.class_obj)
        instance.duration_minutes = validated_data.get('duration_minutes', instance.duration_minutes)
        instance.deadline = validated_data.get('deadline', instance.deadline)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.max_attempts = validated_data.get('max_attempts', instance.max_attempts)
        instance.save()
        
        if 'questions' in validated_data:
            questions_data = validated_data.pop('questions')
            with transaction.atomic():
                instance.questions.all().delete()
                for q_data in questions_data:
                    Question.objects.create(quiz=instance, **q_data)
                
                instance.total_questions = instance.questions.count()
                # Recalculate max_score
                total_points = sum(q.points for q in instance.questions.all())
                instance.max_score = total_points
                instance.save()
                
        return instance

class QuestionStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'text', 'order', 'points', 'options']

class QuizDetailSerializer(serializers.ModelSerializer):
    questions = QuestionStudentSerializer(many=True, read_only=True)
    class_id = serializers.PrimaryKeyRelatedField(read_only=True, source='class_obj')
    class_name = serializers.CharField(source='class_obj.name', read_only=True)
    user_attempts_count = serializers.SerializerMethodField()
    latest_score = serializers.SerializerMethodField()
    
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'class_id', 'class_name', 'duration_minutes', 'deadline', 'is_active', 'questions', 'max_attempts', 'user_attempts_count', 'latest_score']

    def get_user_attempts_count(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return 0
        return QuizAttempt.objects.filter(quiz=obj, user=user).count()

    def get_latest_score(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return None
        attempt = QuizAttempt.objects.filter(quiz=obj, user=user).order_by('-submitted_at').first()
        return attempt.score if attempt else None

class QuizAttemptSerializer(serializers.ModelSerializer):
    answers = serializers.ListField(write_only=True)
    student_name = serializers.CharField(source='user.full_name', read_only=True)
    student_avatar = serializers.ImageField(source='user.profile_picture', read_only=True)
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    attempt_number = serializers.SerializerMethodField()

    class Meta:
        model = QuizAttempt
        fields = ['id', 'quiz', 'quiz_title', 'user', 'student_name', 'student_avatar', 'score', 'submitted_at', 'answers', 'attempt_number']
        read_only_fields = ['score', 'submitted_at', 'user', 'quiz']

    def get_attempt_number(self, obj):
        # Hitung urutan attempt ini
        all_attempts = QuizAttempt.objects.filter(quiz=obj.quiz, user=obj.user).order_by('submitted_at')
        for index, attempt in enumerate(all_attempts):
            if attempt.id == obj.id:
                return index + 1
        return 1

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        user = self.context['request'].user
        quiz = validated_data.get('quiz')
        
        # Validate Attempt Limit
        if quiz.max_attempts > 0:
            count = QuizAttempt.objects.filter(quiz=quiz, user=user).count()
            if count >= quiz.max_attempts:
               raise serializers.ValidationError("Anda telah mencapai batas maksimal percobaan untuk kuis ini.")
        
        total_score = 0
        
        with transaction.atomic():
            attempt = QuizAttempt.objects.create(user=user, quiz=quiz, score=0)
            
            for item in answers_data:
                q_id = item.get('question_id')
                user_ans_text = item.get('answer_text')
                
                try:
                    question_obj = Question.objects.get(id=q_id, quiz=quiz)

                    UserAnswer.objects.create(
                        attempt=attempt,
                        question=question_obj,
                        answer_text=user_ans_text
                    )
                    if str(user_ans_text).strip() == str(question_obj.answer).strip():
                        total_score += question_obj.points
                        
                except Question.DoesNotExist:
                    continue

            attempt.score = total_score
            attempt.save()
            
        return attempt