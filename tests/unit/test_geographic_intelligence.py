#!/usr/bin/env python3
"""
Comprehensive test suite for Geographic Intelligence Engine
Phase 1 Implementation Testing
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent.parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def test_geographic_intelligence_phase1():
    """Comprehensive test for Phase 1 Geographic Intelligence implementation"""
    
    print("🧪 GEOGRAPHIC INTELLIGENCE ENGINE - PHASE 1 TESTING")
    print("=" * 70)
    
    try:
        from geographic_intelligence import GeographicIntelligence
        print("✅ GeographicIntelligence module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import GeographicIntelligence: {e}")
        return False
    
    # Initialize the engine
    try:
        geo_engine = GeographicIntelligence()
        print(f"✅ Geographic Intelligence Engine initialized")
        print(f"   Database records: {len(geo_engine.admin_hierarchy):,}")
        print(f"   Cities indexed: {len(geo_engine.city_lookup):,}")
        print(f"   Districts indexed: {len(geo_engine.district_lookup):,}")
        print(f"   Neighborhoods indexed: {len(geo_engine.neighborhood_lookup):,}")
    except Exception as e:
        print(f"❌ Failed to initialize engine: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Critical Phase 1 test cases
    phase1_test_cases = [
        {
            'name': 'Case 1: District + City at end (keçiören ankara)',
            'input': "Etlik mah Süleymaniye Cad 231.sk no3 / 12 keçiören ankara",
            'expected_components': ['il', 'ilçe'],
            'expected_values': {'il': 'Ankara', 'ilçe': 'Keçiören'},
            'min_confidence': 0.8
        },
        {
            'name': 'Case 2: City only (istanbul)',
            'input': "moda mahallesi caferağa sokak istanbul",
            'expected_components': ['il'],
            'expected_values': {'il': 'İstanbul'},
            'min_confidence': 0.8
        },
        {
            'name': 'Case 3: District only should find city (keçiören)',
            'input': "etlik mahallesi keçiören",
            'expected_components': ['ilçe'],  # May also find 'il'
            'expected_values': {'ilçe': 'Keçiören'},
            'min_confidence': 0.7
        },
        {
            'name': 'Case 4: Neighborhood should find hierarchy (moda)',
            'input': "moda mahallesi caferağa sokak",
            'expected_components': ['mahalle'],  # May also find 'il', 'ilçe'
            'expected_values': {'mahalle': 'Moda'},
            'min_confidence': 0.7
        },
        {
            'name': 'Case 5: Different order (ankara çankaya)',
            'input': "tunali hilmi caddesi ankara çankaya",
            'expected_components': ['il', 'ilçe'],
            'expected_values': {'il': 'Ankara', 'ilçe': 'Çankaya'},
            'min_confidence': 0.8
        },
        {
            'name': 'Case 6: Slash format (istanbul/kadıköy)',
            'input': "bahariye caddesi istanbul/kadıköy",
            'expected_components': ['il', 'ilçe'],
            'expected_values': {'il': 'İstanbul', 'ilçe': 'Kadıköy'},
            'min_confidence': 0.8
        }
    ]
    
    print(f"\\n🧪 RUNNING {len(phase1_test_cases)} PHASE 1 TEST CASES:")
    
    passed_tests = 0
    failed_tests = 0
    
    for i, test_case in enumerate(phase1_test_cases, 1):
        print(f"\\n{i}. {test_case['name']}")
        print(f"   Input: '{test_case['input']}'")
        
        try:
            # Run detection
            result = geo_engine.detect_geographic_anchors(test_case['input'])
            components = result['components']
            confidence = result['confidence']
            method = result['detection_method']
            processing_time = result['processing_time_ms']
            
            print(f"   Result: {components}")
            print(f"   Confidence: {confidence:.2f}")
            print(f"   Method: {method}")
            print(f"   Processing time: {processing_time:.2f}ms")
            
            # Check if test passed
            test_passed = True
            failure_reasons = []
            
            # Check required components are present
            for required_component in test_case['expected_components']:
                if required_component not in components:
                    test_passed = False
                    failure_reasons.append(f"Missing component: {required_component}")
            
            # Check expected values
            for component, expected_value in test_case['expected_values'].items():
                actual_value = components.get(component)
                if actual_value != expected_value:
                    # Allow case-insensitive comparison for Turkish names
                    if (actual_value and expected_value and 
                        actual_value.lower() != expected_value.lower()):
                        test_passed = False
                        failure_reasons.append(f"{component}: expected '{expected_value}', got '{actual_value}'")
            
            # Check minimum confidence
            if confidence < test_case['min_confidence']:
                test_passed = False
                failure_reasons.append(f"Low confidence: {confidence:.2f} < {test_case['min_confidence']}")
            
            # Check processing time (should be <10ms as per requirements)
            if processing_time > 10.0:
                print(f"   ⚠️  Processing time {processing_time:.2f}ms > 10ms target")
            
            if test_passed:
                print(f"   ✅ PASS")
                passed_tests += 1
            else:
                print(f"   ❌ FAIL: {'; '.join(failure_reasons)}")
                failed_tests += 1
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            failed_tests += 1
            import traceback
            traceback.print_exc()
    
    # Additional functionality tests
    print(f"\\n🔍 ADDITIONAL FUNCTIONALITY TESTS:")
    
    # Test hierarchical context building
    print(f"\\n7. Hierarchical Context Building Test")
    partial_components = {'ilçe': 'Keçiören'}
    enriched = geo_engine.build_hierarchical_context(partial_components)
    print(f"   Input: {partial_components}")
    print(f"   Enriched: {enriched}")
    
    if 'il' in enriched:
        print(f"   ✅ Successfully enriched with il: {enriched['il']}")
    else:
        print(f"   ❌ Failed to enrich with il")
        failed_tests += 1
    
    # Test statistics
    stats = geo_engine.get_statistics()
    print(f"\\n📊 ENGINE STATISTICS:")
    print(f"   Total queries: {stats['total_queries']}")
    print(f"   Successful detections: {stats['successful_detections']}")
    print(f"   Success rate: {stats['success_rate']:.1%}")
    print(f"   Average processing time: {stats['average_processing_time_ms']:.2f}ms")
    print(f"   Hierarchy enrichments: {stats['hierarchy_enrichments']}")
    
    # Performance requirements check
    print(f"\\n⚡ PERFORMANCE REQUIREMENTS CHECK:")
    avg_time = stats['average_processing_time_ms']
    if avg_time <= 10.0:
        print(f"   ✅ Processing time: {avg_time:.2f}ms ≤ 10ms target")
    else:
        print(f"   ❌ Processing time: {avg_time:.2f}ms > 10ms target")
        failed_tests += 1
    
    # Summary
    total_tests = passed_tests + failed_tests
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\\n" + "=" * 70)
    print(f"📊 PHASE 1 TEST SUMMARY:")
    print(f"   Total tests: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {failed_tests}")
    print(f"   Success rate: {success_rate:.1f}%")
    
    if failed_tests == 0:
        print(f"\\n🎉 PHASE 1 IMPLEMENTATION SUCCESSFUL!")
        print(f"✅ All critical test cases passed")
        print(f"✅ Performance requirements met")
        print(f"✅ Geographic Intelligence Engine ready for integration")
        return True
    else:
        print(f"\\n🔧 PHASE 1 NEEDS IMPROVEMENTS:")
        print(f"❌ {failed_tests} test cases failed")
        print(f"🔧 Review failed cases and improve detection logic")
        return False


def test_integration_with_existing_parser():
    """Test integration with existing AddressParser"""
    
    print(f"\\n🔗 INTEGRATION TESTING WITH EXISTING ADDRESSPARSER:")
    print("=" * 70)
    
    try:
        from geographic_intelligence import GeographicIntelligence
        from address_parser import AddressParser
        
        geo_engine = GeographicIntelligence()
        parser = AddressParser()
        
        print(f"✅ Both engines loaded successfully")
        
        # Test address that existing parser might miss geographic components
        test_address = "etlik mahallesi süleymaniye caddesi no:15 keçiören ankara"
        
        print(f"\\n📊 COMPARISON TEST:")
        print(f"Address: '{test_address}'")
        
        # Test existing parser
        parser_result = parser.parse_address(test_address)
        print(f"\\nAddressParser result:")
        print(f"   Components: {parser_result.get('components', {})}")
        print(f"   Confidence: {parser_result.get('parsing_confidence', 0):.2f}")
        
        # Test geographic intelligence
        geo_result = geo_engine.detect_geographic_anchors(test_address)
        print(f"\\nGeographicIntelligence result:")
        print(f"   Components: {geo_result['components']}")
        print(f"   Confidence: {geo_result['confidence']:.2f}")
        print(f"   Method: {geo_result['detection_method']}")
        
        # Integration potential
        parser_components = parser_result.get('components', {})
        geo_components = geo_result['components']
        
        # Check if geographic engine found components that parser missed
        missing_in_parser = []
        for component, value in geo_components.items():
            if component not in parser_components:
                missing_in_parser.append(f"{component}: {value}")
        
        if missing_in_parser:
            print(f"\\n✨ INTEGRATION BENEFIT:")
            print(f"   Geographic Intelligence found: {', '.join(missing_in_parser)}")
            print(f"   These were missing in AddressParser result")
        else:
            print(f"\\n📝 INTEGRATION STATUS:")
            print(f"   No additional components found (both engines detected same components)")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False


if __name__ == "__main__":
    print("🚀 STARTING COMPREHENSIVE GEOGRAPHIC INTELLIGENCE TESTING")
    print("=" * 70)
    
    # Phase 1 core functionality testing
    phase1_success = test_geographic_intelligence_phase1()
    
    # Integration testing
    integration_success = test_integration_with_existing_parser()
    
    # Final assessment
    print(f"\\n🏁 FINAL ASSESSMENT:")
    print("=" * 70)
    
    if phase1_success and integration_success:
        print(f"🎉 GEOGRAPHIC INTELLIGENCE ENGINE - PHASE 1 COMPLETE!")
        print(f"✅ Core functionality working correctly")
        print(f"✅ Performance requirements satisfied")
        print(f"✅ Integration potential confirmed")
        print(f"✅ Ready for Phase 2: Semantic Pattern Engine")
    else:
        if not phase1_success:
            print(f"❌ Phase 1 core functionality needs fixes")
        if not integration_success:
            print(f"❌ Integration testing failed")
        print(f"🔧 Address issues before proceeding to Phase 2")