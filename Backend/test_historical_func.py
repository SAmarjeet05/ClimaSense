#!/usr/bin/env python3
"""Test the get_historical_data function directly"""
import sys
sys.path.insert(0, '/c/Old Data/Amarjeet/AI-Based Climate Change Data Analysis System/Backend')

from app.services import ml_service_v2 as ml_service

# Test the function
historical = ml_service.get_historical_data("Mumbai", 6, years_back=20)
print("Historical data returned:")
print(f"  Count: {len(historical)}")
if len(historical) > 0:
    print("\n  First 3:")
    for item in historical[:3]:
        print(f"    {item}")
    print("\n  Last 3:")
    for item in historical[-3:]:
        print(f"    {item}")
else:
    print("  No data returned!")
