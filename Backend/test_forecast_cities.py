#!/usr/bin/env python3
"""Test forecast endpoint with multiple cities"""
import requests
import json

BASE_URL = "http://localhost:8000"

cities_to_test = ["Delhi", "Bangalore", "Chennai", "Kolkata"]

for city in cities_to_test:
    try:
        response = requests.get(
            f"{BASE_URL}/api/forecast",
            params={
                "region": city,
                "month": 6,
                "years_ahead": 2
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ {city}: {data['count']['historical']} historical, {data['count']['predicted']} predicted")
        else:
            print(f"\n❌ {city}: Status {response.status_code}")
            print(f"   Error: {response.json().get('detail', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n❌ {city}: {e}")
