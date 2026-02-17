from rest_framework import viewsets

from core.models import Machine
from core.serializers import MachineSerializer


class MachineViewSet(viewsets.ModelViewSet):
    queryset = Machine.objects.all()
    serializer_class = MachineSerializer
