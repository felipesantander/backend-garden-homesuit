import pytest
import uuid
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from core.models import Role, Permission, UserRole
from rest_framework_simplejwt.tokens import RefreshToken

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def test_user(db):
    user = User.objects.create_user(username="testuser", password="password123")
    return user

@pytest.fixture
def superadmin_role(db):
    # Create Full Access Permission
    perm = Permission.objects.create(
        name="Full Access",
        endpoints=[
            {"path": "/api/machines/*", "host": "*", "method": "*"},
            {"path": "/api/channels/*", "host": "*", "method": "*"},
            {"path": "/api/data/*", "host": "*", "method": "*"},
            {"path": "/api/businesses/*", "host": "*", "method": "*"},
            {"path": "/api/notifications/*", "host": "*", "method": "*"},
            {"path": "/api/permissions/*", "host": "*", "method": "*"},
            {"path": "/api/roles/*", "host": "*", "method": "*"},
            {"path": "/api/user-roles/*", "host": "*", "method": "*"},
            {"path": "/api/configuration-channels/*", "host": "*", "method": "*"},
            {"path": "/api/machine-candidates/*", "host": "*", "method": "*"},
        ]
    )
    # Create Role
    role = Role.objects.create(name="SuperAdmin")
    role.permissions.add(perm)
    return role

@pytest.fixture
def authenticated_client(api_client, test_user, superadmin_role):
    UserRole.objects.create(user=test_user, role=superadmin_role)
    refresh = RefreshToken.for_user(test_user)
    refresh["role"] = superadmin_role.name
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client

@pytest.fixture
def forbidden_client(api_client, test_user):
    # User with NO role assigned (middleware should block)
    refresh = RefreshToken.for_user(test_user)
    # Token without role claim
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client
