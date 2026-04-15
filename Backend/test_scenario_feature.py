"""
Test Climate Scenario Feature
Tests: "What happens if global temperature rises by 2°C?"
"""
import sys
sys.path.insert(0, r'C:\Old Data\Amarjeet\AI-Based Climate Change Data Analysis System\Backend')

from app.services.intent_detector import IntentDetector

# Test queries
test_queries = [
    "What happens if global temperature rises by 2°C?",
    "What if temperature increases by 3 degrees?",
    "Tell me the impact of a +2°C warming scenario",
    "+1°C temperature rise scenario",
    "What is the impact of 2 degree warming?",
    "Show me what happens with a 2°C increase",
]

print("=" * 80)
print("CLIMATE SCENARIO FEATURE - BACKEND TEST")
print("=" * 80)

for query in test_queries:
    print(f"\n{'='*80}")
    print(f"Query: {query}")
    print(f"{'='*80}")
    
    parsed = IntentDetector.parse_query(query)
    
    print(f"\nIntent: {parsed['intent']}")
    print(f"Cities: {parsed['cities']}")
    print(f"Parameters: {parsed['parameters']}")
    
    if parsed['intent'] == 'scenario':
        temp_change = parsed['parameters'].get('temperature_change', 2)
        
        # Map to scenario mode
        scenario_mode = "+2c"
        if temp_change == 3:
            scenario_mode = "+3c"
        elif temp_change == 1:
            scenario_mode = "+1c"
        
        print(f"\n✓ Scenario detected!")
        print(f"  Temperature Change: {temp_change}°C")
        print(f"  Scenario Mode: {scenario_mode}")
        print(f"  Navigation URL: /map?scenario={scenario_mode}")
    else:
        print(f"\n✗ Not detected as scenario (detected as: {parsed['intent']})")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
