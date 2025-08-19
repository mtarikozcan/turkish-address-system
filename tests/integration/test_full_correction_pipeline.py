#!/usr/bin/env python3
"""
Test full Turkish address correction pipeline including capitalization
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from address_corrector import AddressCorrector

def test_full_correction_pipeline():
    """Test the full correction pipeline with Turkish abbreviations"""
    
    print("🎯 FULL TURKISH CORRECTION PIPELINE TEST")
    print("=" * 70)
    
    corrector = AddressCorrector()
    
    # Test cases from user's original problem report
    test_cases = [
        {
            'input': "Ank. Çank. Kızılay Mh.",
            'expected_contains': ["Ankara", "Çankaya", "Kızılay", "Mahallesi"],
            'description': "Full correction with proper capitalization"
        },
        {
            'input': "İst. Beşiktaş Levent Mah.",
            'expected_contains': ["İstanbul", "Beşiktaş", "Levent", "Mahallesi"],
            'description': "İst. should become İstanbul with proper Turkish chars"
        },
        {
            'input': "İzm. Konak Alsancak",
            'expected_contains': ["İzmir", "Konak", "Alsancak"],
            'description': "İzm. should become İzmir"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. {test['description']}")
        print(f"   Input: '{test['input']}'")
        
        # Test the full correction pipeline
        result = corrector.correct_address(test['input'])
        corrected = result['corrected_address']
        
        print(f"   Output: '{corrected}'")
        
        # Check if all expected components are present
        all_present = True
        for expected_part in test['expected_contains']:
            if expected_part not in corrected:
                print(f"   ❌ Missing: '{expected_part}'")
                all_present = False
        
        if all_present:
            print(f"   ✅ PASS - All expected components present")
        else:
            print(f"   ❌ FAIL - Some components missing")
            
        # Show corrections that were applied
        if result.get('corrections_applied'):
            print(f"   Applied: {', '.join(result['corrections_applied'])}")

    # Test individual steps to see where Turkish characters get handled
    print(f"\n🔍 STEP-BY-STEP ANALYSIS:")
    test_input = "İst. Çank."
    print(f"Original: '{test_input}'")
    
    # Step 1: Abbreviation expansion
    step1 = corrector.expand_abbreviations(test_input)
    print(f"After abbreviation expansion: '{step1}'")
    
    # Step 2: Spelling correction
    step2 = corrector.correct_spelling_errors(step1)
    print(f"After spelling correction: '{step2}'")
    
    # Step 3: Full correction (includes Turkish capitalization)
    step3 = corrector.correct_address(test_input)
    print(f"After full correction: '{step3['corrected_address']}'")

if __name__ == "__main__":
    test_full_correction_pipeline()