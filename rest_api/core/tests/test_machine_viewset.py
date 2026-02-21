import pytest
import uuid
from django.urls import reverse
from core.models import Machine

@pytest.mark.django_db
class TestMachineViewSet:
    endpoint = "/api/machines/"

    def test_create_machine_success(self, authenticated_client):
        payload = {
            "serial": f"SN_{uuid.uuid4().hex[:8]}",
            "Name": "Test Machine"
        }
        response = authenticated_client.post(self.endpoint, payload, format="json")
        assert response.status_code == 201
        assert response.data["serial"] == payload["serial"]
        assert Machine.objects.filter(serial=payload["serial"]).count() == 1

    def test_create_machine_duplicate_serial(self, authenticated_client):
        serial = "DUPE_SN"
        Machine.objects.create(serial=serial, Name="Existing")
        
        payload = {"serial": serial, "Name": "New Name"}
        response = authenticated_client.post(self.endpoint, payload, format="json")
        
        assert response.status_code == 400
        assert "serial" in response.data

    def test_create_machine_missing_name(self, authenticated_client):
        payload = {"serial": "MISSING_NAME"}
        response = authenticated_client.post(self.endpoint, payload, format="json")
        
        assert response.status_code == 400
        assert "Name" in response.data

    def test_list_machines(self, authenticated_client):
        Machine.objects.create(serial="SN1", Name="M1")
        Machine.objects.create(serial="SN2", Name="M2")
        
        response = authenticated_client.get(self.endpoint)
        assert response.status_code == 200
        assert len(response.data) >= 2

    def test_get_machine_detail(self, authenticated_client):
        m = Machine.objects.create(serial="DETAIL_SN", Name="Detail M")
        url = f"{self.endpoint}{m.machineId}/"
        
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert response.data["Name"] == "Detail M"

    def test_update_machine_success(self, authenticated_client):
        m = Machine.objects.create(serial="UPDATE_SN", Name="Old Name")
        url = f"{self.endpoint}{m.machineId}/"
        
        response = authenticated_client.patch(url, {"Name": "New Name"}, format="json")
        assert response.status_code == 200
        assert response.data["Name"] == "New Name"

    def test_delete_machine_success(self, authenticated_client):
        m = Machine.objects.create(serial="DELETE_SN", Name="Delete Me")
        url = f"{self.endpoint}{m.machineId}/"
        
        response = authenticated_client.delete(url)
        assert response.status_code == 204
        assert Machine.objects.filter(pk=m.pk).count() == 0

    def test_unauthorized_access(self, api_client):
        response = api_client.get(self.endpoint)
        # RBAC Middleware returns 401 if header is missing
        assert response.status_code == 401

    def test_forbidden_access(self, forbidden_client):
        response = forbidden_client.get(self.endpoint)
        # RBAC Middleware returns 403 if role is missing in token
        assert response.status_code == 403
