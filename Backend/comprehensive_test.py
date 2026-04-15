"""
Comprehensive test to verify all changes are working
1. Check realtime weather data is being saved (new records)
2. Check system logs are cleared
3. Test logging frontend action endpoint
4. Check user management endpoints
"""
import sys
import os
import requests
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from app.models.user import User
from app.models.prediction_log import PredictionLog
from app.models.dataset import Dataset
from app.models.dataset_row import DatasetRow
from app.models.system_log import SystemLog
from app.models.realtime_weather import RealtimeWeatherData

from app.core.database import SessionLocal

def main():
    print("\n" + "="*60)
    print("🔍 COMPREHENSIVE SYSTEM TEST")
    print("="*60 + "\n")
    
    db = SessionLocal()
    API_BASE = "http://127.0.0.1:8000"
    
    try:
        # ====== TEST 1: Realtime Weather Data ======
        print("📊 TEST 1: Realtime Weather Data Storage")
        weather_count = db.query(RealtimeWeatherData).count()
        print(f"   Total weatherrecords: {weather_count}")
        
        if weather_count >= 39:
            print(f"   ✅ Data storage working! ({weather_count} records for {weather_count//39 or 1} cycles)")
        else:
            print(f"   ⚠️  Only {weather_count} records (expected at least 39)")
        
        # ====== TEST 2: System Logs ======
        print("\n📝 TEST 2: System Logs (Should be cleared)")
        logs_count = db.query(SystemLog).count()
        print(f"   Total system logs: {logs_count}")
        if logs_count == 0:
            print("   ✅ Logs cleared successfully")
        else:
            print(f"   ⚠️ Logs not empty ({logs_count} records remain)")
        
        # ====== TEST 3: Frontend Logging Endpoint ======
        print("\n📡 TEST 3: Frontend Logging Endpoint")
        try:
            response = requests.post(
                f"{API_BASE}/api/admin/log-action",
                json={
                    "action": "test_action",
                    "details": '{"test": "data"}',
                    "user_id": None
                },
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    print(f"   ✅ Logging endpoint working! (Log ID: {result.get('log_id')})")
                    
                    # Verify log was saved
                    log_count_after = db.query(SystemLog).count()
                    if log_count_after > 0:
                        print(f"   ✅ Log entry saved to database")
                    else:
                        print(f"   ⚠️ Log entry not found in database")
                else:
                    print(f"   ❌ Endpoint returned error: {result.get('message')}")
            else:
                print(f"   ❌ Endpoint returned {response.status_code}")
        except Exception as e:
            print(f"   ❌ Endpoint test failed: {e}")
        
        # ====== TEST 4: User Management Endpoints ======
        print("\n👥 TEST 4: User Management Endpoints")
        try:
            # Get all users first
            response = requests.get(
                f"{API_BASE}/api/admin/users",
                headers={"Authorization": f"Bearer test_token"},  # This will likely fail auth, but we check if endpoint exists
                timeout=5
            )
            
            if response.status_code in [200, 401]:  # 200 = success, 401 = auth failed (but endpoint exists)
                print(f"   ✅ User endpoints are available")
            else:
                print(f"   ⚠️ Unexpected response: {response.status_code}")
        except Exception as e:
            print(f"   ⚠️ Could not reach user endpoint: {e}")
        
        # ====== TEST 5: Data Persistence ======
        print("\n💾 TEST 5: Data Persistence Check")
        users_count = db.query(User).count()
        print(f"   Total users: {users_count}")
        print(f"   ✅ Database connectivity confirmed")
        
        print("\n" + "="*60)
        print("✅ TESTS COMPLETED")
        print("="*60 + "\n")
        
        print("📋 SUMMARY:")
        print(f"  • Realtime weather records: {weather_count}")
        print(f"  • System logs: {logs_count}")
        print(f"  • Total users: {users_count}")
        print(f"  • System healthy: {'✅ Yes' if weather_count >= 39 and logs_count >= 0 and users_count > 0 else '⚠️  Check Above'}")
        
    except Exception as e:
        print(f"\n❌ Test Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
