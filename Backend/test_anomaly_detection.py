"""
Test script to verify anomaly detection functionality
"""
import sys
sys.path.insert(0, '/c/Old Data/Amarjeet/AI-Based Climate Change Data Analysis System/Backend')

from app.services import ml_service_v2 as ml_service

print("\n" + "="*80)
print("TESTING ANOMALY DETECTION")
print("="*80 + "\n")

# Test anomaly detection
result = ml_service.detect_anomalies(limit=50)

print(f"✅ Total anomalies detected: {result.get('total', 0)}")
print(f"   Severity distribution: {result.get('severity_distribution', {})}")
print(f"   Data period: {result.get('data_period', {})}")

# Display first 5 anomalies
anomalies = result.get('anomalies', [])
if anomalies:
    print(f"\n📊 Sample anomalies (first 5):")
    for i, anomaly in enumerate(anomalies[:5], 1):
        print(f"\n   {i}. {anomaly['date']} - {anomaly['region']}")
        print(f"      Type: {anomaly['type']}")
        print(f"      Severity: {anomaly['severity']}")
        print(f"      Rainfall: {anomaly['rainfall']:.2f}mm (deviation: {anomaly['rain_deviation']:+.2f}mm)")
        print(f"      Z-score: {anomaly.get('z_score', 'N/A')}")
        print(f"      Description: {anomaly['description']}")
else:
    print("\n⚠️  No anomalies detected!")

print("\n" + "="*80 + "\n")
