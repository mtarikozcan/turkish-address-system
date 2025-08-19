#!/usr/bin/env python3
"""
Test final building number fix with all original test cases
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from address_parser import AddressParser

def test_final_fix():
    """Test all original problematic building number cases"""
    
    print("🎯 FINAL BUILDING NUMBER FIX TEST")
    print("=" * 70)
    
    parser = AddressParser()
    
    test_cases = [
        {
            'input': "İstanbul Kadıköy Moda Mahallesi Caferağa Sokak 10/A Daire:3",
            'expected_bina': "10/A",
            'expected_daire': "3"
        },
        {
            'input': "Sokak 25/B Daire:4",
            'expected_bina': "25/B", 
            'expected_daire': "4"
        },
        {
            'input': "No:15/C Kat:2",
            'expected_bina': "15/C",
            'expected_daire': None
        },
        {
            'input': "Numara:8/D",
            'expected_bina': "8/D",
            'expected_daire': None
        },
        {
            'input': "10/A Daire:3",
            'expected_bina': "10/A",
            'expected_daire': "3"
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: '{test['input']}'")
        result = parser.parse_address(test['input'])
        components = result.get('components', {})
        
        actual_bina = components.get('bina_no', 'NOT_FOUND')
        actual_daire = components.get('daire_no', components.get('daire', 'NOT_FOUND'))
        
        print(f"   Expected: bina_no='{test['expected_bina']}', daire_no='{test['expected_daire']}'")
        print(f"   Actual:   bina_no='{actual_bina}', daire_no='{actual_daire}'")
        
        # Check if building number is preserved (allow case differences)
        bina_match = (actual_bina.lower() == test['expected_bina'].lower() if test['expected_bina'] else actual_bina == 'NOT_FOUND')
        daire_match = (actual_daire == test['expected_daire'] if test['expected_daire'] else actual_daire == 'NOT_FOUND')
        
        if bina_match and daire_match:
            print(f"   ✅ PASS")
            passed += 1
        else:
            print(f"   ❌ FAIL")
    
    print(f"\n" + "=" * 70)
    print(f"🎯 RESULTS: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print(f"🎉 ALL TESTS PASSED! Building number parsing is now working correctly!")
    else:
        print(f"⚠️  Some tests still failing")

if __name__ == "__main__":
    test_final_fix()