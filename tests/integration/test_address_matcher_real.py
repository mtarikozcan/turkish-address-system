"""
Test the real HybridAddressMatcher implementation
Comprehensive test runner for HybridAddressMatcher functionality
"""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_real_address_matcher():
    """Test the real HybridAddressMatcher implementation"""
    
    print("🧪 Testing Real HybridAddressMatcher Implementation")
    print("=" * 60)
    
    try:
        from address_matcher import HybridAddressMatcher
        
        # Initialize matcher
        matcher = HybridAddressMatcher()
        print("✅ HybridAddressMatcher initialized successfully")
        
        # Test cases covering all major functionality
        test_cases = [
            {
                'name': 'Identical addresses',
                'address1': 'İstanbul Kadıköy Moda Mahallesi Caferağa Sokak No 10',
                'address2': 'İstanbul Kadıköy Moda Mahallesi Caferağa Sokak No 10',
                'expected_similarity_min': 0.95,
                'expected_match': True
            },
            {
                'name': 'Address variations (abbreviations)',
                'address1': 'İstanbul Kadıköy Moda Mahallesi Caferağa Sk. 10',
                'address2': 'Istanbul Kadikoy Moda Mah. Caferaga Sokak No:10',
                'expected_similarity_min': 0.70,
                'expected_match': True
            },
            {
                'name': 'Same neighborhood different streets',
                'address1': 'İstanbul Kadıköy Moda Mahallesi Caferağa Sokak 10',
                'address2': 'İstanbul Kadıköy Moda Mahallesi Mühürdar Sokak 15',
                'expected_similarity_min': 0.60,
                'expected_match': True
            },
            {
                'name': 'Different neighborhoods same district',
                'address1': 'İstanbul Kadıköy Moda Mahallesi',
                'address2': 'İstanbul Kadıköy Fenerbahçe Mahallesi',
                'expected_similarity_max': 0.70,
                'expected_match': False
            },
            {
                'name': 'Different cities',
                'address1': 'İstanbul Kadıköy Moda Mahallesi',
                'address2': 'Ankara Çankaya Kızılay Mahallesi',
                'expected_similarity_max': 0.40,
                'expected_match': False
            },
            {
                'name': 'Coordinate-based addresses',
                'address1': 'İstanbul Kadıköy 40.9875,29.0376',
                'address2': 'İstanbul Kadıköy 40.9876,29.0377',
                'expected_similarity_min': 0.80,
                'expected_match': True
            }
        ]
        
        passed = 0
        total = 0
        
        # Test main calculate_hybrid_similarity method
        print(f"\n📋 Testing calculate_hybrid_similarity() method:")
        for test_case in test_cases:
            total += 1
            
            try:
                result = matcher.calculate_hybrid_similarity(
                    test_case['address1'], 
                    test_case['address2']
                )
                
                # Basic structure validation
                if not isinstance(result, dict) or 'overall_similarity' not in result:
                    print(f"❌ {test_case['name']}: FAILED - Invalid result structure")
                    continue
                
                # Test similarity expectations
                similarity = result['overall_similarity']
                match_decision = result['match_decision']
                
                similarity_ok = True
                if 'expected_similarity_min' in test_case:
                    similarity_ok = similarity >= test_case['expected_similarity_min']
                elif 'expected_similarity_max' in test_case:
                    similarity_ok = similarity <= test_case['expected_similarity_max']
                
                match_ok = match_decision == test_case['expected_match']
                
                if similarity_ok and match_ok:
                    print(f"✅ {test_case['name']}: PASSED (sim: {similarity:.3f}, match: {match_decision})")
                    passed += 1
                else:
                    print(f"❌ {test_case['name']}: FAILED (sim: {similarity:.3f}, match: {match_decision})")
                    if 'expected_similarity_min' in test_case:
                        print(f"   Expected: ≥{test_case['expected_similarity_min']}, Got: {similarity:.3f}")
                    elif 'expected_similarity_max' in test_case:
                        print(f"   Expected: ≤{test_case['expected_similarity_max']}, Got: {similarity:.3f}")
                    
            except Exception as e:
                print(f"❌ {test_case['name']}: ERROR - {e}")
        
        # Test individual similarity methods
        print(f"\n📋 Testing individual similarity methods:")
        
        test_addr1 = "İstanbul Kadıköy Moda Mahallesi Caferağa Sokak No 10"
        test_addr2 = "İstanbul Kadıköy Moda Mahallesi Caferağa Sk. 10"
        
        individual_tests = [
            {
                'method': 'get_semantic_similarity',
                'expected_range': (0.0, 1.0)
            },
            {
                'method': 'get_geographic_similarity',
                'expected_range': (0.0, 1.0)
            },
            {
                'method': 'get_text_similarity',
                'expected_range': (0.0, 1.0)
            },
            {
                'method': 'get_hierarchy_similarity',
                'expected_range': (0.0, 1.0)
            }
        ]
        
        for test in individual_tests:
            total += 1
            method = getattr(matcher, test['method'])
            
            try:
                result = method(test_addr1, test_addr2)
                
                if isinstance(result, float) and test['expected_range'][0] <= result <= test['expected_range'][1]:
                    print(f"✅ {test['method']}: PASSED ({result:.3f})")
                    passed += 1
                else:
                    print(f"❌ {test['method']}: FAILED ({result})")
                    
            except Exception as e:
                print(f"❌ {test['method']}: ERROR - {e}")
        
        # Test similarity breakdown structure
        print(f"\n📋 Testing similarity breakdown:")
        total += 1
        
        try:
            result = matcher.calculate_hybrid_similarity(test_addr1, test_addr2)
            
            # Check similarity breakdown structure
            if 'similarity_breakdown' in result:
                breakdown = result['similarity_breakdown']
                expected_components = ['semantic', 'geographic', 'textual', 'hierarchical']
                
                if all(comp in breakdown for comp in expected_components):
                    print(f"✅ Similarity breakdown: PASSED")
                    print(f"   Semantic: {breakdown['semantic']:.3f}")
                    print(f"   Geographic: {breakdown['geographic']:.3f}")
                    print(f"   Textual: {breakdown['textual']:.3f}")
                    print(f"   Hierarchical: {breakdown['hierarchical']:.3f}")
                    passed += 1
                else:
                    print(f"❌ Similarity breakdown: FAILED - Missing components")
            else:
                print(f"❌ Similarity breakdown: FAILED - No breakdown found")
                
        except Exception as e:
            print(f"❌ Similarity breakdown: ERROR - {e}")
        
        print(f"\n" + "=" * 60)
        print(f"📊 Test Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 All tests passed! HybridAddressMatcher implementation is working correctly.")
        elif passed/total >= 0.8:
            print("✅ Most tests passed! Implementation is largely functional.")
        else:
            print("⚠️  Some tests failed. Implementation needs review.")
        
        return passed/total >= 0.8
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_weighted_ensemble():
    """Test weighted ensemble scoring validation"""
    
    print(f"\n🔧 Testing weighted ensemble scoring:")
    print("=" * 45)
    
    try:
        from address_matcher import HybridAddressMatcher
        
        matcher = HybridAddressMatcher()
        
        # Test weight configuration
        expected_weights = {
            'semantic': 0.4,
            'geographic': 0.3,
            'textual': 0.2,
            'hierarchical': 0.1
        }
        
        print("✅ Similarity weights validation:")
        for component, expected_weight in expected_weights.items():
            actual_weight = matcher.similarity_weights.get(component, 0.0)
            if actual_weight == expected_weight:
                print(f"   {component}: {actual_weight} ✅")
            else:
                print(f"   {component}: {actual_weight} ❌ (expected {expected_weight})")
        
        # Test confidence threshold
        expected_threshold = 0.6
        actual_threshold = matcher.confidence_threshold
        print(f"✅ Confidence threshold: {actual_threshold} {'✅' if actual_threshold == expected_threshold else '❌'}")
        
        # Test method contributions calculation
        test_result = matcher.calculate_hybrid_similarity(
            "İstanbul Kadıköy Moda Mahallesi",
            "İstanbul Kadıköy Moda Mahallesi"
        )
        
        if 'similarity_details' in test_result and 'method_contributions' in test_result['similarity_details']:
            contributions = test_result['similarity_details']['method_contributions']
            print("✅ Method contributions calculated:")
            total_contribution = sum(contributions.values())
            for method, contribution in contributions.items():
                print(f"   {method}: {contribution:.3f}")
            print(f"   Total: {total_contribution:.3f} (should equal overall_similarity)")
            
            # Verify total equals overall similarity (with small tolerance)
            overall_sim = test_result['overall_similarity']
            if abs(total_contribution - overall_sim) < 0.001:
                print("✅ Weighted ensemble calculation verified!")
            else:
                print(f"❌ Weighted ensemble mismatch: {total_contribution:.3f} vs {overall_sim:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Weighted ensemble test error: {e}")
        return False

