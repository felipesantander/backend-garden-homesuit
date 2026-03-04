from rest_framework import serializers
from core.models import Alert, AlertCriteria, Machine, Channel

class AlertCriteriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertCriteria
        fields = ['idAlertCriteria', 'channel', 'condition', 'threshold', 'logical_operator', 'order']
        read_only_fields = ['idAlertCriteria']

class AlertSerializer(serializers.ModelSerializer):
    criteria = AlertCriteriaSerializer(many=True)

    class Meta:
        model = Alert
        fields = [
            'idAlert', 'name', 'machines', 'criteria', 'duration',
            'data_frequency', 'contacts', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['idAlert', 'created_at', 'updated_at']

    def create(self, validated_data):
        criteria_data = validated_data.pop('criteria')
        machines_data = validated_data.pop('machines')
        alert = Alert.objects.create(**validated_data)
        alert.machines.set(machines_data)
        for index, criterion_data in enumerate(criteria_data):
            criterion_data['order'] = criterion_data.get('order', index)
            AlertCriteria.objects.create(alert=alert, **criterion_data)
        return alert

    def update(self, instance, validated_data):
        criteria_data = validated_data.pop('criteria', None)
        machines_data = validated_data.pop('machines', None)

        # Update Alert fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if machines_data is not None:
            instance.machines.set(machines_data)

        if criteria_data is not None:
            # Simple approach: clear and recreate
            instance.criteria.all().delete()
            for index, criterion_data in enumerate(criteria_data):
                criterion_data['order'] = criterion_data.get('order', index)
                AlertCriteria.objects.create(alert=instance, **criterion_data)

        return instance
