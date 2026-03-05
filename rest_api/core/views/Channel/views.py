from rest_framework import viewsets

from core.models import Channel
from core.serializers import ChannelSerializer
from core.views.mixins import BusinessFilterMixin


class ChannelViewSet(BusinessFilterMixin, viewsets.ModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
