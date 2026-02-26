import pytest
import uuid
from core.models import Machine, Channel, ConfigurationChannel

@pytest.mark.django_db
class TestMachineUpdate:
    endpoint = "/api/machines/"

    def test_update_machine_with_configurations(self, authenticated_client):
        """Verify that updating a machine correctly synchronizes configurations and frequencies."""
        # 1. Create initial machine and channels
        channel_old = Channel.objects.create(name="Old Channel")
        machine = Machine.objects.create(
            serial="SN_OLD",
            Name="Old Machine",
            supported_frequencies=["5_minutes"],
            dashboard_frequency="5_minutes"
        )
        ConfigurationChannel.objects.create(
            machine=machine,
            type="temp",
            channel=channel_old,
            serial=machine.serial
        )

        # 2. Create new channel for update
        channel_new = Channel.objects.create(name="New Channel")
        
        url = f"{self.endpoint}{machine.machineId}/"
        payload = {
            "serial": "SN_NEW",
            "Name": "New Machine Name",
            "supported_frequencies": ["10_minutes"],
            "dashboard_frequency": "10_minutes",
            "configurations": [
                {"type": "humidity", "channel": str(channel_new.idChannel)}
            ]
        }

        # 3. Perform update
        response = authenticated_client.put(url, payload, format="json")
        assert response.status_code == 200
        
        # 4. Verify machine fields
        machine.refresh_from_db()
        assert machine.Name == "New Machine Name"
        assert machine.serial == "SN_NEW"
        # 1_minutes should NOT have been added if not in payload
        assert "10_minutes" in machine.supported_frequencies
        assert "1_minutes" not in machine.supported_frequencies
        # dashboard_frequency should be 10_minutes from payload
        assert machine.dashboard_frequency == "10_minutes"

        # 5. Verify configurations
        configs = ConfigurationChannel.objects.filter(machine=machine)
        assert configs.count() == 1
        config = configs.first()
        assert config.type == "humidity"
        assert config.channel == channel_new
        assert config.serial == "SN_NEW" # Should be updated to match the new machine serial

        # Verify old configuration is gone
        assert ConfigurationChannel.objects.filter(channel=channel_old).count() == 0

    def test_partial_update_machine(self, authenticated_client):
        """Verify that partial updates (PATCH) work correctly."""
        machine = Machine.objects.create(serial="PATCH_SN", Name="Old Name")
        url = f"{self.endpoint}{machine.machineId}/"
        
        response = authenticated_client.patch(url, {"Name": "Patched Name"}, format="json")
        assert response.status_code == 200
        
        machine.refresh_from_db()
        assert machine.Name == "Patched Name"
        assert machine.serial == "PATCH_SN" # Should remain unchanged
