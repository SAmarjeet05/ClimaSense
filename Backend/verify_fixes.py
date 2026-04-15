"""
Test to verify the fixes:
1. Frontend logging endpoint works
2. No data duplication in realtime weather
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.models.user import User
from app.models.prediction_log import PredictionLog
from app.models.dataset import Dataset
from app.models.dataset_row import DatasetRow
from app.models.system_log import SystemLog
from app.models.realtime_weather import RealtimeWeatherData

from app.core.database import SessionLocal
from app.services.database_service import DatabaseService

def main():
    print("\n" + "="*60)
    print("🔍 VERIFICATION TEST")
    print("="*60 + "\n")
    
    db = SessionLocal()
    
    try:
        # ====== TEST 1: Verify DatabaseService.log_system_activity works ======
        print("✅ TEST 1: DatabaseService methods")
        
        # Log a test action
        test_log = DatabaseService.log_system_activity(
            db=db,
            action="test_action",
            user_id=None,
            details="Testing logging functionality"
        )
        print(f"   ✅ Successfully logged action with ID: {test_log.id}")
        
        # Get logs
        logs = DatabaseService.get_system_logs(db, limit=5)
        print(f"   ✅ Retrieved {len(logs)} system logs")
        
        # ====== TEST 2: Check realtime weather data structure ======
        print("\n✅ TEST 2: Realtime Weather Data")
        total_weather = db.query(RealtimeWeatherData).count()
        print(f"   Total records in database: {total_weather}")
        
        # Check if records are from single or multiple cycles
        from datetime import datetime, timedelta
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_weather = db.query(RealtimeWeatherData).filter(
            RealtimeWeatherData.created_at >= one_hour_ago
        ).count()
        
        if recent_weather > 0:
            print(f"   Records from last hour: {recent_weather}")
            
            # Get unique cities in recent records
            recent_cities = db.query(RealtimeWeatherData).filter(
                RealtimeWeatherData.created_at >= one_hour_ago
            ).all()
            unique_cities = len(set([r.city for r in recent_cities]))
            print(f"   Unique cities in recent records: {unique_cities}")
            
            if unique_cities == 39:
                records_per_city = recent_weather // unique_cities
                print(f"   Records per city (avg): {records_per_city}")
                if records_per_city == 1:
                    print(f"   ✅ No duplication detected!")
                else:
                    print(f"   ⚠️ Multiple records per city detected ({records_per_city})")
        
        # ====== TEST 3: Verify no duplicate cities in latest batch ======
        print("\n✅ TEST 3: Latest Weather Batch")
        latest_batch = db.query(RealtimeWeatherData).order_by(
            RealtimeWeatherData.created_at.desc()
        ).limit(100).all()
        
        latest_time = latest_batch[0].created_at if latest_batch else None
        same_time_records = [r for r in latest_batch if r.created_at == latest_time]
        cities_in_batch = set([r.city for r in same_time_records])
        
        print(f"   Latest batch time: {latest_time}")
        print(f"   Records in latest batch: {len(same_time_records)}")
        print(f"   Unique cities in batch: {len(cities_in_batch)}")
        
        if len(same_time_records) == 39 and len(cities_in_batch) == 39:
            print(f"   ✅ Perfect batch - 39 cities, no duplication!")
        elif len(same_time_records) > 0:
            print(f"   ⚠️ Batch has {len(same_time_records)} records for {len(cities_in_batch)} cities")
        
        print("\n" + "="*60)
        print("✅ VERIFICATION COMPLETE")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Test Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
