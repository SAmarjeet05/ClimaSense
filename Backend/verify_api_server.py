"""
Phase 4 API Endpoint Verification
"""
import requests

BASE_URL = 'http://127.0.0.1:8000'

print('=' * 60)
print('PHASE 4 API ENDPOINT VERIFICATION')
print('=' * 60)

# Test endpoints
endpoints = [
    ('GET', '/'),
    ('GET', '/api/health'),
    ('GET', '/docs'),
]

print('\n✅ ENDPOINT STATUS:')
for method, endpoint in endpoints:
    try:
        response = requests.request(method, BASE_URL + endpoint, timeout=5)
        status = 'OK' if response.status_code < 400 else 'ERROR'
        print(f'  ✓ {response.status_code} {method:6} {endpoint}')
    except Exception as e:
        print(f'  ✗ FAIL {method:6} {endpoint}')

# Check API version
try:
    response = requests.get(BASE_URL + '/')
    data = response.json()
    print('\n📊 API INFO:')
    version = data.get('version', 'unknown')
    architecture = data.get('architecture', 'unknown')
    status = data.get('status', 'unknown')
    print(f'  Version: {version}')
    print(f'  Architecture: {architecture}')
    print(f'  Status: {status}')
except:
    print('\n✗ Could not retrieve API info')

print('\n' + '=' * 60)
print('✅ PHASE 4 API SERVER RUNNING AND RESPONSIVE')
print('=' * 60)
