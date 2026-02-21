import requests

BASE_URL = "http://localhost:8000/api"

def get_auth_token():
    url = f"{BASE_URL}/token/"
    payload = {
        "username": "admin",
        "password": "admin123"
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()["access"]
    raise Exception(f"Authentication failed: {response.text}")

def get_headers():
    token = get_auth_token()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
