import pandas as pd
from app.services import ml_service_v2

print("\n=== Testing get_annual_temperature_trends ===")
result = ml_service_v2.get_annual_temperature_trends()
print(f"Result keys: {list(result.keys())}")
print(f"Years count: {len(result.get('years', []))}")
print(f"Data count: {result.get('count', 0)}")
print(f"First 10 years: {result.get('years', [])[:10]}")
print(f"First 10 temps: {result.get('temperatures', [])[:10]}")

print("\n=== Testing get_annual_rainfall_trends ===")
result = ml_service_v2.get_annual_rainfall_trends()
print(f"Result keys: {list(result.keys())}")
print(f"Years count: {len(result.get('years', []))}")
print(f"Data count: {result.get('count', 0)}")
print(f"First 10 years: {result.get('years', [])[:10]}")
print(f"First 10 rainfalls: {result.get('rainfall_mm', []) if 'rainfall_mm' in result else result.get('rainfalls', [])[:10]}")

print("\n=== Testing get_statewise_temperature_trends ===")
result = ml_service_v2.get_statewise_temperature_trends()
print(f"Result type: {type(result)}")
print(f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
if isinstance(result, dict):
    for key in list(result.keys())[:3]:
        print(f"  {key}: {result[key][:3] if isinstance(result[key], list) else 'scalar'}")

print("\n=== Testing get_statewise_rainfall_trends ===")
result = ml_service_v2.get_statewise_rainfall_trends()
print(f"Result type: {type(result)}")
print(f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
if isinstance(result, dict):
    for key in list(result.keys())[:3]:
        print(f"  {key}: {result[key][:3] if isinstance(result[key], list) else 'scalar'}")
