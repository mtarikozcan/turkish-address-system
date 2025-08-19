#!/usr/bin/env python3
"""
Direct comparison of extract_components_rule_based vs full pipeline
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from address_parser import AddressParser

def test_direct_vs_pipeline():
    """Test direct call vs pipeline call using the same parser instance"""
    
    print("🔍 DIRECT VS PIPELINE COMPARISON")
    print("=" * 70)
    
    test_address = "İstanbul Kadıköy Moda Mahallesi Caferağa Sokak 10/A Daire:3"
    parser = AddressParser()  # Single instance
    
    print(f"Test address: {test_address}")
    print("-" * 70)
    
    # Test 1: Direct call to extract_components_rule_based
    print("1. Direct call to extract_components_rule_based:")
    direct_result = parser.extract_components_rule_based(test_address)
    print(f"   bina_no: {direct_result.get('components', {}).get('bina_no', 'NOT_FOUND')}")
    
    # Test 2: Full pipeline call
    print("\n2. Full pipeline call (parse_address):")
    pipeline_result = parser.parse_address(test_address)
    print(f"   bina_no: {pipeline_result.get('components', {}).get('bina_no', 'NOT_FOUND')}")
    
    # Test 3: Call direct again to see if it changes
    print("\n3. Direct call again after pipeline:")
    direct_result2 = parser.extract_components_rule_based(test_address)
    print(f"   bina_no: {direct_result2.get('components', {}).get('bina_no', 'NOT_FOUND')}")
    
    # Test 4: Different parser instance
    print("\n4. New parser instance - direct call:")
    parser2 = AddressParser()
    direct_result3 = parser2.extract_components_rule_based(test_address)
    print(f"   bina_no: {direct_result3.get('components', {}).get('bina_no', 'NOT_FOUND')}")

if __name__ == "__main__":
    test_direct_vs_pipeline()