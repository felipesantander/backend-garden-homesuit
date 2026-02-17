import logging

from .utils import mqtt_topic

logger = logging.getLogger(__name__)


@mqtt_topic("machine/+/subscribe")
def handle_machine_subscription(_sender, **kwargs):
    topic = kwargs.get("topic")
    machine_id = topic.split("/")[1] if topic else "unknown"
    logger.info(f"Subscription request for machine {machine_id} received via MQTT")
