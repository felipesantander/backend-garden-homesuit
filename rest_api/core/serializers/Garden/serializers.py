from rest_framework import serializers
from core.models import Garden

class GardenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Garden
        fields = '__all__'
