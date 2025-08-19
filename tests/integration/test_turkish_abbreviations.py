#!/usr/bin/env python3
"""
Test Turkish city/district abbreviation expansion fixes
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from address_corrector import AddressCorrector

def test_turkish_abbreviations():
    """Test all Turkish abbreviation expansion issues reported by user"""
    
    print("🎯 TURKISH ABBREVIATION EXPANSION TEST")
    print("=" * 70)
    
    corrector = AddressCorrector()
    
    # Test cases based on user's problem report
    test_cases = [
        {
            'input': "Ank. Çank. Kızılay Mh.",
            'expected': "Ankara Çankaya Kızılay Mahallesi",
            'description': "Ank. → Ankara, Çank. → Çankaya"
        },
        {
            'input': "İst. Beşiktaş Levent Mah.",
            'expected': "İstanbul Beşiktaş Levent Mahallesi", 
            'description': "İst. → İstanbul (not İstasyonu)"
        },
        {
            'input': "İzm. Konak Alsancak",
            'expected': "İzmir Konak Alsancak",
            'description': "İzm. → İzmir"
        },
        {
            'input': "Brs. Merkez",
            'expected': "Bursa Merkez",
            'description': "Brs. → Bursa"
        },
        {
            'input': "IST. BEYOĞLU",
            'expected': "İstanbul BEYOĞLU",
            'description': "IST. → İstanbul (uppercase)"
        },
        {
            'input': "ANK ÇANK",
            'expected': "Ankara Çankaya", 
            'description': "No periods, uppercase"
        },
        {
            'input': "ist beşiktaş",
            'expected': "İstanbul beşiktaş",
            'description': "ist → İstanbul (lowercase)"
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. {test['description']}")
        print(f"   Input:    '{test['input']}'")
        
        # Test abbreviation expansion
        result = corrector.expand_abbreviations(test['input'])
        
        print(f"   Expected: '{test['expected']}'")
        print(f"   Actual:   '{result}'")
        
        # Check if expansion is correct (case insensitive comparison for flexibility)
        if result.lower() == test['expected'].lower():
            print(f"   ✅ PASS")
            passed += 1
        else:
            print(f"   ❌ FAIL")
            # Let's also test full correction to see complete pipeline
            full_correction = corrector.correct_address(test['input'])
            print(f"   Full correction: '{full_correction['corrected_address']}'")
    
    print(f"\n" + "=" * 70)
    print(f"🎯 RESULTS: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print(f"🎉 ALL TESTS PASSED! Turkish abbreviation expansion is working correctly!")
    else:
        print(f"⚠️  Some abbreviations still not working correctly")
        
    # Additional debug: Test individual problematic cases
    print(f"\n🔍 DEBUGGING INDIVIDUAL CASES:")
    debug_cases = ["Ank.", "Çank.", "İst.", "ist.", "IST."]
    
    for case in debug_cases:
        result = corrector.expand_abbreviations(case)
        print(f"   '{case}' → '{result}'")

if __name__ == "__main__":
    test_turkish_abbreviations()