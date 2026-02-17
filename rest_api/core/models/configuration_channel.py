import uuid

from django.db import models

from .channel import Channel
from .machine import Machine


class ConfigurationChannel(models.Model):
    idConfigurationChannel = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, to_field="machineId")
    type = models.CharField(max_length=100)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, to_field="idChannel")
    serial = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Configuration Channels"
        # Ensure that for a specific machine and data type, there's only one channel configuration
        unique_together = ("machine", "type")

    def __str__(self):
        return f"{self.serial} - {self.type} -> {self.channel.name}"
