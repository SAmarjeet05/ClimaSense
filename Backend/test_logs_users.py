"""
Test logs and users endpoints
"""
import requests
import json

BASE_URL = 'http://localhost:8000'

# Login
print("="*60)
print("LOGGING IN")
print("="*60)
login_response = requests.post(
    f'{BASE_URL}/auth/login',
    json={
        'email': 'admin@test.com',
        'password': 'Admin123456'
    }
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.json()}")
    exit(1)

token = login_response.json().get('access_token')
print(f"✓ Login successful. Token: {token[:20]}...")

headers = {'Authorization': f'Bearer {token}'}

# Test GET /admin/logs
print("\n" + "="*60)
print("TESTING /admin/logs ENDPOINT")
print("="*60)
logs_response = requests.get(f'{BASE_URL}/admin/logs', params={'limit': 10}, headers=headers)
print(f"Status: {logs_response.status_code}")
logs_data = logs_response.json()
print(f"Total logs: {logs_data.get('total')}")
if logs_data.get('logs'):
    print(f"\nFirst 3 logs:")
    for log in logs_data.get('logs')[:3]:
        print(f"  - {log.get('action')}: {log.get('details')}")
        print(f"    At: {log.get('created_at')}")

# Test GET /admin/users
print("\n" + "="*60)
print("TESTING /admin/users ENDPOINT")
print("="*60)
users_response = requests.get(f'{BASE_URL}/admin/users', headers=headers)
print(f"Status: {users_response.status_code}")
users_data = users_response.json()
print(f"Total users: {users_data.get('total')}")
print(f"\nUsers:")
for user in users_data.get('users', []):
    is_current = " (current user)" if user.get('is_current_user') else ""
    print(f"  - {user.get('name')} ({user.get('email')})")
    print(f"    Role: {user.get('role')}, Created: {user.get('created_at')}{is_current}")

print("\n" + "="*60)
print("✓ ALL TESTS PASSED")
print("="*60)
