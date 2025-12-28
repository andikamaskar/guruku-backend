from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register(r'manage', views.QuizManageViewSet, basename='quiz-manage')

router.register(r'student', views.QuizStudentViewSet, basename='quiz-student')

urlpatterns = [
    path('', include(router.urls)),
]