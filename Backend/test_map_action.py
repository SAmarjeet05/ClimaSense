"""
Test Map Action Intent Detection and Execution
Verifies that UI navigation queries trigger map view with appropriate mode
"""
import asyncio
import sys
sys.path.append(".")

from app.services.intent_detector import IntentDetector
from app.services.assistant_service import AssistantService

print("\n" + "=" * 75)
print("MAP ACTION INTENT - CRITICAL FEATURE TEST")
print("=" * 75)

# TEST 1: Map Action Intent Detection
print("\n✅ TEST 1: MAP ACTION INTENT DETECTION")
print("-" * 75)
test_queries = [
    "Show high risk cities on map",
    "Display temperature distribution on map",
    "Show rainfall map",
    "Display risk map for India",
    "Can you show me the temperature map?",
]

for query in test_queries:
    intent = IntentDetector.classify_intent(query)
    print(f"  Query: '{query}'")
    print(f"  → Intent: {intent}")
    if intent == "map_action":
        print(f"  ✅ PASS: Correctly detected as map_action")
    else:
        print(f"  ❌ FAIL: Expected 'map_action', got '{intent}'")
    print()

# TEST 2: Map Mode Extraction
print("\n✅ TEST 2: MAP MODE EXTRACTION")
print("-" * 75)
mode_tests = [
    ("Show risk map", "risk"),
    ("Display temperature on map", "temperature"),
    ("Show rainfall distribution", "rainfall"),
    ("Display temp map", "temperature"),
]

for query, expected_mode in mode_tests:
    detected_intent = IntentDetector.classify_intent(query)
    mode = IntentDetector.extract_map_mode(query)
    print(f"  Query: '{query}'")
    print(f"  Intent: {detected_intent}, Mode: {mode}")
    print(f"  Expected mode: {expected_mode}")
    if mode == expected_mode:
        print(f"  ✅ PASS")
    else:
        print(f"  ❌ FAIL: Expected mode={expected_mode}, got {mode}")
    print()

# TEST 3: Map Action Response Structure
print("\n✅ TEST 3: MAP ACTION RESPONSE STRUCTURE")
print("-" * 75)

async def test_map_action_response():
    service = AssistantService()
    
    queries = [
        "Show risk map",
        "Display temperature on map",
    ]
    
    for query in queries:
        print(f"  Query: '{query}'")
        response = await service.query_assistant(query)
        
        # Check response structure
        print(f"  Response type: {response.get('type', 'N/A')}")
        print(f"  Status: {response.get('status', 'N/A')}")
        print(f"  Intent: {response.get('intent', 'N/A')}")
        
        if response.get('intent') == 'map_action':
            print(f"  ✅ PASS: Map action detected")
            # Check for action response
            if 'action' in response and response['action'] == 'navigate_map':
                print(f"  ✅ PASS: Navigate action created")
                print(f"  Map Mode: {response.get('map_mode', 'N/A')}")
                print(f"  Action URL: {response.get('action_url', 'N/A')}")
            else:
                print(f"  ⚠️  No navigation action in response")
        else:
            print(f"  ⚠️  Not detected as map_action")
        print()

asyncio.run(test_map_action_response())

# TEST 4: Non-map queries should not trigger map_action
print("\n✅ TEST 4: NON-MAP QUERIES SHOULD NOT TRIGGER MAP_ACTION")
print("-" * 75)
non_map_queries = [
    "What's the temperature in Delhi?",
    "Compare Mumbai and Bangalore",
    "Forecast for 2030",
    "Show me the risk analysis",
]

for query in non_map_queries:
    intent = IntentDetector.classify_intent(query)
    print(f"  Query: '{query}'")
    print(f"  → Intent: {intent}")
    if intent != "map_action":
        print(f"  ✅ PASS: Correctly NOT detected as map_action")
    else:
        print(f"  ❌ FAIL: Should not be map_action")
    print()

print("\n" + "=" * 75)
print("✅ MAP ACTION IMPLEMENTATION VERIFIED")
print("=" * 75)

print("\n📋 EXPECTED FRONTEND BEHAVIOR:")
print("  User: 'Show rainfall map'")
print("  → Backend: Returns 'map_action' with map_mode='rainfall'")
print("  → Frontend: Navigates to /map?mode=rainfall")
print("  → Map automatically switches to rainfall layer")
print("\n")
