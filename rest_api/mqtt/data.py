import json
import logging
from datetime import datetime
from .utils import mqtt_topic
from cerberus import Validator

logger = logging.getLogger(__name__)

# Cerberus schema for machine data
DATA_SCHEMA = {
    'date_of_capture': {'type': 'datetime', 'required': True},
    'frequency': {'type': 'float', 'required': True},
    'value': {'type': 'float', 'required': True},
    'type': {'type': 'string', 'required': True},
    'serial_machine': {'type': 'string', 'required': True},
}

v = Validator(DATA_SCHEMA)

def _process_entry(payload, topic, Data, Machine, ConfigurationChannel, default_channel):
    """Internal helper to process a single data entry."""
    # Pre-parse date_of_capture if it's a string
    if 'date_of_capture' in payload and isinstance(payload['date_of_capture'], str):
        try:
            payload['date_of_capture'] = datetime.fromisoformat(payload['date_of_capture'])
        except ValueError:
            pass # Let validator handle it

    if not v.validate(payload):
        logger.error(f"Invalid payload on topic {topic}: {v.errors}")
        return

    logger.debug(f"Received valid machine data on topic {topic}: {payload}")
    
    # Infer serial from payload
    serial_machine = payload['serial_machine']
    data_type = payload['type']
    
    # Get all machines with this serial
    machines = Machine.objects.filter(serial=serial_machine)
    count = machines.count()
    
    if count == 0:
        logger.warning(f"No machines found with serial {serial_machine}. Ignoring data.")
        return

    if count > 1:
        for machine in machines:
            # Resolve channel dynamically
            config = ConfigurationChannel.objects.filter(machine=machine, type=data_type).first()
            channel = config.channel if config else default_channel
            
            Data.objects.create(
                date_of_capture=payload['date_of_capture'],
                frequency=payload['frequency'],
                value=payload['value'],
                type=data_type,
                serial_machine=serial_machine,
                machineId=machine, # Add machineId because there are multiple
                channelId=channel
            )
            logger.info(f"Data saved for machine {machine.machineId} (Serial: {serial_machine}) on channel {channel.idChannel}")
    else:
        # Only one machine found
        machine = machines.first()
        # Resolve channel dynamically
        config = ConfigurationChannel.objects.filter(machine=machine, type=data_type).first()
        channel = config.channel if config else default_channel

        Data.objects.create(
            date_of_capture=payload['date_of_capture'],
            frequency=payload['frequency'],
            value=payload['value'],
            type=data_type,
            serial_machine=serial_machine,
            machineId=None, # Explicitly None for single match as requested before
            channelId=channel
        )
        logger.info(f"Data saved for serial {serial_machine} (single machine) on channel {channel.idChannel}")


@mqtt_topic("machine/+/data")
def handle_machine_data(sender, **kwargs):
    topic = kwargs.get('topic')
    data = kwargs.get('data')
    
    from core.models import Data, Machine, Channel, ConfigurationChannel
    try:
        # We no longer strictly need a default_channel fallback if None is valid
        # However, we still fetch it just in case or if there's a reason to keep it as a 'potential' fallback.
        # But based on the user's request, let's keep it simple: use None if config is missing.
        
        if isinstance(data, list):
            logger.info(f"Processing batch of {len(data)} entries on topic {topic}")
            for entry in data:
                _process_entry(entry, topic, Data, Machine, ConfigurationChannel, None)
        elif isinstance(data, dict):
            _process_entry(data, topic, Data, Machine, ConfigurationChannel, None)
        else:
            logger.error(f"Unexpected data type received on topic {topic}: {type(data)}")

    except Exception as e:
        logger.error(f"Error processing MQTT message on {topic}: {e}")
