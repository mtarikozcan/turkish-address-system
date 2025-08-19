#!/usr/bin/env python3
"""
Test address validation confidence scoring issue
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def test_validation_confidence():
    """Test the validation confidence issue"""
    
    print("🎯 ADDRESS VALIDATION CONFIDENCE TEST")
    print("=" * 60)
    
    try:
        from address_validator import AddressValidator
        validator = AddressValidator()
        print("✅ AddressValidator loaded successfully")
    except ImportError as e:
        print(f"❌ Could not import AddressValidator: {e}")
        return
    except Exception as e:
        print(f"❌ Error creating AddressValidator: {e}")
        return
    
    # User's test cases
    test_cases = [
        {
            'address': "Ankara Çankaya Kızılay Mahallesi",
            'description': "High quality address",
            'expected_confidence': ">0.7"
        },
        {
            'address': "asdfghjkl qwertyuiop",
            'description': "Invalid/garbage text",
            'expected_confidence': "<0.3"
        },
        {
            'address': "İstanbul Kadıköy", 
            'description': "Medium quality address",
            'expected_confidence': "0.5-0.7"
        },
        {
            'address': "İstanbul Kadıköy Moda Mahallesi Caferağa Sokak No:10",
            'description': "Complete high quality address",
            'expected_confidence': ">0.8"
        },
        {
            'address': "Türkiye",
            'description': "Only country name",
            'expected_confidence': "<0.3"
        }
    ]
    
    print(f"\n🧪 TESTING {len(test_cases)} VALIDATION CASES:")
    print(f"Expected: Different addresses should get different confidence scores")
    print("-" * 60)
    
    confidence_scores = []
    all_zero = True
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. {test['description']}")
        print(f"   Address: '{test['address']}'")
        print(f"   Expected: {test['expected_confidence']}")
        
        try:
            result = validator.validate_address(test['address'])
            
            print(f"   Raw result: {result}")
            print(f"   Type: {type(result)}")
            
            # Try to extract confidence
            confidence = None
            
            if isinstance(result, dict):
                confidence = result.get('confidence', result.get('validation_confidence', result.get('score')))
            elif isinstance(result, (int, float)):
                confidence = result
            
            if confidence is not None:
                print(f"   Confidence: {confidence:.3f}")
                confidence_scores.append(confidence)
                
                if confidence != 0.0:
                    all_zero = False
                    
                # Check expected range
                if test['expected_confidence'].startswith('>'):
                    threshold = float(test['expected_confidence'][1:])
                    if confidence > threshold:
                        print(f"   ✅ GOOD: Above expected threshold")
                    else:
                        print(f"   ❌ LOW: Below expected threshold {threshold}")
                elif test['expected_confidence'].startswith('<'):
                    threshold = float(test['expected_confidence'][1:])
                    if confidence < threshold:
                        print(f"   ✅ GOOD: Below expected threshold") 
                    else:
                        print(f"   ❌ HIGH: Above expected threshold {threshold}")
                elif '-' in test['expected_confidence']:
                    low, high = map(float, test['expected_confidence'].split('-'))
                    if low <= confidence <= high:
                        print(f"   ✅ GOOD: Within expected range")
                    else:
                        print(f"   ❌ RANGE: Outside expected range {low}-{high}")
            else:
                print(f"   ❌ No confidence score found in result")
                confidence_scores.append(0.0)
                
        except Exception as e:
            print(f"   ❌ Error validating address: {e}")
            confidence_scores.append(0.0)
    
    print(f"\n" + "=" * 60)
    print(f"📊 CONFIDENCE ANALYSIS:")
    print(f"   All confidence scores: {confidence_scores}")
    
    unique_scores = set(confidence_scores)
    print(f"   Unique scores: {len(unique_scores)} ({unique_scores})")
    
    if all_zero:
        print(f"   ❌ CRITICAL ISSUE: All confidences are 0.000!")
        print(f"   Problem confirmed: No differentiation in validation quality")
        return True  # Issue exists
    elif len(unique_scores) == 1:
        print(f"   ❌ ISSUE: All addresses get same confidence {list(unique_scores)[0]}")
        return True  # Issue exists
    else:
        print(f"   ✅ GOOD: Different addresses get different confidence scores")
        return False  # No issue

if __name__ == "__main__":
    issue_found = test_validation_confidence()
    if issue_found:
        print(f"\n🔧 RECOMMENDATION: Fix confidence calculation in AddressValidator")
    else:
        print(f"\n🎉 RECOMMENDATION: Confidence scoring working correctly")