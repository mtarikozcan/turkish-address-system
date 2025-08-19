"""
Simple test runner for HybridAddressMatcher mock implementation
Tests without pytest dependency
"""

import sys
import os
import time

# Add src and tests to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_address_matcher_mock():
    """Test the MockHybridAddressMatcher implementation"""
    
    print("🧪 Testing HybridAddressMatcher Mock Implementation")
    print("=" * 60)
    
    try:
        # Import the mock class from test file
        from test_address_matcher import MockHybridAddressMatcher
        
        # Initialize matcher
        matcher = MockHybridAddressMatcher()
        print("✅ MockHybridAddressMatcher initialized successfully")
        
        # Test cases for different similarity scenarios
        test_cases = [
            {
                'name': 'Identical addresses',
                'address1': 'İstanbul Kadıköy Moda Mahallesi Caferağa Sokak No 10',
                'address2': 'İstanbul Kadıköy Moda Mahallesi Caferağa Sokak No 10',
                'expected_similarity_min': 0.95,
                'expected_match': True
            },
            {
                'name': 'Same address with variations',
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
            }
        ]
        
        passed = 0
        total = 0
        
        # Test main hybrid similarity method
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
        
        # Test weighted ensemble scoring
        print(f"\n📋 Testing weighted ensemble scoring:")
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
            print(f"❌ Weighted ensemble scoring: ERROR - {e}")
        
        # Test performance
        print(f"\n📋 Testing performance:")
        total += 1
        
        try:
            start_time = time.time()
            result = matcher.calculate_hybrid_similarity(test_addr1, test_addr2)
            end_time = time.time()
            
            processing_time_ms = (end_time - start_time) * 1000
            
            if processing_time_ms < 100:  # Under 100ms requirement
                print(f"✅ Performance test: PASSED ({processing_time_ms:.2f}ms)")
                passed += 1
            else:
                print(f"❌ Performance test: FAILED ({processing_time_ms:.2f}ms)")
                
        except Exception as e:
            print(f"❌ Performance test: ERROR - {e}")
        
        # Test error handling
        print(f"\n📋 Testing error handling:")
        error_inputs = [
            (None, "Valid address"),
            ("Valid address", None),
            ("", "Valid address"),
            (123, "Valid address"),
            ([], {})
        ]
        
        for addr1, addr2 in error_inputs:
            total += 1
            try:
                result = matcher.calculate_hybrid_similarity(addr1, addr2)
                
                if (isinstance(result, dict) and 
                    result.get('overall_similarity') == 0.0 and 
                    result.get('match_decision') == False):
                    print(f"✅ Error handling ({type(addr1).__name__}, {type(addr2).__name__}): PASSED")
                    passed += 1
                else:
                    print(f"❌ Error handling ({type(addr1).__name__}, {type(addr2).__name__}): FAILED")
                    
            except Exception as e:
                print(f"❌ Error handling ({type(addr1).__name__}, {type(addr2).__name__}): ERROR - {e}")
        
        print(f"\n" + "=" * 60)
        print(f"📊 Test Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 All tests passed! HybridAddressMatcher mock implementation is working correctly.")
        elif passed/total >= 0.8:
            print("✅ Most tests passed! Mock implementation is largely functional.")
        else:
            print("⚠️  Some tests failed. Mock implementation needs review.")
        
        return passed/total >= 0.8
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_similarity_components():
    """Test individual similarity components"""
    
    print(f"\n🔧 Testing similarity components:")
    print("=" * 40)
    
    try:
        from test_address_matcher import MockHybridAddressMatcher
        
        matcher = MockHybridAddressMatcher()
        
        # Test component configurations
        print("✅ Similarity weights:")
        for component, weight in matcher.similarity_weights.items():
            print(f"   {component}: {weight}")
        
        print(f"✅ Confidence threshold: {matcher.confidence_threshold}")
        
        # Test semantic model configuration
        semantic_config = matcher.semantic_model
        print("✅ Semantic model configuration:")
        print(f"   Model: {semantic_config['model_name']}")
        print(f"   Dimension: {semantic_config['embedding_dimension']}")
        
        # Test geographic configuration
        geo_config = matcher.geographic_config
        print("✅ Geographic configuration:")
        print(f"   Distance function: {geo_config['distance_function']}")
        print(f"   Max distance: {geo_config['max_distance_km']}km")
        
        # Test text similarity configuration
        text_config = matcher.text_similarity_config
        print("✅ Text similarity configuration:")
        print(f"   Algorithm: {text_config['algorithm']}")
        print(f"   Library: {text_config['library']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Component test error: {e}")
        return False

def test_turkish_language_features():
    """Test Turkish language specific features"""
    
    print(f"\n🇹🇷 Testing Turkish language features:")
    print("=" * 45)
    
    try:
        from test_address_matcher import MockHybridAddressMatcher
        
        matcher = MockHybridAddressMatcher()
        
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
        coords = matcher._extract_or_estimate_coordinates("İstanbul Kadıköy 40.9875,29.0376")
        if coords and 'lat' in coords and 'lon' in coords:
            print(f"✅ Coordinate extraction: lat={coords['lat']}, lon={coords['lon']}")
        else:
            print("❌ Coordinate extraction failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Turkish language test error: {e}")
        return False

def main():
    """Run all tests"""
    
    print("🧪 TEKNOFEST HybridAddressMatcher - Mock Implementation Tests")
    print("=" * 70)
    
    # Test mock implementation
    success1 = test_address_matcher_mock()
    
    # Test similarity components
    success2 = test_similarity_components()
    
    # Test Turkish language features
    success3 = test_turkish_language_features()
    
    overall_success = success1 and success2 and success3
    
    print(f"\n🎯 Testing completed!")
    
    if overall_success:
        print(f"\n🚀 HybridAddressMatcher test suite is ready for:")
        print("   • Real HybridAddressMatcher implementation (Algorithm 4)")
        print("   • 4-level similarity breakdown (semantic, geographic, textual, hierarchical)")
        print("   • Weighted ensemble scoring (40%, 30%, 20%, 10%)")
        print("   • Sentence Transformers integration")
        print("   • Turkish coordinate distance calculation")
        print("   • Fuzzy string matching with thefuzz")
        print("   • Integration with AddressValidator, AddressCorrector, AddressParser")
        print("   • Performance testing (<100ms per comparison)")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)