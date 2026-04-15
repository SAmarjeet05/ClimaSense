"""
Test file upload endpoint with data storage in database
"""
import requests
import json
from pathlib import Path
import pandas as pd

# Create a test CSV file
test_data = {
    'Date': ['2024-01-01', '2024-01-02', '2024-01-03'],
    'Temperature': [25.5, 26.3, 24.8],
    'Rainfall': [0.0, 5.2, 3.1],
    'Humidity': [65, 70, 68]
}

df = pd.DataFrame(test_data)
test_file_path = Path('data/test_sample.csv')
df.to_csv(test_file_path, index=False)

# Test the upload endpoint
# First, login to get a token
login_response = requests.post(
    'http://localhost:8000/auth/login',
    json={
        'email': 'admin@test.com',
        'password': 'Admin123456'
    }
)

if login_response.status_code == 200:
    token = login_response.json().get('access_token')
    print(f"✓ Login successful. Token: {token[:20]}...")
    
    # Upload file
    headers = {'Authorization': f'Bearer {token}'}
    
    with open(test_file_path, 'rb') as f:
        files = {'file': ('test_sample.csv', f)}
        upload_response = requests.post(
            'http://localhost:8000/admin/datasets/upload',
            files=files,
            headers=headers
        )
    
    print(f"\n{'='*60}")
    print(f"UPLOAD RESPONSE")
    print(f"{'='*60}")
    print(f"Status: {upload_response.status_code}")
    upload_data = upload_response.json()
    print(json.dumps(upload_data, indent=2))
    
    if upload_response.status_code == 200:
        print("\n✓ File upload successful!")
        dataset_id = upload_data.get('id')
        print(f"  - Dataset ID: {dataset_id}")
        print(f"  - Dataset Name: {upload_data.get('name')}")
        print(f"  - Row Count: {upload_data.get('row_count')}")
        print(f"  - Rows Stored in DB: {upload_data.get('rows_stored')}")
        print(f"  - File Size: {upload_data.get('file_size_mb')} MB")
        print(f"  - Columns: {upload_data.get('columns')}")
        
        # Now retrieve the data from the database
        print(f"\n{'='*60}")
        print(f"RETRIEVING DATA FROM DATABASE")
        print(f"{'='*60}")
        
        retrieve_response = requests.get(
            f'http://localhost:8000/admin/datasets/{dataset_id}/rows',
            headers=headers
        )
        
        print(f"Status: {retrieve_response.status_code}")
        retrieve_data = retrieve_response.json()
        print(json.dumps(retrieve_data, indent=2))
        
        if retrieve_response.status_code == 200:
            print(f"\n✓ Data retrieval successful!")
            print(f"  - Total rows in dataset: {retrieve_data.get('total_rows')}")
            print(f"  - Rows returned: {retrieve_data.get('returned')}")
            print(f"\nFirst row data:")
            if retrieve_data.get('rows'):
                print(json.dumps(retrieve_data['rows'][0], indent=2))
        else:
            print(f"\n✗ Data retrieval failed!")
    else:
        print("\n✗ File upload failed!")
else:
    print(f"✗ Login failed: {login_response.json()}")
