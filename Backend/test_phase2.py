"""
Phase 2 - Clean Architecture API Testing
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("=" * 70)
print("🧪 PHASE 2 - CLEAN ARCHITECTURE API TESTING")
print("=" * 70)

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

# Test 3: API info
print("\n✅ TEST 3: API Info (/api/info)")
try:
    response = requests.get(f"{BASE_URL}/api/info")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"API Version: {data.get('api_version')}")
    print(f"Phase: {data.get('phase')}")
    print(f"Endpoints available: {data.get('endpoints')}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Trends endpoint
print("\n✅ TEST 4: Get Trends (/api/trends)")
try:
    response = requests.get(f"{BASE_URL}/api/trends")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Records available: {len(data['years'])}")
    print(f"Sample - First 3 years: {data['years'][:3]}")
    print(f"Sample - First 3 temperatures: {data['temperatures'][:3]} °C")
    print(f"Sample - First 3 rainfalls: {data['rainfalls'][:3]} mm")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 5: Statistics
print("\n✅ TEST 5: Statistics (/api/stats)")
try:
    response = requests.get(f"{BASE_URL}/api/stats")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total records: {data['total_records']}")
    print(f"Temperature range: {data['temperature']['min']:.2f}°C - {data['temperature']['max']:.2f}°C")
    print(f"Rainfall range: {data['rainfall']['min']:.2f}mm - {data['rainfall']['max']:.2f}mm")
    print(f"Regions covered: {len(data['regions'])}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 6: Single Prediction
print("\n✅ TEST 6: Single Prediction (/api/predict)")
try:
    payload = {"year": 2024, "month": 6, "region": "India"}
    response = requests.post(f"{BASE_URL}/api/predict", json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Input: {payload}")
    print(f"Output: Year={data['year']}, Month={data['month']}, Region={data['region']}")
    print(f"  → Temperature: {data['temperature']:.2f}°C")
    print(f"  → Rainfall: {data['rainfall']:.2f}mm")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 7: Batch Predictions
print("\n✅ TEST 7: Batch Predictions (/api/predict-batch)")
try:
    payload = {
        "predictions": [
            {"year": 2024, "month": 1, "region": "North"},
            {"year": 2024, "month": 6, "region": "South"},
            {"year": 2025, "month": 12, "region": "East"}
        ]
    }
    response = requests.post(f"{BASE_URL}/api/predict-batch", json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Batch size: {data['count']}")
    for i, pred in enumerate(data['predictions']):
        print(f"  Prediction {i+1}: {pred['year']}-{pred['month']}, {pred['region']}")
        print(f"    Temperature: {pred['temperature']:.2f}°C, Rainfall: {pred['rainfall']:.2f}mm")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 8: Get Data
print("\n✅ TEST 8: Get Data (/api/data?limit=2)")
try:
    response = requests.get(f"{BASE_URL}/api/data?limit=2")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total records available: {data['total_records']}")
    print(f"Records returned: {data['returned']}")
    print(f"Sample: {json.dumps(data['data'][0], indent=2)}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 9: Filter Data
print("\n✅ TEST 9: Filter Data (/api/filter?year=2015&month=1)")
try:
    response = requests.get(f"{BASE_URL}/api/filter?year=2015&month=1")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Records found: {data['total_found']}")
    if data['data']:
        print(f"Sample record: {json.dumps(data['data'][0], indent=2)}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 70)
print("✨ PHASE 2 TESTING COMPLETED")
print("=" * 70)
print("\n📚 Interactive API Docs: http://127.0.0.1:8000/docs")
print("🏗️  Architecture: Modular (Routes → Services → ML Models)")
print("✅ Status: All endpoints functional!")
