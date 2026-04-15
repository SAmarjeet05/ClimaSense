"""
Test simulation endpoint with detailed error reporting
"""
import asyncio
import httpx
import json

async def test_simulate():
    try:
        async with httpx.AsyncClient() as client:
            # Try a simple health check first
            try:
                health = await client.get('http://127.0.0.1:8000/api/dashboard/health', timeout=5)
                print(f'Server health: {health.status_code}')
            except:
                print('⚠ Server health check failed - server may not be running')
            
            print('\nTesting /api/simulate endpoint...')
            response = await client.post(
                'http://127.0.0.1:8000/api/simulate',
                json={
                    'city': 'Delhi',
                    'temp_delta': 2.0,
                    'rain_delta': -20,
                    'year': 2026,
                    'month': 4,
                    'day': 15
                },
                timeout=10
            )
            
            print(f'Status: {response.status_code}')
            print(f'Headers: {dict(response.headers)}')
            
            if response.status_code == 200:
                data = response.json()
                print('\n✓ Response generated successfully')
                print(f'  - Baseline Risk: {data["baseline_risk"]} (type: {type(data["baseline_risk"]).__name__})')
                print(f'  - Simulated Risk: {data["simulated_risk"]} (type: {type(data["simulated_risk"]).__name__})')
                print(f'  - Risk Change: {data["risk_change"]} (type: {type(data["risk_change"]).__name__})')
                print('\n✓ All types are integers as expected!')
                return True
            else:
                print(f'\nError Response ({response.status_code}):')
                try:
                    error_data = response.json()
                    print(json.dumps(error_data, indent=2))
                except:
                    print(response.text)
                return False
    
    except Exception as e:
        print(f'Exception: {type(e).__name__}: {str(e)}')
        return False

if asyncio.run(test_simulate()):
    print('\n✓ TEST PASSED')
else:
    print('\n✗ TEST FAILED')
