from rest_framework import serializers
from core.models import Machine, Channel

class ConfigurationItemSerializer(serializers.Serializer):
    type = serializers.CharField(max_length=100)
    channel = serializers.UUIDField()

class MachineRegistrationSerializer(serializers.Serializer):
    serial = serializers.CharField(max_length=100)
    Name = serializers.CharField(max_length=255)
    garden = serializers.UUIDField(required=False, allow_null=True)
    supported_frequencies = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        default=[]
    )
    dashboard_frequency = serializers.CharField(max_length=50, required=False, default="1_minutes")
    configurations = ConfigurationItemSerializer(many=True, required=False, default=[])

    def validate_serial(self, value):
        # Workaround for Djongo .exists() RecursionError
        if Machine.objects.filter(serial=value).count() > 0:
            raise serializers.ValidationError("Machine with this serial already exists.")
        return value

    def validate_configurations(self, value):
        for item in value:
            channel_id = item.get("channel")
            if not Channel.objects.filter(idChannel=channel_id).count() > 0:
                raise serializers.ValidationError(f"Channel with id {channel_id} does not exist")
        return value
