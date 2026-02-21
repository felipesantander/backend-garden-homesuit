import requests
import time
import uuid
from auth import get_headers, BASE_URL

def test_data_crud():
    print("\n--- Testing Data CRUD ---")
    headers = get_headers()
    
    # Pre-requisite: Create Machine and Channel
    print("Setting up pre-requisites (Machine & Channel)...")
    m_res = requests.post(f"{BASE_URL}/machines/", json={"serial": f"DATA_SN_{int(time.time())}", "Name": "Data Test Mach"}, headers=headers)
    c_res = requests.post(f"{BASE_URL}/channels/", json={"name": f"CH_DATA_{int(time.time())}"}, headers=headers)
    
    machine_id = m_res.json()["machineId"]
    channel_id = c_res.json()["idChannel"]
    serial = m_res.json()["serial"]

    endpoint = f"{BASE_URL}/data/"
    
    # 1. Create (POST)
    data_id = f"DATA_{int(time.time())}"
    payload = {
        "dataId": data_id,
        "frequency": 1.5,
        "value": 42.0,
        "type": "float",
        "serial_machine": serial,
        "machineId": machine_id,
        "channelId": channel_id
    }
    print(f"Creating data entry {data_id}...")
    response = requests.post(endpoint, json=payload, headers=headers)
    assert response.status_code == 201, f"Create failed: {response.text}"
    data_obj = response.json()
    id_data = data_obj["idData"]
    print(f"Created successfully. Internal ID: {id_data}")
    
    # 2. Read (GET Detail)
    detail_url = f"{endpoint}{id_data}/"
    print(f"Testing GET /data/{id_data}/ (detail)...")
    response = requests.get(detail_url, headers=headers)
    assert response.status_code == 200, f"Read failed: {response.text}"
    print(f"Read successful. Value: {response.json()['value']}")
    
    # 3. Update (PATCH)
    print("Updating value to 99.9...")
    response = requests.patch(detail_url, json={"value": 99.9}, headers=headers)
    assert response.status_code == 200, f"Update failed: {response.text}"
    print(f"Update successful. New value: {response.json()['value']}")
    
    # 4. Delete (DELETE)
    print(f"Deleting data {id_data}...")
    response = requests.delete(detail_url, headers=headers)
    assert response.status_code == 204, f"Delete failed: {response.text}"
    print("Delete successful.")

if __name__ == "__main__":
    try:
        test_data_crud()
        print("\nAll Data CRUD tests PASSED!")
    except Exception as e:
        print(f"\nTest FAILED: {e}")
