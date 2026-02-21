from rest_framework import serializers

class DataQuerySerializer(serializers.Serializer):
    machineId = serializers.UUIDField(required=True)
    channels = serializers.CharField(required=False, allow_blank=True)
    start = serializers.DateTimeField(required=False, allow_null=True)
    end = serializers.DateTimeField(required=False, allow_null=True)
    f = serializers.CharField(required=False, allow_blank=True)

    def validate_channels(self, value):
        if not value:
            return []
        try:
            # Basic validation of comma-separated UUIDs
            channel_list = value.split(",")
            import uuid
            for cid in channel_list:
                uuid.UUID(cid.strip())
            return channel_list
        except ValueError:
            raise serializers.ValidationError("channels must be a comma-separated list of valid UUIDs")
