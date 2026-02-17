import json
import logging

from .machine.data.insert import insert_data
from .utils import mqtt_topic
from .validations import mqtt_input_validator

logger = logging.getLogger(__name__)


@mqtt_topic("machine/+/data")
def handle_machine_data(sender, **kwargs):
    """Main MQTT handler for machine data."""
    if not mqtt_input_validator.validate(kwargs):
        logger.error(f"Invalid MQTT handler input: {mqtt_input_validator.errors}")
        return

    # Use the normalized document (coerced types)
    normalized = mqtt_input_validator.document
    topic = normalized.get("topic")
    data = normalized.get("data")

    # Call the modular insertion logic
    insert_data(data, topic)

    # Send acknowledgment back to the sender
    result_topic = f"{topic}/result"
    payload = {"status": "ok", "message": "Insertion successful"}
    sender.publish(result_topic, json.dumps(payload))
    logger.info(f"Acknowledgment sent to {result_topic}")
