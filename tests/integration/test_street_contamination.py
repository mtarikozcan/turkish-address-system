#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test street contamination issue
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from address_parser import AddressParser

def test_street_contamination():
    """Test street contamination with detailed logging"""
    
    # Set up debug logging
    logging.basicConfig(level=logging.DEBUG, 
                       format='%(name)s - %(levelname)s - %(message)s')
    
    parser = AddressParser()
    
    test_address = "istanbul moda bagdat caddesi"
    print(f"\nTesting street contamination: {test_address}")
    print("=" * 60)
    
    result = parser.parse_address(test_address)
    components = result.get('components', {})
    
    print(f"\nFinal Components:")
    for comp, value in components.items():
        print(f"  {comp}: {value}")
    
    print(f"\nExpected sokak: 'Bağdat Caddesi'")
    print(f"Actual sokak: '{components.get('sokak', 'MISSING')}'")
    
    # Check if street contains city/neighborhood contamination
    sokak = components.get('sokak', '')
    if 'İstanbul' in sokak or 'istanbul' in sokak.lower():
        print("🚨 CONTAMINATION: Street contains city name")
    if 'Moda' in sokak or 'moda' in sokak.lower():
        print("🚨 CONTAMINATION: Street contains neighborhood name")
    
    if sokak == "Bağdat Caddesi":
        print("✅ Street extraction is clean!")
    else:
        print("❌ Street extraction has contamination")

if __name__ == "__main__":
    test_street_contamination()