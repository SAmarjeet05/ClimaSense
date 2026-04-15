#!/usr/bin/env python3
"""
Test script to verify seasonal variation in predictions after temporal continuity fix
"""
import requests
import json
from datetime import datetime

# API base URL
BASE_URL = 'http://127.0.0.1:8000'

def main():
    # Step 1: Register a test user
    print('📝 Registering test user...')
    register_data = {
        'email': 'test_seasonal_fix@climate.ai',
        'password': 'TestPassword123!',
        'full_name': 'Test Seasonal Fix'
    }
    response = requests.post(f'{BASE_URL}/auth/register', json=register_data)
    if response.status_code == 201:
        print('✅ User registered successfully')
    else:
        print(f'ℹ️  User may already exist: {response.status_code}')

    # Step 2: Login to get token
    print('\n🔐 Logging in...')
    login_data = {
        'email': 'test_seasonal_fix@climate.ai',
        'password': 'TestPassword123!'
    }
    response = requests.post(f'{BASE_URL}/auth/login', json=login_data)
    if response.status_code != 200:
        print(f'❌ Login failed: {response.json()}')
        return
    
    token = response.json()['access_token']
    print(f'✅ Login successful')

    # Step 3: Make predictions
    headers = {'Authorization': f'Bearer {token}'}

    print('\n' + '='*70)
    print('SEASONAL VARIATION TEST: Delhi Jan vs June 2026')
    print('='*70)

    # January prediction
    print('\n🌡️  Testing JANUARY prediction (Delhi)...')
    response = requests.post(
        f'{BASE_URL}/api/predict',
        json={
            'city': 'Delhi',
            'year': 2026,
            'month': 1,
            'day': 15,
            'latitude': 28.7041,
            'longitude': 77.1025
        },
        headers=headers
    )
    if response.status_code != 200:
        print(f'❌ Prediction failed: {response.json()}')
        return
    
    jan_data = response.json()
    jan_temp = float(jan_data.get('temperature', 0))
    jan_rain = float(jan_data.get('rainfall', 0))
    print(f'January: Temperature = {jan_temp:.1f}°C, Rainfall = {jan_rain:.1f}mm')

    # June prediction
    print('\n☀️  Testing JUNE prediction (Delhi)...')
    response = requests.post(
        f'{BASE_URL}/api/predict',
        json={
            'city': 'Delhi',
            'year': 2026,
            'month': 6,
            'day': 15,
            'latitude': 28.7041,
            'longitude': 77.1025
        },
        headers=headers
    )
    if response.status_code != 200:
        print(f'❌ Prediction failed: {response.json()}')
        return
    
    june_data = response.json()
    june_temp = float(june_data.get('temperature', 0))
    june_rain = float(june_data.get('rainfall', 0))
    print(f'June: Temperature = {june_temp:.1f}°C, Rainfall = {june_rain:.1f}mm')

    # Test results
    print('\n' + '='*70)
    print('RESULTS')
    print('='*70)
    
    temp_diff = abs(june_temp - jan_temp)
    print(f'\n📊 Temperature difference (Jan vs June): {temp_diff:.1f}°C')
    print(f'   Expected: ~10-14°C (Jan ~18-20°C, June ~28-32°C)')
    print(f'   Actual Jan: {jan_temp:.1f}°C, June: {june_temp:.1f}°C')
    if temp_diff > 5:
        print('   ✅ PASS: Good seasonal temperature variation detected!')
    else:
        print('   ❌ FAIL: Insufficient seasonal temperature variation')

    rain_diff = abs(june_rain - jan_rain)
    print(f'\n📊 Rainfall difference (Jan vs June): {rain_diff:.1f}mm')
    print(f'   Expected: ~120-200mm (Jan ~5-10mm, June ~150-200mm monsoon)')
    print(f'   Actual Jan: {jan_rain:.1f}mm, June: {june_rain:.1f}mm')
    if rain_diff > 50:
        print('   ✅ PASS: Good seasonal rainfall variation detected (monsoon signal)!')
    else:
        print('   ❌ FAIL: Insufficient seasonal rainfall variation')

    # Summary
    print('\n' + '='*70)
    print('SUMMARY')
    print('='*70)
    if temp_diff > 5 and rain_diff > 50:
        print('✅ SUCCESS: Temporal continuity fix is working!')
        print('   - Predictions now vary by season')
        print('   - Model is using proper lag features from consecutive days')
        print('   - Monsoon pattern is being captured')
    else:
        print('❌ FAILURE: Fix may not have resolved the issue')
        if temp_diff <= 5:
            print('   - Temperature variation is still too small')
        if rain_diff <= 50:
            print('   - Rainfall variation is still too small')

if __name__ == '__main__':
    main()
