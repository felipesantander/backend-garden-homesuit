import uuid
from django.db import models
from .machine import Machine
from .channel import Channel
from core.fields import SafeJSONField

class Alert(models.Model):
    idAlert = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    machines = models.ManyToManyField(Machine, related_name='alerts')
    duration = models.IntegerField(help_text="Time in seconds that the condition must persist")
    data_frequency = models.CharField(max_length=50, help_text="Frequency of the data to monitor")
    contacts = SafeJSONField(default=list, help_text="List of contacts to notify")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Alerts"

class AlertCriteria(models.Model):
    CONDITION_CHOICES = [
        ('>', 'Greater than'),
        ('<', 'Less than'),
        ('=', 'Equal to'),
    ]

    idAlertCriteria = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name='criteria')
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    condition = models.CharField(max_length=1, choices=CONDITION_CHOICES)
    threshold = models.FloatField()

    def __str__(self):
        return f"{self.alert.name} - {self.channel.name} {self.condition} {self.threshold}"
