from django.contrib.auth.models import User
from rest_framework import serializers
from core.models import Business, UserBusiness

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    business_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password', 'business_id')

    def create(self, validated_data):
        business_id = validated_data.pop('business_id', None)
        user = User.objects.create_user(**validated_data)
        
        if business_id:
            try:
                business = Business.objects.get(pk=business_id)
                UserBusiness.objects.create(user=user, business=business)
            except Business.DoesNotExist:
                pass # Or raise serializers.ValidationError
                
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
            
        business_id = validated_data.pop('business_id', None)
        if business_id:
            try:
                business = Business.objects.get(pk=business_id)
                UserBusiness.objects.update_or_create(user=instance, defaults={'business': business})
            except Business.DoesNotExist:
                pass
                
        return super().update(instance, validated_data)
