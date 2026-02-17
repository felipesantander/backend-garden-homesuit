from rest_framework import serializers

from core.models import ConfigurationChannel


class ConfigurationChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfigurationChannel
        fields = '__all__'
