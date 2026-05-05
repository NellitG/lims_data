from django.urls import path
from .views import get_sample_by_id

urlpatterns = [
    path('meru/<str:sample_id>/', get_sample_by_id),
    
]