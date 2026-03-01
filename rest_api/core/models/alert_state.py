import uuid
from django.db import models
from .alert import Alert
from .machine import Machine

class AlertState(models.Model):
    STATUS_CHOICES = [
        ('NORMAL', 'Normal'),
        ('TRIGGERED', 'Triggered'),
    ]

    idAlertState = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name="states")
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name="alert_states")
    current_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NORMAL')
    last_triggered_at = models.DateTimeField(null=True, blank=True)
    last_condition_met_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('alert', 'machine')
        verbose_name_plural = "Alert States"

    def __str__(self):
        return f"{self.alert.name} - {self.machine.serial} - {self.current_status}"
