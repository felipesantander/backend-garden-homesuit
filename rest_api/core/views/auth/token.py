from rest_framework_simplejwt.views import TokenObtainPairView

from core.serializers.auth.token import CustomTokenObtainPairSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
