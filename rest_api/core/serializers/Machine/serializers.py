from rest_framework import serializers

from core.models import Machine


class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = "__all__"
        extra_kwargs = {
            "serial": {"validators": []}  # Disable default UniqueValidator (uses .exists())
        }

    def validate_serial(self, value):
        # Workaround for Djongo .exists() RecursionError
        queryset = Machine.objects.filter(serial=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.count() > 0:
            raise serializers.ValidationError("Machine with this serial already exists.")
        return value
