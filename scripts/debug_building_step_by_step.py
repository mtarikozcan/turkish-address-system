#!/usr/bin/env python3
"""
Step-by-step debug of building number extraction
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from address_parser import AddressParser

def debug_step_by_step():
    """Debug building number extraction step by step"""
    
    print("🔍 STEP-BY-STEP BUILDING NUMBER DEBUG")
    print("=" * 70)
    
    # Test with the problematic address
    test_address = "İstanbul Kadıköy Moda Mahallesi Caferağa Sokak 10/A Daire:3"
    print(f"Full Address: '{test_address}'")
    print("-" * 70)
    
    parser = AddressParser()
    
    # Step 1: Test direct building extraction
    print("\n1. Testing _extract_building_components directly:")
    components = {}
    confidence_scores = {}
    
    result_components, result_confidence = parser._extract_building_components(
        test_address, components, confidence_scores
    )
    print(f"   Direct extraction result: {result_components}")
    
    # Step 2: Test rule-based extraction  
    print("\n2. Testing extract_components_rule_based:")
    rule_result = parser.extract_components_rule_based(test_address)
    print(f"   Rule-based components: {rule_result.get('components', {})}")
    
    # Step 3: Test full parse_address
    print("\n3. Testing full parse_address:")
    full_result = parser.parse_address(test_address)
    print(f"   Full parse components: {full_result.get('components', {})}")
    
    # Step 4: Test with simplified address
    simple_address = "10/A Daire:3"
    print(f"\n4. Testing simplified address: '{simple_address}'")
    
    simple_result = parser.parse_address(simple_address)
    print(f"   Simple parse result: {simple_result.get('components', {})}")
    
    # Step 5: Test even simpler  
    minimal_address = "Sokak 10/A"
    print(f"\n5. Testing minimal address: '{minimal_address}'")
    
    minimal_result = parser.parse_address(minimal_address)
    print(f"   Minimal parse result: {minimal_result.get('components', {})}")

if __name__ == "__main__":
    debug_step_by_step()