from rest_framework import viewsets
from core.models import UserBusiness
from core.serializers import UserBusinessSerializer

class UserBusinessViewSet(viewsets.ModelViewSet):
    queryset = UserBusiness.objects.all()
    serializer_class = UserBusinessSerializer
