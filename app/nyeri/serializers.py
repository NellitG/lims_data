from rest_framework import serializers
from .models import SoilSample

class SoilSampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoilSample
        fields = '__all__'