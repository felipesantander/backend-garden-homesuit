import uuid
from django.db import models
class Garden(models.Model):
    idGarden = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    business = models.ForeignKey("core.Business", on_delete=models.CASCADE, related_name="gardens")

    def __str__(self):
        return f"{self.name}"
