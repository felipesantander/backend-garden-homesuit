import pytest
import uuid
from django.contrib.auth.models import User
from core.models import Business, Machine

@pytest.mark.django_db
class TestBusinessViewSet:
    endpoint = "/api/businesses/"

    @pytest.fixture
    def setup_business(self, db):
        business = Business.objects.create(name=f"Test Business {uuid.uuid4().hex[:6]}")
        return business

    def test_create_business_success(self, authenticated_client):
        payload = {
            "name": "New Business"
        }
        response = authenticated_client.post(self.endpoint, payload, format="json")
        assert response.status_code == 201
        assert response.data["name"] == "New Business"

    def test_list_business(self, authenticated_client, setup_business):
        response = authenticated_client.get(self.endpoint)
        assert response.status_code == 200
        assert len(response.data) >= 1

    def test_delete_business(self, authenticated_client, setup_business):
        b = setup_business
        url = f"{self.endpoint}{b.idBusiness}/"
        response = authenticated_client.delete(url)
        assert response.status_code == 204
        assert Business.objects.filter(pk=b.pk).count() == 0
