#!/usr/bin/env python3
"""
Debug address normalization to see if it corrupts building numbers
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from address_parser import AddressParser

def debug_normalization():
    """Debug what happens during address normalization"""
    
    print("🔍 DEBUGGING ADDRESS NORMALIZATION")
    print("=" * 70)
    
    raw_address = "İstanbul Kadıköy Moda Mahallesi Caferağa Sokak 10/A Daire:3"
    parser = AddressParser()
    
    print(f"Raw address: '{raw_address}'")
    
    # Test normalization
    normalized_address = parser._normalize_text(raw_address)
    print(f"Normalized:  '{normalized_address}'")
    
    # Check if normalization changed anything critical
    if raw_address != normalized_address:
        print("⚠️  NORMALIZATION CHANGED THE ADDRESS!")
        print("   This could be the source of the issue")
    else:
        print("✅ Normalization didn't change the address")
    
    # Test extraction on both versions
    print(f"\nTesting extraction on both versions:")
    
    print(f"1. Rule-based on raw address:")
    result_raw = parser.extract_components_rule_based(raw_address)
    print(f"   bina_no: {result_raw.get('components', {}).get('bina_no', 'NOT_FOUND')}")
    
    print(f"2. Rule-based on normalized address:")
    result_norm = parser.extract_components_rule_based(normalized_address)
    print(f"   bina_no: {result_norm.get('components', {}).get('bina_no', 'NOT_FOUND')}")
    
    print(f"3. Full pipeline (uses normalized):")
    result_full = parser.parse_address(raw_address)
    print(f"   bina_no: {result_full.get('components', {}).get('bina_no', 'NOT_FOUND')}")

if __name__ == "__main__":
    debug_normalization()