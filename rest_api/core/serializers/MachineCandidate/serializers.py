from rest_framework import serializers

from core.models import MachineCandidate


class MachineCandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineCandidate
        fields = '__all__'
