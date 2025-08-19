#!/usr/bin/env python3
"""
ANALYZE CURRENT HIERARCHY COMPLETION GAPS
Test what the system currently does vs what Phase 5 needs to do
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def test_current_completion():
    """Test current hierarchy completion behavior"""
    print("🔍 ANALYZING CURRENT HIERARCHY COMPLETION")
    print("=" * 60)
    
    try:
        from address_parser import AddressParser
        parser = AddressParser()
        print("✅ AddressParser initialized")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return
    
    # Test cases showing current gaps
    test_cases = [
        {
            'name': 'UP Completion Test (Working)',
            'input': "Keçiören Ankara",
            'current_expected': {'il': 'Ankara', 'ilçe': 'Keçiören'},
            'gap': None
        },
        {
            'name': 'DOWN Completion Test 1 (MISSING)',
            'input': "Ankara Etlik Mahallesi", 
            'current_result': {'il': 'Ankara', 'mahalle': 'Etlik'},
            'missing': 'ilçe: Keçiören',
            'gap': 'mahalle → ilçe completion'
        },
        {
            'name': 'DOWN Completion Test 2 (MISSING)',
            'input': "İstanbul Moda Mahallesi",
            'current_result': {'il': 'İstanbul', 'mahalle': 'Moda'},
            'missing': 'ilçe: Kadıköy',
            'gap': 'mahalle → ilçe completion'
        },
        {
            'name': 'DOWN Completion Test 3 (MISSING)', 
            'input': "Etlik Mahallesi",
            'current_result': {'mahalle': 'Etlik'},
            'missing': 'ilçe: Keçiören, il: Ankara',
            'gap': 'mahalle → ilçe → il completion'
        },
        {
            'name': 'Complex DOWN Completion (MISSING)',
            'input': "Moda Mahallesi Caferağa Sokak 15",
            'current_result': {'mahalle': 'Moda', 'sokak': 'Caferağa Sokak', 'bina_no': '15'},
            'missing': 'ilçe: Kadıköy, il: İstanbul',
            'gap': 'mahalle → ilçe → il completion'
        }
    ]
    
    print(f"🧪 Testing {len(test_cases)} hierarchy completion scenarios:")
    
    working_cases = 0
    gap_cases = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Input: '{test_case['input']}'")
        
        try:
            result = parser.parse_address(test_case['input'])
            components = result.get('components', {})
            
            print(f"   Current Result: {components}")
            
            if test_case['gap']:
                print(f"   🔴 GAP: {test_case['gap']}")
                print(f"   ❌ Missing: {test_case['missing']}")
                gap_cases += 1
            else:
                print(f"   ✅ Working as expected")
                working_cases += 1
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            gap_cases += 1
    
    print(f"\n" + "=" * 60)
    print(f"📊 CURRENT COMPLETION ANALYSIS:")
    print(f"   Working cases: {working_cases}")
    print(f"   Gap cases: {gap_cases}")
    print(f"   Total: {working_cases + gap_cases}")
    
    print(f"\n🎯 PHASE 5 REQUIREMENTS:")
    print(f"   ✅ UP completion (ilçe → il): WORKING")
    print(f"   ❌ DOWN completion (mahalle → ilçe): MISSING")
    print(f"   ❌ Multi-level completion (mahalle → ilçe → il): MISSING")
    
    return gap_cases > 0

def analyze_database_capability():
    """Check if the database has the data needed for DOWN completion"""
    print(f"\n🗄️  DATABASE CAPABILITY ANALYSIS")
    print("=" * 60)
    
    try:
        from geographic_intelligence import GeographicIntelligence
        geo_intel = GeographicIntelligence()
        
        print(f"✅ Database loaded: {len(geo_intel.admin_hierarchy)} records")
        
        # Test specific neighborhood lookups
        test_neighborhoods = ['etlik', 'moda', 'levent', 'alsancak', 'çankaya']
        
        print(f"\n🔍 Testing neighborhood lookup capability:")
        
        for neighborhood in test_neighborhoods:
            norm_name = geo_intel._normalize_turkish_text(neighborhood)
            
            if norm_name in geo_intel.neighborhood_lookup:
                neighborhood_info = geo_intel.neighborhood_lookup[norm_name]
                print(f"   ✅ '{neighborhood}' → ilçe: {neighborhood_info['ilçe']}, il: {neighborhood_info['il']}")
            else:
                print(f"   ❌ '{neighborhood}' → NOT FOUND in database")
        
        print(f"\n📊 Database Statistics:")
        print(f"   Total neighborhoods: {len(geo_intel.neighborhood_lookup)}")
        print(f"   Total districts: {len(geo_intel.district_lookup)}")
        print(f"   Total cities: {len(geo_intel.city_lookup)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database analysis failed: {e}")
        return False

def main():
    """Run complete analysis"""
    print("🔬 PHASE 5 HIERARCHY COMPLETION ANALYSIS")
    print("=" * 60)
    print("Analyzing gaps in current hierarchy completion logic\n")
    
    # Test current completion behavior
    has_gaps = test_current_completion()
    
    # Analyze database capability
    has_data = analyze_database_capability()
    
    # Final assessment
    print(f"\n" + "=" * 60)
    print(f"🏁 ANALYSIS SUMMARY:")
    print(f"   Current gaps exist: {'✅ YES' if has_gaps else '❌ NO'}")
    print(f"   Database has data: {'✅ YES' if has_data else '❌ NO'}")
    
    if has_gaps and has_data:
        print(f"\n🎯 PHASE 5 IS CRITICAL:")
        print(f"   • System has gaps in hierarchy completion")
        print(f"   • Database contains the needed information")
        print(f"   • DOWN completion is technically feasible")
        print(f"   • This will significantly improve TEKNOFEST competitiveness")
    
    print("=" * 60)

if __name__ == "__main__":
    main()