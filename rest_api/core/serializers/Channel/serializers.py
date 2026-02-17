from rest_framework import serializers

from core.models import Channel


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = "__all__"
        extra_kwargs = {
            "name": {"validators": []}  # Disable default UniqueValidator (uses .exists())
        }

    def validate_name(self, value):
        # Workaround for Djongo .exists() RecursionError
        queryset = Channel.objects.filter(name=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.count() > 0:
            raise serializers.ValidationError("Channel with this name already exists.")
        return value
