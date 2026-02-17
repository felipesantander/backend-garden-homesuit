import uuid

from django.db import models


class Machine(models.Model):
    machineId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    serial = models.CharField(max_length=100, default="", unique=True)
    Name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.Name} ({self.machineId})"
