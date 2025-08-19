#!/usr/bin/env python3
"""
DEBUG NEIGHBORHOOD LOOKUP ISSUES
Find out why some neighborhoods are not being found in database
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def debug_neighborhood_lookup():
    """Debug why neighborhood lookups are failing"""
    print("🔍 DEBUGGING NEIGHBORHOOD LOOKUP")
    print("=" * 50)
    
    try:
        from geographic_intelligence import GeographicIntelligence
        geo_intel = GeographicIntelligence()
        
        print(f"✅ GeographicIntelligence loaded")
        print(f"   Database records: {len(geo_intel.admin_hierarchy)}")
        print(f"   Neighborhood lookup size: {len(geo_intel.neighborhood_lookup)}")
        
        # Test specific neighborhoods
        test_neighborhoods = ['etlik', 'moda', 'levent', 'alsancak', 'çankaya']
        
        for neighborhood in test_neighborhoods:
            print(f"\n🔍 Testing '{neighborhood}':")
            
            # Test normalization
            norm_name = geo_intel._normalize_turkish_text(neighborhood)
            print(f"   Normalized: '{norm_name}'")
            
            # Check if in lookup
            in_lookup = norm_name in geo_intel.neighborhood_lookup
            print(f"   In lookup: {in_lookup}")
            
            if not in_lookup:
                # Search in actual database records
                matches = []
                for record in geo_intel.admin_hierarchy[:100]:  # Check first 100
                    if record['mahalle'] and neighborhood.lower() in record['mahalle'].lower():
                        matches.append(record)
                
                if matches:
                    print(f"   Found in raw data: {matches[0]}")
                else:
                    print(f"   Not found in raw data sample")
        
        # Show sample of what's actually in the lookup
        print(f"\n📋 Sample neighborhood lookup entries:")
        sample_keys = list(geo_intel.neighborhood_lookup.keys())[:10]
        for key in sample_keys:
            neighborhood_info = geo_intel.neighborhood_lookup[key]
            print(f"   '{key}' → {neighborhood_info['proper_name']} ({neighborhood_info['ilçe']}, {neighborhood_info['il']})")
        
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_database_search():
    """Test direct database search for neighborhoods"""
    print(f"\n🗄️  DIRECT DATABASE SEARCH")
    print("=" * 50)
    
    try:
        from geographic_intelligence import GeographicIntelligence
        geo_intel = GeographicIntelligence()
        
        target_neighborhoods = ['etlik', 'moda', 'levent', 'alsancak']
        
        for target in target_neighborhoods:
            print(f"\n🔍 Searching for '{target}' in database:")
            
            matches = []
            for record in geo_intel.admin_hierarchy:
                if (record['mahalle'] and 
                    target.lower() in record['mahalle'].lower()):
                    matches.append({
                        'mahalle': record['mahalle'],
                        'ilçe': record['ilçe'],
                        'il': record['il']
                    })
            
            if matches:
                print(f"   Found {len(matches)} matches:")
                for i, match in enumerate(matches[:3]):  # Show first 3
                    print(f"   {i+1}. {match['mahalle']} → {match['ilçe']}, {match['il']}")
                if len(matches) > 3:
                    print(f"   ... and {len(matches) - 3} more")
            else:
                print(f"   ❌ No matches found")
    
    except Exception as e:
        print(f"❌ Database search failed: {e}")

def main():
    """Run debugging"""
    print("🔬 NEIGHBORHOOD LOOKUP DEBUG SESSION")
    print("=" * 50)
    
    debug_neighborhood_lookup()
    test_direct_database_search()
    
    print(f"\n" + "=" * 50)
    print("🎯 FINDINGS SUMMARY:")
    print("   - Check if normalization is affecting lookups")
    print("   - Verify neighborhood data exists in raw database")
    print("   - Identify why lookup index might be incomplete")

if __name__ == "__main__":
    main()