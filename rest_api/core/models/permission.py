import uuid
from django.db import models
from core.fields import SafeJSONField

class Permission(models.Model):
    idPermission = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    endpoints = SafeJSONField(default=list)  # List of {path: str, host: str, method: str}
    channels = SafeJSONField(default=list)  # List of allowed channels
    machines = SafeJSONField(default=list)  # List of allowed machines
    gardens = SafeJSONField(default=list)   # List of allowed gardens
    businesses = SafeJSONField(default=list) # List of allowed businesses
    components = SafeJSONField(default=list)  # List of allowed UI components

    def __str__(self):
        return self.name
