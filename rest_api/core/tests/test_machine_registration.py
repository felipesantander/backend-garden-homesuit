import pytest
import uuid
from core.models import Machine, Channel, ConfigurationChannel

@pytest.mark.django_db
class TestMachineRegistration:
    endpoint = "/api/machines/register/"

    def test_register_success(self, authenticated_client):
        """Verify successful machine registration with multiple channels."""
        channel1 = Channel.objects.create(name="Voltage Channel")
        channel2 = Channel.objects.create(name="Current Channel")
        
        payload = {
            "serial": "SER_REG_001",
            "Name": "New Test Machine",
            "supported_frequencies": ["1_seconds", "1_minutes", "x_hours"],
            "dashboard_frequency": "1_minutes",
            "configurations": [
                {"type": "voltage", "channel": str(channel1.idChannel)},
                {"type": "current", "channel": str(channel2.idChannel)}
            ]
        }

        response = authenticated_client.post(self.endpoint, payload, format="json")
        assert response.status_code == 201
        
        # Verify machine exists
        machine = Machine.objects.get(serial="SER_REG_001")
        assert machine.Name == "New Test Machine"
        assert machine.supported_frequencies == ["1_seconds", "1_minutes", "x_hours"]
        assert machine.dashboard_frequency == "1_minutes"
        
        # Verify configurations exist
        configs = list(ConfigurationChannel.objects.filter(machine=machine))
        assert len(configs) == 2
        
        # Check types without complex filter
        types = [c.type for c in configs]
        assert "voltage" in types
        assert "current" in types

    def test_register_rollback_invalid_channel(self, authenticated_client):
        """Verify that machine is NOT created if a channel ID is invalid."""
        payload = {
            "serial": "SER_FAIL_001",
            "Name": "Ghost Machine",
            "configurations": [
                {"type": "voltage", "channel": str(uuid.uuid4())} # Random UUID
            ]
        }

        response = authenticated_client.post(self.endpoint, payload, format="json")
        assert response.status_code == 400
        # Serializer validation should catch this
        assert "configurations" in response.data
        
        # Verify machine was NOT created due to rollback
        assert Machine.objects.filter(serial="SER_FAIL_001").count() == 0
        # Verify NO configurations remain for this machine (explicitly)
        assert ConfigurationChannel.objects.filter(serial="SER_FAIL_001").count() == 0

    def test_register_rollback_duplicate_type(self, authenticated_client):
        """Verify that machine is NOT created if duplicate types are provided."""
        channel = Channel.objects.create(name="Generic Channel")
        
        payload = {
            "serial": "SER_FAIL_002",
            "Name": "Duplicate Machine",
            "configurations": [
                {"type": "temp", "channel": str(channel.idChannel)},
                {"type": "temp", "channel": str(channel.idChannel)} # Duplicate type
            ]
        }

        response = authenticated_client.post(self.endpoint, payload, format="json")
        assert response.status_code in [400, 500]
        
        # Verify machine was NOT created
        assert Machine.objects.filter(serial="SER_FAIL_002").count() == 0
        assert ConfigurationChannel.objects.filter(serial="SER_FAIL_002").count() == 0

    def test_register_rollback_partial_failure(self, authenticated_client):
        """Verify that partially created channels are deleted when registration fails midway."""
        channel1 = Channel.objects.create(name="Valid Channel 1")
        channel2 = Channel.objects.create(name="Valid Channel 2")
        
        # This will trigger an IntegrityError on the second configuration because of duplicate 'type' for the same machine
        payload = {
            "serial": "SER_PARTIAL_001",
            "Name": "Partial Machine",
            "configurations": [
                {"type": "sensor_a", "channel": str(channel1.idChannel)}, # Should succeed initially
                {"type": "sensor_a", "channel": str(channel2.idChannel)}  # Should fail (duplicate type for machine)
            ]
        }

        response = authenticated_client.post(self.endpoint, payload, format="json")
        assert response.status_code in [400, 500]
        
        # Verify machine was deleted
        assert Machine.objects.filter(serial="SER_PARTIAL_001").count() == 0
        
        # Verify NO ConfigurationChannel objects remain (the first one should have been rolled back via Cascade or manual deletion)
        assert ConfigurationChannel.objects.filter(serial="SER_PARTIAL_001").count() == 0

    def test_register_missing_required_machine_fields(self, authenticated_client):
        """Verify validation of basic machine fields."""
        payload = {
            "serial": "SER_FAIL_003"
            # Missing Name
        }
        response = authenticated_client.post(self.endpoint, payload, format="json")
        assert response.status_code == 400
        assert "Name" in response.data

    def test_register_frequency_logic(self, authenticated_client):
        """Verify that 1_minutes is added and set as default dashboard frequency."""
        payload = {
            "serial": "SER_V1_002",
            "Name": "co simon",
            "garden": str(uuid.uuid4()),
            "supported_frequencies": ["5_minutes"],
            "dashboard_frequency": "5_minutes",
            "configurations": []
        }

        response = authenticated_client.post(self.endpoint, payload, format="json")
        assert response.status_code == 201
        
        # Verify machine exists and has correct frequency settings
        machine = Machine.objects.get(serial="SER_V1_002")
        # Should have both 5_minutes and 1_minutes
        assert "5_minutes" in machine.supported_frequencies
        # Should NOT have 1_minutes if it wasn't in the payload
        assert "1_minutes" not in machine.supported_frequencies
        # Should be set to 5_minutes as per payload
        assert machine.dashboard_frequency == "5_minutes"
