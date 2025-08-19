#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
URGENT: Test Enhanced Database Integration
Verify that AddressValidator and AddressParser load 55,955 records
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_enhanced_integration():
    """Test that system loads enhanced database with 55,955 records"""
    
    print("🚨 URGENT: Testing Enhanced Database Integration")
    print("=" * 60)
    
    # Test AddressValidator
    print("1. Testing AddressValidator...")
    try:
        from address_validator import AddressValidator
        validator = AddressValidator()
        
        # Check if it loaded enhanced data
        hierarchy_count = len(validator.admin_hierarchy) if hasattr(validator, 'admin_hierarchy') else 0
        print(f"   ✅ AddressValidator loaded {hierarchy_count:,} hierarchy records")
        
        if hierarchy_count > 300:  # Should be much more than old 355
            print(f"   🎯 SUCCESS: Using enhanced database!")
        else:
            print(f"   ❌ FAILED: Still using old database (expected >300, got {hierarchy_count})")
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Test AddressParser
    print("\n2. Testing AddressParser...")
    try:
        from address_parser import AddressParser
        parser = AddressParser()
        
        # Check if it loaded enhanced data
        if hasattr(parser, 'turkish_locations') and parser.turkish_locations:
            locations = parser.turkish_locations
            provinces_count = len(locations.get('provinces', []))
            all_neighborhoods_count = len(locations.get('all_neighborhoods', []))
            
            print(f"   ✅ AddressParser loaded:")
            print(f"      - Provinces: {provinces_count:,}")
            print(f"      - All neighborhoods: {all_neighborhoods_count:,}")
            
            if all_neighborhoods_count > 50000:  # Should be ~55,955
                print(f"   🎯 SUCCESS: Using enhanced neighborhood database!")
            else:
                print(f"   ❌ FAILED: Missing enhanced neighborhoods (expected >50,000, got {all_neighborhoods_count:,})")
        else:
            print(f"   ❌ FAILED: turkish_locations not loaded")
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Test neighborhood recognition
    print("\n3. Testing Neighborhood Recognition...")
    try:
        test_addresses = [
            "istanbul mecidiyekoy",
            "ankara kizilay", 
            "izmir alsancak"
        ]
        
        for address in test_addresses:
            print(f"\n   Testing: {address}")
            result = parser.parse_address(address)
            components = result.get('components', {})
            
            print(f"   📍 Components: {components}")
            
            if 'mahalle' in components and components['mahalle']:
                print(f"   ✅ Neighborhood extracted: {components['mahalle']}")
            else:
                print(f"   ❌ No neighborhood extracted")
                
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    print(f"\n🎯 Integration test complete!")

if __name__ == "__main__":
    test_enhanced_integration()