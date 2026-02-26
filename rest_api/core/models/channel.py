import uuid

from django.db import models


class Channel(models.Model):
    idChannel = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    unit = models.CharField(max_length=20, default="", blank=True)
    color = models.CharField(max_length=7, default="#FFFFFF", blank=True, help_text="Hex color code")
    icon = models.CharField(max_length=50, default="", blank=True, help_text="Icon name or class")
    business = models.ForeignKey("core.Business", on_delete=models.CASCADE, related_name="channels", null=True, blank=True)

    def __str__(self):
        return self.name
