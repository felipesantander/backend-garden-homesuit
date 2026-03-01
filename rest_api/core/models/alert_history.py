import uuid
from django.db import models
from .alert import Alert
from .machine import Machine
from core.fields import SafeJSONField

class AlertHistory(models.Model):
    idAlertHistory = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name="history")
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name="alert_history")
    triggered_at = models.DateTimeField(auto_now_add=True)
    details = SafeJSONField(default=list, help_text="Details of which criteria were met")
    contacts_notified = SafeJSONField(default=list, help_text="Copy of contacts notified at the time")

    class Meta:
        verbose_name_plural = "Alert Histories"
        ordering = ['-triggered_at']

    def __str__(self):
        return f"{self.alert.name} - {self.machine.serial} - {self.triggered_at}"
