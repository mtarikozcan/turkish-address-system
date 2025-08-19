#!/usr/bin/env python3
"""
Debug why confidence scores are lower than expected (0.47 instead of >0.7)
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def debug_confidence_calculation():
    """Debug detailed confidence calculation"""
    
    print("🔍 DEBUGGING CONFIDENCE CALCULATION")
    print("=" * 60)
    
    try:
        from address_validator import AddressValidator
        from address_parser import AddressParser
        validator = AddressValidator()
        parser = AddressParser()
        print("✅ Modules loaded")
    except ImportError as e:
        print(f"❌ Could not import modules: {e}")
        return
    
    # Test with a high-quality address that should get >0.7
    test_address = "Ankara Çankaya Kızılay Mahallesi"
    print(f"\nTesting: '{test_address}'")
    print(f"Expected: >0.7 confidence for complete address")
    
    # Parse the address
    parsed_result = parser.parse_address(test_address)
    components = parsed_result.get('components', {})
    
    print(f"\nParsed components: {components}")
    
    # Create validation input
    validation_input = {
        'raw_address': test_address,
        'parsed_components': components
    }
    
    # Validate and get detailed results
    result = validator.validate_address(validation_input)
    
    print(f"\n📊 VALIDATION RESULTS:")
    print(f"   Confidence: {result.get('confidence', 0.0):.3f}")
    print(f"   Is Valid: {result.get('is_valid', False)}")
    print(f"   Errors: {result.get('errors', [])}")
    print(f"   Suggestions: {result.get('suggestions', [])}")
    
    validation_details = result.get('validation_details', {})
    print(f"\n🔍 VALIDATION DETAILS:")
    for key, value in validation_details.items():
        print(f"   {key}: {value}")
    
    # Let's test individual hierarchy validation
    il = components.get('il', '')
    ilce = components.get('ilce', '')
    mahalle = components.get('mahalle', '')
    
    print(f"\n🧪 INDIVIDUAL HIERARCHY TEST:")
    print(f"   il: '{il}'")
    print(f"   ilce: '{ilce}'")
    print(f"   mahalle: '{mahalle}'")
    
    if il and ilce and mahalle:
        hierarchy_valid = validator.validate_hierarchy(il, ilce, mahalle)
        print(f"   Hierarchy valid: {hierarchy_valid}")
        
        # Test partial hierarchy validation to see scoring
        partial_result = validator._validate_partial_hierarchy(il, ilce, mahalle)
        print(f"   Partial validation result: {partial_result}")
        
        # Check if this gets the expected confidence weight
        confidence_weight = partial_result.get('confidence_weight', 0.0)
        print(f"   Confidence weight from hierarchy: {confidence_weight}")
        
        if confidence_weight < 0.4:
            print(f"   ⚠️  Issue: Hierarchy confidence weight is low ({confidence_weight})")
            print(f"   Expected: Complete hierarchy should get ~0.4 confidence weight")
    
    # Analyze why confidence is low
    final_confidence = result.get('confidence', 0.0)
    if final_confidence < 0.7:
        print(f"\n❌ CONFIDENCE ISSUE ANALYSIS:")
        print(f"   Final confidence: {final_confidence:.3f} (expected >0.7)")
        print(f"   Possible issues:")
        
        if not validation_details.get('hierarchy_valid', False):
            print(f"   - Hierarchy validation failed")
        
        completeness_score = validation_details.get('completeness_score', 0.0)
        print(f"   - Completeness score: {completeness_score}")
        
        if completeness_score < 0.5:
            print(f"   - Low completeness score - missing key components")
        
        errors = result.get('errors', [])
        if errors:
            print(f"   - Has validation errors: {errors}")

if __name__ == "__main__":
    debug_confidence_calculation()