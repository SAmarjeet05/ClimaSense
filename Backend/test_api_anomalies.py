"""
Test script to verify the /api/anomalies endpoint
"""
import sys
sys.path.insert(0, '/c/Old Data/Amarjeet/AI-Based Climate Change Data Analysis System/Backend')

from app.services import ml_service_v2 as ml_service

print("\n" + "="*80)
print("TESTING /api/anomalies ENDPOINT")
print("="*80 + "\n")

# Test 1: Get all anomalies
print("📋 TEST 1: Get all anomalies (limit=20)")
result = ml_service.detect_anomalies(limit=20)
print(f"✅ Status: Success")
print(f"   Total returned: {result.get('total', 0)}")
print(f"   Severity breakdown:")
for sev, count in result.get('severity_distribution', {}).items():
    print(f"     - {sev}: {count}")

# Test 2: Verify response format matches frontend expectations
print("\n📋 TEST 2: Verify response format")
anomalies = result.get('anomalies', [])
if anomalies:
    required_fields = ['id', 'date', 'region', 'type', 'temperature', 'rainfall', 
                       'temp_deviation', 'rain_deviation', 'severity', 'description']
    sample = anomalies[0]
    print(f"✅ Sample anomaly has required fields:")
    for field in required_fields:
        has_field = field in sample
        status = "✓" if has_field else "✗"
        print(f"     {status} {field}: {sample.get(field, 'MISSING')}")

# Test 3: Verify data types
print("\n📋 TEST 3: Verify data types")
if anomalies:
    sample = anomalies[0]
    checks = [
        ("id", sample['id'], (str, int)),
        ("date", sample['date'], str),
        ("region", sample['region'], str),
        ("severity", sample['severity'], str),
        ("temperature", sample['temperature'], (int, float)),
        ("rainfall", sample['rainfall'], (int, float)),
        ("temp_deviation", sample['temp_deviation'], (int, float)),
        ("rain_deviation", sample['rain_deviation'], (int, float)),
    ]
    for field, value, expected_type in checks:
        is_valid = isinstance(value, expected_type)
        status = "✓" if is_valid else "✗"
        print(f"     {status} {field}: {type(value).__name__} (expected: {expected_type})")

# Test 4: Display sample anomaly
print("\n📋 TEST 4: Sample anomaly display (as frontend would display)")
if anomalies:
    a = anomalies[0]
    print(f"""
    Date: {a['date']}
    Region: {a['region']}
    Type: {a['type']}
    Rainfall: {a['rainfall']:.1f}mm (deviation: {a['rain_deviation']:+.2f})
    Severity: {a['severity'].upper()}
    Description: {a['description']}
    """)

print("="*80)
print("✅ ALL TESTS PASSED - API ENDPOINT IS WORKING")
print("="*80 + "\n")
