#!/usr/bin/env python3
"""
Test Open-Meteo API connectivity and response
"""
import requests
import json
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

print("=" * 80)
print("TESTING OPEN-METEO API CONNECTIVITY")
print("=" * 80)

# Test 1: Simple direct request without retry
print("\n1️⃣  DIRECT REQUEST (no retries):")
print("-" * 80)
try:
    print("Making request to: https://api.open-meteo.com/v1/forecast")
    print("  Params: latitude=28.7041, longitude=77.1025 (Delhi)")
    print("  Timeout: 5 seconds connect, 15 seconds read")
    
    start = time.time()
    response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": 28.7041,
            "longitude": 77.1025,
            "current_weather": True,
        },
        timeout=(5, 15)
    )
    elapsed = time.time() - start
    
    print(f"\n✅ Response received in {elapsed:.2f}s")
    print(f"   Status Code: {response.status_code}")
    print(f"   Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Response keys: {list(data.keys())}")
        if "current_weather" in data:
            print(f"   Current weather: {data['current_weather']}")
        else:
            print(f"   Full response (first 500 chars):")
            print(f"   {str(data)[:500]}")
    else:
        print(f"   Response: {response.text[:200]}")
        
except requests.exceptions.Timeout as e:
    print(f"❌ TIMEOUT: {e}")
except requests.exceptions.ConnectionError as e:
    print(f"❌ CONNECTION ERROR: {e}")
except requests.exceptions.RequestException as e:
    print(f"❌ REQUEST ERROR: {e}")
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 2: With retry logic
print("\n\n2️⃣  WITH RETRY LOGIC:")
print("-" * 80)
try:
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    
    print("Session created with retry strategy:")
    print("  Total retries: 3")
    print("  Backoff factor: 1s")
    print("  Retry on: 429, 500, 502, 503, 504")
    print("\nMaking request...")
    
    start = time.time()
    response = session.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": 28.7041,
            "longitude": 77.1025,
            "current_weather": True,
        },
        timeout=(5, 15)
    )
    elapsed = time.time() - start
    
    print(f"\n✅ Response received in {elapsed:.2f}s")
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Current weather: {data.get('current_weather', 'N/A')}")
    else:
        print(f"   Response: {response.text[:200]}")
        
except requests.exceptions.Timeout as e:
    print(f"❌ TIMEOUT: {e}")
except requests.exceptions.ConnectionError as e:
    print(f"❌ CONNECTION ERROR: {e}")
except requests.exceptions.RequestException as e:
    print(f"❌ REQUEST ERROR: {e}")
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 3: Test multiple cities quickly
print("\n\n3️⃣  TESTING MULTIPLE CITIES (sequential):")
print("-" * 80)

test_cities = {
    "Delhi": (28.7041, 77.1025),
    "Mumbai": (19.0760, 72.8777),
    "Bangalore": (12.9716, 77.5946),
}

session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)

for city, (lat, lon) in test_cities.items():
    try:
        print(f"\n{city} ({lat}, {lon})... ", end="", flush=True)
        start = time.time()
        response = session.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current_weather": True,
            },
            timeout=(5, 15)
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            temp = data.get("current_weather", {}).get("temperature", "N/A")
            print(f"✅ {temp}°C ({elapsed:.2f}s)")
        else:
            print(f"❌ Status {response.status_code}")
    except Exception as e:
        print(f"❌ {type(e).__name__}: {str(e)[:50]}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
