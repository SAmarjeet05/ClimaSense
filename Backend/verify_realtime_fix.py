"""
Verify the realtime weather data fix - check that only real API data is saved
"""
import sqlite3
from datetime import datetime, timedelta
import os

db_path = r"C:\Old Data\Amarjeet\AI-Based Climate Change Data Analysis System\Backend\climate.db"

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print("=" * 80)
    print("POST-FIX VERIFICATION: Realtime Weather Data Quality")
    print("=" * 80)
    
    # Check if the new columns exist
    cursor.execute("PRAGMA table_info(realtime_weather_data)")
    columns = [row[1] for row in cursor.fetchall()]
    
    has_quality_flag = "is_real_data" in columns
    has_quality_notes = "data_quality_notes" in columns
    
    print(f"\n✓ Database schema updated: is_real_data column exists: {has_quality_flag}")
    print(f"✓ Database schema updated: data_quality_notes column exists: {has_quality_notes}")
    
    if not (has_quality_flag and has_quality_notes):
        print("\n⚠️  WARNING: Database columns not yet updated!")
        print("   Please run: python -c \"from app.core.database import engine; from app.models import *; engine.create_all()\"")
    else:
        print("\n✓ Schema update successful!")
    
    # Get statistics on data quality
    if has_quality_flag:
        cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN is_real_data = 1 THEN 1 ELSE 0 END) as real_data,
            SUM(CASE WHEN is_real_data = 0 THEN 1 ELSE 0 END) as fallback_data
        FROM realtime_weather_data
        WHERE created_at >= datetime('now', '-24 hours')
        """)
        
        result = cursor.fetchone()
        if result:
            total, real, fallback = result
            real = real or 0
            fallback = fallback or 0
            
            print(f"\nData Quality Statistics (Last 24 hours):")
            print(f"  Total records: {total}")
            print(f"  Real API data: {real} ({100*real/total if total > 0 else 0:.1f}%)")
            print(f"  Fallback data: {fallback} ({100*fallback/total if total > 0 else 0:.1f}%)")
            
            if real == 0 and fallback > 0:
                print("\n⚠️  STATUS: Still storing old fallback data")
                print("   FIX: The old data had 0mm rainfall (default values)")
                print("   ACTION: Clear old records and let new ones be fetched with the fix")
                print("   COMMAND: DELETE FROM realtime_weather_data WHERE is_real_data = 0;")
            elif real > 0 and fallback == 0:
                print("\n✓ STATUS: Only real API data being saved!")
            elif real > 0:
                print("\n✓ STATUS: Mostly real API data, some legacy records may exist")
        
        # Show sample of what's being saved now
        cursor.execute("""
        SELECT city, temperature, rainfall, humidity, wind_speed, is_real_data, created_at
        FROM realtime_weather_data
        WHERE created_at >= datetime('now', '-1 hour')
        ORDER BY created_at DESC
        LIMIT 5
        """)
        
        print(f"\nLatest 5 records (last hour):")
        print("-" * 80)
        for row in cursor.fetchall():
            city, temp, rain, humidity, wind, is_real, created_at = row
            data_type = "✓ REAL" if is_real == 1 else "✗ FALLBACK"
            print(f"{city:15} | {temp:5.1f}°C | {rain:5.1f}mm | {humidity:5.1f}% | {data_type}")
    
    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print("1. Restart the FastAPI server to load the updated code")
    print("2. The scheduler will fetch data with strict validation")
    print("3. Records will only be saved if ALL fields come from the API")
    print("4. Data with missing/default values will be rejected")
    print("5. Check logs for 'Incomplete API response' messages - these indicate API issues")

finally:
    conn.close()

print("\n✓ Verification complete!")
