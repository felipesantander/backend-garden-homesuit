import pytest
import uuid
from django.contrib.auth.models import User
from core.models import Business, UserBusiness

@pytest.mark.django_db
class TestUserBusinessViewSet:
    endpoint = "/api/user-businesses/"

    @pytest.fixture
    def setup_user_business(self, db, test_user):
        business = Business.objects.create(name=f"Association Business {uuid.uuid4().hex[:6]}")
        user_business = UserBusiness.objects.create(user=test_user, business=business)
        return user_business

    def test_create_user_business_success(self, authenticated_client, db):
        # Create a new user for the association (since it's a OneToOneField)
        new_user = User.objects.create_user(username=f"user_{uuid.uuid4().hex[:6]}", password="password123")
        business = Business.objects.create(name=f"New Biz {uuid.uuid4().hex[:6]}")
        
        payload = {
            "user": new_user.id,
            "business": str(business.idBusiness)
        }
        response = authenticated_client.post(self.endpoint, payload, format="json")
        assert response.status_code == 201
        assert response.data["user"] == new_user.id
        assert str(response.data["business"]) == str(business.idBusiness)

    def test_list_user_businesses(self, authenticated_client, setup_user_business):
        response = authenticated_client.get(self.endpoint)
        assert response.status_code == 200
        assert len(response.data) >= 1

    def test_delete_user_business(self, authenticated_client, setup_user_business):
        ub = setup_user_business
        url = f"{self.endpoint}{ub.idUserBusiness}/"
        response = authenticated_client.delete(url)
        assert response.status_code == 204
        assert UserBusiness.objects.filter(pk=ub.pk).count() == 0
