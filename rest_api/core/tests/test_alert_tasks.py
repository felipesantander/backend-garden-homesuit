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
        
        # Readings for the last 2 minutes, all > 20.0 (MongoDB format is {v: float, t: str, f: str})
        readings = [
            {"v": 25.0, "t": (now - timedelta(seconds=10)).isoformat(), "f": 60},
            {"v": 26.0, "t": (now - timedelta(seconds=40)).isoformat(), "f": 60},
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

        # 3. Mock send_whatsapp_message to check if it's called
        mock_send = mocker.patch('core.tasks.alerts.send_whatsapp_message')

        # 4. Run Task
        result = monitor_alerts_task()
        
        # 5. Assertions
        assert result == "Alert monitoring complete."
        # No contacts where added to alert but we just check the function ran ok. 
        # For simplicity, if AlertHistory.count == 1 we know trigger_alert was fired.
        
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
            {"v": 15.0, "t": (now - timedelta(seconds=10)).isoformat(), "f": 60},
        ]
        
        Data.objects.create(
            machineId=machine, channelId=channel, type="temp", serial_machine="MT2",
            frequency="1_minutes", base_date=now.replace(minute=0, second=0),
            readings=readings, count=len(readings)
        )

        mock_send = mocker.patch('core.tasks.alerts.send_whatsapp_message')
        monitor_alerts_task()
        
        assert AlertHistory.objects.count() == 0

    def test_monitor_alerts_task_and_or_logic(self, mocker):
        channel_a = Channel.objects.create(name="A")
        channel_b = Channel.objects.create(name="B")
        channel_c = Channel.objects.create(name="C")
        machine = Machine.objects.create(serial="MT3", Name="Logic Test")
        
        alert = Alert.objects.create(
            name="Logic Alert",
            duration=60,
            data_frequency="1_minutes"
        )
        alert.machines.add(machine)
        
        # Criteria: (A > 10 AND B > 10) OR C > 10
        AlertCriteria.objects.create(alert=alert, channel=channel_a, condition=">", threshold=10.0, order=0)
        AlertCriteria.objects.create(alert=alert, channel=channel_b, condition=">", threshold=10.0, logical_operator="AND", order=1)
        AlertCriteria.objects.create(alert=alert, channel=channel_c, condition=">", threshold=10.0, logical_operator="OR", order=2)
        
        now = timezone.now()
        readings_a = [{"v": 5.0, "t": (now - timedelta(seconds=10)).isoformat()}] # Fails A > 10
        readings_b = [{"v": 5.0, "t": (now - timedelta(seconds=10)).isoformat()}] # Fails B > 10
        readings_c = [{"v": 15.0, "t": (now - timedelta(seconds=10)).isoformat()}] # Passes C > 10
        
        base_date = now.replace(minute=0, second=0, microsecond=0)
        for ch, rd in [(channel_a, readings_a), (channel_b, readings_b), (channel_c, readings_c)]:
            Data.objects.create(
                machineId=machine, channelId=ch, type="test", serial_machine="MT3",
                frequency="1_minutes", base_date=base_date,
                readings=rd, count=1
            )
            
        mock_send = mocker.patch('core.tasks.alerts.send_whatsapp_message')
        monitor_alerts_task()
        
        # (False AND False) OR True -> True, so it should trigger
        assert AlertHistory.objects.count() == 1