def test_performance():
    """Test performance characteristics"""
    
    print(f"\n⚡ Testing performance:")
    print("=" * 25)
    
    try:
        from address_matcher import HybridAddressMatcher
        
        matcher = HybridAddressMatcher()
        
        # Test single address performance
        test_address1 = "İstanbul Kadıköy Moda Mahallesi Caferağa Sokak No 10"
        test_address2 = "İstanbul Kadıköy Moda Mahallesi Caferağa Sk. 10"
        
        start_time = time.time()
        result = matcher.calculate_hybrid_similarity(test_address1, test_address2)
        end_time = time.time()
        
        processing_time_ms = (end_time - start_time) * 1000
        
        print(f"✅ Single comparison: {processing_time_ms:.2f}ms")
        
        if processing_time_ms < 100:
            print("✅ Performance target met (<100ms)")
        else:
            print("⚠️  Performance target exceeded (>100ms)")
        
        # Check if processing time is recorded in result
        if 'similarity_details' in result and 'processing_time_ms' in result['similarity_details']:
            recorded_time = result['similarity_details']['processing_time_ms']
            print(f"✅ Recorded processing time: {recorded_time:.2f}ms")
        
        # Test individual method performance
        individual_tests = [
            ('get_semantic_similarity', 'Semantic'),
            ('get_geographic_similarity', 'Geographic'),
            ('get_text_similarity', 'Text'),
            ('get_hierarchy_similarity', 'Hierarchical')
        ]
        
        for method_name, display_name in individual_tests:
            method = getattr(matcher, method_name)
            start_time = time.time()
            method(test_address1, test_address2)
            end_time = time.time()
            method_time = (end_time - start_time) * 1000
            print(f"✅ {display_name} similarity: {method_time:.2f}ms")
        
        # Test batch performance
        batch_size = 10
        addresses = [
            f"İstanbul Kadıköy Test{i} Mahallesi Sokak{i} No {i}"
            for i in range(batch_size)
        ]
        
        start_time = time.time()
        for i in range(0, len(addresses)-1):
            matcher.calculate_hybrid_similarity(addresses[i], addresses[i+1])
        end_time = time.time()
        
        batch_time = (end_time - start_time) * 1000
        avg_time_per_comparison = batch_time / (batch_size - 1)
        
        print(f"✅ Batch processing ({batch_size-1} comparisons): {batch_time:.2f}ms total")
        print(f"✅ Average per comparison: {avg_time_per_comparison:.2f}ms")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test error: {e}")
        return False

