from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Role, UserRole
from core.serializers.User import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing user instances.
    Provides an extra action to assign roles and update passwords.
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()

    @action(detail=True, methods=['post'], url_path='assign_role')
    def assign_role(self, request, pk=None):
        user = self.get_object()
        role_id = request.data.get('role_id')
        
        if not role_id:
            return Response(
                {"detail": "role_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            role = Role.objects.get(pk=role_id)
        except Role.DoesNotExist:
            return Response(
                {"detail": "Role not found."},
                status=status.HTTP_404_NOT_FOUND
            )
            
        user_role, created = UserRole.objects.get_or_create(user=user, role=role)
        
        if created:
            return Response(
                {"detail": f"Role '{role.name}' assigned correctly."},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"detail": f"User already has role '{role.name}'."},
                status=status.HTTP_200_OK
            )
