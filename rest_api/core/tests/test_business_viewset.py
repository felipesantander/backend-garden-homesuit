import pytest
import uuid
from django.contrib.auth.models import User
from core.models import Business, Machine

@pytest.mark.django_db
class TestBusinessViewSet:
    endpoint = "/api/businesses/"

    @pytest.fixture
    def setup_business(self, db, test_user):
        machine = Machine.objects.create(serial=f"BIZ_{uuid.uuid4().hex[:6]}", Name="Biz Machine")
        return machine

    def test_create_business_success(self, authenticated_client, test_user, setup_business):
        machine = setup_business
        payload = {
            "user": test_user.id,
            "machine": str(machine.machineId)
        }
        response = authenticated_client.post(self.endpoint, payload, format="json")
        assert response.status_code == 201
        assert response.data["user"] == test_user.id

    def test_list_business(self, authenticated_client, test_user, setup_business):
        machine = setup_business
        Business.objects.create(user=test_user, machine=machine)
        response = authenticated_client.get(self.endpoint)
        assert response.status_code == 200
        assert len(response.data) >= 1

    def test_delete_business(self, authenticated_client, test_user, setup_business):
        machine = setup_business
        b = Business.objects.create(user=test_user, machine=machine)
        url = f"{self.endpoint}{b.idBusiness}/"
        response = authenticated_client.delete(url)
        assert response.status_code == 204
        assert Business.objects.filter(pk=b.pk).count() == 0
