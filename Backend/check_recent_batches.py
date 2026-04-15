"""
Check if recent batches are properly formatted (last 30 minutes)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.models.realtime_weather import RealtimeWeatherData
from app.models.user import User
from app.models.prediction_log import PredictionLog
from app.models.system_log import SystemLog
from app.models.dataset import Dataset
from app.models.dataset_row import DatasetRow

from app.core.database import SessionLocal
from datetime import datetime, timedelta

db = SessionLocal()

try:
    print("\n" + "="*60)
    print("🔍 RECENT BATCH ANALYSIS (Last 30 minutes)")
    print("="*60 + "\n")
    
    # Get records from last 30 minutes
    thirty_min_ago = datetime.utcnow() - timedelta(minutes=30)
    recent_records = db.query(RealtimeWeatherData).filter(
        RealtimeWeatherData.created_at >= thirty_min_ago
    ).order_by(RealtimeWeatherData.created_at.desc()).all()
    
    print(f"Records from last 30 minutes: {len(recent_records)}\n")
    
    # Group by created_at
    batches = {}
    for record in recent_records:
        ts = record.created_at
        if ts not in batches:
            batches[ts] = {}
        batches[ts][record.city] = batches[ts].get(record.city, 0) + 1
    
    print(f"Batches found: {len(batches)}\n")
    
    # Analyze each batch
    print("📋 Batch Analysis:\n")
    for i, (timestamp, cities) in enumerate(sorted(batches.items(), reverse=True)[:10]):
        total = sum(cities.values())
        unique = len(cities)
        duplicates = sum(1 for count in cities.values() if count > 1)
        
        print(f"Batch {i+1}: {timestamp}")
        print(f"  Records: {total}, Unique cities: {unique}")
        
        if duplicates > 0:
            print(f"  ⚠️ Duplicates: {duplicates} cities have multiple records")
            for city, count in cities.items():
                if count > 1:
                    print(f"     - {city}: {count} times")
        else:
            if unique == 39:
                print(f"  ✅ Perfect! 39 cities, no duplicates")
            else:
                print(f"  ℹ️ Partial batch ({unique} cities)")
        print()
    
    # Summary
    print("\n" + "="*60)
    perfect_batches = sum(1 for _, cities in batches.items() if len(cities) == 39 and all(c == 1 for c in cities.values()))
    print(f"Perfect batches (39 cities, no duplicates): {perfect_batches} out of {len(batches)}")
    
    if perfect_batches > 0:
        print("✅ Fix is working! New batches are properly formatted")
    else:
        print("❌ Issue persists - check old data")
    print("="*60 + "\n")
    
finally:
    db.close()
