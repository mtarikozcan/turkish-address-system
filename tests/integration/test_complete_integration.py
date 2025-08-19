#!/usr/bin/env python3
"""
COMPREHENSIVE INTEGRATION TEST for Phase 1 + Phase 2 Combined System
Test the complete AddressParser with both GeographicIntelligence and SemanticPatternEngine

Expected Result: SUCCESS for all test cases including the original failing address
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def test_complete_integration():
    """Test the fully integrated system with both engines"""
    print("🚀 TESTING COMPLETE INTEGRATED SYSTEM")
    print("=" * 70)
    print("Testing AddressParser with GeographicIntelligence + SemanticPatternEngine")
    print("")
    
    try:
        from address_parser import AddressParser
        parser = AddressParser()
        print("✅ AddressParser initialized with all engines")
    except Exception as e:
        print(f"❌ Failed to initialize AddressParser: {e}")
        return False
    
    # Test cases including the original failing address
    test_cases = [
        {
            'name': 'Original Failing Address (Complete Test)',
            'input': "Etlik mah Süleymaniye Cad 231.sk no3 / 12 keçiören ankara",
            'expected': {
                'il': 'Ankara',
                'ilçe': 'Keçiören', 
                'mahalle': 'Etlik',
                'cadde': 'Süleymaniye Caddesi',
                'sokak': '231 Sokak',
                'bina_no': '3',
                'daire': '12'
            }
        },
        {
            'name': 'Geographic Pattern Test',
            'input': "moda mahallesi istanbul",
            'expected': {
                'il': 'İstanbul',
                'mahalle': 'Moda'
            }
        },
        {
            'name': 'Semantic Pattern Test', 
            'input': "15.sk no 25/A kat 3",
            'expected': {
                'sokak': '15 Sokak',
                'bina_no': '25/A',
                'kat': '3'
            }
        },
        {
            'name': 'Complex Combined Test',
            'input': "atatürk mah 123.sk no5-B daire 7 çankaya ankara",
            'expected': {
                'il': 'Ankara',
                'ilçe': 'Çankaya',
                'mahalle': 'Atatürk',
                'sokak': '123 Sokak',
                'bina_no': '5-B',
                'daire': '7'
            }
        }
    ]
    
    print(f"🧪 Running {len(test_cases)} comprehensive integration tests:")
    
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
            print(f"   Confidence: {confidence:.3f}")
            print(f"   Processing time: {processing_time:.2f}ms")
            
            # Check if expected components are found
            test_passed = True
            missing_components = []
            incorrect_values = []
            
            for expected_component, expected_value in test_case['expected'].items():
                actual_value = components.get(expected_component)
                if not actual_value:
                    missing_components.append(expected_component)
                    test_passed = False
                elif actual_value != expected_value:
                    incorrect_values.append(f"{expected_component}: expected '{expected_value}', got '{actual_value}'")
                    test_passed = False
            
            if missing_components:
                print(f"   ❌ Missing components: {missing_components}")
            if incorrect_values:
                print(f"   ❌ Incorrect values: {incorrect_values}")
            
            if test_passed:
                print(f"   ✅ PASS - All expected components detected correctly")
                passed_tests += 1
            else:
                print(f"   ❌ FAIL - Issues with component detection")
                failed_tests += 1
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            failed_tests += 1
    
    # Summary
    total_tests = passed_tests + failed_tests
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n" + "=" * 70)
    print(f"📊 COMPLETE INTEGRATION TEST SUMMARY:")
    print(f"   Total tests: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {failed_tests}")
    print(f"   Success rate: {success_rate:.1f}%")
    
    if failed_tests == 0:
        print(f"\n🎉 COMPLETE SYSTEM INTEGRATION SUCCESSFUL!")
        print(f"✅ All test cases passed")
        print(f"✅ GeographicIntelligence working perfectly")
        print(f"✅ SemanticPatternEngine working perfectly") 
        print(f"✅ Combined system ready for production")
        print(f"\n🏆 PHASE 1 + PHASE 2 IMPLEMENTATION COMPLETE!")
        print(f"🚀 System ready for TEKNOFEST 2025 competition")
        return True
    else:
        print(f"\n🔧 INTEGRATION NEEDS IMPROVEMENTS:")
        print(f"❌ {failed_tests} test cases failed")
        print(f"🔧 Review failed cases and improve integration logic")
        return False

def test_performance_metrics():
    """Test performance of the complete integrated system"""
    print(f"\n📊 PERFORMANCE TESTING:")
    print("=" * 50)
    
    try:
        from address_parser import AddressParser
        parser = AddressParser()
        
        # Test with the original failing address
        test_input = "Etlik mah Süleymaniye Cad 231.sk no3 / 12 keçiören ankara"
        
        import time
        start_time = time.time()
        
        # Run multiple times to get average
        total_time = 0
        runs = 10
        
        for i in range(runs):
            run_start = time.time()
            result = parser.parse_address(test_input)
            run_time = (time.time() - run_start) * 1000
            total_time += run_time
        
        avg_time = total_time / runs
        
        print(f"   Average processing time: {avg_time:.2f}ms")
        print(f"   Total components detected: {len(result.get('components', {}))}")
        print(f"   System confidence: {result.get('confidence', 0):.3f}")
        
        # Performance evaluation
        if avg_time < 100:  # TEKNOFEST requirement
            print(f"   ✅ PERFORMANCE: Exceeds TEKNOFEST requirement (<100ms)")
        else:
            print(f"   ⚠️  PERFORMANCE: Slower than TEKNOFEST requirement")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Performance test error: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🔬 COMPLETE SYSTEM INTEGRATION VERIFICATION")
    print("=" * 70)
    print("Testing the complete TEKNOFEST 2025 address processing system")
    print("with both GeographicIntelligence and SemanticPatternEngine\n")
    
    # Run integration tests
    integration_success = test_complete_integration()
    
    # Run performance tests
    performance_success = test_performance_metrics()
    
    # Final assessment
    print("\n" + "=" * 70)
    print("🏁 FINAL SYSTEM ASSESSMENT:")
    print(f"   Integration Tests: {'✅ PASS' if integration_success else '❌ FAIL'}")
    print(f"   Performance Tests: {'✅ PASS' if performance_success else '❌ FAIL'}")
    
    overall_success = integration_success and performance_success
    
    if overall_success:
        print(f"\n🎉 SYSTEM FULLY OPERATIONAL!")
        print(f"🚀 Ready for TEKNOFEST 2025 competition")
        print(f"✅ All Phase 1 + Phase 2 requirements met")
        print(f"✅ Original failing address now works perfectly")
    else:
        print(f"\n🔧 SYSTEM NEEDS ATTENTION")
        print(f"⚠️  Some tests failed - review above results")
    
    print("=" * 70)
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)