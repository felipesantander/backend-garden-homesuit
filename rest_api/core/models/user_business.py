import uuid

from django.conf import settings
from django.db import models

from .business import Business

class UserBusiness(models.Model):
    idUserBusiness = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_business")
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="user_businesses")

    class Meta:
        verbose_name_plural = "User Businesses"

    def __str__(self):
        return f"{self.user} - {self.business}"
