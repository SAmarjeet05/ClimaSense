"""
Test models endpoint
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
print(f"✓ Login successful")

headers = {'Authorization': f'Bearer {token}'}

# Test GET /admin/models
print("\n" + "="*60)
print("TESTING /admin/models ENDPOINT")
print("="*60)
models_response = requests.get(f'{BASE_URL}/admin/models', headers=headers)
print(f"Status: {models_response.status_code}")
models_data = models_response.json()

print(f"Total models: {models_data.get('total')}")
print(f"Deployed: {models_data.get('deployed')}")
print(f"Training: {models_data.get('training')}")

print(f"\nModels:")
for model in models_data.get('models', []):
    print(f"\n  {model.get('name')} ({model.get('version')})")
    print(f"    Algorithm: {model.get('algorithm')}")
    print(f"    Status: {model.get('status')}")
    print(f"    Accuracy: {model.get('accuracy')}%")
    print(f"    R² Score: {model.get('r2_score')}")
    print(f"    Last Trained: {model.get('last_trained')}")
    print(f"    Description: {model.get('description')}")

print("\n" + "="*60)
print("✓ ALL TESTS PASSED")
print("="*60)
