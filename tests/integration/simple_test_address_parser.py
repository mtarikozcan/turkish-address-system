"""
Simple test runner for AddressParser mock implementation
Tests without pytest dependency
"""

import sys
import os
import time

# Add src and tests to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_address_parser_mock():
    """Test the MockAddressParser implementation"""
    
    print("🧪 Testing AddressParser Mock Implementation")
    print("=" * 55)
    
    try:
        # Import the mock class from test file
        from test_address_parser import MockAddressParser
        
        # Initialize parser
        parser = MockAddressParser()
        print("✅ MockAddressParser initialized successfully")
        
        # Test cases for different functionalities
        test_cases = [
            {
                'name': 'Complete Turkish address parsing',
                'address': 'İstanbul Kadıköy Moda Mahallesi Caferağa Sokak No 10 Daire 3',
                'expected_components': ['il', 'ilce', 'mahalle', 'sokak', 'bina_no', 'daire']
            },
            {
                'name': 'Ankara address parsing',
                'address': 'Ankara Çankaya Kızılay Mahallesi Atatürk Caddesi 25',
                'expected_components': ['il', 'ilce', 'mahalle', 'sokak', 'bina_no']
            },
            {
                'name': 'İzmir address parsing', 
                'address': 'İzmir Konak Alsancak Mahallesi',
                'expected_components': ['il', 'ilce', 'mahalle']
            },
            {
                'name': 'Incomplete address handling',
                'address': 'Kadıköy Moda',
                'expected_confidence_max': 0.8
            }
        ]
        
        passed = 0
        total = 0
        
        # Test main parse_address method
        print(f"\n📋 Testing parse_address() method:")
        for test_case in test_cases:
            total += 1
            
            try:
                result = parser.parse_address(test_case['address'])
                
                # Basic structure validation
                if not isinstance(result, dict) or 'components' not in result:
                    print(f"❌ {test_case['name']}: FAILED - Invalid result structure")
                    continue
                
                # Test specific expectations
                if 'expected_components' in test_case:
                    components = result['components']
                    found_components = len(components)
                    expected_min = len(test_case['expected_components']) - 2  # Allow some flexibility
                    
                    if found_components >= expected_min:
                        print(f"✅ {test_case['name']}: PASSED ({found_components} components extracted)")
                        passed += 1
                    else:
                        print(f"❌ {test_case['name']}: FAILED (only {found_components} components)")
                        
                elif 'expected_confidence_max' in test_case:
                    confidence = result.get('overall_confidence', 0.0)
                    if confidence <= test_case['expected_confidence_max']:
                        print(f"✅ {test_case['name']}: PASSED (confidence: {confidence})")
                        passed += 1
                    else:
                        print(f"❌ {test_case['name']}: FAILED (confidence too high: {confidence})")
                
                else:
                    # Basic success test
                    if result.get('overall_confidence', 0.0) > 0.0:
                        print(f"✅ {test_case['name']}: PASSED")
                        passed += 1
                    else:
                        print(f"❌ {test_case['name']}: FAILED")
                        
            except Exception as e:
                print(f"❌ {test_case['name']}: ERROR - {e}")
        
        # Test individual methods
        print(f"\n📋 Testing individual methods:")
        
        individual_tests = [
            {
                'method': 'extract_components_rule_based',
                'input': 'İstanbul Kadıköy Moda Mahallesi',
                'expected_min_components': 1
            },
            {
                'method': 'extract_components_ml_based',
                'input': 'Ankara Çankaya Kızılay',
                'expected_keys': ['components', 'confidence_scores', 'ner_entities']
            },
            {
                'method': 'validate_extracted_components',
                'input': {'il': 'İstanbul', 'ilce': 'Kadıköy', 'mahalle': 'Moda'},
                'expected_keys': ['is_valid', 'component_validity', 'completeness_score']
            }
        ]
        
        for test in individual_tests:
            total += 1
            method = getattr(parser, test['method'])
            
            try:
                result = method(test['input'])
                
                if 'expected_min_components' in test:
                    if isinstance(result, dict) and len(result) >= test['expected_min_components']:
                        print(f"✅ {test['method']}: PASSED")
                        passed += 1
                    else:
                        print(f"❌ {test['method']}: FAILED")
                        
                elif 'expected_keys' in test:
                    if isinstance(result, dict) and all(key in result for key in test['expected_keys']):
                        print(f"✅ {test['method']}: PASSED")
                        passed += 1
                    else:
                        print(f"❌ {test['method']}: FAILED - Missing keys")
                        
            except Exception as e:
                print(f"❌ {test['method']}: ERROR - {e}")
        
        # Test performance
        print(f"\n📋 Testing performance:")
        total += 1
        
        test_address = "İstanbul Kadıköy Moda Mahallesi Caferağa Sokak No 10"
        
        start_time = time.time()
        result = parser.parse_address(test_address)
        end_time = time.time()
        
        processing_time_ms = (end_time - start_time) * 1000
        
        if processing_time_ms < 100:  # Under 100ms requirement
            print(f"✅ Performance test: PASSED ({processing_time_ms:.2f}ms)")
            passed += 1
        else:
            print(f"❌ Performance test: FAILED ({processing_time_ms:.2f}ms)")
        
        # Test error handling
        print(f"\n📋 Testing error handling:")
        error_inputs = [None, "", 123, [], {}]
        
        for error_input in error_inputs:
            total += 1
            try:
                result = parser.parse_address(error_input)
                
                if isinstance(result, dict) and ('error' in result or result.get('overall_confidence', 1.0) == 0.0):
                    print(f"✅ Error handling ({type(error_input).__name__}): PASSED")
                    passed += 1
                else:
                    print(f"❌ Error handling ({type(error_input).__name__}): FAILED")
                    
            except Exception as e:
                print(f"❌ Error handling ({type(error_input).__name__}): ERROR - {e}")
        
        print(f"\n" + "=" * 55)
        print(f"📊 Test Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 All tests passed! AddressParser mock implementation is working correctly.")
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

