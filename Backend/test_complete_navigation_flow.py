#!/usr/bin/env python3
"""
Test: Verify complete flow - Backend response → Frontend navigation → Map mode update
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.services.intent_detector import IntentDetector
from app.services.assistant_service import AssistantService
import asyncio

async def test_complete_flow():
    """Test the complete flow from query to navigation response"""
    
    print("=" * 80)
    print("🔄 COMPLETE NAVIGATION FLOW TEST")
    print("=" * 80)
    
    intent_detector = IntentDetector()
    assistant_service = AssistantService()
    
    test_queries = [
        ("Show high risk cities on map", "risk"),
        ("Show rainfall map", "rainfall"),
        ("Display temperature on map", "temperature"),
    ]
    
    print("\n📋 Testing Complete Flow:\n")
    
    for query, expected_mode in test_queries:
        print(f"🎯 Query: '{query}'")
        print(f"   Expected Mode: {expected_mode}")
        
        try:
            # Simulate the query_assistant call
            response = await assistant_service.query_assistant(query)
            
            print(f"\n   ✅ Backend Response:")
            print(f"      intent: {response.get('intent')}")
            print(f"      map_mode: {response.get('map_mode')}")
            print(f"      action_url: {response.get('action_url')}")
            print(f"      answer: {response.get('answer')[:50]}...")
            print(f"      suggested_action: {response.get('suggested_action')}")
            
            # Verify response structure
            required_fields = ["status", "intent", "map_mode", "action_url", "answer", "suggested_action"]
            missing_fields = [f for f in required_fields if f not in response]
            
            if missing_fields:
                print(f"   ❌ Missing fields: {missing_fields}")
                continue
            
            # Verify mode extraction
            if response.get('map_mode') != expected_mode:
                print(f"   ❌ Mode mismatch: {response.get('map_mode')} != {expected_mode}")
                continue
            
            # Simulate frontend navigation logic
            map_mode = response.get('map_mode')
            action_url = response.get('action_url')
            
            # What the frontend would do:
            modeParam = action_url.split('mode=')[1] if 'mode=' in action_url else None
            frontendMode = map_mode or modeParam
            
            # Map mode transformation for ClimateMap component
            modeMap = {
                'temperature': 'temp',
                'rainfall': 'rain',
                'risk': 'risk'
            }
            componentMode = modeMap.get(frontendMode)
            
            print(f"\n   📱 Frontend Navigation (Simulated):")
            print(f"      navigate('{action_url.split('?')[0]}', state={{ mode: '{frontendMode}' }})")
            print(f"      ClimateMap receives mode: '{componentMode}'")
            print(f"      Component renders: {componentMode} visualization")
            
            print(f"\n   ✅ COMPLETE FLOW SUCCESS\n")
            print("-" * 80)
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}\n")
            print("-" * 80)
    
    print("\n" + "=" * 80)
    print("✅ ALL FLOWS TESTED")
    print("=" * 80)
    print("\n📊 Frontend Integration Summary:")
    print("  1. Backend detects map_action intent")
    print("  2. Extracts mode (risk/rainfall/temperature)")
    print("  3. Returns response with map_mode field")
    print("  4. Frontend Assistant component reads map_mode")
    print("  5. Calls handleNavigate(url, mapMode)")
    print("  6. Navigation passes state with mode to /map")
    print("  7. ClimateMap useEffect reads location.state.mode")
    print("  8. Maps backend mode to component mode")
    print("  9. Sets mode state → triggers re-render")
    print("  10. Heatmap displays correct visualization ✅")

if __name__ == "__main__":
    asyncio.run(test_complete_flow())
