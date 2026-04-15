"""
Test that data is being fetched from API and saved to database
"""
import asyncio
from app.core.database import SessionLocal
from app.services.realtime_weather_service import RealtimeWeatherService
from app.models.realtime_weather import RealtimeWeatherData
from datetime import datetime, timedelta

async def test_api_fetch():
    """Test fetching data from API for a few cities"""
    print("=" * 80)
    print("TESTING API DATA FETCH")
    print("=" * 80)
    
    # Test a few cities
    test_cities = {
        "Delhi": (28.7041, 77.1025),
        "Mumbai": (19.0760, 72.8777),
        "Bangalore": (12.9716, 77.5946)
    }
    
    print("\n1️⃣  TESTING API FETCH:")
    print("-" * 80)
    
    for city, (lat, lon) in test_cities.items():
        data = RealtimeWeatherService.fetch_weather_from_api(city, lat, lon)
        if data:
            print(f"\n✓ {city}:")
            print(f"  Temperature: {data['temperature']}°C")
            print(f"  Rainfall: {data['rainfall']}mm")
            print(f"  Humidity: {data['humidity']}%")
            print(f"  Wind: {data['wind_speed']}km/h")
            print(f"  is_real_data: {data['is_real_data']}")
            print(f"  Quality: {data['data_quality_notes']}")
        else:
            print(f"\n✗ {city}: No data returned (API fetch failed)")
    
    # Test batch update
    print("\n\n2️⃣  TESTING BATCH UPDATE (will save to database):")
    print("-" * 80)
    
    db = SessionLocal()
    try:
        results = RealtimeWeatherService.update_all_cities_from_api(db)
        
        print(f"\nResults:")
        print(f"  ✓ Created: {results['created']}")
        print(f"  ✗ Failed: {results['failed']}")
        print(f"  Total: {results['success']}")
        
        if results['created'] > 0:
            print(f"\n✓ Data saved to database!")
        else:
            print(f"\n✗ No data was saved to database")
            
    finally:
        db.close()
    
    # Check what's in the database
    print("\n\n3️⃣  CHECKING DATABASE:")
    print("-" * 80)
    
    db = SessionLocal()
    try:
        # Get records from last hour
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent = db.query(RealtimeWeatherData).filter(
            RealtimeWeatherData.created_at >= one_hour_ago
        ).order_by(RealtimeWeatherData.created_at.desc()).limit(5).all()
        
        if recent:
            print(f"\nRecent records (last hour): {len(recent)}")
            print("-" * 80)
            for record in recent:
                print(f"\n✓ {record.city}")
                print(f"  Temp: {record.temperature}°C | Rain: {record.rainfall}mm | Humidity: {record.humidity}%")
                print(f"  Real data: {record.is_real_data} | Quality: {record.data_quality_notes}")
        else:
            print("\n⚠️  No recent records found in database")
            
    finally:
        db.close()

print("\n" + "=" * 80)
print("DATA FETCH & SAVE TEST")
print("=" * 80)
asyncio.run(test_api_fetch())
print("\n✓ Test complete!")
print("\nIf data is showing up, the system is working correctly.")
print("If data is NOT showing up, check the logs for error messages.")
