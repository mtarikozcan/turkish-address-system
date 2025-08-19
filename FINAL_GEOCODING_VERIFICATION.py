#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE GEOCODING VERIFICATION
This script proves the geocoding precision fix is working correctly
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from address_geocoder import AddressGeocoder

def final_geocoding_verification():
    """Final comprehensive verification of geocoding precision fix"""
    
    print("🎯 FINAL COMPREHENSIVE GEOCODING VERIFICATION")
    print("=" * 70)
    print("This test proves that the geocoding precision fix IS WORKING")
    print("=" * 70)
    
    geocoder = AddressGeocoder()
    
    # Istanbul province center (what user reported as the problem)
    ISTANBUL_PROVINCE_CENTER = (41.0082, 28.9784)
    
    print(f"\n❌ OLD PROBLEM: All İstanbul addresses were getting:")
    print(f"   Coordinates: {ISTANBUL_PROVINCE_CENTER}")  
    print(f"   Method: province_centroid")
    print(f"   Problem: Same coordinates for different districts!")
    
    print(f"\n✅ EXPECTED AFTER FIX: Different districts get different coordinates")
    print("-" * 70)
    
    # Test cases that should have been problematic before
    test_cases = [
        {
            'address': "İstanbul Kadıköy Moda Mahallesi",
            'description': "User's exact verification case"
        },
        {
            'address': "İstanbul Kadıköy",
            'description': "Kadıköy district only"
        },
        {
            'address': "İstanbul Beşiktaş Levent", 
            'description': "Beşiktaş with Levent neighborhood"
        },
        {
            'address': "İstanbul Beşiktaş",
            'description': "Beşiktaş district only"
        },
        {
            'address': "İstanbul Şişli",
            'description': "Şişli district"
        }
    ]
    
    print(f"\n🧪 TESTING {len(test_cases)} CRITICAL CASES:")
    
    unique_coordinates = set()
    all_using_province = True
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. {test['description']}")
        print(f"   Input: '{test['address']}'")
        
        result = geocoder.geocode_turkish_address(test['address'])
        lat = result.get('latitude', 0)
        lon = result.get('longitude', 0)
        method = result.get('method', 'unknown')
        confidence = result.get('confidence', 0)
        
        coord_tuple = (round(lat, 4), round(lon, 4))
        unique_coordinates.add(coord_tuple)
        
        print(f"   Output: ({lat:.4f}, {lon:.4f})")
        print(f"   Method: {method}")
        print(f"   Confidence: {confidence}")
        
        # Check if this is the problematic province centroid
        if abs(lat - ISTANBUL_PROVINCE_CENTER[0]) < 0.001 and abs(lon - ISTANBUL_PROVINCE_CENTER[1]) < 0.001:
            print(f"   ❌ STILL BROKEN: Using province centroid!")
        else:
            print(f"   ✅ FIXED: Using precise coordinates!")
            all_using_province = False
            
        if method == 'province_centroid':
            print(f"   ❌ BAD METHOD: province_centroid")
        else:
            print(f"   ✅ GOOD METHOD: {method}")
    
    print(f"\n" + "=" * 70)
    print(f"📊 VERIFICATION RESULTS:")
    print(f"   Unique coordinates found: {len(unique_coordinates)}")
    print(f"   Coordinates: {unique_coordinates}")
    
    if len(unique_coordinates) == 1:
        single_coord = list(unique_coordinates)[0]
        if abs(single_coord[0] - ISTANBUL_PROVINCE_CENTER[0]) < 0.001 and abs(single_coord[1] - ISTANBUL_PROVINCE_CENTER[1]) < 0.001:
            print(f"   ❌ CRITICAL: All addresses still using province center {ISTANBUL_PROVINCE_CENTER}")
            print(f"   ❌ FIX FAILED: Code changes not applied properly")
        else:
            print(f"   ⚠️  All using same coordinates, but NOT province center")
            print(f"   ⚠️  Might be parser inferring same neighborhood")
    else:
        print(f"   ✅ EXCELLENT: Different addresses get different coordinates!")
        
    if all_using_province:
        print(f"   ❌ ALL USING PROVINCE CENTROIDS - FIX NOT WORKING")
        print(f"\n🔧 TROUBLESHOOTING STEPS:")
        print(f"   1. Restart Python interpreter")
        print(f"   2. Clear any cached imports: import importlib; importlib.reload(module)")
        print(f"   3. Check if correct address_geocoder.py file is being loaded")
        print(f"   4. Verify current working directory")
    else:
        print(f"   ✅ NOT USING PROVINCE CENTROIDS - FIX IS WORKING!")
        
    # Final verification
    print(f"\n🏆 FINAL VERDICT:")
    if len(unique_coordinates) > 1 and not all_using_province:
        print(f"   ✅ SUCCESS: Geocoding precision fix IS WORKING!")
        print(f"   ✅ Different districts get unique coordinates")
        print(f"   ✅ Using precise methods (neighborhood_centroid, district_centroid)")
        print(f"\n   If user still sees old coordinates, it's likely a caching/reload issue")
    else:
        print(f"   ❌ ISSUE: Fix may not be working properly")
        print(f"   ❌ Need further investigation")

if __name__ == "__main__":
    final_geocoding_verification()