"""
Analyze realtime_weather_data table directly with raw SQL
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
    print("REALTIME WEATHER DATA ANALYSIS (Direct SQL)")
    print("=" * 80)
    
    # Get all records from last 24 hours
    yesterday = datetime.utcnow() - timedelta(days=1)
    yesterday_str = yesterday.isoformat()
    
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='realtime_weather_data'")
    if not cursor.fetchone():
        print("⚠️  realtime_weather_data table does not exist")
        exit(1)
    
    # Get recent records
    query = f"""
    SELECT id, city, temperature, rainfall, humidity, wind_speed, weather_code, source, created_at
    FROM realtime_weather_data
    WHERE created_at >= '{yesterday_str}'
    ORDER BY created_at DESC
    LIMIT 1000
    """
    
    cursor.execute(query)
    recent_records = cursor.fetchall()
    
    print(f"\nTotal records in last 24 hours: {len(recent_records)}\n")
    
    if recent_records:
        print("SUSPICIOUS PATTERNS TO LOOK FOR:")
        print("-" * 80)
        
        # Extract columns into lists
        temps = [r[2] for r in recent_records]
        rainfalls = [r[3] for r in recent_records]
        humidities = [r[4] for r in recent_records]
        wind_speeds = [r[5] for r in recent_records]
        weather_codes = [r[6] for r in recent_records]
        sources = [r[7] for r in recent_records]
        cities = [r[1] for r in recent_records]
        
        # 1. Check for duplicate temperatures
        print("\n1. DUPLICATE TEMPERATURES (sign of demo/failed API):")
        temp_counts = {}
        for temp in temps:
            temp_counts[temp] = temp_counts.get(temp, 0) + 1
        
        suspicious_temps = [(t, c) for t, c in temp_counts.items() if c > 5]
        if suspicious_temps:
            for temp, count in sorted(suspicious_temps, key=lambda x: x[1], reverse=True):
                print(f"   Temperature {temp}°C found in {count} cities (suspicious!)")
        else:
            print("   ✓ No suspicious temperature duplicates")
        
        # 2. Check for round numbers (demo pattern)
        print("\n2. ROUND NUMBER TEMPERATURES (demo data pattern):")
        round_temps = [t for t in temps if t % 5 == 0 or t == 25.0]
        print(f"   {len(round_temps)} of {len(temps)} records have round number temps")
        if round_temps:
            print(f"   Examples: {set(round_temps)}")
        
        # 3. Check rainfall patterns
        print("\n3. RAINFALL PATTERNS (all zeros = fallback/failed API):")
        zero_rain = len([r for r in rainfalls if r == 0.0])
        print(f"   {zero_rain} of {len(rainfalls)} records with 0.0mm rainfall")
        if zero_rain > len(rainfalls) * 0.8:
            print("   ⚠️  Likely demo/fallback data (most records have 0 rainfall)")
        
        # 4. Check humidity
        print("\n4. HUMIDITY PATTERNS (50.0 = default fallback):")
        default_humidity = len([h for h in humidities if h == 50.0])
        print(f"   {default_humidity} of {len(humidities)} records with 50.0% humidity")
        if default_humidity > 10:
            print("   ⚠️  Many records use 50.0 humidity (suspected default)")
        
        #5. Check weather codes
        print("\n5. WEATHER CODE PATTERNS (0 = missing/demo data):")
        zero_codes = len([c for c in weather_codes if c == 0])
        print(f"   {zero_codes} of {len(weather_codes)} records with weather_code=0")
        if zero_codes > len(weather_codes) * 0.8:
            print("   ⚠️  Likely demo/fallback data")
        
        # 6. Check wind speed
        print("\n6. WIND SPEED PATTERNS (5.0 = default fallback):")
        default_wind = len([w for w in wind_speeds if w == 5.0])
        print(f"   {default_wind} of {len(wind_speeds)} records with 5.0 km/h wind speed")
        if default_wind > 10:
            print("   ⚠️  Many records use 5.0 wind speed (suspected default)")
        
        # 7. Check source
        print("\n7. DATA SOURCE FIELD:")
        source_counts = {}
        for source in sources:
            source_counts[source] = source_counts.get(source, 0) + 1
        for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   {source}: {count} records")
        
        # 8. Show sample records
        print("\n8. SAMPLE RECORDS FROM DATABASE:")
        print("-" * 80)
        print(f"{'City':<15} | {'Temp':>6} | {'Rain':>6} | {'Humidity':>7} | {'Wind':>5} | {'Code':>4} | {'Source':<20}")
        print("-" * 80)
        for record in recent_records[:10]:
            city, temp, rain, humidity, wind, code, source = record[1], record[2], record[3], record[4], record[5], record[6], record[7]
            print(f"{city:<15} | {temp:>6.1f}°C | {rain:>5.1f}mm | {humidity:>6.1f}% | {wind:>5.1f} | {code:>4} | {source:<20}")
        
        # Final diagnosis
        print("\n" + "=" * 80)
        print("DIAGNOSIS:")
        print("=" * 80)
        
        avg_temp = sum(temps) / len(temps) if temps else 0
        avg_humidity = sum(humidities) / len(humidities) if humidities else 0
        avg_rain = sum(rainfalls) / len(rainfalls) if rainfalls else 0
        
        is_likely_demo = (
            (zero_rain > len(rainfalls) * 0.8) or
            (default_humidity > 10) or
            (zero_codes > len(weather_codes) * 0.5) or
            (default_wind > 10) or
            (len(suspicious_temps) > 0)
        )
        
        if is_likely_demo:
            print("⚠️  DEMO/FALLBACK DATA DETECTED!")
            print("\nEvidence:")
            if zero_rain > len(rainfalls) * 0.8:
                print(f"  • {zero_rain}/{len(rainfalls)} records have 0mm rainfall (default)")
            if default_humidity > 10:
                print(f"  • {default_humidity} records have 50.0% humidity (default)")
            if zero_codes > len(weather_codes) * 0.5:
                print(f"  • {zero_codes}/{len(weather_codes)} records have weather_code=0 (missing)")
            if default_wind > 10:
                print(f"  • {default_wind} records have 5.0 km/h wind (default)")
            if suspicious_temps:
                print(f"  • Multiple cities have identical temperatures (not real API data)")
            
            print("\nPossible causes:")
            print("  1. Open-Meteo API is failing/unavailable")
            print("  2. Network connectivity issues")
            print("  3. API rate limiting")
            print("  4. Default fallback values being used when API fails")
                
        else:
            print("✓ Data looks like real API data")
            print(f"  Average temperature: {avg_temp:.1f}°C (varied)")
            print(f"  Average rainfall: {avg_rain:.1f}mm (varied)")
            print(f"  Average humidity: {avg_humidity:.1f}% (varied)")
            
    else:
        print("No records found in last 24 hours")

finally:
    conn.close()
