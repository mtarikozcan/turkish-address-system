#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direct test of building extraction method
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from address_parser import AddressParser

def test_building_direct():
    """Test building extraction method directly"""
    
    parser = AddressParser()
    
    # Test the building extraction method directly
    address = "istanbul bagdat caddesi 127/A"
    components = {}
    confidence_scores = {}
    
    print(f"Testing: {address}")
    
    # Call building extraction directly
    components, confidence_scores = parser._extract_building_components(
        address, components, confidence_scores
    )
    
    print(f"After building extraction:")
    print(f"  Components: {components}")
    print(f"  Expected daire_no: A")
    print(f"  Actual daire_no: {components.get('daire_no', 'MISSING')}")
    
    # Also test the regex directly
    import re
    pattern = r'\b(\d+)[\/\-]([a-zA-Z]+)\b'
    match = re.search(pattern, address)
    if match:
        print(f"\nDirect regex test:")
        print(f"  Pattern: {pattern}")
        print(f"  Groups: {match.groups()}")
        print(f"  Group 1 (number): {match.group(1)}")
        print(f"  Group 2 (letter): {match.group(2)}")

if __name__ == "__main__":
    test_building_direct()