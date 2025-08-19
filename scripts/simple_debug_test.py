#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple debug test for district extraction
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from address_parser import AddressParser

def test_district_debug():
    """Test district extraction with debug"""
    
    parser = AddressParser()
    
    # Enable debug logging
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Test simple case
    test_address = "istanbul kadikoy moda"
    print(f"Testing: {test_address}")
    
    result = parser.parse_address(test_address)
    components = result.get('components', {})
    
    print(f"Components: {components}")
    print(f"Expected ilce: Kadıköy")
    print(f"Actual ilce: {components.get('ilce', 'MISSING')}")

if __name__ == "__main__":
    test_district_debug()