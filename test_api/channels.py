import requests
import time
from auth import get_headers, BASE_URL

def test_channel_crud():
    print("\n--- Testing Channel CRUD ---")
    headers = get_headers()
    endpoint = f"{BASE_URL}/channels/"
    
    # 1. Create (POST)
    timestamp = int(time.time())
    name = f"Channel_{timestamp}"
    payload = {
        "name": name
    }
    print(f"Creating channel with name {name}...")
    response = requests.post(endpoint, json=payload, headers=headers)
    assert response.status_code == 201, f"Create failed: {response.text}"
    channel = response.json()
    channel_id = channel["idChannel"]
    print(f"Created successfully. ID: {channel_id}")
    
    # 2. List (GET Index)
    print("Testing GET /channels/ (index)...")
    response = requests.get(endpoint, headers=headers)
    assert response.status_code == 200, f"List failed: {response.text}"
    print(f"List successful. Found {len(response.json())} channels.")
    
    # 3. Read (GET Detail)
    detail_url = f"{endpoint}{channel_id}/"
    print(f"Testing GET /channels/{channel_id}/ (detail)...")
    response = requests.get(detail_url, headers=headers)
    assert response.status_code == 200, f"Read failed: {response.text}"
    print(f"Read successful: {response.json()['name']}")
    
    # 4. Update (PATCH)
    new_name = f"Updated_Channel_{timestamp}"
    print(f"Updating channel name to {new_name}...")
    response = requests.patch(detail_url, json={"name": new_name}, headers=headers)
    assert response.status_code == 200, f"Update failed: {response.text}"
    print(f"Update successful. New name: {response.json()['name']}")
    
    # 5. Delete (DELETE)
    print(f"Deleting channel {channel_id}...")
    response = requests.delete(detail_url, headers=headers)
    assert response.status_code == 204, f"Delete failed: {response.text}"
    print("Delete successful.")

if __name__ == "__main__":
    try:
        test_channel_crud()
        print("\nAll Channel CRUD tests PASSED!")
    except Exception as e:
        print(f"\nTest FAILED: {e}")
