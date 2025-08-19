#!/usr/bin/env python3
"""
TEST COMPLEX ADDRESS GEOCODING
Test the full integration with a complex address to identify the real issue
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def test_complex_address():
    """Test a complex address through the full system"""
    print("🧪 COMPLEX ADDRESS GEOCODING TEST")
    print("=" * 60)
    
    # Test the specific complex address mentioned in the issue
    complex_address = "Etlik Mahallesi Süleymaniye Caddesi No:25 Keçiören Ankara"
    print(f"Testing: '{complex_address}'")
    print("Expected: Use detected components (mahalle: Etlik, ilçe: Keçiören, il: Ankara)")
    print("Expected result: Neighborhood or district coordinates, NOT province_centroid\n")
    
    try:
        from address_parser import AddressParser
        parser = AddressParser()
        print("✅ AddressParser loaded with all engines")
        
        # Step 1: Parse the address
        print("🔍 STEP 1: PARSING ADDRESS")
        parsing_result = parser.parse_address(complex_address)
        
        components = parsing_result.get('components', {})
        print(f"Detected components: {components}")
        print(f"Components count: {len(components)}")
        
        # Extract key components
        mahalle = components.get('mahalle', 'N/A')
        ilce = components.get('ilçe', 'N/A')  
        il = components.get('il', 'N/A')
        
        print(f"Key components:")
        print(f"  mahalle: '{mahalle}'")
        print(f"  ilçe: '{ilce}'")
        print(f"  il: '{il}'")
        
        # Step 2: Test geocoding with these components
        print(f"\n🌍 STEP 2: GEOCODING WITH DETECTED COMPONENTS")
        
        if parser.advanced_geocoding_engine:
            geocoding_result = parser.advanced_geocoding_engine.geocode_address(components)
            
            print(f"Geocoding result:")
            print(f"  Coordinates: {geocoding_result.latitude}, {geocoding_result.longitude}")
            print(f"  Precision level: {geocoding_result.precision_level}")
            print(f"  Method: {geocoding_result.method}")
            print(f"  Confidence: {geocoding_result.confidence}")
            print(f"  Components used: {geocoding_result.components_used}")
            
            # Analyze the result
            if geocoding_result.precision_level == 'province':
                print(f"❌ ISSUE CONFIRMED: Falling back to province_centroid")
                print(f"   This means component lookup failed")
            elif geocoding_result.precision_level in ['neighborhood', 'district']:
                print(f"✅ SUCCESS: Using precise components")
                print(f"   Precision level: {geocoding_result.precision_level}")
            else:
                print(f"⚠️  Unexpected precision level: {geocoding_result.precision_level}")
        
        # Step 3: Test complete integrated method
        print(f"\n🚀 STEP 3: COMPLETE INTEGRATED METHOD")
        complete_result = parser.parse_and_geocode_address(complex_address)
        
        final_coords = complete_result.get('coordinates', {})
        final_precision = complete_result.get('precision_level', 'unknown')
        final_success = complete_result.get('success', False)
        
        print(f"Final result:")
        print(f"  Success: {final_success}")
        print(f"  Coordinates: {final_coords.get('latitude', 0)}, {final_coords.get('longitude', 0)}")
        print(f"  Precision level: {final_precision}")
        
        # Analysis
        print(f"\n📊 ANALYSIS:")
        
        # Expected coordinates for comparison
        expected_coords = {
            'neighborhood_etlik': (40.0, 32.85),      # Etlik neighborhood
            'district_kecioren': (39.9833, 32.8333),  # Keçiören district  
            'province_ankara': (39.9334, 32.8597)     # Ankara province
        }
        
        actual_lat = final_coords.get('latitude', 0)
        actual_lon = final_coords.get('longitude', 0)
        
        for level, (exp_lat, exp_lon) in expected_coords.items():
            if abs(actual_lat - exp_lat) < 0.01 and abs(actual_lon - exp_lon) < 0.01:
                print(f"✅ Matches {level}: {exp_lat}, {exp_lon}")
                break
        else:
            print(f"❓ Coordinates don't match expected values")
            print(f"   Actual: {actual_lat}, {actual_lon}")
            print(f"   Expected neighborhood: {expected_coords['neighborhood_etlik']}")
            print(f"   Expected district: {expected_coords['district_kecioren']}")
            print(f"   Expected province: {expected_coords['province_ankara']}")
        
        # Success criteria  
        is_precise = final_precision in ['neighborhood', 'district']
        has_coordinates = actual_lat != 0 or actual_lon != 0
        
        return is_precise and has_coordinates, final_precision, components
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False, 'error', {}

def test_multiple_complex_addresses():
    """Test multiple complex addresses to identify pattern"""
    print(f"\n🔬 MULTIPLE COMPLEX ADDRESS TEST")
    print("-" * 60)
    
    test_addresses = [
        "Etlik Mahallesi Süleymaniye Caddesi No:25 Keçiören Ankara",
        "Alsancak Mahallesi Kordon Caddesi No:8 Konak İzmir", 
        "Levent Mahallesi Büyükdere Caddesi No:15 Beşiktaş İstanbul",
        "Mecidiyeköy Mahallesi Şişli İstanbul",
        "Kızılay Mahallesi Atatürk Bulvarı Çankaya Ankara"
    ]
    
    results = []
    
    for i, address in enumerate(test_addresses, 1):
        print(f"\n{i}. Testing: '{address}'")
        success, precision, components = test_complex_address_single(address)
        results.append((address, success, precision, components))
        
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"   Result: {status} - {precision} level")
    
    # Summary
    successful = sum(1 for _, success, _, _ in results if success)
    total = len(results)
    
    print(f"\n📊 SUMMARY: {successful}/{total} addresses successfully geocoded with precision")
    
    # Identify patterns
    province_fallbacks = sum(1 for _, _, precision, _ in results if precision == 'province')
    if province_fallbacks > 0:
        print(f"❌ {province_fallbacks} addresses fell back to province_centroid")
        print("🔧 Root cause analysis needed")
    else:
        print("✅ All addresses used component-based geocoding")
    
    return successful == total

def test_complex_address_single(address):
    """Test single complex address (helper function)"""
    try:
        from address_parser import AddressParser
        parser = AddressParser()
        
        result = parser.parse_and_geocode_address(address)
        
        components = result.get('parsing_result', {}).get('components', {})
        precision = result.get('precision_level', 'unknown') 
        coordinates = result.get('coordinates', {})
        
        has_coords = coordinates.get('latitude', 0) != 0 or coordinates.get('longitude', 0) != 0
        is_precise = precision in ['neighborhood', 'district', 'street']
        
        return is_precise and has_coords, precision, components
        
    except Exception as e:
        return False, 'error', {}

def main():
    """Main test function"""
    print("🔍 COMPLEX ADDRESS GEOCODING PRECISION TEST")
    print("=" * 60)
    print("Testing the claim: 'Complex addresses falling back to province_centroid'")
    print("Goal: Verify if geocoding engine uses detected components correctly\n")
    
    # Test the specific case mentioned
    success, precision, components = test_complex_address()
    
    # Test multiple addresses to see the pattern
    multiple_success = test_multiple_complex_addresses()
    
    # Final analysis
    print(f"\n" + "=" * 60)
    print("🏁 FINAL ANALYSIS")
    print("=" * 60)
    
    if success and multiple_success:
        print("✅ ISSUE NOT REPRODUCED: Geocoding engine working correctly")
        print("✅ Components are being used for precise geocoding")
        print("✅ No evidence of falling back to province_centroid inappropriately")
        print("🎯 System appears to be functioning as designed")
    elif precision == 'province':
        print("❌ ISSUE CONFIRMED: Falling back to province_centroid")
        print("🔧 Root cause: Component lookup failing")
        print("📋 Investigation needed in coordinate database")
    else:
        print("⚠️  MIXED RESULTS: Some addresses working, others not")
        print("🔧 Need targeted fixes for specific cases")
    
    print("=" * 60)
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)