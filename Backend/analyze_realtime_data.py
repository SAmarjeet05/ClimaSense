"""
Analyze realtime_weather_data table to identify demo vs real data
"""
from app.core.database import SessionLocal
from app.models.realtime_weather import RealtimeWeatherData
from sqlalchemy import func
from datetime import datetime, timedelta

db = SessionLocal()

try:
    print("=" * 80)
    print("REALTIME WEATHER DATA ANALYSIS")
    print("=" * 80)
    
    # Get all records from last 24 hours
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_records = db.query(RealtimeWeatherData).filter(
        RealtimeWeatherData.created_at >= yesterday
    ).order_by(RealtimeWeatherData.created_at.desc()).all()
    
    print(f"\nTotal records in last 24 hours: {len(recent_records)}\n")
    
    if recent_records:
        print("SUSPICIOUS PATTERNS TO LOOK FOR:")
        print("-" * 80)
        
        # Group by temperature to find patterns
        temps = {}
        for record in recent_records:
            temp = record.temperature
            if temp not in temps:
                temps[temp] = []
            temps[temp].append(record.city)
        
        print("\n1. DUPLICATE TEMPERATURES (sign of demo data):")
        for temp, cities in sorted(temps.items(), key=lambda x: len(x[1]), reverse=True):
            if len(cities) > 5:  # More than 5 cities with same temp = suspicious
                print(f"   Temperature {temp}°C found in {len(cities)} cities:")
                print(f"      {', '.join(cities[:10])}")
        
        # Check for round numbers (demo data pattern)
        print("\n2. ROUND NUMBER TEMPERATURES (demo data pattern):")
        round_temps = [r for r in recent_records if r.temperature % 5 == 0 or r.temperature == 25.0]
        if round_temps:
            print(f"   Found {len(round_temps)} records with round number temps")
            print(f"   Examples: {[r.temperature for r in round_temps[:5]]}")
        
        # Check rainfall patterns
        print("\n3. RAINFALL PATTERNS (all zeros = demo/failed API):")
        zero_rain = [r for r in recent_records if r.rainfall == 0.0]
        print(f"   {len(zero_rain)} records with 0.0mm rainfall")
        
        # Check humidity patterns
        print("\n4. HUMIDITY PATTERNS (50.0 = default fallback):")
        default_humidity = [r for r in recent_records if r.humidity == 50.0]
        print(f"   {len(default_humidity)} records with 50.0% humidity (suspected default)")
        
        # Check source field
        print("\n5. DATA SOURCE FIELD:")
        sources = db.query(RealtimeWeatherData.source, func.count()).filter(
            RealtimeWeatherData.created_at >= yesterday
        ).group_by(RealtimeWeatherData.source).all()
        
        for source, count in sources:
            print(f"   {source}: {count} records")
        
        # Show sample records
        print("\n6. SAMPLE RECORDS FROM DATABASE:")
        print("-" * 80)
        for record in recent_records[:5]:
            print(f"   {record.city:15} | Temp: {record.temperature:6}°C | Rain: {record.rainfall:6}mm | "
                  f"Humidity: {record.humidity:5}% | Source: {record.source}")
        
        # Check API response patterns
        print("\n7. WEATHER CODE PATTERNS (0 = missing data):")
        zero_code = len([r for r in recent_records if r.weather_code == 0])
        print(f"   {zero_code} records with weather_code=0 (suspected API failure fallback)")
        
    else:
        print("No records found in last 24 hours")
    
    print("\n" + "=" * 80)
    print("DIAGNOSIS:")
    print("=" * 80)
    
    # Final diagnosis
    if recent_records:
        avg_temp = sum(r.temperature for r in recent_records) / len(recent_records)
        avg_humidity = sum(r.humidity for r in recent_records) / len(recent_records)
        
        is_likely_demo = (
            avg_humidity == 50.0 or  # Default humidity
            len([r for r in recent_records if r.rainfall == 0.0]) > len(recent_records) * 0.8 or  # All zero rainfall
            len([r for r in recent_records if r.weather_code == 0]) > len(recent_records) * 0.8  # All zero codes
        )
        
        if is_likely_demo:
            print("⚠️  DEMO DATA DETECTED!")
            print("\nPossible causes:")
            print("  1. Open-Meteo API is failing/unavailable")
            print("  2. API responses are incomplete (using default fallback values)")
            print("  3. Fallback mechanism is saving demo data to database")
        else:
            print("✓ Data looks like real API data")
            print(f"  Average temperature: {avg_temp:.1f}°C")
            print(f"  Average humidity: {avg_humidity:.1f}%")

finally:
    db.close()
