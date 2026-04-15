#!/usr/bin/env python3
import requests
import random

BASE_URL = 'http://127.0.0.1:8000'
email = f'test_user_{random.randint(10000,99999)}@climate.ai'
password = 'TestPass123!'

print(f"Testing with email: {email}")

# Register
reg_resp = requests.post(f'{BASE_URL}/auth/register', json={'email': email, 'password': password, 'full_name': 'Test'})
print(f'Register: {reg_resp.status_code}')

# Login
login_resp = requests.post(f'{BASE_URL}/auth/login', json={'email': email, 'password': password})
if login_resp.status_code == 200:
    token = login_resp.json()['access_token']
    print('✅ Got token')
    
    # Test Jan
    jan = requests.post(
        f'{BASE_URL}/api/predict',
        json={'city': 'Delhi', 'year': 2026, 'month': 1, 'day': 15, 'latitude': 28.7041, 'longitude': 77.1025},
        headers={'Authorization': f'Bearer {token}'}
    ).json()
    
    # Test June
    june = requests.post(
        f'{BASE_URL}/api/predict',
        json={'city': 'Delhi', 'year': 2026, 'month': 6, 'day': 15, 'latitude': 28.7041, 'longitude': 77.1025},
        headers={'Authorization': f'Bearer {token}'}
    ).json()
    
    jan_temp = float(jan.get('temperature', 0))
    jan_rain = float(jan.get('rainfall', 0))
    june_temp = float(june.get('temperature', 0))
    june_rain = float(june.get('rainfall', 0))
    
    temp_diff = abs(june_temp - jan_temp)
    rain_diff = abs(june_rain - jan_rain)
    
    print(f'\nJanuary: {jan_temp:.1f}°C, {jan_rain:.1f}mm')
    print(f'June: {june_temp:.1f}°C, {june_rain:.1f}mm')
    print(f'\nTemp difference: {temp_diff:.1f}°C')
    print(f'Rain difference: {rain_diff:.1f}mm')
    
    if temp_diff > 5 and rain_diff > 50:
        print('\n✅ SEASONAL VARIATION WORKING!')
        print('The temporal continuity fix is successful!')
    else:
        print('\n❌ Still not working as expected')
        if temp_diff <= 5:
            print(f'   Temperature variation too small: {temp_diff:.1f}°C')
        if rain_diff <= 50:
            print(f'   Rainfall variation too small: {rain_diff:.1f}mm')
else:
    print(f'Login failed: {login_resp.status_code}')
    print(login_resp.json())
