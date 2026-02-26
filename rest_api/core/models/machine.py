import uuid
from django.db import models
from core.fields import SafeJSONField


class Machine(models.Model):
    machineId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    serial = models.CharField(max_length=100, default="", unique=True)
    Name = models.CharField(max_length=255)
    garden = models.ForeignKey("core.Garden", on_delete=models.CASCADE, related_name="machines", null=True, blank=True)
    supported_frequencies = SafeJSONField(default=list)
    dashboard_frequency = models.CharField(max_length=50, default="1_minutes")

    def __str__(self):
        return f"{self.Name} ({self.machineId})"
