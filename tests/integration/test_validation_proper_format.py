#!/usr/bin/env python3
"""
Test address validation with proper dictionary format to check confidence calculation
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def test_validation_proper_format():
    """Test validation with proper dictionary format"""
    
    print("🎯 ADDRESS VALIDATION PROPER FORMAT TEST")
    print("=" * 60)
    
    try:
        from address_validator import AddressValidator
        from address_parser import AddressParser
        validator = AddressValidator()
        parser = AddressParser()
        print("✅ AddressValidator and AddressParser loaded")
    except ImportError as e:
        print(f"❌ Could not import modules: {e}")
        return
    
    # Test cases with proper parsing
    test_addresses = [
        "Ankara Çankaya Kızılay Mahallesi",
        "asdfghjkl qwertyuiop",
        "İstanbul Kadıköy",
        "İstanbul Kadıköy Moda Mahallesi Caferağa Sokak No:10",
        "Türkiye"
    ]
    
    print(f"\n🧪 TESTING WITH PROPER DICTIONARY FORMAT:")
    
    confidence_scores = []
    all_zero = True
    
    for i, address in enumerate(test_addresses, 1):
        print(f"\n{i}. Testing: '{address}'")
        
        try:
            # Parse the address first to get components
            parsed_result = parser.parse_address(address)
            components = parsed_result.get('components', {})
            
            print(f"   Parsed components: {components}")
            
            # Create proper validation input
            validation_input = {
                'raw_address': address,
                'parsed_components': components
            }
            
            print(f"   Validation input: {validation_input}")
            
            # Validate with proper format
            result = validator.validate_address(validation_input)
            
            confidence = result.get('confidence', 0.0)
            is_valid = result.get('is_valid', False)
            errors = result.get('errors', [])
            
            print(f"   Confidence: {confidence:.3f}")
            print(f"   Is Valid: {is_valid}")
            print(f"   Errors: {errors}")
            
            confidence_scores.append(confidence)
            
            if confidence != 0.0:
                all_zero = False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            confidence_scores.append(0.0)
    
    print(f"\n" + "=" * 60)
    print(f"📊 CONFIDENCE ANALYSIS:")
    print(f"   All confidence scores: {confidence_scores}")
    
    unique_scores = set(confidence_scores)
    print(f"   Unique scores: {len(unique_scores)} ({unique_scores})")
    
    if all_zero:
        print(f"   ❌ STILL ISSUE: All confidences are 0.000 even with proper format!")
        print(f"   Problem: Confidence calculation logic has bugs")
        return True  # Issue exists
    elif len(unique_scores) == 1:
        print(f"   ❌ ISSUE: All addresses get same confidence {list(unique_scores)[0]}")
        return True  # Issue exists  
    else:
        print(f"   ✅ GOOD: Different addresses get different confidence scores")
        return False  # No issue

if __name__ == "__main__":
    issue_found = test_validation_proper_format()
    if issue_found:
        print(f"\n🔧 NEXT: Debug confidence calculation logic in AddressValidator")
    else:
        print(f"\n🎉 SUCCESS: Confidence calculation working with proper format")