#!/usr/bin/env python3
"""Test forecast endpoint"""
import requests
import json

BASE_URL = "http://localhost:8000"

try:
    # Test forecast endpoint
    response = requests.get(
        f"{BASE_URL}/api/forecast",
        params={
            "region": "Mumbai",
            "month": 6,
            "years_ahead": 3
        }
    )
    
    print(f"Status Code: {response.status_code}")
    print("\nResponse:")
    print(json.dumps(response.json(), indent=2))
    
except Exception as e:
    print(f"Error: {e}")
