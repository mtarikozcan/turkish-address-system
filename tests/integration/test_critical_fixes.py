#!/usr/bin/env python3
"""
Test critical fixes for Turkish Address System
Validates that character corruption and context issues are resolved
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from address_corrector import AddressCorrector
from address_parser import AddressParser
from address_validator import AddressValidator

def test_turkish_character_fixes():
    """Test that Turkish character corruption is fixed"""
    print("🔧 TESTING CRITICAL TURKISH CHARACTER FIXES")
    print("=" * 60)
    
    corrector = AddressCorrector()
    
    # Critical test cases that were failing
    test_cases = [
        {
            "input": "istanbul kadikoy moda mh",
            "expected_contains": "İstanbul",
            "should_not_contain": ["I Stanbul", "i̇stanbul"],
            "description": "Basic Istanbul address"
        },
        {
            "input": "İstiklal Caddesi",
            "expected_exact": "İstiklal Caddesi",
            "should_not_contain": ["I Stiklal", "Istiklal"],
            "description": "İstiklal preservation"
        },
        {
            "input": "ankara tunali hilmi caddesi",
            "expected_contains": "Tunalı Hilmi",
            "should_not_contain": ["Tuna Hilmi", "Tunal Hilmi"],
            "description": "Tunalı Hilmi preservation"
        },
        {
            "input": "şişli mecidiyeköy büyükdere cd.",
            "expected_contains": ["Şişli", "Mecidiyeköy", "Büyükdere"],
            "should_not_contain": ["Sisli", "sisli"],
            "description": "Şişli district with Turkish chars"
        },
        {
            "input": "üsküdar çengelköy",
            "expected_contains": ["Üsküdar", "Çengelköy"],
            "should_not_contain": ["Uskudar", "Cengelkoy"],
            "description": "Üsküdar with Turkish chars"
        }
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['description']}")
        print(f"Input: {test_case['input']}")
        
        result = corrector.correct_address(test_case['input'])
        output = result['corrected_address']
        print(f"Output: {output}")
        
        # Check expected content
        if 'expected_exact' in test_case:
            if output == test_case['expected_exact']:
                print(f"✅ Exact match: '{test_case['expected_exact']}'")
            else:
                print(f"❌ Expected exact: '{test_case['expected_exact']}', got: '{output}'")
                all_passed = False
        
        if 'expected_contains' in test_case:
            expected_items = test_case['expected_contains'] if isinstance(test_case['expected_contains'], list) else [test_case['expected_contains']]
            for expected in expected_items:
                if expected in output:
                    print(f"✅ Contains: '{expected}'")
                else:
                    print(f"❌ Missing: '{expected}'")
                    all_passed = False
        
        # Check unwanted content
        if 'should_not_contain' in test_case:
            for unwanted in test_case['should_not_contain']:
                if unwanted in output:
                    print(f"❌ Contains unwanted: '{unwanted}'")
                    all_passed = False
                else:
                    print(f"✅ Does not contain: '{unwanted}'")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TURKISH CHARACTER TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED - Character corruption still exists")
    
    return all_passed


def test_context_intelligence():
    """Test context inference capabilities"""
    print("\n🧠 TESTING CONTEXT INTELLIGENCE")
    print("=" * 60)
    
    parser = AddressParser()
    
    test_cases = [
        {
            "input": "ankara konur sokak",
            "expected_mahalle": "kızılay",
            "description": "Konur Sokak → Kızılay inference"
        },
        {
            "input": "istanbul istiklal caddesi",
            "expected_ilce": "beyoğlu",
            "expected_mahalle": "beyoğlu",
            "description": "İstiklal → Beyoğlu inference"
        },
        {
            "input": "ankara tunalı hilmi",
            "expected_il": "ankara",
            "expected_ilce": "çankaya",
            "description": "Tunalı Hilmi → Çankaya inference"
        }
    ]
    
    context_working = 0
    
    for test_case in test_cases:
        print(f"\nTest: {test_case['description']}")
        print(f"Input: {test_case['input']}")
        
        result = parser.parse_address(test_case['input'])
        components = result.get('components', {})
        
        # Normalize for comparison
        for key in components:
            if components[key]:
                components[key] = str(components[key]).lower()
        
        success = True
        
        if 'expected_il' in test_case:
            expected = test_case['expected_il'].lower()
            actual = components.get('il', '').lower()
            if expected in actual or actual in expected:
                print(f"✅ Il: {actual} (expected: {expected})")
            else:
                print(f"❌ Il: {actual} (expected: {expected})")
                success = False
        
        if 'expected_ilce' in test_case:
            expected = test_case['expected_ilce'].lower()
            actual = components.get('ilce', '').lower()
            if expected in actual or actual in expected:
                print(f"✅ İlçe: {actual} (expected: {expected})")
            else:
                print(f"❌ İlçe: {actual} (expected: {expected})")
                success = False
        
        if 'expected_mahalle' in test_case:
            expected = test_case['expected_mahalle'].lower()
            actual = components.get('mahalle', '').lower()
            if expected in actual or actual in expected:
                print(f"✅ Mahalle: {actual} (expected: {expected})")
            else:
                print(f"❌ Mahalle: {actual} (expected: {expected})")
                success = False
        
        if success:
            context_working += 1
    
    print("\n" + "=" * 60)
    print(f"Context Intelligence: {context_working}/{len(test_cases)} tests passed")
    
    if context_working == 0:
        print("⚠️ WARNING: Context intelligence is NOT working (only hardcoded mappings)")
    elif context_working < len(test_cases):
        print("⚠️ PARTIAL: Some context inference working but not comprehensive")
    else:
        print("✅ Context intelligence appears to be working")
    
    return context_working


def test_building_parsing():
    """Test building/apartment number parsing"""
    print("\n🏢 TESTING BUILDING PARSING")
    print("=" * 60)
    
    parser = AddressParser()
    
    test_cases = [
        {
            "input": "istanbul bagdat caddesi 127/A",
            "expected_bina": "127",
            "expected_daire": "A",
            "description": "Slash format (127/A)"
        },
        {
            "input": "ankara tunali 25-B",
            "expected_bina": "25",
            "expected_daire": "B",
            "description": "Dash format (25-B)"
        },
        {
            "input": "istanbul kadıköy no:42 daire:5",
            "expected_bina": "42",
            "expected_daire": "5",
            "description": "Explicit format"
        }
    ]
    
    parsing_working = 0
    
    for test_case in test_cases:
        print(f"\nTest: {test_case['description']}")
        print(f"Input: {test_case['input']}")
        
        result = parser.parse_address(test_case['input'])
        components = result.get('components', {})
        
        success = True
        
        if 'expected_bina' in test_case:
            actual_bina = components.get('bina_no', '')
            if str(test_case['expected_bina']) == str(actual_bina):
                print(f"✅ Bina No: {actual_bina}")
            else:
                print(f"❌ Bina No: {actual_bina} (expected: {test_case['expected_bina']})")
                success = False
        
        if 'expected_daire' in test_case:
            actual_daire = components.get('daire_no', '')
            if str(test_case['expected_daire']).upper() == str(actual_daire).upper():
                print(f"✅ Daire No: {actual_daire}")
            else:
                print(f"❌ Daire No: {actual_daire} (expected: {test_case['expected_daire']})")
                success = False
        
        if success:
            parsing_working += 1
    
    print("\n" + "=" * 60)
    print(f"Building Parsing: {parsing_working}/{len(test_cases)} tests passed")
    
    return parsing_working


def main():
    """Run all critical tests"""
    print("\n" + "🚨" * 30)
    print("CRITICAL SYSTEM VALIDATION FOR TEKNOFEST")
    print("🚨" * 30)
    
    # Test 1: Turkish Characters
    char_passed = test_turkish_character_fixes()
    
    # Test 2: Context Intelligence
    context_count = test_context_intelligence()
    
    # Test 3: Building Parsing
    building_count = test_building_parsing()
    
    # Final Summary
    print("\n" + "=" * 60)
    print("📊 FINAL SYSTEM STATUS REPORT")
    print("=" * 60)
    
    if char_passed:
        print("✅ Turkish Character Handling: FIXED")
    else:
        print("❌ Turkish Character Handling: STILL BROKEN")
    
    if context_count > 0:
        print(f"⚠️ Context Intelligence: PARTIALLY WORKING ({context_count}/3)")
    else:
        print("❌ Context Intelligence: NOT WORKING (hardcoded only)")
    
    if building_count > 0:
        print(f"⚠️ Building Parsing: PARTIALLY WORKING ({building_count}/3)")
    else:
        print("❌ Building Parsing: NOT WORKING")
    
    print("\n📋 NEXT STEPS:")
    if not char_passed:
        print("1. CRITICAL: Fix Turkish character corruption immediately")
    if context_count < 3:
        print("2. HIGH: Implement dynamic context inference using OSM data")
    if building_count < 3:
        print("3. MEDIUM: Fix building number parsing patterns")
    print("4. HIGH: Add duplicate detection system (MISSING)")
    print("5. HIGH: Add geocoding system (MISSING)")
    print("6. MEDIUM: Prepare Kaggle submission format")
    
    print("\n" + "🚨" * 30)
    print("END OF CRITICAL SYSTEM VALIDATION")
    print("🚨" * 30)


if __name__ == "__main__":
    main()