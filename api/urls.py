from django.urls import path, include

urlpatterns = [
    path('users/', include('api.users.urls')),
    path('classes/', include('api.classes.urls')),
    path('materials/', include('api.materials.urls')),
    path('quizzes/', include('api.quizzes.urls')),

    path('chatbot/', include('api.chatbot.urls')),
    path('admin/', include('api.admin_panel.urls')),
]
