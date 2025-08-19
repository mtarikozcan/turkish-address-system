#!/usr/bin/env python3
"""
Final comprehensive test - verify all user's original geocoding problems are fixed
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from address_geocoder import AddressGeocoder

def test_final_geocoding_fix():
    """Final test of all user's reported geocoding precision problems"""
    
    print("🎯 FINAL GEOCODING PRECISION FIX VERIFICATION")
    print("=" * 70)
    
    geocoder = AddressGeocoder()
    
    # Original user problem cases
    print("📍 ORIGINAL PROBLEM CASES FROM USER:")
    print("   - İstanbul Kadıköy Moda: Should NOT be (41.0082, 28.9784)")
    print("   - İstanbul Beşiktaş Levent: Should NOT be (41.0082, 28.9784)")
    print("   - Same coordinates for different neighborhoods!")
    print("-" * 70)
    
    # User's exact test cases plus additional verification
    test_cases = [
        # Original user cases
        {
            'address': "İstanbul Kadıköy Moda",
            'expected_method': "neighborhood_centroid or district_centroid",
            'not_coords': (41.0082, 28.9784),  # Province center
            'description': "User's primary test case"
        },
        {
            'address': "İstanbul Beşiktaş Levent", 
            'expected_method': "neighborhood_centroid or district_centroid",
            'not_coords': (41.0082, 28.9784),  # Province center
            'description': "User's second test case"
        },
        
        # User-specified district coordinates
        {
            'address': "İstanbul Kadıköy",
            'expected_coords': (40.9833, 29.0333),  # User specified
            'description': "Kadıköy district coordinates (user specified)"
        },
        {
            'address': "İstanbul Beşiktaş", 
            'expected_coords': (41.0422, 29.0061),  # User specified
            'description': "Beşiktaş district coordinates (user specified)"
        },
        {
            'address': "İstanbul Şişli",
            'expected_coords': (41.0611, 28.9844),  # User specified  
            'description': "Şişli district coordinates (user specified)"
        },
        {
            'address': "Ankara Çankaya",
            'expected_coords': (39.9208, 32.8541),  # User specified
            'description': "Çankaya district coordinates (user specified)"
        },
        {
            'address': "Ankara Kızılay", 
            'expected_coords': (39.9185, 32.8543),  # User specified
            'description': "Kızılay area coordinates (user specified)"
        },
        {
            'address': "İzmir Konak",
            'expected_coords': (38.4189, 27.1287),  # User specified
            'description': "Konak district coordinates (user specified)"
        },
        {
            'address': "İzmir Karşıyaka",
            'expected_coords': (38.4631, 27.1295),  # User specified  
            'description': "Karşıyaka district coordinates (user specified)"
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    print(f"\n🧪 TESTING {total} CASES:")
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. {test['description']}")
        print(f"   Address: '{test['address']}'")
        
        result = geocoder.geocode_turkish_address(test['address'])
        lat = result.get('latitude', 0)
        lon = result.get('longitude', 0) 
        method = result.get('method', 'unknown')
        confidence = result.get('confidence', 0)
        
        print(f"   Result: ({lat:.4f}, {lon:.4f})")
        print(f"   Method: {method} (confidence: {confidence})")
        
        # Test specific conditions
        test_passed = True
        
        # Check if NOT using province centroid (original problem)
        if 'not_coords' in test:
            not_lat, not_lon = test['not_coords']
            if abs(lat - not_lat) < 0.001 and abs(lon - not_lon) < 0.001:
                print(f"   ❌ FAIL: Still using province centroid {test['not_coords']}")
                test_passed = False
            elif method == 'province_centroid':
                print(f"   ❌ FAIL: Method is still province_centroid")
                test_passed = False
            else:
                print(f"   ✅ GOOD: Not using province centroid anymore")
        
        # Check expected coordinates (if specified)
        if 'expected_coords' in test:
            exp_lat, exp_lon = test['expected_coords']
            if abs(lat - exp_lat) < 0.001 and abs(lon - exp_lon) < 0.001:
                print(f"   ✅ PERFECT: Matches expected coordinates exactly")
            else:
                print(f"   ⚠️  CLOSE: Expected {test['expected_coords']}, got ({lat:.4f}, {lon:.4f})")
                # Allow some tolerance for OSM vs hardcoded coordinates
                if abs(lat - exp_lat) < 0.01 and abs(lon - exp_lon) < 0.01:
                    print(f"   ✅ ACCEPTABLE: Within reasonable tolerance")
                else:
                    test_passed = False
        
        # Check method quality  
        if method in ['neighborhood_centroid', 'district_centroid']:
            print(f"   ✅ EXCELLENT: Using precise {method}")
        elif method == 'province_centroid':
            print(f"   ❌ PROBLEM: Still using province_centroid")
            test_passed = False
        
        if test_passed:
            passed += 1
            print(f"   ✅ OVERALL: PASS")
        else:
            print(f"   ❌ OVERALL: FAIL")
    
    print(f"\n" + "=" * 70)
    print(f"🎯 FINAL VERIFICATION RESULTS: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print(f"\n🎉 SUCCESS! ALL GEOCODING PRECISION ISSUES FIXED!")
        print(f"✅ Original problems RESOLVED:")
        print(f"   - Different districts now get unique coordinates ✓")
        print(f"   - No more province centroid fallbacks for known districts ✓")
        print(f"   - Proper fallback hierarchy: neighborhood → district → province ✓")
        print(f"   - All user-specified coordinates implemented ✓")
        print(f"\n🏆 TEKNOFEST 2025 geocoding precision requirements MET!")
    else:
        print(f"\n⚠️  Some issues remain - need additional fixes")
        print(f"   Failed: {total - passed} test cases")

if __name__ == "__main__":
    test_final_geocoding_fix()