def test_fixtures_and_data():
    """Test the pytest fixtures and test data"""
    
    print(f"\n📊 Testing fixtures and test data:")
    print("=" * 40)
    
    try:
        from test_address_parser import MockAddressParser
        
        # Test fixture data structures
        parser = MockAddressParser()
        
        # Test Turkish patterns
        patterns = parser.turkish_patterns
        assert isinstance(patterns, dict)
        assert 'il_patterns' in patterns
        assert 'mahalle_patterns' in patterns
        print("✅ Turkish patterns loaded")
        
        # Test component keywords
        keywords = parser.component_keywords
        assert isinstance(keywords, dict)
        assert 'il_keywords' in keywords
        assert 'mahalle_keywords' in keywords
        print("✅ Component keywords loaded")
        
        # Test NER model config
        ner_model = parser.ner_model
        assert isinstance(ner_model, dict)
        assert 'model_name' in ner_model
        assert ner_model['model_name'] == 'savasy/bert-base-turkish-ner-cased'
        print("✅ NER model configuration loaded")
        
        print("✅ All fixtures and data structures validated!")
        return True
        
    except Exception as e:
        print(f"❌ Fixture test error: {e}")
        return False

def main():
    """Run all tests"""
    
    print("🧪 TEKNOFEST AddressParser - Mock Implementation Tests")
    print("=" * 65)
    
    # Test mock implementation
    success1 = test_address_parser_mock()
    
    # Test fixtures and data
    success2 = test_fixtures_and_data()
    
    overall_success = success1 and success2
    
    print(f"\n🎯 Testing completed!")
    
    if overall_success:
        print(f"\n🚀 AddressParser test suite is ready for:")
        print("   • Real AddressParser implementation (Algorithm 3)")
        print("   • Turkish NER model integration")
        print("   • Rule-based and ML-based parsing methods")
        print("   • Performance testing and validation")
        print("   • Integration with AddressValidator and AddressCorrector")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)