from django.db import models

class Machine(models.Model):
    machineId = models.CharField(max_length=100, unique=True, primary_key=True)
    Name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.Name} ({self.machineId})"

class Channel(models.Model):
    idChannel = models.CharField(max_length=100, unique=True, primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Data(models.Model):
    idData = models.AutoField(primary_key=True)
    createAt = models.DateTimeField(auto_now_add=True)
    dataId = models.CharField(max_length=100)
    frequency = models.FloatField()
    value = models.FloatField()
    type = models.CharField(max_length=50)
    serial_machine = models.CharField(max_length=100)
    
    # Relationships (represented as CharFields if using non-relational MongoDB strictly)
    # However, Djongo supports some Level of ForeignKeys. 
    machineId = models.ForeignKey(Machine, on_delete=models.CASCADE, to_field='machineId')
    channelId = models.ForeignKey(Channel, on_delete=models.CASCADE, to_field='idChannel')

    class Meta:
        verbose_name_plural = "Data"
