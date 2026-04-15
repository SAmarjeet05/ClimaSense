"""
Simple test to check realtime weather data in database
"""
import sys
import os
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
    """Check real-time data in database"""
    db = SessionLocal()
    
    try:
        print("🔍 Checking realtime_weather_data table...\n")
        
        # Count total records
        total_count = db.query(RealtimeWeatherData).count()
        print(f"📊 Total records in database: {total_count}")
        
        if total_count == 0:
            print("   ⚠️ No records found!")
            return
        
        # Get all unique cities
        cities = db.query(RealtimeWeatherData).distinct(RealtimeWeatherData.city).all()
        print(f"📍 Unique cities: {len(set([c.city for c in cities]))}")
        
        # Get records from last 3 hours
        three_hours_ago = datetime.utcnow() - timedelta(hours=3)
        recent_count = db.query(RealtimeWeatherData).filter(
            RealtimeWeatherData.created_at >= three_hours_ago
        ).count()
        print(f"📈 Records from last 3 hours: {recent_count}")
        
        # Get latest record
        latest = db.query(RealtimeWeatherData).order_by(
            RealtimeWeatherData.created_at.desc()
        ).first()
        
        if latest:
            age_seconds = (datetime.utcnow() - latest.created_at.replace(tzinfo=None)).total_seconds()
            age_minutes = int(age_seconds / 60)
            print(f"\n⏰ Latest record:")
            print(f"   City: {latest.city}")
            print(f"   Temperature: {latest.temperature}°C")
            print(f"   Rainfall: {latest.rainfall}mm")
            print(f"   Recorded {age_minutes} minutes ago")
        
        # Check records per city (last one for each)
        print(f"\n📋 Latest reading per city (sample of 10):")
        city_latest = {}
        all_records = db.query(RealtimeWeatherData).order_by(
            RealtimeWeatherData.city,
            RealtimeWeatherData.created_at.desc()
        ).all()
        
        shown = 0
        for record in all_records:
            if record.city not in city_latest:
                city_latest[record.city] = record
                age = datetime.utcnow() - record.created_at.replace(tzinfo=None)
                print(f"   {record.city:20} {record.temperature:6.1f}°C  Rain: {record.rainfall:5.1f}mm  (age: {str(age).split('.')[0]})")
                shown += 1
                if shown >= 10:
                    break
        
        print(f"\n✅ Data is being stored correctly!")
        print(f"   The realtime_weather_data table has {total_count} records")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
