import uuid

from django.db import models

from .channel import Channel
from .machine import Machine
from core.fields import SafeJSONField


class Data(models.Model):
    idData = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    createAt = models.DateTimeField(auto_now_add=True)
    base_date = models.DateTimeField(help_text="Beginning of the hour for this bucket", null=True, blank=True)
    type = models.CharField(max_length=50)
    serial_machine = models.CharField(max_length=100)
    frequency = models.CharField(max_length=50, null=True, blank=True)

    # Bucketed readings: list of {value: float, timestamp: str, frequency: float}
    readings = SafeJSONField(default=list)
    count = models.IntegerField(default=0)

    # Relationships
    machineId = models.ForeignKey(Machine, on_delete=models.CASCADE, to_field="machineId", null=True, blank=True)
    channelId = models.ForeignKey(Channel, on_delete=models.CASCADE, to_field="idChannel", null=True, blank=True)

    class Meta:
        verbose_name_plural = "Data"
        indexes = [
            models.Index(fields=["machineId", "channelId", "base_date", "type", "frequency"]),
        ]
        unique_together = ("machineId", "channelId", "base_date", "type", "frequency")
