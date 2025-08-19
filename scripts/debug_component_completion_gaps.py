#!/usr/bin/env python3
"""
DEBUG COMPONENT COMPLETION GAPS
Systematic analysis of Component Completion Intelligence failures

Purpose: Find and fix the Nişantaşı → Şişli completion failure and any other gaps
"""

import sys
from pathlib import Path
import pandas as pd

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def debug_database_content():
    """Check if problematic neighborhoods exist in the database"""
    print("🔍 DATABASE CONTENT VERIFICATION")
    print("=" * 60)
    
    # Load the database directly
    try:
        database_path = current_dir / "database" / "enhanced_turkish_neighborhoods.csv"
        df = pd.read_csv(database_path, encoding='utf-8')
        print(f"✅ Database loaded: {len(df)} total records")
    except Exception as e:
        print(f"❌ Failed to load database: {e}")
        return False
    
    # Test problematic neighborhoods
    problem_neighborhoods = [
        'nişantaşı', 'nisantasi', 'nişantasi',
        'beşiktaş', 'besiktas', 
        'şişli', 'sisli',
        'çankaya', 'cankaya',
        'bornova'
    ]
    
    print(f"\n🔍 Searching for problematic neighborhoods:")
    
    found_neighborhoods = {}
    
    for neighborhood in problem_neighborhoods:
        print(f"\n   Searching for '{neighborhood}':")
        
        # Search in mahalle_adi column (case insensitive, partial match)
        matches = df[df['mahalle_adi'].str.lower().str.contains(neighborhood, na=False)]
        
        if len(matches) > 0:
            print(f"   ✅ Found {len(matches)} matches:")
            for _, row in matches.head(5).iterrows():  # Show first 5 matches
                print(f"      • {row['mahalle_adi']} → {row['ilce_adi']}, {row['il_adi']}")
            if len(matches) > 5:
                print(f"      ... and {len(matches) - 5} more")
            
            # Store the first good match
            first_match = matches.iloc[0]
            if (pd.notna(first_match['mahalle_adi']) and 
                pd.notna(first_match['ilce_adi']) and 
                pd.notna(first_match['il_adi'])):
                found_neighborhoods[neighborhood] = {
                    'mahalle': str(first_match['mahalle_adi']).strip(),
                    'ilçe': str(first_match['ilce_adi']).strip(), 
                    'il': str(first_match['il_adi']).strip()
                }
        else:
            print(f"   ❌ No matches found for '{neighborhood}'")
    
    print(f"\n📊 Database Summary:")
    print(f"   Total records: {len(df)}")
    print(f"   Records with valid mahalle+ilçe+il: {len(df.dropna(subset=['mahalle_adi', 'ilce_adi', 'il_adi']))}")
    print(f"   Neighborhoods found: {len(found_neighborhoods)}")
    
    return found_neighborhoods

