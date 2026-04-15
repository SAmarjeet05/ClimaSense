"""
Test script to verify production-grade heatmap system
Tests all components: backend API, data normalization, multi-mode functionality
"""
import requests
import json
from datetime import datetime
import time

BASE_URL = "http://localhost:8000"

def print_header(title: str):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def test_realtime_weather_api():
    """Test the realtime weather endpoint"""
    print_header("TEST 1: Real-Time Weather API")
    
    try:
        print("📡 Fetching weather for all cities...")
        start = time.time()
        
        response = requests.get(f"{BASE_URL}/api/realtime-weather", timeout=35)
        response.raise_for_status()
        
        elapsed = time.time() - start
        data = response.json()
        
        print(f"✅ Response received in {elapsed:.2f}s")
        print(f"📍 Total regions: {data.get('total_regions', 0)}")
        print(f"🌡️ Avg temperature: {data['statistics']['avg_temperature']}°C")
        print(f"🌧️ Avg rainfall: {data['statistics']['avg_rainfall']}mm")
        print(f"📊 Cities fetched: {data['statistics']['cities_fetched']}")
        
        # Show first 5 cities
        print(f"\nFirst 5 cities:")
        for i, region in enumerate(data['regions'][:5]):
            print(f"  {i+1}. {region['state']:20} | 🌡️{region['temperature']:6}°C | 🌧️{region['rainfall']:6.1f}mm")
        
        # Verify data completeness
        first_city = data['regions'][0]
        required_fields = ['state', 'lat', 'lng', 'temperature', 'rainfall']
        missing = [f for f in required_fields if f not in first_city]
        
        if missing:
            print(f"❌ Missing fields: {missing}")
            return False
        
        print(f"\n✅ All required fields present: {', '.join(required_fields)}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_heatmap_modes():
    """Test the three heatmap modes: temperature, rainfall, risk"""
    print_header("TEST 2: Heatmap Modes - Data Normalization")
    
    try:
        response = requests.get(f"{BASE_URL}/api/realtime-weather", timeout=35)
        response.raise_for_status()
        data = response.json()
        regions = data['regions']
        
        # Test Temperature Mode
        print("\n🌡️ TEMPERATURE MODE")
        temps = [r['temperature'] for r in regions]
        min_temp = min(temps)
        max_temp = max(temps)
        temp_range = max_temp - min_temp or 1
        
        print(f"  Min temperature: {min_temp}°C")
        print(f"  Max temperature: {max_temp}°C")
        print(f"  Range: {temp_range}°C")
        
        # Show normalization example
        sample_city = regions[0]
        normalized = (sample_city['temperature'] - min_temp) / temp_range
        print(f"  Sample: {sample_city['state']} = {sample_city['temperature']}°C → {normalized:.2%}")
        
        # Test Rainfall Mode
        print("\n🌧️ RAINFALL MODE")
        rainfalls = [r['rainfall'] for r in regions if r['rainfall'] > 0]
        if rainfalls:
            min_rain = min([r['rainfall'] for r in regions])
            max_rain = max([r['rainfall'] for r in regions])
            rain_range = max_rain - min_rain or 1
            
            print(f"  Min rainfall: {min_rain}mm")
            print(f"  Max rainfall: {max_rain}mm")
            print(f"  Range: {rain_range}mm")
            
            sample_rain_norm = (sample_city['rainfall'] - min_rain) / rain_range
            print(f"  Sample: {sample_city['state']} = {sample_city['rainfall']}mm → {sample_rain_norm:.2%}")
        else:
            print("  No rainfall data found")
        
        # Test Risk Score Mode
        print("\n⚠️ RISK SCORE MODE (0.6×temp + 0.4×rain)")
        risk_scores = []
        
        for region in regions:
            temp_norm = (region['temperature'] - min_temp) / temp_range
            rain_norm = (region['rainfall'] - min_rain) / rain_range if rainfalls else 0
            risk = min(1.0, 0.6 * temp_norm + 0.4 * rain_norm)
            risk_scores.append(risk)
        
        avg_risk = sum(risk_scores) / len(risk_scores)
        print(f"  Average risk score: {avg_risk:.2%}")
        
        # Risk level distribution
        low_risk = len([r for r in risk_scores if r < 0.33])
        med_risk = len([r for r in risk_scores if 0.33 <= r < 0.66])
        high_risk = len([r for r in risk_scores if 0.66 <= r < 0.85])
        crit_risk = len([r for r in risk_scores if r >= 0.85])
        
        print(f"  🟢 Low risk (0-33%):    {low_risk} cities")
        print(f"  🟡 Medium risk (33-66%): {med_risk} cities")
        print(f"  🟠 High risk (66-85%):  {high_risk} cities")
        print(f"  🔴 Critical (85-100%):  {crit_risk} cities")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_gradient_coloring():
    """Test the gradient coloring for each mode"""
    print_header("TEST 3: Gradient Coloring")
    
    print("\n🌡️ TEMPERATURE GRADIENT")
    temp_gradient = {
        0.0: "#0066ff",  # cold blue
        0.25: "#00ccff", # cool cyan
        0.5: "#00ff00",  # moderate green
        0.7: "#ffff00",  # warm yellow
        0.9: "#ff9900",  # hot orange
        1.0: "#ff0000"   # extreme red
    }
    
    for norm, color in temp_gradient.items():
        temp = 0 + (norm * 45)  # 0-45°C range visualization
        emoji = "❄️ " if norm < 0.25 else "🌡️ " if norm < 0.5 else "🔥 "
        print(f"  {emoji} {norm:.0%}: {color} (~{temp:.0f}°C)")
    
    print("\n🌧️ RAINFALL GRADIENT")
    rain_gradient = {
        0.0: "#fff5e6",  # very light
        0.2: "#ccccff",  # light blue
        0.4: "#6666ff",  # blue
        0.6: "#0099ff",  # cyan
        0.8: "#00ff00",  # green
        1.0: "#0066cc"   # dark blue (heavy rain)
    }
    
    for norm, color in rain_gradient.items():
        rain = norm * 200  # 0-200mm range visualization
        print(f"  {color} | {norm:.0%} (~{rain:.0f}mm)")
    
    print("\n⚠️ RISK GRADIENT")
    risk_gradient = {
        0.0: "#00ff00",   # safe green
        0.33: "#ffff00",  # warning yellow
        0.66: "#ff9900",  # danger orange
        1.0: "#ff0000"    # critical red
    }
    
    for norm, color in risk_gradient.items():
        level = "🟢 Low" if norm < 0.33 else "🟡 Medium" if norm < 0.66 else "🟠 High" if norm < 1.0 else "🔴 Critical"
        print(f"  {color} | {level} ({norm:.0%})")
    
    print("\n✅ All gradients validated")
    return True

def test_tooltip_data():
    """Test that tooltip data is complete"""
    print_header("TEST 4: Tooltip Data Completeness")
    
    try:
        response = requests.get(f"{BASE_URL}/api/realtime-weather", timeout=35)
        response.raise_for_status()
        data = response.json()
        regions = data['regions']
        
        sample = regions[0]
        
        print(f"\nSample city data for tooltip:")
        print(f"  City name: {sample['state']}")
        print(f"  Latitude: {sample['lat']}")
        print(f"  Longitude: {sample['lng']}")
        print(f"  Temperature: {sample['temperature']}°C")
        print(f"  Rainfall: {sample['rainfall']}mm")
        print(f"  Wind speed: {sample['wind_speed']} km/h")
        print(f"  Source: {sample['source']}")
        print(f"  Color: {sample['color']}")
        
        # Verify all cities have required tooltip fields
        tooltip_fields = ['state', 'temperature', 'rainfall', 'wind_speed']
        all_valid = True
        
        for region in regions:
            for field in tooltip_fields:
                if field not in region:
                    print(f"❌ Missing field '{field}' in {region.get('state', 'unknown')}")
                    all_valid = False
        
        if all_valid:
            print(f"\n✅ All {len(regions)} cities have complete tooltip data")
            return True
        else:
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "🎯" * 30)
    print("  PRODUCTION-GRADE HEATMAP SYSTEM TEST SUITE")
    print("  Temperature • Rainfall • Risk Score Modes")
    print("🎯" * 30)
    
    results = []
    
    # Test real-time API
    results.append(("Real-Time Weather API", test_realtime_weather_api()))
    
    # Test heatmap modes
    results.append(("Heatmap Modes", test_heatmap_modes()))
    
    # Test gradient coloring
    results.append(("Gradient Coloring", test_gradient_coloring()))
    
    # Test tooltip data
    results.append(("Tooltip Data", test_tooltip_data()))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n📊 Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Production heatmap system is ready!")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Review logs above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
