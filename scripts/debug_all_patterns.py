#!/usr/bin/env python3
"""
Test all regex patterns that could match numbers from the address
"""

import re

def test_all_number_patterns():
    """Test all patterns that could match numbers"""
    
    # All possible patterns that could match numbers
    test_patterns = [
        # From building patterns
        (r'\b(?:no|numara|num)\.?\s*:?\s*(\d+[\/\-][a-zA-Z]+)\b', 'building_compound'),
        (r'\b(?:no|numara|num)\.?\s*:?\s*(\d+[a-zA-Z])\b', 'building_letter'),
        (r'\b(?:no|numara|num)\.?\s*:?\s*(\d+)\b', 'building_simple'),
        (r'\b(\d+[\/\-][a-zA-Z]+)(?:\s+|$)', 'building_standalone_compound'),
        (r'\b(\d+[a-zA-Z])(?:\s+|$)', 'building_standalone_letter'),
        (r'(?:caddesi|sokak|bulvar)\s+(\d+[\/\-]?[a-zA-Z]*)\b', 'building_after_street'),
        (r'\b(\d+)(?:\s+(?:no|numara)|\s*$)', 'building_end_or_with_no'),
        
        # From apartment patterns
        (r'\b(?:daire|dair|dt|d|apt|apartman)\.?\s*:?\s*(\d+[a-zA-Z]?)\b', 'apartment_explicit'),
        (r'\b([a-zA-Z])\s+(?:daire|dair|apt)\b', 'apartment_letter'),
        
        # From postal code patterns
        (r'\b(\d{5})\b', 'postal_5digit'),
        (r'(?i)\bpk\s*:?\s*(\d{5})\b', 'postal_pk'),
        (r'(?i)\bposta\s+kodu\s*:?\s*(\d{5})\b', 'postal_full'),
        
        # General number patterns that might interfere
        (r':(\d+)', 'any_after_colon'),
        (r'\b(\d+)\b', 'any_number'),
    ]
    
    test_address = "10/A Daire:3"
    
    print("🔍 TESTING ALL NUMBER PATTERNS")
    print("=" * 60)
    print(f"Address: '{test_address}'")
    print("-" * 60)
    
    for pattern, label in test_patterns:
        match = re.search(pattern, test_address, re.IGNORECASE)
        if match:
            print(f"✅ {label:25} → '{pattern}' → MATCH: '{match.group(1)}'")
        else:
            print(f"❌ {label:25} → No match")

if __name__ == "__main__":
    test_all_number_patterns()