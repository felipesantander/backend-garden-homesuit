import uuid

from django.db import models

from .channel import Channel
from .machine import Machine


class Data(models.Model):
    idData = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    createAt = models.DateTimeField(auto_now_add=True)
    date_of_capture = models.DateTimeField(null=True, blank=True)
    dataId = models.CharField(max_length=100, null=True, blank=True)
    frequency = models.FloatField()
    value = models.FloatField()
    type = models.CharField(max_length=50)
    serial_machine = models.CharField(max_length=100)

    # Relationships
    machineId = models.ForeignKey(Machine, on_delete=models.CASCADE, to_field='machineId', null=True, blank=True)
    channelId = models.ForeignKey(Channel, on_delete=models.CASCADE, to_field='idChannel', null=True, blank=True)

    class Meta:
        verbose_name_plural = "Data"
