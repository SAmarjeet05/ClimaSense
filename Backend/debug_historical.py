#!/usr/bin/env python3
"""Debug forecast historical data"""
import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
NASA_DATA_FILE = os.path.join(DATA_DIR, 'nasa_data', 'nasa_india_40cities.csv')

# Load NASA data
nasa_data = pd.read_csv(NASA_DATA_FILE)
nasa_data['date'] = pd.to_datetime(nasa_data['date'])

print("NASA data shape:", nasa_data.shape)
print("Columns:", nasa_data.columns.tolist())

# Test filtering
city = "Mumbai"
month = 6
print(f"\n--- Filtering for {city}, month {month} ---")

city_data = nasa_data[nasa_data['city'].str.lower() == city.lower()]
print(f"City data shape: {city_data.shape}")

city_month_data = city_data[city_data['month'] == month]
print(f"City-month data shape: {city_month_data.shape}")

if len(city_month_data) > 0:
    print("\nSample data:")
    print(city_month_data[['year', 'month', 'temperature', 'rainfall']].head(10))
    
    # Group by year
    print("\nData by year:")
    for year in sorted(city_month_data['year'].unique())[-5:]:
        year_data = city_month_data[city_month_data['year'] == year]
        avg_temp = year_data['temperature'].mean()
        avg_rain = year_data['rainfall'].mean()
        print(f"  {year}: temp={avg_temp:.2f}, rain={avg_rain:.2f} ({len(year_data)} records)")
