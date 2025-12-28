from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminDashboardViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'', AdminDashboardViewSet, basename='admin')

urlpatterns = [
    path('', include(router.urls)),
]
