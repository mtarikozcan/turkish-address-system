#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug building parsing (127/A format)
"""

import sys
import re
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from address_parser import AddressParser

def debug_building():
    """Debug building parsing for 127/A format"""
    
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    parser = AddressParser()
    
    address = "istanbul bagdat caddesi 127/A"
    result = parser.parse_address(address)
    components = result.get('components', {})
    
    print(f"Address: {address}")
    print(f"Components: {components}")
    print(f"Expected: bina_no='127', daire_no='A'")
    print(f"Actual bina_no: {components.get('bina_no', 'MISSING')}")
    print(f"Actual daire_no: {components.get('daire_no', 'MISSING')}")
    
    # Test the regex pattern directly
    pattern = r'\b(\d+)[\/\-]([a-zA-Z]+)\b'
    match = re.search(pattern, address)
    if match:
        print(f"✅ Regex pattern matches: {match.group(1)}/{match.group(2)}")
        print(f"   Number of groups: {len(match.groups())}")
        print(f"   All groups: {match.groups()}")
    else:
        print("❌ Regex pattern does not match")
    
    # Test all patterns from the building parsing
    bina_patterns = [
        r'\b(\d+)[\/\-]([a-zA-Z]+)\b',  # "127/A", "25-B" - CHECK THIS FIRST
        r'\b(?:no|numara|num)\.?\s*:?\s*(\d+[a-zA-Z]?)\b',  # "No: 127", "Numara 25A"  
        r'\b(\d+)\s+(?:no|numara)\b',  # "127 no", "25 numara"
        r'(?:caddesi|sokak|bulvar)\s+(\d+)\b',  # "Gazi Caddesi 127"
        r'\b(\d+)\s*(?:$|\s)',  # Standalone numbers at end
    ]
    
    print(f"\nTesting all building patterns:")
    for i, pattern in enumerate(bina_patterns):
        match = re.search(pattern, address, re.IGNORECASE)
        if match:
            print(f"  Pattern {i}: {pattern} -> MATCHES")
            print(f"    Groups: {match.groups()}")
            if '/' in pattern or '-' in pattern:
                print(f"    Has slash/dash: YES")
            else:
                print(f"    Has slash/dash: NO")
            break  # Same logic as parser - break on first match
        else:
            print(f"  Pattern {i}: {pattern} -> no match")
    
    # Test if it's being extracted but not assigned correctly
    if 'bina_no' in components and 'daire_no' not in components:
        print("🔍 Building number extracted but apartment number missing")
        print("🔧 Check apartment pattern logic")

if __name__ == "__main__":
    debug_building()