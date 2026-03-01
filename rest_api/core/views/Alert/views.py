from rest_framework import viewsets
from core.models import Alert
from core.serializers.Alert.serializers import AlertSerializer

class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
