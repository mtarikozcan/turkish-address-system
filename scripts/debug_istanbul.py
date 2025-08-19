#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug Istanbul exclusion issue
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from address_parser import AddressParser

def debug_istanbul():
    """Debug why Istanbul is not being excluded from street"""
    
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    parser = AddressParser()
    
    address = "istanbul kadıköy bağdat caddesi"
    result = parser.parse_address(address)
    components = result.get('components', {})
    
    print(f"Address: {address}")
    print(f"Components: {components}")
    print(f"Sokak: '{components.get('sokak', 'MISSING')}'")
    print(f"Expected sokak: 'Bağdat Caddesi'")
    
    # Check if Istanbul should be excluded
    if 'Istanbul' in components.get('sokak', ''):
        print("❌ Istanbul NOT properly excluded from street")
        
        il_component = components.get('il', '')
        print(f"Il component: '{il_component}'")
        print(f"Il normalized: '{parser._normalize_to_ascii(il_component).lower()}'")
        
        # Test the matching logic
        test_word = 'Istanbul'
        test_word_norm = parser._normalize_to_ascii(test_word).lower()
        il_norm = parser._normalize_to_ascii(il_component).lower()
        
        print(f"Test word: '{test_word}'")
        print(f"Test word normalized: '{test_word_norm}'")
        print(f"Should match il: {test_word_norm == il_norm}")
    else:
        print("✅ Istanbul properly excluded")

if __name__ == "__main__":
    debug_istanbul()