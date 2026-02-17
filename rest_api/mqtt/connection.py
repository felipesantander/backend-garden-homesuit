import logging

from django.dispatch import receiver
from dmqtt.signals import connect, message

logger = logging.getLogger(__name__)


@receiver(connect)
def on_mqtt_connect(sender, **_kwargs):
    logger.info("Connected successfully to MQTT Broker via django-mqtt")
    sender.subscribe("machine/+/data")
    sender.subscribe("machine/+/subscribe")


@receiver(message)
def on_mqtt_message(_sender, **kwargs):
    logger.debug(f"DEBUG: Signal message received. Arguments: {list(kwargs.keys())}")

    msg = kwargs.get("msg")
    if msg:
        topic = msg.topic
        payload = msg.payload.decode() if isinstance(msg.payload, bytes) else msg.payload
        logger.debug(f"DEBUG: Topic from msg: {topic}, Payload: {payload}")
    else:
        logger.debug("DEBUG: No 'msg' object found in signal arguments")
