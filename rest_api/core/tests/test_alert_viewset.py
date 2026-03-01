import pytest
import uuid
from core.models import Machine, Channel, Alert, AlertCriteria

@pytest.mark.django_db
class TestAlertViewSet:
    endpoint = "/api/alerts/"

    def test_create_alert_with_multiple_criteria(self, authenticated_client):
        # 1. Prepare data
        channel1 = Channel.objects.create(name="Temp Channel")
        channel2 = Channel.objects.create(name="Humidity Channel")
        machine = Machine.objects.create(serial="M1", Name="Machine 1")
        
        payload = {
            "name": "Advanced Alert",
            "machines": [str(machine.machineId)],
            "criteria": [
                {"channel": str(channel1.idChannel), "condition": ">", "threshold": 30.0},
                {"channel": str(channel2.idChannel), "condition": "<", "threshold": 40.0}
            ],
            "duration": 600,
            "data_frequency": "1_minutes"
        }

        # 2. POST request
        response = authenticated_client.post(self.endpoint, payload, format="json")
        assert response.status_code == 201
        assert response.data["name"] == "Advanced Alert"
        assert len(response.data["criteria"]) == 2

        # 3. Verify in DB
        alert_id = response.data["idAlert"]
        alert = Alert.objects.get(idAlert=alert_id)
        assert alert.criteria.count() == 2
        assert alert.machines.count() == 1

    def test_update_alert_criteria(self, authenticated_client):
        channel = Channel.objects.create(name="Channel")
        alert = Alert.objects.create(
            name="Old Alert", duration=60, data_frequency="5_minutes"
        )
        AlertCriteria.objects.create(alert=alert, channel=channel, condition="=", threshold=10)
        
        url = f"{self.endpoint}{alert.idAlert}/"
        
        new_payload = {
            "name": "Updated Alert",
            "criteria": [
                {"channel": str(channel.idChannel), "condition": ">", "threshold": 100.0}
            ]
        }
        
        response = authenticated_client.patch(url, new_payload, format="json")
        assert response.status_code == 200
        
        alert.refresh_from_db()
        assert alert.name == "Updated Alert"
        assert alert.criteria.count() == 1
        assert alert.criteria.first().threshold == 100.0
