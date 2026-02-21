import pytest
import uuid
from core.models import MachineCandidate

@pytest.mark.django_db
class TestMachineCandidateViewSet:
    endpoint = "/api/machine-candidates/"

    def test_create_candidate_success(self, authenticated_client):
        payload = {
            "serial": f"CAND_{uuid.uuid4().hex[:6]}",
            "detected_at": "2026-02-17T12:00:00Z"
        }
        response = authenticated_client.post(self.endpoint, payload, format="json")
        assert response.status_code == 201
        assert response.data["serial"] == payload["serial"]

    def test_list_candidates(self, authenticated_client):
        MachineCandidate.objects.create(serial="C1")
        response = authenticated_client.get(self.endpoint)
        assert response.status_code == 200
        assert len(response.data) >= 1

    def test_delete_candidate(self, authenticated_client):
        c = MachineCandidate.objects.create(serial="C_DEL")
        url = f"{self.endpoint}{c.id}/"
        response = authenticated_client.delete(url)
        assert response.status_code == 204
        assert MachineCandidate.objects.filter(pk=c.pk).count() == 0
