from django.urls import path
from .views import get_sample_by_id, list_samples

urlpatterns = [
    # List sample
    path('sample/', list_samples),
    path('sample/<str:sample_id>/', get_sample_by_id),
]