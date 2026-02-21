import logging
import traceback

from core.models import ConfigurationChannel, Data, Machine, MachineCandidate
from core.models.data_manager import DataBucketManager

logger = logging.getLogger(__name__)


def _save_data_entry(payload, machine, data_type, serial_machine, default_channel):
    """Helper to resolve channel and save data for a specific machine."""
    channel = default_channel
    if machine:
        config = ConfigurationChannel.objects.filter(machine=machine, type=data_type).first()
        if config:
            channel = config.channel

    DataBucketManager.add_reading(
        machine=machine,
        channel=channel,
        data_type=data_type,
        value=payload["value"],
        timestamp=payload["date_of_capture"],
        frequency=payload["frequency"],
        serial_machine=serial_machine
    )
    return channel


def _process_entry(payload, _topic, default_channel):
    """Internal helper to process a single data entry."""
    serial_machine = payload["serial_machine"]
    data_type = payload["type"]

    # Since unique=True is enforced, we use .first()
    machine = Machine.objects.filter(serial=serial_machine).first()

    if not machine:
        candidate, _ = MachineCandidate.objects.get_or_create(serial=serial_machine)
        if data_type not in candidate.types:
            # Create a new list to ensure the JSONField detects the change
            candidate.types = list({*candidate.types, data_type})
            candidate.save()
            logger.info(f"Updated MachineCandidate {serial_machine} with new type: {data_type}")

    channel = _save_data_entry(payload, machine, data_type, serial_machine, default_channel)

    if machine:
        logger.info(
            f"Data saved for machine {machine.machineId} (Serial: {serial_machine}) on channel {channel.idChannel if channel else 'None'}"
        )
    else:
        logger.info(
            f"Data saved for serial {serial_machine} (anonymous) on channel {channel.idChannel if channel else 'None'}"
        )


def insert_data(data, topic):
    """Main function to insert a batch of data entries."""

    try:
        logger.info(f"Processing batch of {len(data)} entries on topic {topic}")
        for entry in data:
            _process_entry(entry, topic, None)

    except Exception as e:
        logger.error(f"Error processing MQTT message on {topic}: {e}")
        logger.error(traceback.format_exc())
