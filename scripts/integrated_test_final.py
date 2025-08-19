#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FINAL INTEGRATION TEST: Core system with OSM + Enhanced Parser hybrid approach
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_final_integration():
    """Test final integrated system with OSM data + enhanced parsing"""
    
    print("🎯 FINAL INTEGRATION TEST: Core System + OSM Data")
    print("=" * 60)
    
    # Test with Enhanced Parser (hybrid approach)
    print("1. Testing Enhanced Parser with OSM Integration...")
    try:
        from enhanced_address_parser import EnhancedTurkishAddressParser
        
        # Enhanced parser with hybrid traditional + OSM
        enhanced_parser = EnhancedTurkishAddressParser()
        stats = enhanced_parser.get_data_statistics()
        
        print(f"   📊 Enhanced Parser Statistics:")
        print(f"      Traditional neighborhoods: {stats['traditional_data']['neighborhoods_loaded']:,}")
        print(f"      OSM neighborhoods: {stats['osm_data']['neighborhoods_loaded']:,}")
        print(f"      OSM streets: {stats['osm_data']['streets_loaded']:,}")
        print(f"      Total coverage: {stats['total_neighborhoods']:,} locations")
        
        # Test target addresses
        test_cases = [
            "istanbul kadikoy moda bagdat caddesi 127",
            "ankara cankaya kizilay tunali hilmi caddesi 25/A",
            "izmir konak alsancak kordon boyu 15 b blok",
            "istanbul mecidiyekoy",
            "bursa osmangazi ulubatlı hasan bulvarı"
        ]
        
        success_count = 0
        for i, address in enumerate(test_cases, 1):
            print(f"\n   Test {i}: {address}")
            try:
                result = enhanced_parser.analyze_address_enhanced(address)
                components = result['parsing_result'].get('components', {})
                enhanced_analysis = result.get('enhanced_analysis', {})
                
                print(f"      📍 Components: {components}")
                
                # Check for enhanced data
                if enhanced_analysis.get('traditional_neighborhood_found'):
                    neighborhood_data = result['parsing_result'].get('traditional_neighborhood_data', {})
                    print(f"      🏛️  Traditional: {neighborhood_data.get('original_name')}")
                    success_count += 1
                elif enhanced_analysis.get('osm_neighborhood_found'):
                    neighborhood_data = result['parsing_result'].get('osm_neighborhood_data', {})
                    print(f"      🏘️  OSM: {neighborhood_data.get('original_name')}")
                    success_count += 1
                elif components.get('mahalle'):
                    print(f"      ✅ Neighborhood: {components['mahalle']}")
                    success_count += 1
                else:
                    print(f"      ❌ No neighborhood detected")
                    
            except Exception as e:
                print(f"      ❌ ERROR: {e}")
        
        success_rate = success_count / len(test_cases) * 100
        print(f"\n   🎯 Enhanced Parser Success Rate: {success_count}/{len(test_cases)} ({success_rate:.1f}%)")
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Test with Core Parser (now with OSM data)
    print(f"\n2. Testing Core Parser with OSM Data...")
    try:
        from address_parser import AddressParser
        
        core_parser = AddressParser()
        
        # Test a critical neighborhood
        test_address = "istanbul mecidiyekoy"
        result = core_parser.parse_address(test_address)
        components = result.get('components', {})
        
        print(f"   Test: {test_address}")
        print(f"   📍 Components: {components}")
        
        if components.get('mahalle'):
            print(f"   ✅ Core parser with OSM data working!")
        else:
            print(f"   ❌ Core parser needs improvement")
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        
    print(f"\n🎯 FINAL RESULT:")
    if 'success_rate' in locals() and success_rate >= 80:
        print(f"   🎉 SUCCESS: Enhanced system achieving {success_rate:.1f}% success rate!")
        print(f"   ✅ OSM Turkey data fully integrated ({stats['total_neighborhoods']:,} locations)")
        print(f"   ✅ Street-level parsing enabled ({stats['osm_data']['streets_loaded']:,} streets)")
    else:
        print(f"   ⚠️  System operational but needs optimization for >80% target")

if __name__ == "__main__":
    test_final_integration()