"""
Clear system logs table
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

def clear_logs():
    """Clear all system logs"""
    db = SessionLocal()
    
    try:
        # Count before
        before = db.query(SystemLog).count()
        print(f"📊 System logs before: {before}")
        
        # Clear logs
        db.query(SystemLog).delete()
        db.commit()
        
        # Count after
        after = db.query(SystemLog).count()
        print(f"📊 System logs after: {after}")
        print(f"✅ Cleared {before} log entries")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_logs()
