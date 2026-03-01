from rest_framework import serializers
from core.models import AlertHistory

class AlertHistorySerializer(serializers.ModelSerializer):
    alert_name = serializers.CharField(source='alert.name', read_only=True)
    machine_serial = serializers.CharField(source='machine.serial', read_only=True)

    class Meta:
        model = AlertHistory
        fields = [
            'idAlertHistory', 'alert', 'alert_name', 'machine', 'machine_serial',
            'triggered_at', 'details', 'contacts_notified'
        ]
        read_only_fields = fields