def debug_component_completion_engine():
    """Test the Component Completion Engine with problematic cases"""
    print(f"\n🧪 COMPONENT COMPLETION ENGINE DEBUG")
    print("=" * 60)
    
    try:
        from component_completion_engine import ComponentCompletionEngine
        engine = ComponentCompletionEngine()
        print(f"✅ Component Completion Engine loaded")
        print(f"   Database records: {len(engine.admin_database)}")
        print(f"   Neighborhood index: {len(engine.neighborhood_completion_index)}")
    except Exception as e:
        print(f"❌ Failed to load Component Completion Engine: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test problematic cases with detailed debugging
    test_cases = [
        {'mahalle': 'Nişantaşı'},
        {'mahalle': 'Nişantaşı Mahallesi'},
        {'mahalle': 'Beşiktaş'},
        {'mahalle': 'Şişli'},
        {'mahalle': 'Çankaya'},
        {'mahalle': 'Bornova'},
        {'mahalle': 'Etlik'},  # Known working case
        {'mahalle': 'Moda'},   # Known working case
    ]
    
    print(f"\n🧪 Testing {len(test_cases)} completion scenarios:")
    
    working_cases = 0
    failed_cases = 0
    
    for i, test_case in enumerate(test_cases, 1):
        mahalle_name = test_case['mahalle']
        print(f"\n{i}. Testing: {mahalle_name}")
        
        try:
            result = engine.complete_address_hierarchy(test_case)
            completed = result.get('completed_components', {})
            completions = result.get('completions_made', [])
            confidence = result.get('confidence', 0.0)
            
            print(f"   Input: {test_case}")
            print(f"   Result: {completed}")
            print(f"   Completions: {completions}")
            print(f"   Confidence: {confidence:.3f}")
            
            # Check if completion was successful
            has_completion = len(completions) > 0 and any('mahalle→' in comp for comp in completions)
            
            if has_completion:
                print(f"   ✅ SUCCESS - Completion made")
                working_cases += 1
            else:
                print(f"   ❌ FAILED - No completion made")
                failed_cases += 1
                
                # Debug why it failed
                print(f"   🔍 Debug info:")
                norm_name = engine._normalize_turkish_text(mahalle_name.lower())
                print(f"      Normalized: '{norm_name}'")
                in_index = norm_name in engine.neighborhood_completion_index
                print(f"      In index: {in_index}")
                
                if not in_index:
                    # Try variations
                    variations = [
                        norm_name,
                        f"{norm_name} mahallesi",
                        norm_name.replace(' mahallesi', ''),
                    ]
                    print(f"      Trying variations: {variations}")
                    for var in variations:
                        if var in engine.neighborhood_completion_index:
                            match = engine.neighborhood_completion_index[var]
                            print(f"         Found '{var}': {match}")
                            break
                    else:
                        print(f"         No variations found in index")
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            failed_cases += 1
    
    success_rate = (working_cases / (working_cases + failed_cases)) * 100
    print(f"\n📊 Completion Test Summary:")
    print(f"   Working: {working_cases}")
    print(f"   Failed: {failed_cases}")
    print(f"   Success rate: {success_rate:.1f}%")
    
    return success_rate >= 87.5  # 7/8 = 87.5%

def debug_lookup_algorithm():
    """Debug the lookup algorithm step by step"""
    print(f"\n🔬 LOOKUP ALGORITHM DEBUG")
    print("=" * 60)
    
    try:
        from component_completion_engine import ComponentCompletionEngine
        engine = ComponentCompletionEngine()
    except Exception as e:
        print(f"❌ Failed to load engine: {e}")
        return False
    
    # Focus on the failing case: Nişantaşı
    test_input = "Nişantaşı"
    print(f"Debugging lookup for: '{test_input}'")
    
    # Step 1: Normalization
    normalized = engine._normalize_turkish_text(test_input.lower())
    print(f"1. Normalized: '{normalized}'")
    
    # Step 2: Generate lookup candidates
    candidates = [
        normalized,
        f"{normalized} mahallesi",
        normalized.replace(' mahallesi', ''),
    ]
    # Add title case variations
    for candidate in candidates.copy():
        candidates.append(candidate.title())
    
    print(f"2. Lookup candidates: {candidates}")
    
    # Step 3: Search in index
    print(f"3. Index search results:")
    for candidate in candidates:
        if candidate in engine.neighborhood_completion_index:
            match = engine.neighborhood_completion_index[candidate]
            print(f"   ✅ Found '{candidate}': {match}")
        else:
            print(f"   ❌ Not found: '{candidate}'")
    
    # Step 4: Sample what's actually in the index (Nişantaşı-related)
    print(f"4. Searching index for Nişantaşı-related entries:")
    nisantasi_entries = []
    for key, value in engine.neighborhood_completion_index.items():
        if 'nisanta' in key.lower() or 'nişanta' in key.lower():
            nisantasi_entries.append((key, value))
    
    if nisantasi_entries:
        print(f"   Found {len(nisantasi_entries)} Nişantaşı-related entries:")
        for key, value in nisantasi_entries[:5]:
            print(f"   • '{key}' → {value}")
    else:
        print(f"   ❌ No Nişantaşı-related entries found in index")
    
    return len(nisantasi_entries) > 0

def find_systematic_gaps():
    """Find systematic patterns in completion failures"""
    print(f"\n📊 SYSTEMATIC GAP ANALYSIS")
    print("=" * 60)
    
    try:
        from component_completion_engine import ComponentCompletionEngine
        engine = ComponentCompletionEngine()
    except Exception as e:
        print(f"❌ Failed to load engine: {e}")
        return []
    
    # Test a comprehensive set of well-known Turkish neighborhoods
    major_neighborhoods = [
        # İstanbul
        'Nişantaşı', 'Beşiktaş', 'Şişli', 'Kadıköy', 'Üsküdar', 'Fatih', 'Beyoğlu',
        'Moda', 'Levent', 'Maslak', 'Taksim', 'Galata', 'Ortaköy',
        
        # Ankara  
        'Çankaya', 'Keçiören', 'Etlik', 'Kızılay', 'Ulus', 'Bahçelievler',
        
        # İzmir
        'Alsancak', 'Konak', 'Bornova', 'Karşıyaka', 'Güzelyalı',
        
        # Other major cities
        'Nilüfer', 'Osmangazi', 'Muratpaşa', 'Konyaaltı'
    ]
    
    print(f"Testing {len(major_neighborhoods)} major Turkish neighborhoods:")
    
    failed_neighborhoods = []
    working_neighborhoods = []
    
    for neighborhood in major_neighborhoods:
        try:
            result = engine.complete_address_hierarchy({'mahalle': neighborhood})
            completions = result.get('completions_made', [])
            
            has_completion = len(completions) > 0
            
            if has_completion:
                working_neighborhoods.append(neighborhood)
                print(f"✅ {neighborhood}")
            else:
                failed_neighborhoods.append(neighborhood)
                print(f"❌ {neighborhood}")
                
        except Exception as e:
            failed_neighborhoods.append(neighborhood)
            print(f"🔥 {neighborhood} (ERROR: {e})")
    
    print(f"\n📊 Gap Analysis Results:")
    print(f"   Working: {len(working_neighborhoods)}/{len(major_neighborhoods)} ({len(working_neighborhoods)/len(major_neighborhoods)*100:.1f}%)")
    print(f"   Failed: {len(failed_neighborhoods)}")
    
    if failed_neighborhoods:
        print(f"\n❌ Failed neighborhoods:")
        for neighborhood in failed_neighborhoods:
            print(f"   • {neighborhood}")
    
    return failed_neighborhoods

def main():
    """Main debug function"""
    print("🔬 COMPONENT COMPLETION INTELLIGENCE GAP ANALYSIS")
    print("=" * 60)
    print("Debugging Nişantaşı → Şişli completion failure and other gaps\n")
    
    # Step 1: Check database content
    found_in_db = debug_database_content()
    
    # Step 2: Test component completion engine
    engine_working = debug_component_completion_engine()
    
    # Step 3: Debug lookup algorithm
    lookup_working = debug_lookup_algorithm()
    
    # Step 4: Find systematic gaps
    failed_cases = find_systematic_gaps()
    
    # Summary
    print(f"\n" + "=" * 60)
    print("🏁 GAP ANALYSIS SUMMARY:")
    print(f"   Database content: {'✅ GOOD' if found_in_db else '❌ ISSUES'}")
    print(f"   Engine functionality: {'✅ GOOD' if engine_working else '❌ ISSUES'}")
    print(f"   Lookup algorithm: {'✅ GOOD' if lookup_working else '❌ ISSUES'}")
    print(f"   Failed neighborhoods: {len(failed_cases)}")
    
    if failed_cases:
        print(f"\n🎯 PRIORITY FIXES NEEDED:")
        for neighborhood in failed_cases[:5]:  # Top 5 failures
            print(f"   • {neighborhood}")
    
    print("=" * 60)
    
    return len(failed_cases)

if __name__ == "__main__":
    gap_count = main()
    sys.exit(0 if gap_count == 0 else 1)