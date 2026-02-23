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

    def test_query_limit(self, authenticated_client, setup_base_data):
        """Verify that the limit parameter returns only the last x records."""
        machine, channel1, _ = setup_base_data
        now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        
        # Create 5 readings across 2 buckets
        # Bucket 1: 3 readings
        for i in range(3):
            DataBucketManager.add_reading(
                machine=machine,
                channel=channel1,
                data_type="voltage",
                value=200.0 + i,
                timestamp=now - timedelta(hours=1, minutes=i),
                frequency="1_minute",
                serial_machine=machine.serial
            )
            
        # Bucket 2: 2 readings (more recent)
        for i in range(2):
            DataBucketManager.add_reading(
                machine=machine,
                channel=channel1,
                data_type="voltage",
                value=210.0 + i,
                timestamp=now + timedelta(minutes=i),
                frequency="1_minute",
                serial_machine=machine.serial
            )

        # Query with limit=3
        response = authenticated_client.get(f"{self.endpoint}?machineId={machine.machineId}&limit=3")
        assert response.status_code == 200
        assert len(response.data) == 3
        
        # Should return the last 3 in chronological order:
        # 1. Bucket 1 reading 0 (oldest of the 3) -> now - 1h
        # 2. Bucket 2 reading 0 -> now
        # 3. Bucket 2 reading 1 -> now + 1m
        
        # Wait, let's check the logic:
        # Readings are: 
        # T1: now - 1h 2m (v=202)
        # T2: now - 1h 1m (v=201)
        # T3: now - 1h 0m (v=200)
        # T4: now (v=210)
        # T5: now + 1m (v=211)
        
        # Last 3 are T3, T4, T5
        assert response.data[0]["value"] == 200.0
        assert response.data[1]["value"] == 210.0
        assert response.data[2]["value"] == 211.0
