#!/usr/bin/env python3
"""
CRITICAL DEBUG - Verify if geocoding fix actually worked or failed
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from address_geocoder import AddressGeocoder

def debug_geocoding_actual_issue():
    """Debug the actual geocoding issue reported by user"""
    
    print("🚨 CRITICAL DEBUG - GEOCODING FIX VERIFICATION")
    print("=" * 70)
    
    geocoder = AddressGeocoder()
    
    # User's exact verification test
    test_address = "İstanbul Kadıköy Moda Mahallesi"
    
    print(f"🔍 USER'S VERIFICATION TEST:")
    print(f"Input: '{test_address}'")
    print(f"Expected: (40.9833, 29.0333) with district_centroid method")
    print(f"NOT: (41.0082, 28.9784) with province_centroid")
    print("-" * 70)
    
    # Test geocoding
    result = geocoder.geocode_turkish_address(test_address)
    
    print(f"\n📊 ACTUAL RESULT:")
    print(f"Coordinates: ({result.get('latitude', 'N/A')}, {result.get('longitude', 'N/A')})")
    print(f"Method: {result.get('method', 'UNKNOWN')}")
    print(f"Confidence: {result.get('confidence', 'N/A')}")
    print(f"Matched components: {result.get('matched_components', {})}")
    
    # Check if it's the problematic province centroid
    lat = result.get('latitude', 0)
    lon = result.get('longitude', 0)
    method = result.get('method', 'unknown')
    
    istanbul_province = (41.0082, 28.9784)
    if abs(lat - istanbul_province[0]) < 0.001 and abs(lon - istanbul_province[1]) < 0.001:
        print(f"\n❌ CRITICAL ISSUE CONFIRMED: Still using province centroid!")
        print(f"   Getting: ({lat}, {lon}) - İstanbul province center")
        print(f"   Method: {method}")
    else:
        print(f"\n✅ Fix appears to be working - using precise coordinates")
    
    # Test additional cases to confirm the pattern
    print(f"\n🧪 TESTING ADDITIONAL CASES TO CONFIRM PATTERN:")
    
    additional_tests = [
        "İstanbul Beşiktaş Levent",
        "İstanbul Şişli", 
        "Ankara Çankaya",
        "İzmir Konak"
    ]
    
    coords_found = []
    methods_found = []
    
    for address in additional_tests:
        result = geocoder.geocode_turkish_address(address)
        coord = (result.get('latitude', 0), result.get('longitude', 0))
        method = result.get('method', 'unknown')
        
        coords_found.append(coord)
        methods_found.append(method)
        
        print(f"   {address}: {coord} ({method})")
    
    # Analyze results
    print(f"\n🔍 ANALYSIS:")
    unique_coords = set(coords_found)
    unique_methods = set(methods_found)
    
    print(f"   Unique coordinates found: {len(unique_coords)}")
    print(f"   Unique methods found: {unique_methods}")
    
    if len(unique_coords) == 1:
        print(f"   ❌ PROBLEM: All addresses getting same coordinates - fix didn't work!")
    else:
        print(f"   ✅ GOOD: Different addresses getting different coordinates")
        
    if 'province_centroid' in unique_methods:
        print(f"   ❌ PROBLEM: Still falling back to province_centroid")
    
    # Check if the coordinate databases exist
    print(f"\n🔍 CHECKING INTERNAL COORDINATE DATABASES:")
    
    # Try to access the internal coordinate method directly
    components = {'il': 'istanbul', 'ilce': 'kadıköy', 'mahalle': 'moda'}
    print(f"   Testing components: {components}")
    
    try:
        centroid_result = geocoder._find_centroid_coordinates(components)
        if centroid_result:
            print(f"   Internal centroid lookup result: {centroid_result}")
        else:
            print(f"   ❌ Internal centroid lookup returned None - database issue!")
            
        # Check if neighborhood_coords exists
        if hasattr(geocoder, 'neighborhood_coords'):
            print(f"   ✅ neighborhood_coords database exists")
        else:
            print(f"   ❌ neighborhood_coords database NOT FOUND - not added properly!")
            
    except Exception as e:
        print(f"   ❌ Error accessing internal methods: {e}")

if __name__ == "__main__":
    debug_geocoding_actual_issue()