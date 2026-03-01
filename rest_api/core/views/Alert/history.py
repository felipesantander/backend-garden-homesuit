from rest_framework import viewsets, mixins
from core.models import AlertHistory
from core.serializers.Alert.history import AlertHistorySerializer

class AlertHistoryViewSet(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
    """
    ViewSet for viewing alert history.
    ReadOnly (List and Retrieve only).
    """
    queryset = AlertHistory.objects.all()
    serializer_class = AlertHistorySerializer
    filterset_fields = ['alert', 'machine']
