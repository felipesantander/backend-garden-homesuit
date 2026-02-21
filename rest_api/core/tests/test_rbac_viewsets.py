import pytest
import uuid
from core.models import Role, Permission, UserRole

@pytest.mark.django_db
class TestRBACViewSets:
    # Testing Role, Permission, and UserRole ViewSets together due to relationships

    def test_role_crud(self, authenticated_client):
        role_url = "/api/roles/"
        name = f"Role_{uuid.uuid4().hex[:6]}"
        
        # Create
        p = Permission.objects.create(name=f"DummyPerm_{uuid.uuid4().hex[:6]}", endpoints=[])
        payload = {"name": name, "permissions": [str(p.idPermission)]}
        res = authenticated_client.post(role_url, payload, format="json")
        assert res.status_code == 201
        role_id = res.data["idRole"]
        
        # List
        res = authenticated_client.get(role_url)
        assert res.status_code == 200
        
        # Delete
        res = authenticated_client.delete(f"{role_url}{role_id}/")
        assert res.status_code == 204

    def test_permission_crud(self, authenticated_client):
        perm_url = "/api/permissions/"
        name = f"Perm_{uuid.uuid4().hex[:6]}"
        
        # Create
        payload = {
            "name": name,
            "endpoints": [{"path": "/test/", "host": "*", "method": "GET"}]
        }
        res = authenticated_client.post(perm_url, payload, format="json")
        assert res.status_code == 201
        perm_id = res.data["idPermission"]
        
        # List
        res = authenticated_client.get(perm_url)
        assert res.status_code == 200
        
        # Delete
        res = authenticated_client.delete(f"{perm_url}{perm_id}/")
        assert res.status_code == 204

    def test_user_role_crud(self, authenticated_client, test_user):
        ur_url = "/api/user-roles/"
        role = Role.objects.create(name=f"UR_Role_{uuid.uuid4().hex[:6]}")
        
        # Create
        res = authenticated_client.post(ur_url, {"user": test_user.id, "role": str(role.idRole)}, format="json")
        assert res.status_code == 201
        ur_id = res.data["idUserRole"]
        
        # List
        res = authenticated_client.get(ur_url)
        assert res.status_code == 200
        
        # Delete
        res = authenticated_client.delete(f"{ur_url}{ur_id}/")
        assert res.status_code == 204
