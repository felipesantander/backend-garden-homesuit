import pytest
import uuid
from datetime import datetime, timezone, timedelta
from core.models import Data, Machine, Channel
from core.models.data_manager import DataBucketManager

@pytest.mark.django_db
class TestDataQuery:
    endpoint = "/api/data/query/"

    @pytest.fixture
    def setup_base_data(self, db):
        machine = Machine.objects.create(serial=f"SER_{uuid.uuid4().hex[:6]}", Name="Query Machine")
        channel1 = Channel.objects.create(name="Channel 1")
        channel2 = Channel.objects.create(name="Channel 2")
        return machine, channel1, channel2

    def test_query_no_machine_id(self, authenticated_client):
        """Verify that 400 is returned when no machineId is provided."""
        response = authenticated_client.get(self.endpoint)
        assert response.status_code == 400
        assert "machineId" in response.data

    def test_query_success_basic(self, authenticated_client, setup_base_data):
        """Verify basic query with machineId returns data."""
        machine, channel1, _ = setup_base_data
        now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        
        DataBucketManager.add_reading(
            machine=machine,
            channel=channel1,
            data_type="voltage",
            value=220.0,
            timestamp=now,
            frequency="5_second",
            serial_machine=machine.serial
        )

        response = authenticated_client.get(f"{self.endpoint}?machineId={machine.machineId}")
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["value"] == 220.0
        assert response.data[0]["type"] == "Channel 1"

    def test_query_filtering_channels(self, authenticated_client, setup_base_data):
        """Verify filtering by multiple channels."""
        machine, channel1, channel2 = setup_base_data
        now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        
        # Data for channel 1
        DataBucketManager.add_reading(
            machine=machine,
            channel=channel1,
            data_type="voltage",
            value=220.0,
            timestamp=now,
            frequency="5_second",
            serial_machine=machine.serial
        )
        
        # Data for channel 2
        DataBucketManager.add_reading(
            machine=machine,
            channel=channel2,
            data_type="current",
            value=5.0,
            timestamp=now,
            frequency="5_second",
            serial_machine=machine.serial
        )

        # Query only channel 1
        response = authenticated_client.get(f"{self.endpoint}?machineId={machine.machineId}&channels={channel1.idChannel}")
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["channelId"] == str(channel1.idChannel)

        # Query both
        response = authenticated_client.get(f"{self.endpoint}?machineId={machine.machineId}&channels={channel1.idChannel},{channel2.idChannel}")
        assert response.status_code == 200
        assert len(response.data) == 2

    def test_query_date_range(self, authenticated_client, setup_base_data):
        """Verify date range filtering across buckets and individual readings."""
        machine, channel1, _ = setup_base_data
        now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        
        # Bucket 1: 1 hour ago
        t1 = (now - timedelta(hours=1, minutes=30)).isoformat()
        t2 = (now - timedelta(hours=1, minutes=15)).isoformat()
        # Reading 1
        DataBucketManager.add_reading(
            machine=machine,
            channel=channel1,
            data_type="temp",
            value=20.0,
            timestamp=t1,
            frequency="5_second",
            serial_machine=machine.serial
        )
        # Reading 2
        DataBucketManager.add_reading(
            machine=machine,
            channel=channel1,
            data_type="temp",
            value=21.0,
            timestamp=t2,
            frequency="5_second",
            serial_machine=machine.serial
        )
        
        # Bucket 2: Now
        t3 = (now + timedelta(minutes=5)).isoformat()
        t4 = (now + timedelta(minutes=10)).isoformat()
        # Reading 3
        DataBucketManager.add_reading(
            machine=machine,
            channel=channel1,
            data_type="temp",
            value=25.0,
            timestamp=t3,
            frequency="5_second",
            serial_machine=machine.serial
        )
        # Reading 4
        DataBucketManager.add_reading(
            machine=machine,
            channel=channel1,
            data_type="temp",
            value=26.0,
            timestamp=t4,
            frequency="5_second",
            serial_machine=machine.serial
        )

        # Start from t2
        response = authenticated_client.get(self.endpoint, {"machineId": machine.machineId, "start": t2})
        assert response.status_code == 200
        assert len(response.data) == 3 # t2, t3, t4
        
        # End at t3
        response = authenticated_client.get(self.endpoint, {"machineId": machine.machineId, "end": t3})
        assert response.status_code == 200
        assert len(response.data) == 3 # t1, t2, t3

        # Between t2 and t3
        response = authenticated_client.get(self.endpoint, {"machineId": machine.machineId, "start": t2, "end": t3})
        assert response.status_code == 200
        assert len(response.data) == 2 # t2, t3

    def test_query_filtering_frequency(self, authenticated_client, setup_base_data):
        """Verify filtering by frequency."""
        machine, channel1, _ = setup_base_data
        now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        
        # Data with frequency 1_minute
        DataBucketManager.add_reading(
            machine=machine,
            channel=channel1,
            data_type="voltage",
            value=220.0,
            timestamp=now,
            frequency="1_minute",
            serial_machine=machine.serial
        )

        # Data with frequency 5_second
        DataBucketManager.add_reading(
            machine=machine,
            channel=channel1,
            data_type="voltage",
            value=221.0,
            timestamp=now + timedelta(seconds=1),
            frequency="5_second",
            serial_machine=machine.serial
        )

        # Query with 1_minute frequency
        response = authenticated_client.get(f"{self.endpoint}?machineId={machine.machineId}&f=1_minute")
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["frequency"] == "1_minute"

        # Query with 5_second frequency
        response = authenticated_client.get(f"{self.endpoint}?machineId={machine.machineId}&f=5_second")
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["frequency"] == "5_second"
