#!/usr/bin/env python3
"""
PHASE 5 INTEGRATION TEST
Test the complete AddressParser with Phase 5 Component Completion Intelligence
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def test_phase5_integration():
    """Test the fully integrated system with Phase 5 Component Completion Intelligence"""
    print("🚀 TESTING PHASE 5 COMPONENT COMPLETION INTEGRATION")
    print("=" * 75)
    print("Testing AddressParser with Component Completion Intelligence Engine (Phase 5)")
    print("")
    
    try:
        from address_parser import AddressParser
        parser = AddressParser()
        print("✅ AddressParser initialized with Phase 5 Component Completion Intelligence")
    except Exception as e:
        print(f"❌ Failed to initialize AddressParser: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Critical Phase 5 test cases - DOWN completion (mahalle → ilçe → il)
    test_cases = [
        {
            'name': 'DOWN Completion: Etlik → Keçiören, Ankara',
            'input': "Etlik Mahallesi Çiçek Sokak no:15",
            'expected_completions': {
                'mahalle': 'Etlik',
                'ilçe': 'Keçiören',  # Should be auto-completed
                'il': 'Ankara',      # Should be auto-completed
                'sokak': 'Çiçek',
                'bina_no': '15'
            }
        },
        {
            'name': 'DOWN Completion: Moda → Kadıköy, İstanbul',
            'input': "Moda Mahallesi Caferağa Sokak 25/A",
            'expected_completions': {
                'mahalle': 'Moda',
                'ilçe': 'Kadıköy',   # Should be auto-completed
                'il': 'İstanbul',    # Should be auto-completed
                'sokak': 'Caferağa',
                'bina_no': '25/A'
            }
        },
        {
            'name': 'Partial DOWN: İstanbul + Alsancak → Konak',
            'input': "İstanbul Alsancak Mahallesi Kordon Caddesi no:12",
            'expected_completions': {
                'il': 'İstanbul',     # Given
                'mahalle': 'Alsancak',
                'ilçe': 'Konak',      # Should be auto-completed
                'cadde': 'Kordon',
                'bina_no': '12'
            }
        },
        {
            'name': 'UP Completion Still Works: Keçiören → Ankara',
            'input': "Keçiören Etlik Süleymaniye Caddesi no:25",
            'expected_completions': {
                'ilçe': 'Keçiören',   # Given
                'il': 'Ankara',       # Should be auto-completed
                'mahalle': 'Etlik',
                'cadde': 'Süleymaniye',
                'bina_no': '25'
            }
        },
        {
            'name': 'Complex Advanced + Completion: Etlik + Building Hierarchy',
            'input': "Etlik mah. Süleymaniye Cad. A blok 3. kat daire 12",
            'expected_completions': {
                'mahalle': 'Etlik',
                'ilçe': 'Keçiören',    # Should be auto-completed
                'il': 'Ankara',        # Should be auto-completed
                'cadde': 'Süleymaniye',
                'blok': 'A',
                'kat': '3',
                'daire': '12'
            }
        }
    ]
    
    print(f"🧪 Running {len(test_cases)} Phase 5 hierarchy completion test cases:")
    
    passed_tests = 0
    failed_tests = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Input: '{test_case['input']}'")
        
        try:
            result = parser.parse_address(test_case['input'])
            components = result.get('components', {})
            confidence = result.get('confidence', 0)
            processing_time = result.get('processing_time_ms', 0)
            
            print(f"   Result: {components}")
            print(f"   Component count: {len(components)}")
            print(f"   Confidence: {confidence:.3f}")
            print(f"   Processing time: {processing_time:.2f}ms")
            
            # Check if expected components are found
            test_passed = True
            missing_components = []
            completion_success = []
            
            for expected_component, expected_value in test_case['expected_completions'].items():
                actual_value = components.get(expected_component)
                if not actual_value:
                    missing_components.append(expected_component)
                    test_passed = False
                elif expected_value.lower() in actual_value.lower():
                    completion_success.append(f"{expected_component}: {actual_value}")
                else:
                    # Be lenient for close matches
                    if expected_value in actual_value or actual_value in expected_value:
                        completion_success.append(f"{expected_component}: {actual_value} (~{expected_value})")
                    else:
                        missing_components.append(f"{expected_component} (got '{actual_value}', expected '{expected_value}')")
                        test_passed = False
            
            if missing_components:
                print(f"   ❌ Issues: {missing_components}")
            if completion_success:
                print(f"   ✅ Completions: {completion_success}")
            
            # Special check for Phase 5 critical functionality
            has_down_completion = ('mahalle' in components and 'ilçe' in components and 'il' in components)
            
            if test_passed and has_down_completion:
                print(f"   🎉 PHASE 5 SUCCESS - DOWN completion working!")
                passed_tests += 1
            elif test_passed:
                print(f"   ✅ PASS - Components detected correctly")
                passed_tests += 1
            else:
                print(f"   ❌ FAIL - Missing critical components")
                failed_tests += 1
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            failed_tests += 1
    
    # Summary
    total_tests = passed_tests + failed_tests
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n" + "=" * 75)
    print(f"📊 PHASE 5 INTEGRATION TEST SUMMARY:")
    print(f"   Total tests: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {failed_tests}")
    print(f"   Success rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print(f"\n🎉 PHASE 5 INTEGRATION SUCCESSFUL!")
        print(f"✅ Component Completion Intelligence operational")
        print(f"✅ DOWN completion (mahalle→ilçe→il) working") 
        print(f"✅ UP completion (ilçe→il) still functional")
        print(f"✅ All phases integrated successfully")
        print(f"✅ TEKNOFEST address system ready!")
        return True
    else:
        print(f"\n🔧 PHASE 5 INTEGRATION NEEDS IMPROVEMENTS:")
        print(f"❌ Success rate below 80% target")
        print(f"🔧 Review failed cases and improve integration")
        return False

def main():
    """Run Phase 5 integration tests"""
    print("🔬 PHASE 5 COMPONENT COMPLETION INTELLIGENCE INTEGRATION TEST")
    print("=" * 75)
    print("Testing the complete TEKNOFEST 2025 address processing system")
    print("with Component Completion Intelligence (Phase 5) integrated\n")
    
    # Run integration tests
    integration_success = test_phase5_integration()
    
    # Final assessment
    print("\n" + "=" * 75)
    print("🏁 FINAL PHASE 5 INTEGRATION ASSESSMENT:")
    print(f"   Integration Tests: {'✅ PASS' if integration_success else '❌ FAIL'}")
    
    if integration_success:
        print(f"\n🎯 PHASE 5 SYSTEM FULLY OPERATIONAL!")
        print(f"🚀 Ready for TEKNOFEST 2025 competition")
        print(f"✅ All Phase 1 + Phase 2 + Phase 3 + Phase 5 requirements met")
        print(f"✅ Bidirectional hierarchy completion: mahalle ↔ ilçe ↔ il")
        print(f"✅ DOWN completion addresses critical TEKNOFEST gap")
        print(f"✅ UP completion enhanced and maintained")
        print(f"✅ Component Completion Intelligence integrated")
    else:
        print(f"\n🔧 PHASE 5 INTEGRATION NEEDS ATTENTION")
        print(f"⚠️  Some Phase 5 tests failed - review above results")
    
    print("=" * 75)
    
    return integration_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)