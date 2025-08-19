#!/usr/bin/env python3
"""
Final comprehensive test of address validation confidence fix
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def final_validation_confidence_test():
    """Final comprehensive test of validation confidence"""
    
    print("🎯 FINAL VALIDATION CONFIDENCE TEST")
    print("=" * 70)
    print("Verifying that addresses get proper confidence scores (not always 0.000)")
    print("=" * 70)
    
    try:
        from address_validator import AddressValidator
        validator = AddressValidator()
        print("✅ AddressValidator loaded successfully")
    except Exception as e:
        print(f"❌ Error loading validator: {e}")
        return
    
    # User's original test cases
    test_cases = [
        {
            'address': "Ankara Çankaya Kızılay Mahallesi",
            'description': "Complete high quality address",
            'expected_confidence': ">0.7",
            'expected_valid': True
        },
        {
            'address': "asdfghjkl qwertyuiop",
            'description': "Invalid/garbage text",
            'expected_confidence': "<0.3", 
            'expected_valid': False
        },
        {
            'address': "İstanbul Kadıköy",
            'description': "Medium quality address",
            'expected_confidence': "0.4-0.9",  # Flexible range
            'expected_valid': True
        },
        {
            'address': "İstanbul Kadıköy Moda Mahallesi Caferağa Sokak No:10/A Daire:3",
            'description': "Very complete address",
            'expected_confidence': ">0.8",
            'expected_valid': True
        },
        {
            'address': "Türkiye",
            'description': "Only country - very incomplete",
            'expected_confidence': "<0.3",
            'expected_valid': False
        }
    ]
    
    print(f"\n🧪 TESTING {len(test_cases)} COMPREHENSIVE CASES:")
    
    all_passed = True
    confidence_scores = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. {test['description']}")
        print(f"   Address: '{test['address']}'")
        print(f"   Expected confidence: {test['expected_confidence']}")
        print(f"   Expected validity: {test['expected_valid']}")
        
        try:
            # Test with string input (user's original issue)
            result = validator.validate_address(test['address'])
            
            confidence = result.get('confidence', 0.0)
            is_valid = result.get('is_valid', False)
            
            print(f"   Result: confidence={confidence:.3f}, valid={is_valid}")
            
            confidence_scores.append(confidence)
            
            # Check confidence range
            test_passed = True
            
            if test['expected_confidence'].startswith('>'):
                threshold = float(test['expected_confidence'][1:])
                if confidence <= threshold:
                    print(f"   ❌ CONFIDENCE: {confidence:.3f} not > {threshold}")
                    test_passed = False
            elif test['expected_confidence'].startswith('<'):
                threshold = float(test['expected_confidence'][1:])
                if confidence >= threshold:
                    print(f"   ❌ CONFIDENCE: {confidence:.3f} not < {threshold}")
                    test_passed = False
            elif '-' in test['expected_confidence']:
                low, high = map(float, test['expected_confidence'].split('-'))
                if not (low <= confidence <= high):
                    print(f"   ❌ CONFIDENCE: {confidence:.3f} not in range {low}-{high}")
                    test_passed = False
                    
            # Check validity
            if is_valid != test['expected_valid']:
                print(f"   ❌ VALIDITY: Expected {test['expected_valid']}, got {is_valid}")
                test_passed = False
            
            if test_passed:
                print(f"   ✅ PASS: All expectations met")
            else:
                all_passed = False
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            all_passed = False
            confidence_scores.append(0.0)
    
    print(f"\n" + "=" * 70)
    print(f"📊 FINAL ANALYSIS:")
    print(f"   All confidence scores: {confidence_scores}")
    
    unique_scores = set(confidence_scores)
    print(f"   Unique scores: {len(unique_scores)} different values")
    
    all_zero = all(score == 0.0 for score in confidence_scores)
    
    if all_zero:
        print(f"   ❌ CRITICAL: All confidences still 0.000 - fix failed!")
        return False
    else:
        print(f"   ✅ SUCCESS: Confidence scores are differentiated")
    
    if all_passed:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"✅ Address validation confidence scoring is working correctly")
        print(f"✅ Different address qualities get different confidence scores")
        print(f"✅ High quality addresses get >0.7 confidence")
        print(f"✅ Invalid addresses get <0.3 confidence") 
        print(f"✅ String input format works (user's original issue fixed)")
        return True
    else:
        print(f"\n⚠️  Some tests failed - may need additional tuning")
        return False

if __name__ == "__main__":
    success = final_validation_confidence_test()
    if success:
        print(f"\n🏆 TEKNOFEST ADDRESS VALIDATION REQUIREMENTS MET!")
    else:
        print(f"\n🔧 Additional fixes may be needed")