from rest_framework import viewsets

from core.models import UserRole
from core.serializers import UserRoleSerializer


class UserRoleViewSet(viewsets.ModelViewSet):
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
