import requests
import json
from time import sleep

BASE_URL = "http://127.0.0.1:8000"

print("=" * 60)
print("🧪 PHASE 1 API TESTING")
print("=" * 60)

# Test 1: Root endpoint
print("\n✅ TEST 1: Root Endpoint (/)")
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Health check
print("\n✅ TEST 2: Health Check (/health)")
try:
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Trends endpoint
print("\n✅ TEST 3: Get Trends (/trends)")
try:
    response = requests.get(f"{BASE_URL}/trends")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Years available: {len(data['years'])} records")
    print(f"Sample - First 3 years: {data['years'][:3]}")
    print(f"Sample - First 3 temperatures: {data['temperatures'][:3]}")
    print(f"Sample - First 3 rainfalls: {data['rainfalls'][:3]}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Statistics endpoint
print("\n✅ TEST 4: Statistics (/stats)")
try:
    response = requests.get(f"{BASE_URL}/stats")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 5: Prediction endpoint
print("\n✅ TEST 5: Make Prediction (/predict)")
try:
    payload = {"year": 2024, "month": 6, "region": "India"}
    response = requests.post(f"{BASE_URL}/predict", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Prediction Input: {json.dumps(payload, indent=2)}")
    print(f"Prediction Output: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 6: Data endpoint
print("\n✅ TEST 6: Get Data (/data?limit=3)")
try:
    response = requests.get(f"{BASE_URL}/data?limit=3")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Records returned: {data['returned']}/{data['total_records']}")
    print(f"Sample records: {json.dumps(data['data'], indent=2)}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 7: Filter endpoint
print("\n✅ TEST 7: Filter Data (/filter?year=2020&month=1)")
try:
    response = requests.get(f"{BASE_URL}/filter?year=2020&month=1")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Records found: {data['total_found']}")
    print(f"Sample: {json.dumps(data['data'][:2] if data['data'] else [], indent=2)}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 8: API Info
print("\n✅ TEST 8: API Info (/info)")
try:
    response = requests.get(f"{BASE_URL}/info")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("✨ ALL TESTS COMPLETED")
print("=" * 60)
print("\n📚 Interactive API Docs: http://127.0.0.1:8000/docs")
print("🔍 ReDoc API Docs: http://127.0.0.1:8000/redoc")
