#!/usr/bin/env python3
"""Test recursive forecasting to see if we get a curve instead of flat line"""
import requests
import time

BASE_URL = "http://localhost:8000"

print("Testing Recursive Forecasting...\n")
print("⏳ This may take a moment (simulating 5 years day-by-day)...\n")

start_time = time.time()

response = requests.get(
    f"{BASE_URL}/api/forecast",
    params={
        "region": "Mumbai",
        "month": 6,
        "years_ahead": 5
    },
    timeout=60
)

elapsed = time.time() - start_time

print(f"Response Time: {elapsed:.1f}s")
print(f"Status Code: {response.status_code}\n")

if response.status_code == 200:
    data = response.json()
    
    print(f"City: {data['city']}")
    print(f"Month: {data['month']} (June)")
    print(f"Historical Records: {data['count']['historical']}")
    print(f"Predicted Records: {data['count']['predicted']}\n")
    
    if data['predicted']:
        print("📊 PREDICTED TEMPERATURES (checking for variation):")
        print("Year  | Temp    | Rainfall | Confidence")
        print("------|---------|----------|------------")
        for pred in data['predicted']:
            print(f"{pred['year']} | {pred['temperature']:6.2f}°C | {pred['rainfall']:7.2f}mm | {pred['confidence']:.0%}")
        
        # Check if flat line or curve
        temps = [p['temperature'] for p in data['predicted']]
        temp_range = max(temps) - min(temps)
        
        print(f"\n📈 Analysis:")
        print(f"   Min Temp: {min(temps):.2f}°C")
        print(f"   Max Temp: {max(temps):.2f}°C")
        print(f"   Range: {temp_range:.2f}°C")
        
        if temp_range < 0.5:
            print(f"   ❌ Still flat line (range {temp_range:.2f}°C)")
        else:
            print(f"   ✅ Got variation! (range {temp_range:.2f}°C) - FIXED!")
else:
    print(f"Error: {response.json()}")
