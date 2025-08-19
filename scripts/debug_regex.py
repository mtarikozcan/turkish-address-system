#!/usr/bin/env python3
"""
Debug regex patterns for building numbers
"""

import re

def test_building_regex():
    """Test building number regex patterns"""
    
    # Current patterns from address_parser.py
    bina_patterns = [
        r'\b(?:no|numara|num)\.?\s*:?\s*(\d+[\/\-][a-zA-Z]+)\b',  # "No:25/B", "Numara:12/A" 
        r'\b(?:no|numara|num)\.?\s*:?\s*(\d+[a-zA-Z])\b',  # "No:25A", "Numara:12B"
        r'\b(?:no|numara|num)\.?\s*:?\s*(\d+)\b',  # "No:25", "Numara:12"
        r'\b(\d+[\/\-][a-zA-Z]+)(?:\s+|$)',  # "10/A ", "25/B " - PRESERVE AS COMPOUND
        r'\b(\d+[a-zA-Z])(?:\s+|$)',  # "127A ", "25B " - single unit numbers with letters
        r'(?:caddesi|sokak|bulvar)\s+(\d+[\/\-]?[a-zA-Z]*)\b',  # "Gazi Caddesi 127/A"
        r'\b(\d+)(?:\s+(?:no|numara)|\s*$)',  # "127 no", "25 numara", standalone at end
    ]
    
    test_cases = [
        "10/A Daire:3",
        "No:25/B Kat:2",
        "15/C Daire:5",
        "Sokak 20/D",
        "Numara:12/A Daire:8"
    ]
    
    print("🔍 TESTING BUILDING NUMBER REGEX PATTERNS")
    print("=" * 60)
    
    for address in test_cases:
        print(f"\n📍 Testing: '{address}'")
        print("-" * 30)
        
        for i, pattern in enumerate(bina_patterns):
            match = re.search(pattern, address, re.IGNORECASE)
            if match:
                print(f"   Pattern {i+1}: '{pattern}'")
                print(f"   ✅ MATCH: '{match.group(1)}'")
                break
        else:
            print(f"   ❌ No patterns matched")

if __name__ == "__main__":
    test_building_regex()