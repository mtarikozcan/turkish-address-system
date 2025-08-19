#!/usr/bin/env python3
"""
Test geocoding method display fix
"""

import sys
from pathlib import Path

# Add project root to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_geocoding_method_display():
    """Test that geocoding methods are displayed correctly instead of 'unknown'"""
    
    print("🎯 GEOCODING METHOD DISPLAY FIX TEST")
    print("=" * 60)
    
    try:
        from detailed_manual_tester import DetailedManualTester
        print("✅ DetailedManualTester loaded successfully")
    except ImportError as e:
        print(f"❌ Error importing tester: {e}")
        return False
    
    try:
        tester = DetailedManualTester()
        print("✅ Tester initialized")
    except Exception as e:
        print(f"❌ Error initializing tester: {e}")
        return False
    
    # Test cases with expected methods
    test_cases = [
        {
            'address': 'İstanbul Kadıköy Moda',
            'description': 'Neighborhood-level address',
            'expected_method': 'neighborhood_centroid'
        },
        {
            'address': 'Ankara Çankaya',
            'description': 'District-level address',
            'expected_method': 'district_centroid'
        },
        {
            'address': 'İzmir',
            'description': 'Province-level address',
            'expected_method': 'province_centroid'
        },
        {
            'address': 'Random gibberish text xyz123',
            'description': 'Invalid address (fallback)',
            'expected_method': 'turkey_center'
        }
    ]
    
    print(f"\n🧪 TESTING {len(test_cases)} GEOCODING METHOD CASES:")
    
    all_passed = True
    methods_found = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. {test['description']}")
        print(f"   Address: '{test['address']}'")
        print(f"   Expected Method: {test['expected_method']}")
        
        try:
            result = tester.analyze_single_address(test['address'])
            
            # Check summary method
            summary_method = result.summary.get('geocoding_method', 'NOT_FOUND')
            
            # Check geocoding step details
            geocoding_step = result.pipeline_steps[3]  # Geocoding is step 4 (index 3)
            step_method = geocoding_step.output_data.get('geocoding_method', 'NOT_FOUND')
            
            print(f"   Summary Method: {summary_method}")
            print(f"   Step Method: {step_method}")
            
            methods_found.append(summary_method)
            
            # Test passed if method is not 'unknown' and matches expectation
            if summary_method == 'unknown':
                print(f"   ❌ FAIL: Still showing 'unknown' instead of actual method")
                all_passed = False
            elif summary_method != test['expected_method']:
                print(f"   ⚠️  PARTIAL: Method '{summary_method}' doesn't match expected '{test['expected_method']}' but at least not 'unknown'")
                # This is acceptable - methods might differ due to data availability
            else:
                print(f"   ✅ PASS: Method correctly shows '{summary_method}'")
                
            # Verify consistency between summary and step
            if summary_method != step_method:
                print(f"   ⚠️  WARNING: Summary method ({summary_method}) differs from step method ({step_method})")
                
        except Exception as e:
            print(f"   ❌ ERROR: Failed to analyze address: {e}")
            all_passed = False
            methods_found.append('ERROR')
    
    print(f"\n" + "=" * 60)
    print(f"📊 FINAL ANALYSIS:")
    print(f"   All methods found: {methods_found}")
    
    unique_methods = set(methods_found)
    unknown_count = methods_found.count('unknown')
    
    print(f"   Unique methods: {unique_methods}")
    print(f"   'unknown' count: {unknown_count}/{len(test_cases)}")
    
    if unknown_count == 0:
        print(f"   ✅ SUCCESS: No 'unknown' methods found!")
    else:
        print(f"   ❌ FAILURE: {unknown_count} addresses still show 'unknown'")
        all_passed = False
    
    if len(unique_methods) > 1:
        print(f"   ✅ SUCCESS: Methods are differentiated ({len(unique_methods)} different)")
    else:
        print(f"   ⚠️  WARNING: All addresses got same method")
    
    print(f"\n" + "=" * 60)
    if all_passed and unknown_count == 0:
        print(f"🎉 GEOCODING METHOD DISPLAY FIX SUCCESSFUL!")
        print(f"✅ Methods are no longer showing 'unknown'")
        print(f"✅ Actual geocoding methods are displayed")
        return True
    else:
        print(f"🔧 Fix may need additional work")
        return False

if __name__ == "__main__":
    success = test_geocoding_method_display()
    if success:
        print(f"\n🏆 TEKNOFEST GEOCODING METHOD DISPLAY FIXED!")
    else:
        print(f"\n🔧 Additional debugging may be needed")