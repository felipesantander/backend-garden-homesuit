import uuid

from django.db import models


class MachineCandidate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    serial = models.CharField(max_length=100, unique=True)
    types = models.JSONField(default=list)  # Array of types e.g. ["voltaje", "temp"]
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Candidate: {self.serial}"

    class Meta:
        verbose_name_plural = "Machine Candidates"
