import json
import random
import time
import uuid
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

# Configuration
BROKER = "localhost"
PORT = 1883
SERIAL_MACHINE = "SER_V1_004"
DEFAULT_FREQUENCY = "1_minutes"

# Sensor definitions with realistic ranges
SENSORS = {
    "voltage": {"min": 210.0, "max": 240.0, "unit": "V"},
    "current": {"min": 0.0, "max": 15.0, "unit": "A"},
    "temperature": {"min": 15.0, "max": 35.0, "unit": "°C"},
    "humidity": {"min": 30.0, "max": 80.0, "unit": "%"},
    "power": {"min": 0.0, "max": 3500.0, "unit": "W"},
}

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected to broker successfully (code {rc})")
    else:
        print(f"Failed to connect, return code {rc}")

def run():
    # Callback API version 1 is used to match previous implementation
    client = mqtt.Client()
    client.on_connect = on_connect

    try:
        client.connect(BROKER, PORT, 60)
    except Exception as e:
        print(f"Failed to connect to broker: {e}")
        return

    client.loop_start()
    print(f"Starting simulation for serial: {SERIAL_MACHINE}")
    print(f"Variables: {', '.join(SENSORS.keys())}")

    try:
        while True:
            # Randomly decide which sensors to send in this batch (at least one)
            types_to_send = random.sample(list(SENSORS.keys()), random.randint(1, len(SENSORS)))
            
            # Since the current backend expects a list of entries and processes them one by one,
            # and DataBucketManager creates buckets by type, we can send them in a single batch
            # or multiple batches. Let's send them in one batch for efficiency.
            batch = []
            now = datetime.now(timezone.utc).isoformat()
            
            for d_type in types_to_send:
                config = SENSORS[d_type]
                value = round(random.uniform(config["min"], config["max"]), 2)
                
                payload = {
                    "date_of_capture": now,
                    "frequency": DEFAULT_FREQUENCY,
                    "value": value,
                    "type": d_type,
                    "serial_machine": SERIAL_MACHINE,
                }
                batch.append(payload)

            # Using a random UUID for the topic machine ID part to simulate different senders
            # while keeping the data linked to SERIAL_MACHINE
            machine_id = str(uuid.uuid4())
            topic = f"machine/{machine_id}/data"
            
            client.publish(topic, json.dumps(batch))
            
            summary = ", ".join([f"{item['type']}: {item['value']}" for item in batch])
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Published to {topic}: {summary}")

            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nStopping simulation...")
        client.disconnect()
        client.loop_stop()
    except Exception as e:
        print(f"Error during simulation: {e}")

if __name__ == "__main__":
    run()
