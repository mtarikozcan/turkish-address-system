#!/usr/bin/env python3
"""
Debug inside the parse_address method by monkey-patching
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from address_parser import AddressParser

def debug_inside_parse_address():
    """Debug by intercepting the parse_address method"""
    
    print("🔍 DEBUGGING INSIDE PARSE_ADDRESS")
    print("=" * 70)
    
    parser = AddressParser()
    
    # Monkey patch the _combine_extraction_results method to add debugging
    original_combine = parser._combine_extraction_results
    
    def debug_combine(rule_based, ml_based, address):
        print(f"COMBINE INPUT:")
        print(f"  Rule-based: {rule_based.get('components', {})}")
        print(f"  ML-based: {ml_based.get('components', {})}")
        
        result_components, result_confidence = original_combine(rule_based, ml_based, address)
        
        print(f"COMBINE OUTPUT:")
        print(f"  Combined: {result_components}")
        
        return result_components, result_confidence
    
    parser._combine_extraction_results = debug_combine
    
    # Also patch validation method
    original_validate = parser.validate_extracted_components
    
    def debug_validate(components):
        print(f"VALIDATE INPUT: {components}")
        result = original_validate(components)
        print(f"VALIDATE OUTPUT: {result.keys()}")
        return result
    
    parser.validate_extracted_components = debug_validate
    
    # Now test
    test_address = "İstanbul Kadıköy Moda Mahallesi Caferağa Sokak 10/A Daire:3"
    print(f"Testing: {test_address}")
    print("-" * 70)
    
    result = parser.parse_address(test_address)
    
    print(f"\nFINAL RESULT:")
    print(f"  Components: {result.get('components', {})}")

if __name__ == "__main__":
    debug_inside_parse_address()