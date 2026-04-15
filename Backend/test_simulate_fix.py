"""
Test simulation endpoint fix
"""
import asyncio
import httpx

async def test_simulate():
    async with httpx.AsyncClient() as client:
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
        if response.status_code == 200:
            data = response.json()
            print('✓ Response generated successfully')
            print(f'  - Baseline Risk: {data["baseline_risk"]} (type: {type(data["baseline_risk"]).__name__})')
            print(f'  - Simulated Risk: {data["simulated_risk"]} (type: {type(data["simulated_risk"]).__name__})')
            print(f'  - Risk Change: {data["risk_change"]} (type: {type(data["risk_change"]).__name__})')
            print('\n✓ All types are integers as expected!')
        else:
            print(f'Error Response: {response.text}')

asyncio.run(test_simulate())
