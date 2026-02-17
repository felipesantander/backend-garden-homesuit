import uuid

from django.conf import settings
from django.db import models

from .machine import Machine


class Business(models.Model):
    idBusiness = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="businesses"
    )
    machine = models.ForeignKey(
        Machine, on_delete=models.CASCADE, related_name="businesses"
    )

    class Meta:
        verbose_name_plural = "Businesses"
        unique_together = ("user", "machine")

    def __str__(self):
        return f"{self.user} - {self.machine}"
