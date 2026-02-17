from rest_framework import viewsets

from core.models import MachineCandidate
from core.serializers import MachineCandidateSerializer


class MachineCandidateViewSet(viewsets.ModelViewSet):
    queryset = MachineCandidate.objects.all()
    serializer_class = MachineCandidateSerializer
