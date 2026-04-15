#!/usr/bin/env python
"""Test the parallel weather fetching"""
import time
from app.services.open_meteo_service import open_meteo_service

start = time.time()
data = open_meteo_service.fetch_all_cities_weather()
elapsed = time.time() - start

print(f'✅ Fetched in {elapsed:.2f}s')
print(f'📍 Cities: {data.get("total_regions", 0)}')
if data.get("regions"):
    print(f'🌡️  First city: {data.get("regions", [{}])[0].get("state")} - {data.get("regions", [{}])[0].get("temperature")}°C')
print(f'📊 Avg temp: {data.get("statistics", {}).get("avg_temperature")}°C')
print(f'✨ Source: {data.get("statistics", {}).get("source")}')
