from rest_framework import viewsets
from core.models import Garden
from core.serializers.Garden.serializers import GardenSerializer
from core.views.mixins import BusinessFilterMixin

class GardenViewSet(BusinessFilterMixin, viewsets.ModelViewSet):
    queryset = Garden.objects.all()
    serializer_class = GardenSerializer
