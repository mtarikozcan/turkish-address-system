#!/usr/bin/env python3
"""
Comprehensive trace of building number through entire parsing pipeline
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

import re

def test_raw_patterns():
    """Test the raw regex patterns to make sure they work"""
    
    print("🔍 TESTING RAW REGEX PATTERNS")
    print("=" * 70)
    
    test_text = "İstanbul Kadıköy Moda Mahallesi Caferağa Sokak 10/A Daire:3"
    print(f"Test text: '{test_text}'")
    
    # Patterns from _extract_building_components 
    patterns = [
        (r'\b(?:no|numara|num)\.?\s*:?\s*(\d+[\/\-][a-zA-Z]+)\b', 'no_compound'),
        (r'\b(?:no|numara|num)\.?\s*:?\s*(\d+[a-zA-Z])\b', 'no_letter'),
        (r'\b(?:no|numara|num)\.?\s*:?\s*(\d+)\b', 'no_simple'),
        (r'\b(\d+[\/\-][a-zA-Z]+)(?:\s+|$)', 'standalone_compound'),  # This should match 10/A
        (r'\b(\d+[a-zA-Z])(?:\s+|$)', 'standalone_letter'),
        (r'(?:caddesi|sokak|bulvar)\s+(\d+[\/\-]?[a-zA-Z]*)\b', 'after_street'),
        (r'\b(\d+)\s+(?:no|numara)\b', 'with_no_keyword'),
    ]
    
    print("\nPattern matching results:")
    for pattern, label in patterns:
        match = re.search(pattern, test_text, re.IGNORECASE)
        if match:
            print(f"   ✅ {label:20} → '{pattern}' → MATCH: '{match.group(1)}'")
        else:
            print(f"   ❌ {label:20} → No match")
    
    # Also test apartment patterns to see if there's conflict
    print(f"\nApartment pattern matching:")
    apt_patterns = [
        (r'\b(?:daire|dair|dt|d|apt|apartman)\.?\s*:?\s*(\d+[a-zA-Z]?)\b', 'apartment_explicit'),
        (r'\b([a-zA-Z])\s+(?:daire|dair|apt)\b', 'apartment_letter'),
    ]
    
    for pattern, label in apt_patterns:
        match = re.search(pattern, test_text, re.IGNORECASE)
        if match:
            print(f"   ✅ {label:20} → MATCH: '{match.group(1)}'")
        else:
            print(f"   ❌ {label:20} → No match")

def test_parsing_with_different_inputs():
    """Test parsing with different address formats"""
    
    print(f"\n🔍 TESTING DIFFERENT ADDRESS FORMATS") 
    print("=" * 70)
    
    from address_parser import AddressParser
    parser = AddressParser()
    
    test_cases = [
        "10/A Daire:3",
        "Sokak 10/A Daire:3", 
        "Caferağa Sokak 10/A Daire:3",
        "İstanbul Kadıköy Moda Mahallesi Caferağa Sokak 10/A Daire:3",
    ]
    
    for test_addr in test_cases:
        print(f"\nTesting: '{test_addr}'")
        result = parser.parse_address(test_addr)
        components = result.get('components', {})
        bina_no = components.get('bina_no', 'NOT_FOUND')
        daire_no = components.get('daire_no', 'NOT_FOUND') 
        print(f"   bina_no: {bina_no}")
        print(f"   daire_no: {daire_no}")

if __name__ == "__main__":
    test_raw_patterns()
    test_parsing_with_different_inputs()