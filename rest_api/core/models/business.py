import uuid

from django.conf import settings
from django.db import models



class Business(models.Model):
    idBusiness = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, default="Default Business")

    class Meta:
        verbose_name_plural = "Businesses"

    def __str__(self):
        return self.name
