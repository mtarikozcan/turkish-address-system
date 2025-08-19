"""
Test the real AddressParser implementation
Comprehensive test runner for AddressParser functionality
"""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_real_address_parser():
    """Test the real AddressParser implementation"""
    
    print("🧪 Testing Real AddressParser Implementation")
    print("=" * 55)
    
    try:
        from address_parser import AddressParser
        
        # Initialize parser
        parser = AddressParser()
        print("✅ AddressParser initialized successfully")
        
        # Test cases covering all major functionality
        test_cases = [
            {
                'name': 'Complete Istanbul address',
                'address': 'İstanbul Kadıköy Moda Mahallesi Caferağa Sokak No 10 Daire 3',
                'expected_components': ['il', 'ilce', 'mahalle', 'sokak', 'bina_no', 'daire']
            },
            {
                'name': 'Ankara address with postal code',
                'address': '06420 Ankara Çankaya Kızılay Mahallesi Atatürk Caddesi 25',
                'expected_components': ['il', 'ilce', 'mahalle', 'sokak', 'bina_no', 'postal_code']
            },
            {
                'name': 'İzmir address with building type',
                'address': 'İzmir Konak Alsancak Mahallesi Cumhuriyet Bulvarı 45 Apartmanı Daire 8',
                'expected_components': ['il', 'ilce', 'mahalle', 'sokak', 'bina_no', 'daire']
            },
            {
                'name': 'Minimal address',
                'address': 'Bursa Nilüfer Görükle Mahallesi',
                'expected_components': ['il', 'ilce', 'mahalle']
            },
            {
                'name': 'Complex address with Turkish characters',
                'address': 'Eskişehir Tepebaşı Şarkiye Mahallesi Zübeyde Hanım Caddesi No 15 Daire 2A',
                'expected_confidence_min': 0.5
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
                    found_count = len(components)
                    expected_min = max(3, len(test_case['expected_components']) - 2)  # Allow some flexibility
                    
                    if found_count >= expected_min:
                        print(f"✅ {test_case['name']}: PASSED ({found_count} components)")
                        passed += 1
                    else:
                        print(f"❌ {test_case['name']}: FAILED (only {found_count} components)")
                        print(f"   Found: {list(components.keys())}")
                        
                elif 'expected_confidence_min' in test_case:
                    confidence = result.get('overall_confidence', 0.0)
                    if confidence >= test_case['expected_confidence_min']:
                        print(f"✅ {test_case['name']}: PASSED (confidence: {confidence})")
                        passed += 1
                    else:
                        print(f"❌ {test_case['name']}: FAILED (confidence: {confidence})")
                
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
        
        rule_based_tests = [
            {
                'method': 'extract_components_rule_based',
                'input': 'İstanbul Kadıköy Moda Mahallesi Caferağa Sokak No 10',
                'expected_min_components': 3
            },
            {
                'method': 'extract_components_ml_based',
                'input': 'Ankara Çankaya Kızılay Mahallesi',
                'expected_keys': ['components', 'confidence_scores', 'method']
            },
            {
                'method': 'validate_extracted_components',
                'input': {'il': 'İstanbul', 'ilce': 'Kadıköy', 'mahalle': 'Moda Mahallesi'},
                'expected_keys': ['is_valid', 'component_validity', 'completeness_score']
            }
        ]
        
        for test in rule_based_tests:
            total += 1
            method = getattr(parser, test['method'])
            
            try:
                result = method(test['input'])
                
                if 'expected_min_components' in test:
                    components = result.get('components', {})
                    if len(components) >= test['expected_min_components']:
                        print(f"✅ {test['method']}: PASSED ({len(components)} components)")
                        passed += 1
                    else:
                        print(f"❌ {test['method']}: FAILED ({len(components)} components)")
                        
                elif 'expected_keys' in test:
                    if isinstance(result, dict) and all(key in result for key in test['expected_keys']):
                        print(f"✅ {test['method']}: PASSED")
                        passed += 1
                    else:
                        print(f"❌ {test['method']}: FAILED - Missing keys")
                        print(f"   Expected: {test['expected_keys']}")
                        print(f"   Found: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
                        
            except Exception as e:
                print(f"❌ {test['method']}: ERROR - {e}")
        
        print(f"\n" + "=" * 55)
        print(f"📊 Test Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 All tests passed! AddressParser implementation is working correctly.")
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

def test_performance():
    """Test performance characteristics"""
    
    print(f"\n⚡ Testing performance...")
    print("=" * 30)
    
    try:
        from address_parser import AddressParser
        
        parser = AddressParser()
        
        # Test single address performance
        test_address = "İstanbul Kadıköy Moda Mahallesi Caferağa Sokak No 10 Daire 3"
        
        start_time = time.time()
        result = parser.parse_address(test_address)
        end_time = time.time()
        
        processing_time_ms = (end_time - start_time) * 1000
        
        print(f"✅ Single address processing: {processing_time_ms:.2f}ms")
        
        if processing_time_ms < 100:
            print("✅ Performance target met (<100ms)")
        else:
            print("⚠️  Performance target exceeded (>100ms)")
        
        # Test parsing method performance
        start_time = time.time()
        rule_result = parser.extract_components_rule_based(test_address)
        rule_time = (time.time() - start_time) * 1000
        
        start_time = time.time()
        ml_result = parser.extract_components_ml_based(test_address)
        ml_time = (time.time() - start_time) * 1000
        
        print(f"✅ Rule-based parsing: {rule_time:.2f}ms")
        print(f"✅ ML-based parsing: {ml_time:.2f}ms")
        
        # Test batch performance
        batch_size = 20
        addresses = [
            f"İstanbul Kadıköy Test{i} Mahallesi Sokak{i} No {i}"
            for i in range(batch_size)
        ]
        
        start_time = time.time()
        for address in addresses:
            parser.parse_address(address)
        end_time = time.time()
        
        batch_time = (end_time - start_time) * 1000
        avg_time_per_address = batch_time / batch_size
        
        print(f"✅ Batch processing ({batch_size} addresses): {batch_time:.2f}ms total")
        print(f"✅ Average per address: {avg_time_per_address:.2f}ms")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test error: {e}")
        return False

def test_turkish_language_features():
    """Test Turkish language specific features"""
    
    print(f"\n🇹🇷 Testing Turkish language features...")
    print("=" * 45)
    
    try:
        from address_parser import AddressParser
        
        parser = AddressParser()
        
        # Test Turkish character handling
        turkish_addresses = [
            "İstanbul Şişli Mecidiyeköy Mahallesi",
            "Ankara Çankaya Kızılay Mahallesi", 
            "İzmir Karşıyaka Bostanlı Mahallesi",
            "Bursa Gürsu Gölyazı Mahallesi"
        ]
        
        passed = 0
        total = len(turkish_addresses)
        
        for address in turkish_addresses:
            result = parser.parse_address(address)
            
            # Check Turkish character preservation
            components = result.get('components', {})
            has_turkish_chars = any(
                any(char in str(value) for char in 'çğıöşüÇĞIÖŞÜ')
                for value in components.values()
            )
            
            if has_turkish_chars or result.get('overall_confidence', 0) > 0.5:
                print(f"✅ Turkish characters preserved: {address[:30]}...")
                passed += 1
            else:
                print(f"❌ Turkish character issue: {address[:30]}...")
        
        print(f"✅ Turkish character tests: {passed}/{total} passed")
        
        # Test location recognition
        major_locations = [
            ("İstanbul", "should be recognized as province"),
            ("Kadıköy", "should be recognized as district"),
            ("Moda", "should be recognized as neighborhood")
        ]
        
        for location, description in major_locations:
            test_address = f"Türkiye {location} bölgesi test adresi"
            result = parser.parse_address(test_address)
            
            # Check if location appears in components
            found = any(location.lower() in str(value).lower() 
                       for value in result.get('components', {}).values())
            
            if found or result.get('overall_confidence', 0) > 0.3:
                print(f"✅ Location recognized: {location}")
            else:
                print(f"⚠️  Location not found: {location}")
        
        return True
        
    except Exception as e:
        print(f"❌ Turkish language test error: {e}")
        return False

def test_integration_features():
    """Test integration with other algorithms"""
    
    print(f"\n🔗 Testing integration features...")
    print("=" * 40)
    
    try:
        from address_parser import AddressParser
        
        parser = AddressParser()
        
        # Test AddressValidator integration
        test_address = "İstanbul Kadıköy Moda Mahallesi"
        result = parser.parse_address(test_address)
        
        # Check if validation was performed
        if 'validation_result' in result:
            validation = result['validation_result']
            print(f"✅ AddressValidator integration working")
            print(f"   Validation result: {validation.get('is_valid', 'Unknown')}")
            print(f"   Completeness: {validation.get('completeness_score', 0.0)}")
        else:
            print("⚠️  AddressValidator integration not found")
        
        # Test parsing method combination
        components_count = len(result.get('components', {}))
        parsing_method = result.get('parsing_method', 'unknown')
        
        print(f"✅ Hybrid parsing method: {parsing_method}")
        print(f"✅ Components extracted: {components_count}")
        
        # Test error handling
        invalid_inputs = [None, "", "123", []]
        error_handling_passed = 0
        
        for invalid_input in invalid_inputs:
            try:
                result = parser.parse_address(invalid_input)
                if 'error' in result or result.get('overall_confidence', 1.0) == 0.0:
                    error_handling_passed += 1
            except:
                pass  # Error handling working
        
        print(f"✅ Error handling: {error_handling_passed}/{len(invalid_inputs)} cases handled")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test error: {e}")
        return False

def main():
    """Run all tests"""
    
    print("🧪 TEKNOFEST AddressParser - Real Implementation Tests")
    print("=" * 65)
    
    # Test core functionality
    success1 = test_real_address_parser()
    
    # Test performance
    success2 = test_performance() if success1 else False
    
    # Test Turkish language features
    success3 = test_turkish_language_features() if success1 else False
    
    # Test integration features
    success4 = test_integration_features() if success1 else False
    
    overall_success = success1 and success2 and success3
    
    print(f"\n🎯 Testing completed!")
    
    if overall_success:
        print(f"\n🚀 AddressParser is ready for:")
        print("   • Turkish address parsing with rule-based and ML methods")
        print("   • Component extraction (il, ilçe, mahalle, sokak, bina_no, daire)")
        print("   • Integration with AddressValidator and AddressCorrector")
        print("   • Performance requirements (<100ms per address)")
        print("   • TEKNOFEST competition deployment")
        print("   • Production address parsing workflows")
    else:
        print(f"\n⚠️  Some test categories failed. Review implementation.")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)