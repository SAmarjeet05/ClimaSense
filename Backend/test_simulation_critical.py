"""
Critical Test: Simulation Intent Detection & Handling
Verifies that the system properly handles what-if/simulation queries
"""
import asyncio
import sys
sys.path.append(".")

from app.services.intent_detector import IntentDetector
from app.services.assistant_service import AssistantService

async def test_simulation_intent():
    """Test 1: Verify simulation intent detection"""
    print("=" * 70)
    print("TEST 1: SIMULATION INTENT DETECTION")
    print("=" * 70)
    
    test_queries = [
        "What happens if temperature increases by 2 degrees in Delhi?",
        "Simulate drought in Mumbai",
        "What if rainfall drops by 30% in Delhi?",
        "Simulate a heatwave in Bangalore",
        "What's the impact if temperature rises by 3°C in Kolkata?"
    ]
    
    for query in test_queries:
        parsed = IntentDetector.parse_query(query)
        intent = parsed["intent"]
        params = parsed["parameters"]
        cities = parsed["cities"]
        
        print(f"\nQuery: {query}")
        print(f"✓ Intent: {intent}")
        print(f"✓ Cities: {cities}")
        print(f"✓ Params: {params}")
        
        # Check if it's detected as simulation
        if intent != "simulation":
            print(f"❌ FAIL: Expected 'simulation', got '{intent}'")
        else:
            print(f"✅ PASS: Correctly detected as simulation")

async def test_simulation_parameters():
    """Test 2: Verify parameter extraction"""
    print("\n" + "=" * 70)
    print("TEST 2: SIMULATION PARAMETER EXTRACTION")
    print("=" * 70)
    
    test_cases = [
        {
            "query": "What happens if temperature increases by 2 degrees?",
            "expected_temp_change": 2
        },
        {
            "query": "Simulate rainfall drop by 30% in Delhi",
            "expected_rain_change": -30
        },
        {
            "query": "Drought in Mumbai - what's the climate impact?",
            "expected_rain_change": -40  # Drought = -40%
        },
        {
            "query": "Simulate heatwave scenario",
            "expected_temp_change": 3  # Heatwave = +3°C
        }
    ]
    
    for test in test_cases:
        query = test["query"]
        parsed = IntentDetector.parse_query(query)
        params = parsed["parameters"]
        
        print(f"\nQuery: {query}")
        
        if "expected_temp_change" in test:
            actual = params.get("temperature_change", 0)
            expected = test["expected_temp_change"]
            if actual == expected:
                print(f"✅ PASS: Temperature change = {actual}°C")
            else:
                print(f"❌ FAIL: Expected temp_change={expected}, got {actual}")
        
        if "expected_rain_change" in test:
            actual = params.get("rainfall_change", 0)
            expected = test["expected_rain_change"]
            if actual == expected:
                print(f"✅ PASS: Rainfall change = {actual}%")
            else:
                print(f"❌ FAIL: Expected rain_change={expected}, got {actual}")

async def test_simulation_execution():
    """Test 3: Verify simulation data generation"""
    print("\n" + "=" * 70)
    print("TEST 3: SIMULATION DATA GENERATION")
    print("=" * 70)
    
    service = AssistantService()
    
    test_simulations = [
        {
            "query": "What happens if temperature increases by 2 degrees in Delhi?",
            "name": "Delhi +2°C"
        },
        {
            "query": "Simulate drought in Mumbai",
            "name": "Mumbai Drought"
        },
        {
            "query": "What if rainfall drops by 40% in Bangalore?",
            "name": "Bangalore -40% Rain"
        }
    ]
    
    for test in test_simulations:
        query = test["query"]
        print(f"\nSimulation: {test['name']}")
        print(f"Query: {query}")
        
        response = await service.query_assistant(query)
        
        if response["status"] == "success":
            print(f"✅ PASS: Simulation completed")
            print(f"   Intent: {response['intent']}")
            
            # Check response structure
            data = response.get("data", {})
            if "results" in data.get("data", {}):
                result = data.get("data", {})["results"][0]
                print(f"   City: {result.get('city')}")
                print(f"   Projected Temp: {result.get('projected', {}).get('temperature')}°C")
                print(f"   Projected Rain: {result.get('projected', {}).get('rainfall')}mm")
                print(f"   Risk Level: {result.get('risk_analysis', {}).get('projected_level')}/10")
            
            # Show generated insight
            insight = data.get("insight", "")
            if insight:
                print(f"   Insight Preview: {insight[:100]}...")
        else:
            print(f"❌ FAIL: {response.get('error', 'Unknown error')}")

async def test_multi_query():
    """Test 4: Verify multi-query handling"""
    print("\n" + "=" * 70)
    print("TEST 4: MULTI-QUERY HANDLING")
    print("=" * 70)
    
    service = AssistantService()
    
    multi_queries = [
        "What happens if temperature increases by 2 degrees? And simulate drought in Mumbai?",
        "Compare Delhi and Mumbai. What about risk analysis for Delhi?",
        "Simulate heatwave in Bangalore? And what's the forecast for 2030?"
    ]
    
    for query in multi_queries:
        print(f"\nMulti-Query: {query}")
        
        response = await service.query_assistant(query)
        
        if response["status"] == "success":
            print(f"✅ PASS: Multi-query processed")
            print(f"   Intent: {response['intent']}")
            
            # Check if combined response
            if "multi-" in response["intent"]:
                answer = response.get("answer", "")
                query_count = answer.count("**Query")
                print(f"   Queries processed: {query_count}")
                print(f"   Answer preview: {answer[:150]}...")
        else:
            print(f"❌ FAIL: {response.get('error', 'Unknown error')}")

async def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " CRITICAL SIMULATION SYSTEM TEST ".center(68) + "║")
    print("╚" + "=" * 68 + "╝")
    
    await test_simulation_intent()
    await test_simulation_parameters()
    await test_simulation_execution()
    await test_multi_query()
    
    print("\n" + "=" * 70)
    print("ALL TESTS COMPLETED")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
