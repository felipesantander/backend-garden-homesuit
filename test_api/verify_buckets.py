import requests
import uuid
import time
from datetime import datetime, timezone

BASE_URL = "http://localhost:8000/api"

def get_token():
    res = requests.post(f"{BASE_URL}/token/", json={
        "username": "admin",
        "password": "adminpassword"
    })
    return res.json()["access"]

def test_bucket_ingest():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # IDs from previous setup or seeds
    machine_id = "f0a1b2c3-d4e5-4f6a-8b9c-0d1e2f3a4b5c"
    channel_id = "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d"
    
    print("--- Testing Bucket Ingestion ---")
    
    # 3 readings in the same minute
    for i in range(3):
        payload = {
            "machineId": machine_id,
            "channelId": channel_id,
            "type": "test_bucket",
            "value": 20.0 + i,
            "frequency": "5_seconds",
            "serial_machine": "TEST_SERIAL",
            "date_of_capture": datetime.now(timezone.utc).isoformat()
        }
        res = requests.post(f"{BASE_URL}/data/ingest/", json=payload, headers=headers)
        print(f"Ingest {i+1}: {res.status_code} - {res.json()}")
        time.sleep(0.5)

    print("\nCheck MongoDB for a single document with count=3 and 3 readings.")

if __name__ == "__main__":
    test_bucket_ingest()
