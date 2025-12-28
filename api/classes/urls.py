from django.urls import path
from .views import ClassListCreateView, ClassJoinView, ClassDetailView, ClassStudentsView, ClassAnnouncementListCreateView, ClassLeaveView

urlpatterns = [
    path('', ClassListCreateView.as_view(), name='class-list-create'),
    path('join/', ClassJoinView.as_view(), name='class-join'),
    path('<uuid:pk>/', ClassDetailView.as_view(), name='class-detail'),
    path('<uuid:pk>/students/', ClassStudentsView.as_view(), name='class-students'),
    path('<uuid:pk>/announcements/', ClassAnnouncementListCreateView.as_view(), name='class-announcements'),
    path('<uuid:pk>/leave/', ClassLeaveView.as_view(), name='class-leave'),
]
