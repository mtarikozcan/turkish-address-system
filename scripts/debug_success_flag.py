#!/usr/bin/env python3
"""
DEBUG SUCCESS FLAG ISSUE
Check why success is False when geocoding is clearly working
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def debug_success_flag():
    """Debug the success flag calculation"""
    print("🔍 SUCCESS FLAG DEBUG")
    print("=" * 50)
    
    try:
        from address_parser import AddressParser
        parser = AddressParser()
        
        test_address = "Etlik Mahallesi, Keçiören, Ankara"
        
        # Step 1: Check parsing result
        parsing_result = parser.parse_address(test_address)
        parsing_success = parsing_result.get('success', False)
        print(f"Parsing success: {parsing_success}")
        print(f"Parsing result keys: {list(parsing_result.keys())}")
        
        # Step 2: Check geocoding result
        components = parsing_result.get('components', {})
        geocoding_result = parser.geocode_address(components)
        geocoding_confidence = geocoding_result.get('confidence', 0)
        print(f"Geocoding confidence: {geocoding_confidence}")
        print(f"Geocoding result keys: {list(geocoding_result.keys())}")
        print(f"Geocoding result structure: {geocoding_result}")
        
        # Step 3: Check complete result
        complete_result = parser.parse_and_geocode_address(test_address)
        complete_success = complete_result.get('success', False)
        print(f"Complete success: {complete_success}")
        
        # Analysis
        print(f"\n📊 ANALYSIS:")
        print(f"parsing_result.get('success', False): {parsing_success}")
        print(f"geocoding_result.get('confidence', 0): {geocoding_confidence}")
        print(f"geocoding_result.get('confidence', 0) > 0: {geocoding_confidence > 0}")
        print(f"Final success calculation: {parsing_success} AND {geocoding_confidence > 0} = {parsing_success and geocoding_confidence > 0}")
        
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        return False

def main():
    success = debug_success_flag()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)