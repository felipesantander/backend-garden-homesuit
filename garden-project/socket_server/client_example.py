import paho.mqtt.client as mqtt
import json
import time

# Configuration
BROKER_HOST = "localhost"
BROKER_PORT = 1883
MACHINE_ID = "MAC_001"
TOPIC_DATA = f"machine/{MACHINE_ID}/data"
TOPIC_SUBSCRIBE = f"machine/{MACHINE_ID}/subscribe"

# Create an MQTT client
client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Conectado al Broker MQTT en {BROKER_HOST}")
        # Enviar un mensaje inicial de 'suscripción' o presencia
        payload = {"status": "online", "machineId": MACHINE_ID}
        client.publish(TOPIC_SUBSCRIBE, json.dumps(payload))
        print(f"Mensaje de suscripción enviado a {TOPIC_SUBSCRIBE}")
    else:
        print(f"Error de conexión, código: {rc}")

def send_simulated_data():
    """Simula el envío de datos desde una máquina vía MQTT"""
    print(f"Publicando datos en {TOPIC_DATA} cada 5 segundos...")
    try:
        while True:
            payload = {
                'serial_machine': MACHINE_ID,
                'temperature': 23.8,
                'humidity': 55,
                'timestamp': time.time()
            }
            print(f"Publicando: {payload}")
            client.publish(TOPIC_DATA, json.dumps(payload))
            time.sleep(5)
    except KeyboardInterrupt:
        print("Deteniendo cliente...")

if __name__ == '__main__':
    client.on_connect = on_connect
    
    try:
        client.connect(BROKER_HOST, BROKER_PORT, 60)
        # Iniciar el loop en un hilo separado para no bloquear
        client.loop_start()
        
        send_simulated_data()
        
    except Exception as e:
        print(f"No se pudo conectar al broker: {e}")
    finally:
        client.loop_stop()
        client.disconnect()
