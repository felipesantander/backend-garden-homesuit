from rest_framework import viewsets

from core.models import Business
from core.serializers import BusinessSerializer


class BusinessViewSet(viewsets.ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
