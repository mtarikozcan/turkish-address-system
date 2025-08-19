#!/usr/bin/env python3
"""
Debug each step in extract_components_rule_based
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from address_parser import AddressParser

def debug_rule_based_steps():
    """Debug each step in the rule-based extraction"""
    
    print("🔍 DEBUGGING RULE-BASED EXTRACTION STEPS")
    print("=" * 70)
    
    parser = AddressParser()
    test_address = "İstanbul Kadıköy Moda Mahallesi Caferağa Sokak 10/A Daire:3"
    
    # Patch each method to add debugging
    original_extract_building = parser._extract_building_components
    original_extract_street = parser._extract_street_optimized
    original_context_inference = parser._teknofest_context_inference
    original_geo_validation = parser._geographic_validation
    
    def debug_extract_building(address, components, confidence_scores):
        print(f"\n🏢 BEFORE _extract_building_components:")
        print(f"   bina_no: {components.get('bina_no', 'NOT_FOUND')}")
        
        result_comp, result_conf = original_extract_building(address, components, confidence_scores)
        
        print(f"   AFTER _extract_building_components:")
        print(f"   bina_no: {result_comp.get('bina_no', 'NOT_FOUND')}")
        
        return result_comp, result_conf
    
    def debug_extract_street(address, components, confidence_scores):
        print(f"\n🛣️  BEFORE _extract_street_optimized:")
        print(f"   bina_no: {components.get('bina_no', 'NOT_FOUND')}")
        
        result_comp, result_conf = original_extract_street(address, components, confidence_scores)
        
        print(f"   AFTER _extract_street_optimized:")
        print(f"   bina_no: {result_comp.get('bina_no', 'NOT_FOUND')}")
        
        return result_comp, result_conf
    
    def debug_context_inference(address, components, confidence_scores):
        print(f"\n🧠 BEFORE _teknofest_context_inference:")
        print(f"   bina_no: {components.get('bina_no', 'NOT_FOUND')}")
        
        result_comp, result_conf = original_context_inference(address, components, confidence_scores)
        
        print(f"   AFTER _teknofest_context_inference:")
        print(f"   bina_no: {result_comp.get('bina_no', 'NOT_FOUND')}")
        
        return result_comp, result_conf
    
    def debug_geo_validation(address, components, confidence_scores):
        print(f"\n🌍 BEFORE _geographic_validation:")
        print(f"   bina_no: {components.get('bina_no', 'NOT_FOUND')}")
        
        result_comp, result_conf = original_geo_validation(address, components, confidence_scores)
        
        print(f"   AFTER _geographic_validation:")
        print(f"   bina_no: {result_comp.get('bina_no', 'NOT_FOUND')}")
        
        return result_comp, result_conf
    
    # Apply patches
    parser._extract_building_components = debug_extract_building
    parser._extract_street_optimized = debug_extract_street
    parser._teknofest_context_inference = debug_context_inference
    parser._geographic_validation = debug_geo_validation
    
    print(f"Testing: {test_address}")
    
    result = parser.extract_components_rule_based(test_address)
    
    print(f"\n🏁 FINAL RESULT:")
    print(f"   bina_no: {result.get('components', {}).get('bina_no', 'NOT_FOUND')}")

if __name__ == "__main__":
    debug_rule_based_steps()