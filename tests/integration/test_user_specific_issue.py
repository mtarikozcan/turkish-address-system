#!/usr/bin/env python3
"""
Test the exact user verification case to see if there's a discrepancy
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from address_geocoder import AddressGeocoder

def test_user_specific_issue():
    """Test exact user verification case"""
    
    print("🔍 USER'S EXACT VERIFICATION TEST")
    print("=" * 50)
    
    geocoder = AddressGeocoder()
    
    # User's exact test cases
    test_cases = [
        {
            'address': "İstanbul Kadıköy Moda Mahallesi",
            'expected_NOT': (41.0082, 28.9784),
            'expected_method_NOT': 'province_centroid'
        },
        {
            'address': "İstanbul Kadıköy", 
            'expected_coords': (40.9833, 29.0333),
            'expected_method': 'district_centroid'
        },
        {
            'address': "İstanbul Beşiktaş",
            'expected_coords': (41.0422, 29.0061),
            'expected_method': 'district_centroid'
        }
    ]
    
    print("Testing cases reported as still failing by user...")
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. Address: '{test['address']}'")
        
        result = geocoder.geocode_turkish_address(test['address'])
        lat = result.get('latitude', 0)
        lon = result.get('longitude', 0)
        method = result.get('method', 'unknown')
        confidence = result.get('confidence', 0)
        
        print(f"   Result: ({lat:.4f}, {lon:.4f})")
        print(f"   Method: {method}")
        print(f"   Confidence: {confidence}")
        
        # Check what user reported as broken
        if 'expected_NOT' in test:
            not_lat, not_lon = test['expected_NOT']
            if abs(lat - not_lat) < 0.001 and abs(lon - not_lon) < 0.001:
                print(f"   ❌ USER IS RIGHT: Still getting wrong coordinates!")
                print(f"   ❌ Getting province center: {test['expected_NOT']}")
            else:
                print(f"   ✅ FIXED: Not getting province center anymore")
                
        if 'expected_method_NOT' in test:
            if method == test['expected_method_NOT']:
                print(f"   ❌ USER IS RIGHT: Still using {method}")
            else:
                print(f"   ✅ FIXED: Not using {test['expected_method_NOT']} anymore")
                
        if 'expected_coords' in test:
            exp_lat, exp_lon = test['expected_coords']
            if abs(lat - exp_lat) < 0.01 and abs(lon - exp_lon) < 0.01:
                print(f"   ✅ CLOSE: Near expected coordinates")
            else:
                print(f"   ⚠️  Expected: {test['expected_coords']}")
                
        if 'expected_method' in test:
            if method == test['expected_method']:
                print(f"   ✅ CORRECT METHOD: {method}")
            else:
                print(f"   ⚠️  Expected method: {test['expected_method']}, got: {method}")
    
    # Summary
    print(f"\n" + "=" * 50)
    print(f"SUMMARY: If user is still seeing (41.0082, 28.9784) province_centroid,")
    print(f"it might be:")
    print(f"1. Code not reloaded properly")
    print(f"2. Different version of file being used")  
    print(f"3. Caching issue")
    print(f"4. Different test conditions")

if __name__ == "__main__":
    test_user_specific_issue()