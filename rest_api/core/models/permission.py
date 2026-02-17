import uuid

from django.db import models


class Permission(models.Model):
    idPermission = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    endpoints = models.JSONField(default=list)  # List of allowed endpoints
    channels = models.JSONField(default=list)   # List of allowed channels
    machines = models.JSONField(default=list)   # List of allowed machines

    def __str__(self):
        return self.name
