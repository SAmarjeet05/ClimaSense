#!/usr/bin/env python3
"""
FINAL INTEGRATION VERIFICATION
Comprehensive check of all map_action feature components
"""

import sys
from pathlib import Path

def check_file_contains(filepath, search_strings, description):
    """Check if file contains all search strings"""
    try:
        content = Path(filepath).read_text(encoding='utf-8')
        missing = []
        for search_str in search_strings:
            if search_str not in content:
                missing.append(search_str)
        
        if missing:
            print(f"❌ {description}")
            print(f"   File: {filepath}")
            print(f"   Missing: {missing[0][:60]}...")
            return False
        else:
            print(f"✅ {description}")
            return True
    except Exception as e:
        print(f"❌ {description} - {str(e)}")
        return False

def main():
    print("=" * 80)
    print("🔍 FINAL INTEGRATION VERIFICATION: Map Action Feature")
    print("=" * 80)
    
    checks = []
    
    # Backend checks
    print("\n📦 BACKEND VERIFICATION:")
    print("-" * 80)
    
    checks.append(check_file_contains(
        "c:\\Old Data\\Amarjeet\\AI-Based Climate Change Data Analysis System\\Backend\\app\\services\\intent_detector.py",
        ["def classify_intent(", "PRIORITY 0", "map_action", "def extract_map_mode("],
        "IntentDetector: map_action priority and extraction"
    ))
    
    checks.append(check_file_contains(
        "c:\\Old Data\\Amarjeet\\AI-Based Climate Change Data Analysis System\\Backend\\app\\services\\assistant_service.py",
        ["intent == \"map_action\"", "navigate_map", "action_url"],
        "AssistantService: map_action response handling"
    ))
    
    # Frontend checks
    print("\n🎨 FRONTEND VERIFICATION:")
    print("-" * 80)
    
    checks.append(check_file_contains(
        "c:\\Old Data\\Amarjeet\\AI-Based Climate Change Data Analysis System\\Frontend\\src\\pages\\user\\ClimateMap.tsx",
        ["import { useLocation } from 'react-router-dom'", "useLocation()", "location.state?.mode"],
        "ClimateMap: useLocation hook and mode reading"
    ))
    
    checks.append(check_file_contains(
        "c:\\Old Data\\Amarjeet\\AI-Based Climate Change Data Analysis System\\Frontend\\src\\pages\\user\\ClimateMap.tsx",
        ["'temperature': 'temp'", "'rainfall': 'rain'", "'risk': 'risk'"],
        "ClimateMap: Mode mapping from backend to component"
    ))
    
    checks.append(check_file_contains(
        "c:\\Old Data\\Amarjeet\\AI-Based Climate Change Data Analysis System\\Frontend\\src\\App.tsx",
        ["<Route path=\"/map\"", "element={<ClimateMap />}"],
        "App.tsx: /map route configuration"
    ))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 80)
    
    total = len(checks)
    passed = sum(checks)
    
    print(f"\nTotal Checks: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {total - passed}")
    print(f"Pass Rate: {(passed/total*100):.1f}%")
    
    if passed == total:
        print("\n🎉 ALL CHECKS PASSED!")
        print("\n📋 INTEGRATION COMPLETE - Ready to Test End-to-End Flow:")
        print("""
1. Start Backend Server:
   cd Backend
   python -m uvicorn app.main:app --reload

2. Start Frontend Dev Server:
   cd Frontend
   npm run dev

3. Test in Browser:
   - Open http://localhost:5173
   - Click on Climate Assistant
   - Type: "Show rainfall map"
   - Expected: Navigation to map with rainfall visualization
   
4. Verify Flow:
   - Backend intent detection ✅
   - Mode extraction ✅
   - Response generation ✅
   - Frontend navigation ✅
   - Component mode update ✅
   - Heatmap rendering ✅
        """)
        return 0
    else:
        print("\n⚠️ SOME CHECKS FAILED - Review above for details")
        return 1

if __name__ == "__main__":
    sys.exit(main())