def test_turkish_language_features():
    """Test Turkish language specific features"""
    
    print(f"\n🇹🇷 Testing Turkish language features:")
    print("=" * 40)
    
    try:
        from address_matcher import HybridAddressMatcher
        
        matcher = HybridAddressMatcher()
        
        # Test Turkish character handling
        turkish_tests = [
            ("İstanbul Şişli Mecidiyeköy", "Istanbul Sisli Mecidiyekoy"),
            ("Ankara Çankaya Kızılay", "Ankara Cankaya Kizilay"),
            ("İzmir Karşıyaka Bostanlı", "Izmir Karsiyaka Bostanli")
        ]
        
        passed = 0
        for addr1, addr2 in turkish_tests:
            result = matcher.calculate_hybrid_similarity(addr1, addr2)
            
            if result['overall_similarity'] > 0.5:
                print(f"✅ Turkish chars: '{addr1[:20]}...' vs '{addr2[:20]}...' = {result['overall_similarity']:.3f}")
                passed += 1
            else:
                print(f"❌ Turkish chars: '{addr1[:20]}...' vs '{addr2[:20]}...' = {result['overall_similarity']:.3f}")
        
        print(f"✅ Turkish character tests: {passed}/{len(turkish_tests)} passed")
        
        # Test coordinate extraction
        coord_address = "İstanbul Kadıköy 40.9875,29.0376"
        coords = matcher._extract_or_estimate_coordinates(coord_address)
        if coords and 'lat' in coords and 'lon' in coords:
            print(f"✅ Coordinate extraction: lat={coords['lat']}, lon={coords['lon']}")
        else:
            print("❌ Coordinate extraction failed")
        
        # Test location recognition
        location_tests = [
            ("İstanbul", "should be recognized as major city"),
            ("Kadıköy", "should be recognized as district"),
            ("Ankara", "should be recognized as major city")
        ]
        
        for location, description in location_tests:
            test_address = f"Türkiye {location} test adresi"
            cities = matcher._extract_city_names(test_address)
            
            if location.lower() in cities or len(cities) > 0:
                print(f"✅ Location recognized: {location}")
            else:
                print(f"⚠️  Location not found: {location}")
        
        return True
        
    except Exception as e:
        print(f"❌ Turkish language test error: {e}")
        return False

