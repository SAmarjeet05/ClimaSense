"""
Detailed test to check for duplicates within update cycles
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Import all models first
from app.models.user import User
from app.models.prediction_log import PredictionLog
from app.models.dataset import Dataset
from app.models.dataset_row import DatasetRow
from app.models.system_log import SystemLog
from app.models.realtime_weather import RealtimeWeatherData

from app.core.database import SessionLocal
from datetime import datetime, timedelta

db = SessionLocal()

try:
    print("\n" + "="*60)
    print("🔍 DUPLICATE CHECK - DETAILED ANALYSIS")
    print("="*60 + "\n")
    
    # Get all records ordered by created_at
    all_records = db.query(RealtimeWeatherData).order_by(
        RealtimeWeatherData.created_at.desc()
    ).all()
    
    print(f"Total records in database: {len(all_records)}\n")
    
    # Group records by created_at timestamp
    batches = {}
    for record in all_records:
        timestamp = record.created_at
        if timestamp not in batches:
            batches[timestamp] = []
        batches[timestamp].append(record)
    
    print(f"Total unique timestamps (batches): {len(batches)}\n")
    
    # Show last 5 batches with duplicate analysis
    print("📋 Last 5 Batches:\n")
    for i, (timestamp, records) in enumerate(sorted(batches.items(), reverse=True)[:5]):
        cities = {}
        for record in records:
            if record.city not in cities:
                cities[record.city] = 0
            cities[record.city] += 1
        
        duplicate_cities = [city for city, count in cities.items() if count > 1]
        
        print(f"Batch {i+1}: {timestamp}")
        print(f"  Total records: {len(records)}")
        print(f"  Unique cities: {len(cities)}")
        
        if duplicate_cities:
            print(f"  ⚠️ DUPLICATES FOUND!")
            for city in duplicate_cities:
                print(f"     - {city}: {cities[city]} times")
        else:
            if len(cities) == 39:
                print(f"  ✅ Perfect batch (39 cities, 1 record each)")
            else:
                print(f"  ℹ️ Partial batch ({len(cities)} cities)")
        print()
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    
    batch_sizes = [len(records) for records in batches.values()]
    avg_size = sum(batch_sizes) / len(batch_sizes)
    
    print(f"Average batch size: {avg_size:.1f}")
    print(f"Expected batch size: 39")
    
    if avg_size == 39:
        print("✅ No duplication detected!")
    elif avg_size == 78:
        print("❌ Each entry stored TWICE (2x duplication)")
    else:
        print(f"ℹ️ Data pattern: {avg_size}x expected size")
    
    print("\n" + "="*60 + "\n")
    
finally:
    db.close()
