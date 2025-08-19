#!/usr/bin/env python3
"""
Debug detailed regex patterns for building numbers
"""

import re

def test_building_regex_detailed():
    """Test building number regex patterns with detailed debugging"""
    
    # Patterns from _extract_building_components
    bina_patterns = [
        r'\b(?:no|numara|num)\.?\s*:?\s*(\d+[\/\-][a-zA-Z]+)\b',  # "No:25/B", "Numara:12/A" 
        r'\b(?:no|numara|num)\.?\s*:?\s*(\d+[a-zA-Z])\b',  # "No:25A", "Numara:12B"
        r'\b(?:no|numara|num)\.?\s*:?\s*(\d+)\b',  # "No:25", "Numara:12"
        r'\b(\d+[\/\-][a-zA-Z]+)(?:\s+|$)',  # "10/A ", "25/B " - PRESERVE AS COMPOUND
        r'\b(\d+[a-zA-Z])(?:\s+|$)',  # "127A ", "25B " - single unit numbers with letters
        r'(?:caddesi|sokak|bulvar)\s+(\d+[\/\-]?[a-zA-Z]*)\b',  # "Gazi Caddesi 127/A"
        r'\b(\d+)(?:\s+(?:no|numara)|\s*$)',  # "127 no", "25 numara", standalone at end
    ]
    
    # Also include apartment patterns to see if there's confusion
    daire_patterns = [
        r'\b(?:daire|dair|dt|d|apt|apartman)\.?\s*:?\s*(\d+[a-zA-Z]?)\b',  # "Daire:3", "Dt:5"
        r'\b([a-zA-Z])\s+(?:daire|dair|apt)\b',  # "A daire"
    ]
    
    test_cases = [
        "10/A Daire:3",
        "No:25/B Kat:2",
        "15/C Daire:5",
        "Sokak 20/D",
        "Numara:12/A Daire:8"
    ]
    
    print("🔍 DETAILED BUILDING NUMBER REGEX DEBUG")
    print("=" * 60)
    
    for address in test_cases:
        print(f"\n📍 Testing: '{address}'")
        print("-" * 50)
        
        print("Building number patterns:")
        building_match_found = False
        for i, pattern in enumerate(bina_patterns):
            match = re.search(pattern, address, re.IGNORECASE)
            if match:
                print(f"   ✅ Pattern {i+1}: '{pattern}' → MATCH: '{match.group(1)}'")
                building_match_found = True
                break  # Simulate the break in the actual code
            else:
                print(f"   ❌ Pattern {i+1}: '{pattern}' → No match")
        
        print("\nApartment number patterns:")
        for i, pattern in enumerate(daire_patterns):
            match = re.search(pattern, address, re.IGNORECASE)
            if match:
                print(f"   ✅ Pattern {i+1}: '{pattern}' → MATCH: '{match.group(1)}'")
            else:
                print(f"   ❌ Pattern {i+1}: '{pattern}' → No match")

if __name__ == "__main__":
    test_building_regex_detailed()