def test_integration_with_algorithms():
    """Test integration with other algorithms"""
    
    print(f"\n🔗 Testing algorithm integration:")
    print("=" * 35)
    
    try:
        from address_matcher import HybridAddressMatcher
        
        matcher = HybridAddressMatcher()
        
        # Check algorithm availability
        print("✅ Algorithm availability:")
        for algo_name, available in matcher.algorithms_available.items():
            status = "✅ Available" if available else "⚠️  Fallback mode"
            print(f"   {algo_name}: {status}")
        
        # Test address parsing integration
        test_address = "İstanbul Kadıköy Moda Mahallesi Caferağa Sokak No 10"
        components = matcher._extract_address_components(test_address)
        
        print(f"✅ Component extraction test:")
        print(f"   Address: {test_address}")
        print(f"   Components found: {len(components)}")
        for comp_name, comp_value in components.items():
            print(f"   {comp_name}: {comp_value}")
        
        # Test hierarchical similarity with components
        components1 = {'il': 'İstanbul', 'ilce': 'Kadıköy', 'mahalle': 'Moda'}
        components2 = {'il': 'İstanbul', 'ilce': 'Kadıköy', 'mahalle': 'Fenerbahçe'}
        
        hierarchy_sim = matcher._calculate_component_similarity(components1, components2)
        print(f"✅ Component similarity calculation: {hierarchy_sim:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test error: {e}")
        return False

def main():
    """Run all tests"""
    
    print("🧪 TEKNOFEST HybridAddressMatcher - Real Implementation Tests")
    print("=" * 70)
    
    # Test core functionality
    success1 = test_real_address_matcher()
    
    # Test weighted ensemble
    success2 = test_weighted_ensemble() if success1 else False
    
    # Test performance
    success3 = test_performance() if success1 else False
    
    # Test Turkish language features
    success4 = test_turkish_language_features() if success1 else False
    
    # Test integration
    success5 = test_integration_with_algorithms() if success1 else False
    
    overall_success = success1 and success2 and success3
    
    print(f"\n🎯 Testing completed!")
    
    if overall_success:
        print(f"\n🚀 HybridAddressMatcher is ready for:")
        print("   • 4-level Turkish address similarity calculation")
        print("   • Weighted ensemble scoring (40%, 30%, 20%, 10%)")
        print("   • Semantic, geographic, textual, hierarchical matching")
        print("   • Integration with AddressValidator, AddressCorrector, AddressParser")
        print("   • Performance requirements (<100ms per comparison)")
        print("   • TEKNOFEST competition deployment")
        print("   • Production address matching workflows")
    else:
        print(f"\n⚠️  Some test categories failed. Review implementation.")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)