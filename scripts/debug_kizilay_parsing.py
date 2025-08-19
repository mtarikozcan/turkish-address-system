#!/usr/bin/env python3
"""
Debug why "Ankara Kızılay" gets Çankaya coordinates instead of Kızılay coordinates
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from address_geocoder import AddressGeocoder

def debug_kizilay_parsing():
    """Debug Kızılay coordinate issue"""
    
    print("🔍 DEBUGGING ANKARA KIZILAY COORDINATE ISSUE")
    print("=" * 70)
    
    geocoder = AddressGeocoder()
    
    test_addresses = [
        "Ankara Çankaya",
        "Ankara Kızılay", 
        "Ankara Kizilay"
    ]
    
    for address in test_addresses:
        print(f"\nTesting: '{address}'")
        
        # Parse the address to see components
        if hasattr(geocoder, 'parser'):
            parsed = geocoder.parser.parse_address(address)
            print(f"  Parsed components: {parsed.get('components', {})}")
        
        # Test geocoding
        result = geocoder.geocode_turkish_address(address)
        print(f"  Coordinates: ({result.get('latitude')}, {result.get('longitude')})")
        print(f"  Method: {result.get('method')}")
        print(f"  Matched components: {result.get('matched_components', {})}")
    
    # Check if Kızılay coordinates are in the district database
    print(f"\n🔍 CHECKING DISTRICT COORDINATE DATABASE:")
    
    # Access the internal coordinate method to see what's matched
    components_kizilay = {'il': 'ankara', 'ilce': 'kızılay'}
    components_cankaya = {'il': 'ankara', 'ilce': 'çankaya'}
    
    print(f"Testing components for Kızılay: {components_kizilay}")
    kizilay_coords = geocoder._find_centroid_coordinates(components_kizilay)
    print(f"  Result: {kizilay_coords}")
    
    print(f"Testing components for Çankaya: {components_cankaya}")
    cankaya_coords = geocoder._find_centroid_coordinates(components_cankaya)
    print(f"  Result: {cankaya_coords}")

if __name__ == "__main__":
    debug_kizilay_parsing()