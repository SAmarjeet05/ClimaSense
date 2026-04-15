#!/usr/bin/env python
"""Quick test of the backend API"""
import requests
import json

try:
    r = requests.get('http://localhost:8000/api/realtime-weather')
    print(f'✅ Backend OK: {r.status_code}')
    data = r.json()
    print(f'📍 Cities: {len(data.get("regions", []))}')
    if data.get("regions"):
        print(f'🌡️  First city: {data["regions"][0]["state"]} - {data["regions"][0]["temperature"]}°C')
except Exception as e:
    print(f'❌ Error: {e}')
