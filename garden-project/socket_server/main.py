import paho.mqtt.client as mqtt
import json
import os
from logger import logger

# Configuration from environment variables
MQTT_HOST = os.environ.get('MQTT_HOST', 'localhost')
MQTT_PORT = int(os.environ.get('MQTT_PORT', 1883))
TOPIC_MACHINE_DATA = "machine/+/data"
TOPIC_SUBSCRIPTIONS = "machine/+/subscribe"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info(f"Connected to MQTT Broker at {MQTT_HOST}:{MQTT_PORT}")
        # Subscribe to all machine data and subscription requests
        client.subscribe(TOPIC_MACHINE_DATA)
        client.subscribe(TOPIC_SUBSCRIPTIONS)
        logger.info(f"Subscribed to topics: {TOPIC_MACHINE_DATA}, {TOPIC_SUBSCRIPTIONS}")
    else:
        logger.error(f"Failed to connect to MQTT Broker, return code {rc}")

def on_message(client, userdata, msg):
    try:
        topic = msg.topic
        payload = json.loads(msg.payload.decode())
        logger.info(f"Received message on {topic}: {payload}")

        if "subscribe" in topic:
            # Handle subscription logic if needed (e.g., logging or database entry)
            machine_id = topic.split('/')[1]
            logger.info(f"Subscription request received for machine: {machine_id}")
        
        elif "data" in topic:
            # Process machine data
            machine_id = topic.split('/')[1]
            logger.info(f"Data update for machine {machine_id}: {payload}")
            # Here you could broadcast to other MQTT clients or save to DB

    except Exception as e:
        logger.error(f"Error processing message: {e}")

def run_server():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        logger.info(f"Connecting to MQTT Broker at {MQTT_HOST}...")
        client.connect(MQTT_HOST, MQTT_PORT, 60)
        client.loop_forever()
    except Exception as e:
        logger.error(f"MQTT Server Error: {e}")

if __name__ == '__main__':
    run_server()
