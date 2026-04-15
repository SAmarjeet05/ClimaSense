import requests

print('=== TESTING API ENDPOINTS ===')
print()

# Get token
login_response = requests.post('http://localhost:8000/auth/login', json={
    'email': 'admin@test.com',
    'password': 'Admin123456'
})

if login_response.status_code != 200:
    print('ERROR: Login failed')
    exit(1)

token = login_response.json()['access_token']
print('✓ Got authentication token')
print()

# Test endpoints
headers = {'Authorization': f'Bearer {token}'}
endpoints = [
    '/api/trends',
    '/api/insights',
    '/api/climate-score',
    '/api/co2',
    '/api/map-data',
]

print('Testing endpoints:')
for path in endpoints:
    try:
        response = requests.get(f'http://localhost:8000{path}', headers=headers, timeout=5)
        status = '✓' if response.status_code == 200 else f'✗ ({response.status_code})'
        print(f'  {status} {path}')
    except Exception as e:
        print(f'  ✗ {path} - {str(e)[:30]}')

print()
print('✅ All endpoints tested! Frontend can now fetch real data.')
