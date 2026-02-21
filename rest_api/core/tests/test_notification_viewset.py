import pytest
import uuid
from django.contrib.auth.models import User
from core.models import Notification

@pytest.mark.django_db
class TestNotificationViewSet:
    endpoint = "/api/notifications/"

    def test_create_notification_success(self, authenticated_client, test_user):
        payload = {
            "user": test_user.id,
            "title": "Test Notify",
            "msg": "Hello World",
            "seen": False
        }
        response = authenticated_client.post(self.endpoint, payload, format="json")
        assert response.status_code == 201
        assert response.data["title"] == "Test Notify"

    def test_list_notifications(self, authenticated_client, test_user):
        Notification.objects.create(user=test_user, title="N1", msg="M1")
        response = authenticated_client.get(self.endpoint)
        assert response.status_code == 200
        assert len(response.data) >= 1

    def test_update_notification(self, authenticated_client, test_user):
        n = Notification.objects.create(user=test_user, title="N2", msg="M2")
        url = f"{self.endpoint}{n.idNotification}/"
        response = authenticated_client.patch(url, {"seen": True}, format="json")
        assert response.status_code == 200
        assert response.data["seen"] is True

    def test_delete_notification(self, authenticated_client, test_user):
        n = Notification.objects.create(user=test_user, title="N3", msg="M3")
        url = f"{self.endpoint}{n.idNotification}/"
        response = authenticated_client.delete(url)
        assert response.status_code == 204
        assert Notification.objects.filter(pk=n.pk).count() == 0
