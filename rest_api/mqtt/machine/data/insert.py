import logging
import traceback

logger = logging.getLogger(__name__)


def _save_data_entry(payload, machine, data_type, serial_machine, data_model, config_channel_model, default_channel):
    """Helper to resolve channel and save data for a specific machine."""
    config = config_channel_model.objects.filter(machine=machine, type=data_type).first()
    channel = config.channel if config else default_channel

    data_model.objects.create(
        date_of_capture=payload["date_of_capture"],
        frequency=payload["frequency"],
        value=payload["value"],
        type=data_type,
        serial_machine=serial_machine,
        machineId=machine,
        channelId=channel,
    )
    return channel


def _process_entry(payload, topic, data_model, machine_model, config_channel_model, default_channel):
    """Internal helper to process a single data entry."""
    serial_machine = payload["serial_machine"]
    data_type = payload["type"]

    machines = machine_model.objects.filter(serial=serial_machine)
    count = machines.count()

    if count == 0:
        logger.warning(f"No machines found with serial {serial_machine}. Ignoring data.")
        return

    if count > 1:
        for machine in machines:
            channel = _save_data_entry(
                payload, machine, data_type, serial_machine, data_model, config_channel_model, default_channel
            )
            logger.info(
                f"Data saved for machine {machine.machineId} (Serial: {serial_machine}) on channel {channel.idChannel}"
            )
    else:
        machine = machines.first()
        channel = _save_data_entry(
            payload, None, data_type, serial_machine, data_model, config_channel_model, default_channel
        )
        logger.info(f"Data saved for serial {serial_machine} (single machine) on channel {channel.idChannel}")


def insert_data(data, topic):
    """Main function to insert a batch of data entries."""
    from core.models import ConfigurationChannel, Data, Machine

    try:
        logger.info(f"Processing batch of {len(data)} entries on topic {topic}")
        for entry in data:
            _process_entry(entry, topic, Data, Machine, ConfigurationChannel, None)

    except Exception as e:
        logger.error(f"Error processing MQTT message on {topic}: {e}")
        logger.error(traceback.format_exc())
