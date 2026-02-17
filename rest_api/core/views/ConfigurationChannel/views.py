from rest_framework import viewsets

from core.models import ConfigurationChannel
from core.serializers import ConfigurationChannelSerializer


class ConfigurationChannelViewSet(viewsets.ModelViewSet):
    queryset = ConfigurationChannel.objects.all()
    serializer_class = ConfigurationChannelSerializer
