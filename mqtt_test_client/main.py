import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime

BROKER = "localhost"
PORT = 1883
MACHINE_ID = "MAC_001"

def on_connect(client, userdata, flags, rc):
    print(f"Connected to broker with code {rc}")

def run():
    client = mqtt.Client()
    client.on_connect = on_connect
    
    try:
        client.connect(BROKER, PORT, 60)
    except Exception as e:
        print(f"Failed to connect: {e}")
        return

    client.loop_start()
    
    try:
        while True:
            # Prepare payload matching the final schema
            payload = {
                "date_of_capture": datetime.now().isoformat(),
                "frequency": round(random.uniform(49.5, 50.5), 2),
                "value": round(random.uniform(210.0, 230.0), 2),
                "type": "voltage",
                "serial_machine": "SER_V1_001" # Serial used for lookup
            }
            
            # Using a random UUID for the topic machine ID part
            topic = f"machine/{uuid.uuid4()}/data"
            client.publish(topic, json.dumps(payload))
            print(f"Published to {topic}: {payload}")
            
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nStopping simulation...")
        client.disconnect()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
