from rest_framework import serializers
from core.models import UserBusiness

class UserBusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBusiness
        fields = '__all__'
