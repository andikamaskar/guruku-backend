from django.urls import path
from .views import MaterialListCreateView, MaterialDetailView, MarkMaterialCompleteView, GenerateMaterialContentView

urlpatterns = [
    path('class/<uuid:class_id>/', MaterialListCreateView.as_view(), name='material-list-create'),
    path('<uuid:pk>/', MaterialDetailView.as_view(), name='material-detail'),
    path('<uuid:material_id>/complete/', MarkMaterialCompleteView.as_view(), name='material-complete'),
    path('generate-content/', GenerateMaterialContentView.as_view(), name='material-generate-content'),
]
