#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEKNOFEST Enhanced Parser Comprehensive Testing
Test the enhanced parser against target examples to verify Phase 3.5 capabilities
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from enhanced_address_parser import EnhancedTurkishAddressParser

def test_target_examples():
    """Test the enhanced parser with target examples from Phase 3.5"""
    
    print("🎯 TEKNOFEST Phase 3.5 Target Examples Testing")
    print("=" * 60)
    
    parser = EnhancedTurkishAddressParser()
    
    # Target examples from Phase 3.5 requirements
    target_examples = [
        {
            "address": "istanbul kadikoy moda bagdat caddesi 127",
            "expected": {
                "il": "İstanbul",
                "ilce": "Kadıköy", 
                "mahalle": "Moda",
                "street": "Bağdat Caddesi",
                "building_number": "127"
            },
            "description": "Full street-level parsing with building number"
        },
        {
            "address": "ankara cankaya kizilay tunali hilmi caddesi 25/A",
            "expected": {
                "il": "Ankara",
                "ilce": "Çankaya",
                "mahalle": "Kızılay", 
                "street": "Tunalı Hilmi Caddesi",
                "building_number": "25/A"
            },
            "description": "Complete components with apartment notation"
        },
        {
            "address": "izmir konak alsancak kordon boyu 15 b blok",
            "expected": {
                "il": "İzmir",
                "ilce": "Konak",
                "mahalle": "Alsancak",
                "street": "Kordon Boyu",
                "building_number": "15",
                "block": "B Blok"
            },
            "description": "Building-level detail with block info"
        },
        {
            "address": "istanbul mecidiyekoy",
            "expected": {
                "il": "İstanbul",
                "mahalle": "Mecidiyeköy"
            },
            "description": "Standalone neighborhood recognition"
        },
        {
            "address": "bursa osmangazi ulubatlı hasan bulvarı",
            "expected": {
                "il": "Bursa",
                "ilce": "Osmangazi",
                "street": "Uluabatlı Hasan Bulvarı"
            },
            "description": "Regional address with bulvar"
        }
    ]
    
    print(f"Testing {len(target_examples)} target examples...\n")
    
    success_count = 0
    for i, test_case in enumerate(target_examples, 1):
        address = test_case["address"]
        expected = test_case["expected"]
        description = test_case["description"]
        
        print(f"Test {i}: {address}")
        print(f"Goal: {description}")
        
        try:
            result = parser.analyze_address_enhanced(address)
            components = result['parsing_result'].get('components', {})
            
            print(f"📍 Parsed Components:")
            for key, value in components.items():
                print(f"   {key}: {value}")
            
            # Check enhanced data
            enhanced_analysis = result.get('enhanced_analysis', {})
            
            if enhanced_analysis.get('traditional_neighborhood_found'):
                neighborhood_data = result['parsing_result'].get('traditional_neighborhood_data', {})
                print(f"🏛️  Traditional Neighborhood: {neighborhood_data.get('original_name')} ({neighborhood_data.get('il')}, {neighborhood_data.get('ilce')})")
            elif enhanced_analysis.get('osm_neighborhood_found'):
                neighborhood_data = result['parsing_result'].get('osm_neighborhood_data', {})
                print(f"🏘️  OSM Neighborhood: {neighborhood_data.get('original_name')} ({neighborhood_data.get('place_type')})")
            
            if enhanced_analysis.get('street_found'):
                street_data = result['parsing_result'].get('osm_street_data', {})
                print(f"🛣️  OSM Street: {street_data.get('original_name')} ({street_data.get('highway_type')})")
            
            if enhanced_analysis.get('coordinates_available'):
                coords = result['parsing_result'].get('coordinates', {})
                print(f"📍 Coordinates: {coords.get('latitude'):.4f}, {coords.get('longitude'):.4f}")
            
            confidence = result['parsing_result'].get('confidence', 0)
            boost = result['parsing_result'].get('data_confidence_boost', 0)
            print(f"✅ Confidence: {confidence:.2f} (Data boost: +{boost:.2f})")
            
            # Check if key components match expectations
            success = True
            if 'il' in expected and components.get('il') != expected['il']:
                print(f"❌ Province mismatch: expected {expected['il']}, got {components.get('il')}")
                success = False
            
            if 'mahalle' in expected:
                # Check component, traditional, and OSM neighborhood data
                mahalle_found = (
                    components.get('mahalle') == expected['mahalle'] or
                    (traditional_data := result['parsing_result'].get('traditional_neighborhood_data')) and
                    traditional_data.get('original_name') == expected['mahalle'] or
                    (osm_data := result['parsing_result'].get('osm_neighborhood_data')) and
                    osm_data.get('original_name') == expected['mahalle']
                )
                if not mahalle_found:
                    print(f"❌ Neighborhood mismatch: expected {expected['mahalle']}")
                    success = False
            
            if success:
                success_count += 1
                print("✅ Test PASSED")
            else:
                print("❌ Test FAILED")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        print("-" * 50)
    
    print(f"\n🎯 FINAL RESULTS:")
    print(f"   Success Rate: {success_count}/{len(target_examples)} ({success_count/len(target_examples)*100:.1f}%)")
    print(f"   Target: ≥80% success rate")
    
    if success_count >= len(target_examples) * 0.8:
        print("🎉 SUCCESS: Phase 3.5 targets achieved!")
    else:
        print("⚠️  More improvements needed to reach 80% target")
    
    # Show system statistics
    stats = parser.get_data_statistics()
    print(f"\n📊 Enhanced System Statistics:")
    print(f"   Traditional Neighborhoods: {stats['traditional_data']['neighborhoods_loaded']:,}")
    print(f"   OSM Neighborhoods: {stats['osm_data']['neighborhoods_loaded']:,}")
    print(f"   OSM Streets: {stats['osm_data']['streets_loaded']:,}")
    print(f"   Total Neighborhoods: {stats['total_neighborhoods']:,}")
    print(f"   Coverage: Traditional (famous areas) + OSM (comprehensive)")

if __name__ == "__main__":
    test_target_examples()