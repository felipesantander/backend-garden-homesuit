import pytest
import uuid
from django.utils import timezone
from datetime import timedelta
from core.models import Machine, Channel, Alert, AlertCriteria, Data, AlertHistory
from core.tasks.alerts import monitor_alerts_task

@pytest.mark.django_db
class TestAlertTasks:
    def test_monitor_alerts_task_triggers(self, mocker):
        # 1. Setup Data
        channel = Channel.objects.create(name="Temp")
        machine = Machine.objects.create(serial="MT1", Name="Machine Test")
        
        alert = Alert.objects.create(
            name="Test Task Alert",
            duration=60, # 1 minute
            data_frequency="1_minutes"
        )
        AlertCriteria.objects.create(
            alert=alert,
            channel=channel,
            condition=">",
            threshold=20.0
        )
        alert.machines.add(machine)

        # 2. Add triggering data
        now = timezone.now()
        # Create a bucket for the current hour
        base_date = now.replace(minute=0, second=0, microsecond=0)
        
        # Readings for the last 2 minutes, all > 20.0
        readings = [
            {"value": 25.0, "timestamp": (now - timedelta(seconds=10)).isoformat(), "frequency": 60},
            {"value": 26.0, "timestamp": (now - timedelta(seconds=40)).isoformat(), "frequency": 60},
        ]
        
        Data.objects.create(
            machineId=machine,
            channelId=channel,
            type="temperature",
            serial_machine=machine.serial,
            frequency="1_minutes",
            base_date=base_date,
            readings=readings,
            count=len(readings)
        )

        # 3. Mock trigger_alert to check if it's called
        mock_trigger = mocker.patch('core.tasks.alerts.trigger_alert')

        # 4. Run Task
        result = monitor_alerts_task()
        
        # 5. Assertions
        assert result == "Alert monitoring complete."
        assert mock_trigger.called
        
        # Verify history record
        assert AlertHistory.objects.count() == 1
        
        # Verify state record
        from core.models import AlertState
        state = AlertState.objects.get(alert=alert, machine=machine)
        assert state.current_status == 'TRIGGERED'
        assert state.last_condition_met_at is not None

    def test_monitor_alerts_task_no_trigger_low_value(self, mocker):
        channel = Channel.objects.create(name="Temp")
        machine = Machine.objects.create(serial="MT2", Name="Machine Test 2")
        
        alert = Alert.objects.create(
            name="Low Value Alert",
            duration=60,
            data_frequency="1_minutes"
        )
        AlertCriteria.objects.create(
            alert=alert, channel=channel, condition=">", threshold=20.0
        )
        alert.machines.add(machine)

        now = timezone.now()
        readings = [
            {"value": 15.0, "timestamp": (now - timedelta(seconds=10)).isoformat(), "frequency": 60},
        ]
        
        Data.objects.create(
            machineId=machine, channelId=channel, type="temp", serial_machine="MT2",
            frequency="1_minutes", base_date=now.replace(minute=0, second=0),
            readings=readings, count=len(readings)
        )

        mock_trigger = mocker.patch('core.tasks.alerts.trigger_alert')
        monitor_alerts_task()
        
        assert not mock_trigger.called
