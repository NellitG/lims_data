from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import SoilSample
from .serializers import SoilSampleSerializer
from rest_framework import status

# Create your views here.
@api_view(['GET'])
def get_sample_by_id(request, sample_id):

    samples = SoilSample.objects.filter(sample_id=sample_id)

    if not samples.exists():
        return Response({'error': 'Sample not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = SoilSampleSerializer(samples, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)