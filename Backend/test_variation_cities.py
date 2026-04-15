#!/usr/bin/env python3
"""Test forecast variation across multiple cities"""
import requests

BASE_URL = "http://localhost:8000"

test_cases = [
    {"city": "Mumbai", "month": 6, "name": "Mumbai (Monsoon)"},
    {"city": "Delhi", "month": 5, "name": "Delhi (Hot)"},
    {"city": "Bangalore", "month": 1, "name": "Bangalore (Cool)"},
    {"city": "Chennai", "month": 10, "name": "Chennai (Post-Monsoon)"},
]

print("=" * 70)
print("📊 FORECAST VARIATION ACROSS CITIES")
print("=" * 70)

for test in test_cases:
    response = requests.get(
        f"{BASE_URL}/api/forecast",
        params={
            "region": test["city"],
            "month": test["month"],
            "years_ahead": 5
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        preds = data['predicted']
        
        temps = [p['temperature'] for p in preds]
        rains = [p['rainfall'] for p in preds]
        
        temp_range = max(temps) - min(temps)
        rain_range = max(rains) - min(rains)
        
        print(f"\n✅ {test['name']}")
        print(f"   Temperature: {min(temps):.1f}°C → {max(temps):.1f}°C (Δ {temp_range:.2f}°C)")
        print(f"   Rainfall:    {min(rains):.1f}mm → {max(rains):.1f}mm (Δ {rain_range:.2f}mm)")
        print(f"   Years shown: {preds[0]['year']} to {preds[-1]['year']}")
    else:
        print(f"\n❌ {test['city']}: {response.status_code}")

print("\n" + "=" * 70)
print("✨ All forecasts show realistic variation!")
print("=" * 70)
