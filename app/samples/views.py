from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import SoilSample
from .serializers import SoilSampleSerializer


@api_view(['GET'])
def get_sample_by_id(request,sample_id):

    samples = SoilSample.objects.filter(sample_id=sample_id)

    if not samples.exists():
        return Response({"error": "Sample not found"}, status=404)

    serializer = SoilSampleSerializer(samples, many=True)
    return Response(serializer.data)

# List all samples
@api_view(['GET'])
def list_samples(request):
    samples = SoilSample.objects.all()
    serializer = SoilSampleSerializer(samples, many=True)
    return Response(serializer.data)