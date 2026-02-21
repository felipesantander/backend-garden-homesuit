import pytest
import uuid
from core.models import Channel

@pytest.mark.django_db
class TestChannelViewSet:
    endpoint = "/api/channels/"

    def test_create_channel_success(self, authenticated_client):
        payload = {"name": f"CH_{uuid.uuid4().hex[:8]}"}
        response = authenticated_client.post(self.endpoint, payload, format="json")
        assert response.status_code == 201
        assert response.data["name"] == payload["name"]

    def test_create_channel_duplicate_name(self, authenticated_client):
        name = "DUPE_CH"
        Channel.objects.create(name=name)
        response = authenticated_client.post(self.endpoint, {"name": name}, format="json")
        assert response.status_code == 400
        assert "name" in response.data

    def test_list_channels(self, authenticated_client):
        Channel.objects.create(name="CH1")
        response = authenticated_client.get(self.endpoint)
        assert response.status_code == 200
        assert len(response.data) >= 1

    def test_update_channel(self, authenticated_client):
        c = Channel.objects.create(name="OLD_CH")
        url = f"{self.endpoint}{c.idChannel}/"
        response = authenticated_client.patch(url, {"name": "NEW_CH"}, format="json")
        assert response.status_code == 200
        assert response.data["name"] == "NEW_CH"

    def test_delete_channel(self, authenticated_client):
        c = Channel.objects.create(name="DEL_CH")
        url = f"{self.endpoint}{c.idChannel}/"
        response = authenticated_client.delete(url)
        assert response.status_code == 204
        assert Channel.objects.filter(pk=c.pk).count() == 0
