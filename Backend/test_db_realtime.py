"""
Test if real-time weather data is being saved to database
"""
import sys
import os
import requests
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import all models first to ensure relationships are set up
from app.models.user import User
from app.models.prediction_log import PredictionLog
from app.models.dataset import Dataset
from app.models.dataset_row import DatasetRow
from app.models.system_log import SystemLog
from app.models.realtime_weather import RealtimeWeatherData

from app.core.database import SessionLocal

def main():
    """Test real-time data storage"""
    db = SessionLocal()
    
    try:
        # First, check how many records exist before API call
        before_count = db.query(RealtimeWeatherData).count()
        print(f"📊 Records in DB before API call: {before_count}")
        
        # Show oldest and newest records if any exist
        if before_count > 0:
            oldest = db.query(RealtimeWeatherData).order_by(RealtimeWeatherData.created_at.asc()).first()
            newest = db.query(RealtimeWeatherData).order_by(RealtimeWeatherData.created_at.desc()).first()
            print(f"  ⏱️ Oldest record: {oldest.created_at} - {oldest.city}")
            print(f"  ⏱️ Newest record: {newest.created_at} - {newest.city}")
        
        # Call the API endpoint
        print("\n📡 Calling /api/realtime-weather endpoint...")
        response = requests.get('http://127.0.0.1:8000/api/realtime-weather', timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Response: {data['total_regions']} regions fetched")
        else:
            print(f"❌ API Error: {response.status_code}")
            return
        
        # Check how many records exist after API call
        after_count = db.query(RealtimeWeatherData).count()
        new_records = after_count - before_count
        
        print(f"\n📊 Records in DB after API call: {after_count}")
        print(f"  📈 New records added: {new_records}")
        
        if new_records == 0:
            print("\n⚠️ WARNING: No new records were saved!")
            print("  - API returned data, but database was not updated")
            print("  - Checking for recent records...")
            
            # Check last 10 records
            recent = db.query(RealtimeWeatherData).order_by(
                RealtimeWeatherData.created_at.desc()
            ).limit(10).all()
            
            if recent:
                print(f"  ✅ Found {len(recent)} recent records:")
                for r in recent:
                    age = datetime.utcnow() - r.created_at.replace(tzinfo=None)
                    print(f"     - {r.city}: {r.temperature}°C (age: {age})")
            else:
                print("  ❌ No records found at all!")
        else:
            print(f"\n✅ SUCCESS: {new_records} new records were saved!")
            # Show a sample
            latest = db.query(RealtimeWeatherData).order_by(
                RealtimeWeatherData.created_at.desc()
            ).limit(5).all()
            
            print("  📝 Latest records saved:")
            for r in latest:
                print(f"     - {r.city}: {r.temperature}°C, Rain: {r.rainfall}mm")
        
        # Check for any records from the last hour
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_count = db.query(RealtimeWeatherData).filter(
            RealtimeWeatherData.created_at >= one_hour_ago
        ).count()
        print(f"\n⏰ Records from last hour: {recent_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
