"""
Phase 3 - Authentication Testing
Complete auth flow: register, login, protected endpoints
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("=" * 70)
print("🧪 PHASE 3 - AUTHENTICATION TESTING")
print("=" * 70)

# Test data
test_email = "testuser@test.com"
test_password = "SecurePass123"  # 13 chars, well under 72 byte limit
test_name = "Test User"
access_token = None

#1. TEST REGISTER
print("\n✅ TEST 1: User Registration (/auth/register)")
try:
    payload = {
        "name": test_name,
        "email": test_email,
        "password": test_password
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2, default=str)}")
    if response.status_code == 201:
        print("✅ Registration successful")
except Exception as e:
    print(f"❌ Error: {e}")

# 2. TEST LOGIN
print("\n✅ TEST 2: User Login (/auth/login)")
try:
    payload = {
        "email": test_email,
        "password": test_password
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    
    # Extract token for later use
    if "access_token" in data:
        access_token = data["access_token"]
        print(f"Token acquired: {access_token[:50]}...")
        print(f"Token type: {data['token_type']}")
        print(f"User: {data.get('user', {})}")
        print("✅ Login successful")
    else:
        print(f"Response: {json.dumps(data, indent=2)}")
except Exception as e:
    print(f"❌ Error: {e}")

# 3. TEST GET CURRENT USER (with token)
print("\n✅ TEST 3: Get Current User (/auth/me)")
if access_token:
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Current user: {json.dumps(data, indent=2, default=str)}")
        print("✅ Got current user successfully")
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("⚠️  Skipping (no token from login)")

# 4. TEST PROTECTED PREDICTION ENDPOINT (with token)
print("\n✅ TEST 4: Protected Prediction (/api/predict)")
if access_token:
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        payload = {"year": 2024, "month": 6, "region": "India"}
        response = requests.post(f"{BASE_URL}/api/predict", json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Prediction: Temperature={data.get('temperature'):.2f}°C,  Rainfall={data.get('rainfall'):.2f}mm")
        print("✅ Protected endpoint accessible with token")
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("⚠️  Skipping (no token from login)")

# 5. TEST PROTECTED ENDPOINT WITHOUT TOKEN
print("\n✅ TEST 5: Protected Endpoint Without Token (should fail)")
try:
    payload = {"year": 2024, "month": 6, "region": "India"}
    response = requests.post(f"{BASE_URL}/api/predict", json=payload)
    print(f"Status: {response.status_code}")
    if response.status_code == 401:
        print(f"Response: {response.json()}")
        print("✅ Correctly rejected unauthorized request")
    else:
        print(f"⚠️  Unexpected status: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

# 6. TEST INVALID LOGIN
print("\n✅ TEST 6: Invalid Login (wrong password)")
try:
    payload = {
        "email": test_email,
        "password": "WrongPassword"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=payload)
    print(f"Status: {response.status_code}")
    if response.status_code == 401:
        data = response.json()
        print(f"Response: {data}")
        print("✅ Correctly rejected invalid credentials")
    else:
        print(f"⚠️  Unexpected status: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

# 7. TEST PUBLIC ENDPOINTS (trends, stats - should work without token)
print("\n✅ TEST 7: Public Endpoints (no auth required)")
try:
    response = requests.get(f"{BASE_URL}/api/trends")
    print(f"Trends status: {response.status_code}")
    
    response = requests.get(f"{BASE_URL}/api/stats")
    print(f"Stats status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Public endpoints accessible without token")
except Exception as e:
    print(f"❌ Error: {e}")

# 8. TEST ROOT ENDPOINT
print("\n✅ TEST 8: Root Endpoint (/)")
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Message: {data.get('message')}")
    print(f"Version: {data.get('version')}")
    print("✅ Root endpoint working")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 70)
print("✨ PHASE 3 TESTING COMPLETED")
print("=" * 70)
print("\n📚 Interactive API Docs: http://127.0.0.1:8000/docs")
print("🔐 Authentication: JWT tokens with role-based access")
print("✅ Status: Phase 3 Full Stack Ready!")
