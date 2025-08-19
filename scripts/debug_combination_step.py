#!/usr/bin/env python3
"""
Debug the combination step where building number gets corrupted
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from address_parser import AddressParser

def debug_combination():
    """Debug the combination step specifically"""
    
    print("🔍 DEBUGGING COMBINATION STEP")
    print("=" * 70)
    
    test_address = "İstanbul Kadıköy Moda Mahallesi Caferağa Sokak 10/A Daire:3"
    normalized_address = "İstanbul Kadıköy Moda Mahallesi Caferağa Sokak 10/A Daire:3"  # Assume same
    
    parser = AddressParser()
    
    # Step 1: Get rule-based result
    print("1. Rule-based extraction:")
    rule_based_result = parser.extract_components_rule_based(normalized_address)
    print(f"   Rule-based: {rule_based_result.get('components', {})}")
    
    # Step 2: Get ML-based result 
    print("\n2. ML-based extraction:")
    ml_based_result = parser.extract_components_ml_based(normalized_address)
    print(f"   ML-based: {ml_based_result.get('components', {})}")
    
    # Step 3: Test combination
    print("\n3. Combining results:")
    combined_components, combined_confidence = parser._combine_extraction_results(
        rule_based_result, ml_based_result, normalized_address
    )
    print(f"   Combined components: {combined_components}")
    print(f"   Combined confidence: {combined_confidence}")
    
    # Step 4: Test validation
    print("\n4. Validation step:")
    validation_result = parser.validate_extracted_components(combined_components)
    print(f"   Validation result keys: {validation_result.keys()}")
    if 'corrected_components' in validation_result:
        print(f"   Corrected components: {validation_result['corrected_components']}")

if __name__ == "__main__":
    debug_combination()