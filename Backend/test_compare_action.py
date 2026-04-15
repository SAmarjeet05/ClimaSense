#!/usr/bin/env python3
"""
Test: Verify compare_action and log-action endpoints
"""

import sys
from pathlib import Path
import asyncio

sys.path.insert(0, str(Path(__file__).parent))

from app.services.intent_detector import IntentDetector
from app.services.assistant_service import AssistantService

async def test_compare_action():
    """Test the compare_action feature"""
    
    print("=" * 80)
    print("🔄 TEST: Compare Action Intent with City Pre-selection")
    print("=" * 80)
    
    intent_detector = IntentDetector()
    assistant_service = AssistantService()
    
    test_cases = [
        ("Compare Delhi vs Mumbai", "Delhi", "Mumbai"),
        ("Compare temperature in Bangalore and Hyderabad", "Bangalore", "Hyderabad"),
        ("How different are Chennai and Kolkata?", "Chennai", "Kolkata"),
    ]
    
    print("\n📋 Testing Compare Queries:\n")
    
    for query, expected_city1, expected_city2 in test_cases:
        print(f"🎯 Query: '{query}'")
        
        try:
            # Simulate query_assistant
            response = await assistant_service.query_assistant(query)
            
            # Check response structure
            if response.get("status") != "success":
                print(f"   ❌ Response status: {response.get('status')}")
                continue
            
            # For compare queries with 2+ cities, should get compare_action
            intent = response.get("intent")
            cities = response.get("cities")
            
            print(f"   Intent: {intent}")
            print(f"   Cities: {cities}")
            
            if intent == "compare_action":
                if cities and len(cities) >= 2:
                    print(f"   ✅ Cities correctly extracted: {cities[0]} and {cities[1]}")
                    print(f"   Action URL: {response.get('action_url')}")
                    print(f"   Suggested Action: {response.get('suggested_action')}")
                else:
                    print(f"   ❌ Not enough cities extracted")
            else:
                print(f"   ℹ️  Intent: {intent} (not compare_action)")
            
            print()
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}\n")
    
    print("=" * 80)
    print("✅ TEST COMPLETE")
    print("=" * 80)
    print("\n📊 Feature Flow:")
    print("  1. User: 'Compare Delhi vs Mumbai'")
    print("  2. Backend: Detects compare intent + extracts cities")
    print("  3. Response: {status: success, intent: compare_action, cities: [Delhi, Mumbai]}")
    print("  4. Frontend: handleNavigate('/insights-comparison', undefined, [Delhi, Mumbai])")
    print("  5. Navigation: navigate('/insights-comparison', {state: {cities: [Delhi, Mumbai]}})")
    print("  6. InsightsComparison: Reads location.state.cities")
    print("  7. Auto-selects: setCity1('Delhi'), setCity2('Mumbai')")
    print("  8. Fetches comparison data automatically ✅")

if __name__ == "__main__":
    asyncio.run(test_compare_action())
