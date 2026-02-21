import pytest
import uuid
from datetime import datetime, timezone, timedelta
from core.models import Data, Machine, Channel

@pytest.mark.django_db
class TestDataLatest:
    endpoint = "/api/data/latest/"

    @pytest.fixture
    def setup_base_data(self, db):
        serial = f"SER_{uuid.uuid4().hex[:6]}"
        machine = Machine.objects.create(serial=serial, Name="Test Machine")
        channel = Channel.objects.create(name="Test Channel")
        return machine, channel

    def test_latest_no_serial(self, authenticated_client):
        """Verify that 400 is returned when no serial is provided."""
        response = authenticated_client.get(self.endpoint)
        assert response.status_code == 400
        assert response.data["error"] == "Serial parameter is required"

    def test_latest_no_data(self, authenticated_client, setup_base_data):
        """Verify that an empty dictionary is returned if no data exists for the serial."""
        machine, _ = setup_base_data
        response = authenticated_client.get(f"{self.endpoint}?serial={machine.serial}")
        assert response.status_code == 200
        assert response.data == {}

    def test_latest_success(self, authenticated_client, setup_base_data):
        """Verify that the endpoint returns the latest reading for each data type."""
        machine, channel = setup_base_data
        now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        
        # Create a bucket with some readings
        Data.objects.create(
            base_date=now - timedelta(hours=1),
            type="float",
            serial_machine=machine.serial,
            machineId=machine,
            channelId=channel,
            readings=[
                 {"v": 10.5, "t": (now - timedelta(hours=1, minutes=30)).isoformat(), "f": "1_seconds"},
                 {"v": 11.5, "t": (now - timedelta(hours=1, minutes=15)).isoformat(), "f": "1_seconds"}
            ],
            count=2
        )
        
        # Create a more recent bucket
        Data.objects.create(
            base_date=now,
            type="float",
            serial_machine=machine.serial,
            machineId=machine,
            channelId=channel,
            readings=[
                 {"v": 20.5, "t": (now + timedelta(minutes=5)).isoformat(), "f": "1_seconds"},
                 {"v": 25.5, "t": (now + timedelta(minutes=10)).isoformat(), "f": "1_seconds"}
            ],
            count=2
        )

        response = authenticated_client.get(f"{self.endpoint}?serial={machine.serial}")
        assert response.status_code == 200
        assert "float" in response.data
        # Should return the last reading of the most recent bucket
        assert response.data["float"]["v"] == 25.5

    def test_latest_multiple_types(self, authenticated_client, setup_base_data):
        """Verify that it correctly aggregates latest readings from different data types."""
        machine, channel = setup_base_data
        now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        
        # Float data
        Data.objects.create(
            base_date=now,
            type="float",
            serial_machine=machine.serial,
            machineId=machine,
            channelId=channel,
            readings=[{"v": 12.3, "t": now.isoformat(), "f": "1_seconds"}],
            count=1
        )
        
        # Int data
        Data.objects.create(
            base_date=now,
            type="int",
            serial_machine=machine.serial,
            machineId=machine,
            channelId=channel,
            readings=[{"v": 42, "t": now.isoformat(), "f": "1_seconds"}],
            count=1
        )

        response = authenticated_client.get(f"{self.endpoint}?serial={machine.serial}")
        assert response.status_code == 200
        assert response.data["float"]["v"] == 12.3
        assert response.data["int"]["v"] == 42

    def test_latest_wrong_serial(self, authenticated_client, setup_base_data):
        """Verify that data for one serial is not leaked to another."""
        machine1, channel = setup_base_data
        machine2 = Machine.objects.create(serial=f"SER_{uuid.uuid4().hex[:6]}", Name="Machine 2")
        
        now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        Data.objects.create(
            base_date=now,
            type="float",
            serial_machine=machine1.serial,
            machineId=machine1,
            channelId=channel,
            readings=[{"v": 100.0, "t": now.isoformat(), "f": "1_seconds"}],
            count=1
        )

        # Query for machine2
        response = authenticated_client.get(f"{self.endpoint}?serial={machine2.serial}")
        assert response.status_code == 200
        assert response.data == {}

    def test_latest_with_databucketmanager(self, authenticated_client, setup_base_data):
        """
        Reproduce the JSON decoding error when data is ingested via DataBucketManager (pymongo).
        """
        from core.models.data_manager import DataBucketManager
        machine, channel = setup_base_data
        
        # Ingest data using DataBucketManager which uses pymongo straight
        DataBucketManager.add_reading(
            machine=machine,
            channel=channel,
            data_type="voltage",
            value=220.0,
            timestamp=datetime.now(timezone.utc),
            frequency="5_second",
            serial_machine=machine.serial
        )

        # This call should fail with TypeError if readings is models.JSONField
        response = authenticated_client.get(f"{self.endpoint}?serial={machine.serial}")
        assert response.status_code == 200
        assert "voltage" in response.data
        assert response.data["voltage"]["v"] == 220.0
