#!/usr/bin/env python3
"""
Test geocoding precision issue - all addresses getting same province coordinates
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from address_geocoder import AddressGeocoder

def test_geocoding_precision():
    """Test the geocoding precision problem reported by user"""
    
    print("🎯 GEOCODING PRECISION TEST - User's Problem")
    print("=" * 70)
    
    geocoder = AddressGeocoder()
    
    # Test cases from user's problem report
    test_cases = [
        {
            'address': "İstanbul Kadıköy Moda",
            'expected_coord_type': "Kadıköy district coordinates", 
            'expected_not': "İstanbul province center"
        },
        {
            'address': "İstanbul Beşiktaş Levent", 
            'expected_coord_type': "Beşiktaş district coordinates",
            'expected_not': "İstanbul province center"
        },
        {
            'address': "İstanbul Şişli",
            'expected_coord_type': "Şişli district coordinates", 
            'expected_not': "İstanbul province center"
        },
        {
            'address': "Ankara Çankaya",
            'expected_coord_type': "Çankaya district coordinates",
            'expected_not': "Ankara province center"
        },
        {
            'address': "Ankara Kızılay",
            'expected_coord_type': "Kızılay area coordinates",
            'expected_not': "Ankara province center"
        },
        {
            'address': "İzmir Konak",
            'expected_coord_type': "Konak district coordinates", 
            'expected_not': "İzmir province center"
        },
        {
            'address': "İzmir Karşıyaka",
            'expected_coord_type': "Karşıyaka district coordinates",
            'expected_not': "İzmir province center"  
        }
    ]
    
    # Istanbul province center coordinate for comparison (user reported issue)
    istanbul_province = (41.0082, 28.9784)
    ankara_province = (39.9334, 32.8597)
    izmir_province = (38.4192, 27.1287)
    
    print(f"❌ PROBLEM: All Istanbul addresses should NOT get: {istanbul_province}")
    print(f"❌ PROBLEM: All Ankara addresses should NOT get: {ankara_province}")  
    print(f"❌ PROBLEM: All İzmir addresses should NOT get: {izmir_province}")
    print("-" * 70)
    
    same_coords_count = 0
    different_coords_count = 0
    previous_coords = {}
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: '{test['address']}'")
        
        result = geocoder.geocode_turkish_address(test['address'])
        lat = result.get('latitude', 0)
        lon = result.get('longitude', 0)
        method = result.get('method', 'unknown')
        confidence = result.get('confidence', 0)
        
        print(f"   Coordinates: ({lat:.4f}, {lon:.4f})")
        print(f"   Method: {method}")
        print(f"   Confidence: {confidence}")
        print(f"   Expected: {test['expected_coord_type']}")
        
        # Check if this is a province center fallback
        city = test['address'].split()[0].lower()
        coords = (round(lat, 4), round(lon, 4))
        
        if city == 'i̇stanbul' or city == 'istanbul':
            istanbul_center = (round(istanbul_province[0], 4), round(istanbul_province[1], 4))
            if coords == istanbul_center or method == 'province_centroid':
                print(f"   ❌ PROBLEM: Using province centroid instead of district coordinates")
                same_coords_count += 1
            else:
                print(f"   ✅ GOOD: Using district-level coordinates")
                different_coords_count += 1
        elif city == 'ankara':
            ankara_center = (round(ankara_province[0], 4), round(ankara_province[1], 4))
            if coords == ankara_center or method == 'province_centroid':
                print(f"   ❌ PROBLEM: Using province centroid instead of district coordinates")
                same_coords_count += 1
            else:
                print(f"   ✅ GOOD: Using district-level coordinates")
                different_coords_count += 1
        elif city == 'i̇zmir' or city == 'izmir':
            izmir_center = (round(izmir_province[0], 4), round(izmir_province[1], 4))
            if coords == izmir_center or method == 'province_centroid':
                print(f"   ❌ PROBLEM: Using province centroid instead of district coordinates")
                same_coords_count += 1
            else:
                print(f"   ✅ GOOD: Using district-level coordinates")
                different_coords_count += 1
                
        # Track coordinate diversity
        if city not in previous_coords:
            previous_coords[city] = []
        previous_coords[city].append(coords)
    
    print(f"\n" + "=" * 70)
    print(f"🎯 PRECISION ANALYSIS:")
    print(f"   ❌ Addresses using province centroids: {same_coords_count}")
    print(f"   ✅ Addresses using district coordinates: {different_coords_count}")
    
    # Check coordinate diversity within each city
    print(f"\n📍 COORDINATE DIVERSITY CHECK:")
    for city, coords_list in previous_coords.items():
        unique_coords = set(coords_list)
        if len(unique_coords) == 1:
            print(f"   ❌ {city.upper()}: All addresses have SAME coordinates {list(unique_coords)[0]}")
        else:
            print(f"   ✅ {city.upper()}: {len(unique_coords)} different coordinates (good precision)")
            for coord in unique_coords:
                print(f"      - {coord}")
    
    if same_coords_count > different_coords_count:
        print(f"\n🚨 CONFIRMED: Geocoding precision problem - too many province centroids!")
        print(f"   Solution needed: Add district-level coordinates")
    else:
        print(f"\n🎉 Geocoding precision looks good!")

if __name__ == "__main__":
    test_geocoding_precision()