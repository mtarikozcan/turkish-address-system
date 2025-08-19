#!/usr/bin/env python3
"""
Debug why İstanbul Kadıköy is getting parsed with unexpected mahalle
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from address_geocoder import AddressGeocoder

def debug_parsing_issue():
    """Debug unexpected parsing behavior"""
    
    print("🔍 DEBUGGING PARSING BEHAVIOR")
    print("=" * 50)
    
    geocoder = AddressGeocoder()
    
    # Test different address formats
    test_addresses = [
        "İstanbul Kadıköy",
        "İstanbul Kadıköy Moda", 
        "İstanbul Beşiktaş",
        "İstanbul Beşiktaş Levent"
    ]
    
    for address in test_addresses:
        print(f"\nTesting: '{address}'")
        
        # Parse the address to see components
        if hasattr(geocoder, 'parser'):
            parsed = geocoder.parser.parse_address(address)
            components = parsed.get('components', {})
            print(f"  Parsed components: {components}")
            
            # Test geocoding with these components
            result = geocoder.geocode_turkish_address(address)
            print(f"  Geocoded: ({result.get('latitude'):.4f}, {result.get('longitude'):.4f})")
            print(f"  Method: {result.get('method')}")
            print(f"  Matched: {result.get('matched_components', {})}")
            
            # Check what the centroid lookup returns for these components
            centroid_result = geocoder._find_centroid_coordinates(components)
            if centroid_result:
                print(f"  Direct centroid lookup: {centroid_result.get('method')} - ({centroid_result.get('latitude'):.4f}, {centroid_result.get('longitude'):.4f})")

if __name__ == "__main__":
    debug_parsing_issue()