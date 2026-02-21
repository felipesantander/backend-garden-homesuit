from rest_framework import viewsets
from core.models import Garden
from core.serializers.Garden.serializers import GardenSerializer

class GardenViewSet(viewsets.ModelViewSet):
    queryset = Garden.objects.all()
    serializer_class = GardenSerializer
