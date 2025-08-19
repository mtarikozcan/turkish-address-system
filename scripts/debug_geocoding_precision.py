#!/usr/bin/env python3
"""
DEBUG GEOCODING PRECISION ISSUE
Test specific case: Etlik/Keçiören/Ankara components to see why falling back to province
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def debug_geocoding_components():
    """Debug the specific Etlik/Keçiören/Ankara case"""
    print("🔍 DEBUGGING GEOCODING PRECISION ISSUE")
    print("=" * 60)
    print("Case: Etlik Mahallesi, Keçiören, Ankara")
    print("Expected: District or neighborhood level coordinates")
    print("Current: Falling back to province_centroid\n")
    
    try:
        from advanced_geocoding_engine import AdvancedGeocodingEngine
        geocoding_engine = AdvancedGeocodingEngine()
        print("✅ Advanced Geocoding Engine loaded")
        
        # Test the specific components
        test_components = {
            'mahalle': 'Etlik',
            'ilçe': 'Keçiören', 
            'il': 'Ankara'
        }
        
        print(f"🧪 Testing components: {test_components}")
        
        # Test each level separately to see where it fails
        print("\n🔍 TESTING EACH PRECISION LEVEL:")
        
        # Test neighborhood level
        neighborhood_result = geocoding_engine._geocode_neighborhood_level(test_components)
        print(f"1. Neighborhood level: {'✅ SUCCESS' if neighborhood_result else '❌ FAILED'}")
        if neighborhood_result:
            print(f"   Coordinates: {neighborhood_result.latitude}, {neighborhood_result.longitude}")
            print(f"   Method: {neighborhood_result.method}")
            print(f"   Confidence: {neighborhood_result.confidence}")
        
        # Test district level
        district_result = geocoding_engine._geocode_district_level(test_components)
        print(f"2. District level: {'✅ SUCCESS' if district_result else '❌ FAILED'}")
        if district_result:
            print(f"   Coordinates: {district_result.latitude}, {district_result.longitude}")
            print(f"   Method: {district_result.method}")
            print(f"   Confidence: {district_result.confidence}")
        
        # Test province level
        province_result = geocoding_engine._geocode_province_level(test_components)
        print(f"3. Province level: {'✅ SUCCESS' if province_result else '❌ FAILED'}")
        if province_result:
            print(f"   Coordinates: {province_result.latitude}, {province_result.longitude}")
            print(f"   Method: {province_result.method}")
            print(f"   Confidence: {province_result.confidence}")
        
        # Test full geocoding method
        print(f"\n🎯 FULL GEOCODING METHOD TEST:")
        full_result = geocoding_engine.geocode_address(test_components)
        print(f"Result: {full_result.precision_level} level")
        print(f"Coordinates: {full_result.latitude}, {full_result.longitude}")
        print(f"Method: {full_result.method}")
        print(f"Confidence: {full_result.confidence}")
        print(f"Components used: {full_result.components_used}")
        
        # Debug the coordinate database lookups
        print(f"\n🗄️ DATABASE LOOKUP TESTS:")
        geo_db = geocoding_engine.geo_db
        
        # Test neighborhood lookups
        etlik_coords = geo_db.get_coordinates('neighborhood', 'etlik')
        print(f"Neighborhood 'etlik': {'✅ FOUND' if etlik_coords else '❌ NOT FOUND'}")
        if etlik_coords:
            print(f"   Coordinates: {etlik_coords}")
        
        etlik_kecioren = geo_db.get_coordinates('neighborhood', 'etlik_keçiören')
        print(f"Neighborhood 'etlik_keçiören': {'✅ FOUND' if etlik_kecioren else '❌ NOT FOUND'}")
        if etlik_kecioren:
            print(f"   Coordinates: {etlik_kecioren}")
        
        # Test district lookups
        kecioren_coords = geo_db.get_coordinates('district', 'keçiören')
        print(f"District 'keçiören': {'✅ FOUND' if kecioren_coords else '❌ NOT FOUND'}")
        if kecioren_coords:
            print(f"   Coordinates: {kecioren_coords}")
        
        kecioren_ankara = geo_db.get_coordinates('district', 'keçiören_ankara')
        print(f"District 'keçiören_ankara': {'✅ FOUND' if kecioren_ankara else '❌ NOT FOUND'}")
        if kecioren_ankara:
            print(f"   Coordinates: {kecioren_ankara}")
        
        # Test normalization
        normalized_mahalle = geo_db._normalize_name('Etlik')
        normalized_ilce = geo_db._normalize_name('Keçiören')
        normalized_il = geo_db._normalize_name('Ankara')
        
        print(f"\n🔤 NORMALIZATION TESTS:")
        print(f"'Etlik' → '{normalized_mahalle}'")
        print(f"'Keçiören' → '{normalized_ilce}'")
        print(f"'Ankara' → '{normalized_il}'")
        
        # Test with normalized names
        normalized_etlik = geo_db.get_coordinates('neighborhood', normalized_mahalle)
        print(f"Normalized neighborhood '{normalized_mahalle}': {'✅ FOUND' if normalized_etlik else '❌ NOT FOUND'}")
        if normalized_etlik:
            print(f"   Coordinates: {normalized_etlik}")
        
        normalized_kecioren = geo_db.get_coordinates('district', normalized_ilce)
        print(f"Normalized district '{normalized_ilce}': {'✅ FOUND' if normalized_kecioren else '❌ NOT FOUND'}")
        if normalized_kecioren:
            print(f"   Coordinates: {normalized_kecioren}")
        
        return True
        
    except Exception as e:
        print(f"❌ Debug test failed: {e}")
        return False

def debug_district_coordinates():
    """Check if district coordinates are properly loaded"""
    print(f"\n📍 DISTRICT COORDINATES DATABASE CHECK")
    print("-" * 50)
    
    try:
        from advanced_geocoding_engine import TurkishGeographicDatabase
        geo_db = TurkishGeographicDatabase()
        
        # Check some key districts
        test_districts = ['keçiören', 'çankaya', 'beşiktaş', 'şişli', 'konak']
        
        for district in test_districts:
            coords = geo_db.get_coordinates('district', district)
            status = "✅ FOUND" if coords else "❌ MISSING"
            print(f"District '{district}': {status}")
            if coords:
                print(f"   Coordinates: {coords}")
        
        # Check total district count
        district_count = len(geo_db.district_coordinates)
        print(f"\nTotal districts in database: {district_count}")
        
        # Show first few districts for verification
        district_sample = list(geo_db.district_coordinates.keys())[:10]
        print(f"Sample districts: {district_sample}")
        
        return True
        
    except Exception as e:
        print(f"❌ District check failed: {e}")
        return False

def main():
    """Main debug function"""
    print("🔍 GEOCODING PRECISION DEBUG TEST")
    print("=" * 60)
    print("Root cause analysis: Why complex addresses fall back to province_centroid")
    print("Expected: Use detected components for neighborhood/district lookup\n")
    
    # Debug geocoding components
    component_debug = debug_geocoding_components()
    
    # Debug district database
    district_debug = debug_district_coordinates()
    
    # Analysis
    print(f"\n" + "=" * 60)
    print("🔍 DEBUG ANALYSIS SUMMARY")
    print("=" * 60)
    
    if component_debug and district_debug:
        print("✅ Debug tests completed successfully")
        print("📊 Analysis complete - identify the exact failure point")
        print("🔧 Ready to implement targeted fix")
    else:
        print("❌ Some debug tests failed")
        print("🔧 Need to address fundamental issues first")
    
    print("=" * 60)
    return component_debug and district_debug

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)