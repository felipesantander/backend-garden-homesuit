import pytest
import uuid
from core.models import ConfigurationChannel, Machine, Channel

@pytest.mark.django_db
class TestConfigChannelViewSet:
    endpoint = "/api/configuration-channels/"

    @pytest.fixture
    def setup_config(self, db):
        machine = Machine.objects.create(serial=f"CFG_{uuid.uuid4().hex[:6]}", Name="Cfg Mach")
        channel = Channel.objects.create(name=f"CHAN_CFG_{uuid.uuid4().hex[:6]}")
        return machine, channel

    def test_create_config_success(self, authenticated_client, setup_config):
        machine, channel = setup_config
        payload = {
            "machine": str(machine.machineId),
            "channel": str(channel.idChannel),
            "serial": machine.serial,
            "type": "temperature"
        }
        response = authenticated_client.post(self.endpoint, payload, format="json")
        assert response.status_code == 201
        assert response.data["type"] == "temperature"

    def test_list_config(self, authenticated_client, setup_config):
        machine, channel = setup_config
        ConfigurationChannel.objects.create(
            machine=machine,
            channel=channel,
            serial=machine.serial,
            type="humidity"
        )
        response = authenticated_client.get(self.endpoint)
        assert response.status_code == 200
        assert len(response.data) >= 1

    def test_delete_config(self, authenticated_client, setup_config):
        machine, channel = setup_config
        cfg = ConfigurationChannel.objects.create(
            machine=machine,
            channel=channel,
            serial=machine.serial,
            type="pressure"
        )
        url = f"{self.endpoint}{cfg.idConfigurationChannel}/"
        response = authenticated_client.delete(url)
        assert response.status_code == 204
        assert ConfigurationChannel.objects.filter(pk=cfg.pk).count() == 0
