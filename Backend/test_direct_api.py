"""
Simple test - directly fetch from API and insert to database via SQL
"""
import requests
import sqlite3
from datetime import datetime

db_path = r"C:\Old Data\Amarjeet\AI-Based Climate Change Data Analysis System\Backend\climate.db"

print("=" * 80)
print("DIRECT API TEST - No ORM dependencies")
print("=" * 80)

# Test API
print("\n1️⃣  TESTING OPEN-METEO API:")
print("-" * 80)

test_city = {
    "Delhi": (28.7041, 77.1025),
    "Mumbai": (19.0760, 72.8777)
}

OPEN_METEO_API = "https://api.open-meteo.com/v1/forecast"

for city, (lat, lon) in test_city.items():
    try:
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m",
            "timezone": "Asia/Kolkata",
            "forecast_days": 1
        }
        
        response = requests.get(OPEN_METEO_API, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            current = data.get("current", {})
            
            if current:
                print(f"\n✓ {city}:")
                print(f"  Temperature: {current.get('temperature_2m')}°C")
                print(f"  Rainfall: {current.get('precipitation')}mm")
                print(f"  Humidity: {current.get('relative_humidity_2m')}%")
                print(f"  Wind: {current.get('wind_speed_10m')}km/h")
                print(f"  Weather Code: {current.get('weather_code')}")
            else:
                print(f"\n✗ {city}: Empty current data")
        else:
            print(f"\n✗ {city}: API returned status {response.status_code}")
    
    except Exception as e:
        print(f"\n✗ {city}: {str(e)}")

# Test database write
print("\n\n2️⃣  TESTING DATABASE INSERT:")
print("-" * 80)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check table structure
    cursor.execute("PRAGMA table_info(realtime_weather_data)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"\nTable columns: {columns}")
    
    # Try inserting a test record
    test_record = {
        "city": "TestCity",
        "latitude": 0.0,
        "longitude": 0.0,
        "temperature": 25.5,
        "rainfall": 2.3,
        "wind_speed": 10.5,
        "humidity": 65.0,
        "weather_code": 1,
        "stability_score": 75.0,
        "risk_level": "medium",
        "color": "#ffff00",
        "source": "test",
        "is_real_data": 1,
        "data_quality_notes": "Test record",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Build INSERT statement
    columns_list = ", ".join(test_record.keys())
    placeholders = ", ".join(["?" for _ in test_record])
    values_list = tuple(test_record.values())
    
    query = f"INSERT INTO realtime_weather_data ({columns_list}) VALUES ({placeholders})"
    
    cursor.execute(query, values_list)
    conn.commit()
    
    print("\n✓ Test record inserted successfully!")
    
    # Check if it's in database
    cursor.execute("SELECT COUNT(*) FROM realtime_weather_data")
    total = cursor.fetchone()[0]
    print(f"✓ Total records in database: {total}")
    
    # Show latest records
    cursor.execute("""
    SELECT city, temperature, rainfall, humidity, is_real_data, data_quality_notes 
    FROM realtime_weather_data 
    ORDER BY created_at DESC 
    LIMIT 3
    """)
    
    print("\nLatest 3 records:")
    for row in cursor.fetchall():
        print(f"  {row[0]:15} | {row[1]:6.1f}°C | {row[2]:5.1f}mm | {row[3]:5.1f}% | Real: {row[4]} | {row[5]}")
    
    conn.close()
    
except Exception as e:
    print(f"\n✗ Database error: {str(e)}")

print("\n" + "=" * 80)
print("✓ DIRECT TEST COMPLETE")
print("=" * 80)
print("\nSummary:")
print("1. If API returned data - ✓ Open-Meteo is working")
print("2. If test record was inserted - ✓ Database is writable")
print("3. If columns include is_real_data - ✓ Migration worked")
