#!/usr/bin/env python3
"""
Debug ML method to see if it's truly disabled
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from address_parser import AddressParser

def debug_ml_method():
    """Debug ML method extraction in detail"""
    
    print("🔍 DEBUGGING ML METHOD")
    print("=" * 70)
    
    test_address = "İstanbul Kadıköy Moda Mahallesi Caferağa Sokak 10/A Daire:3"
    
    parser = AddressParser()
    
    # Test ML extraction directly
    print("1. Testing ML-based extraction:")
    ml_result = parser.extract_components_ml_based(test_address)
    print(f"   ML result: {ml_result}")
    print(f"   ML components: {ml_result.get('components', {})}")
    print(f"   ML confidence: {ml_result.get('confidence_scores', {})}")
    
    # Check if ML has any building numbers
    ml_components = ml_result.get('components', {})
    if 'bina_no' in ml_components:
        print(f"   ⚠️  ML method found building number: {ml_components['bina_no']}")
    else:
        print(f"   ✅ ML method has no building number")

if __name__ == "__main__":
    debug_ml_method()