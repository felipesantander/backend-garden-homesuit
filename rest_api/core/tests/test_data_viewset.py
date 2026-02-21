import pytest
import uuid
import json
from core.models import Data, Machine, Channel
from core.models.data_manager import DataBucketManager

@pytest.mark.django_db
class TestDataViewSet:
    endpoint = "/api/ingest/"

    @pytest.fixture
    def setup_data(self, db):
        machine = Machine.objects.create(serial=f"SER_{uuid.uuid4().hex[:6]}", Name="Data Machine")
        channel = Channel.objects.create(name=f"CHAN_{uuid.uuid4().hex[:6]}")
        return machine, channel

    def test_ingest_data_success(self, authenticated_client, setup_data):
        machine, channel = setup_data
        payload = {
            "frequency": "1_seconds",
            "value": 50.5,
            "type": "float",
            "serial_machine": machine.serial,
            "machineId": str(machine.machineId),
            "channelId": str(channel.idChannel)
        }
        response = authenticated_client.post(self.endpoint, payload, format="json")
        assert response.status_code == 201
        resp_data = json.loads(response.content)
        assert response.status_code == 201
        assert "message" in resp_data
        
        # Verify bucket created using DataBucketManager to ensure same DB
        db = DataBucketManager.get_db()
        # Querying by machineId (foreign key field value)
        bucket = db.core_data.find_one({"type": "float", "serial_machine": machine.serial})
        assert bucket is not None
        assert bucket["count"] == 1
        assert len(bucket["readings"]) == 1
        assert bucket["readings"][0]["v"] == 50.5

    def test_list_data(self, authenticated_client, setup_data):
        # Listing now returns buckets
        machine, channel = setup_data
        from datetime import datetime, timezone
        Data.objects.create(
            base_date=datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0),
            count=1,
            readings=[{"v": 10.0, "t": "2026-02-17T00:00:00", "f": "1_seconds"}],
            type="int",
            serial_machine=machine.serial,
            machineId=machine,
            channelId=channel
        )
        response = authenticated_client.get("/api/data/")
        assert response.status_code == 200
        assert len(response.data) >= 1

    def test_delete_data(self, authenticated_client, setup_data):
        machine, channel = setup_data
        from datetime import datetime, timezone
        d = Data.objects.create(
            base_date=datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0),
            count=1,
            readings=[{"v": 10.0, "t": "2026-02-17T00:00:00", "f": "1_seconds"}],
            type="int",
            serial_machine=machine.serial,
            machineId=machine,
            channelId=channel
        )
        url = f"/api/data/{d.idData}/"
        response = authenticated_client.delete(url)
        assert response.status_code == 204
        assert Data.objects.filter(pk=d.pk).count() == 0
