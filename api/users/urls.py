from django.urls import path
from .views import RegisterView, LoginView, DashboardView, ProfileUpdateView, TeacherDashboardView, SystemAnnouncementListView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('profile/', ProfileUpdateView.as_view(), name='profile-update'),
    path('dashboard/teacher/', TeacherDashboardView.as_view(), name='teacher-dashboard'),
    path('announcements/', SystemAnnouncementListView.as_view(), name='system-announcements'),
]
