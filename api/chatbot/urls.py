from django.urls import path
from .views import (
    ConversationListCreateView,
    ChatbotMessageView,
    ConversationDetailView
)

urlpatterns = [
    path("conversations/", ConversationListCreateView.as_view()),
    path("conversations/<int:conversation_id>/", ConversationDetailView.as_view()),
    path("conversations/<int:conversation_id>/message/", ChatbotMessageView.as_view()),
]
