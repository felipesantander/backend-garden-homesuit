import requests
import time
import json
from auth import get_headers, BASE_URL

def test_machine_crud():
    print("\n--- Testing Machine CRUD ---")
    headers = get_headers()
    endpoint = f"{BASE_URL}/machines/"
    
    # 1. Create (POST)
    timestamp = int(time.time())
    serial = f"TEST_SN_{timestamp}"
    payload = {
        "serial": serial,
        "Name": f"Machine {timestamp}"
    }
    print(f"Creating machine with serial {serial}...")
    response = requests.post(endpoint, json=payload, headers=headers)
    assert response.status_code == 201, f"Create failed: {response.text}"
    machine = response.json()
    machine_id = machine["machineId"]
    print(f"Created successfully. ID: {machine_id}")
    
    # 2. List (GET Index)
    print("Testing GET /machines/ (index)...")
    response = requests.get(endpoint, headers=headers)
    assert response.status_code == 200, f"List failed: {response.text}"
    print(f"List successful. Found {len(response.json())} machines.")
    
    # 3. Read (GET Detail)
    detail_url = f"{endpoint}{machine_id}/"
    print(f"Testing GET /machines/{machine_id}/ (detail)...")
    response = requests.get(detail_url, headers=headers)
    assert response.status_code == 200, f"Read failed: {response.text}"
    print(f"Read successful: {response.json()['Name']}")
    
    # 4. Update (PATCH)
    new_name = f"Updated Machine {timestamp}"
    print(f"Updating machine name to {new_name}...")
    response = requests.patch(detail_url, json={"Name": new_name}, headers=headers)
    assert response.status_code == 200, f"Update failed: {response.text}"
    print(f"Update successful. New name: {response.json()['Name']}")
    
    # 5. Delete (DELETE)
    print(f"Deleting machine {machine_id}...")
    response = requests.delete(detail_url, headers=headers)
    assert response.status_code == 204, f"Delete failed: {response.text}"
    print("Delete successful.")

if __name__ == "__main__":
    try:
        test_machine_crud()
        print("\nAll Machine CRUD tests PASSED!")
    except Exception as e:
        print(f"\nTest FAILED: {e}")
