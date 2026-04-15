import requests
import json

# Test the assistant endpoint
url = "http://127.0.0.1:8000/api/assistant/query"

payload = {
    "query": "Will Delhi become hotter?",
    "user_id": None
}

try:
    response = requests.post(url, json=payload, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
