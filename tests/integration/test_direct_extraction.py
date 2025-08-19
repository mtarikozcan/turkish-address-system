#!/usr/bin/env python3
"""
Test _extract_building_components method directly
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from address_parser import AddressParser

def test_direct_building_extraction():
    """Test _extract_building_components directly"""
    print("🔍 TESTING _extract_building_components DIRECTLY")
    print("=" * 60)
    
    parser = AddressParser()
    
    test_cases = [
        "10/A Daire:3",
        "No:25/B Kat:2",
        "15/C Daire:5",
        "Sokak 20/D",
        "Numara:12/A Daire:8"
    ]
    
    for address in test_cases:
        print(f"\n📍 Testing: '{address}'")
        print("-" * 40)
        
        # Test _extract_building_components directly
        components = {}
        confidence_scores = {}
        
        result_components, result_confidence = parser._extract_building_components(
            address, components, confidence_scores
        )
        
        print(f"Direct extraction results:")
        print(f"  Components: {result_components}")
        print(f"  Confidence: {result_confidence}")
        
        # Also test the rule-based extraction
        rule_result = parser.extract_components_rule_based(address)
        print(f"Rule-based extraction:")
        print(f"  Components: {rule_result.get('components', {})}")

if __name__ == "__main__":
    test_direct_building_extraction()