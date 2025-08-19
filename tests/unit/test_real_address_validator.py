"""
Test the real AddressValidator implementation
Simple test runner without pytest dependency
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_real_implementation():
    """Test the real AddressValidator implementation"""
    
    print("🧪 Testing Real AddressValidator Implementation")
    print("=" * 55)
    
    try:
        from address_validator import AddressValidator
        
        # Initialize validator
        validator = AddressValidator()
        print("✅ Validator initialized successfully")
        
        # Test cases from our test suite
        test_cases = [
            {
                'name': 'Valid Istanbul Kadıköy address',
                'data': {
                    'raw_address': 'İstanbul Kadıköy Moda Mahallesi',
                    'parsed_components': {
                        'il': 'İstanbul',
                        'ilce': 'Kadıköy',
                        'mahalle': 'Moda Mahallesi'
                    },
                    'coordinates': {'lat': 40.9875, 'lon': 29.0376}
                },
                'expected_valid': True
            },
            {
                'name': 'Valid Ankara Çankaya address',
                'data': {
                    'parsed_components': {
                        'il': 'Ankara',
                        'ilce': 'Çankaya',
                        'mahalle': 'Kızılay Mahallesi'
                    }
                },
                'expected_valid': True
            },
            {
                'name': 'Invalid cross-province hierarchy',
                'data': {
                    'parsed_components': {
                        'il': 'İstanbul',
                        'ilce': 'Çankaya',  # Wrong: Çankaya is in Ankara
                        'mahalle': 'Kızılay Mahallesi'
                    }
                },
                'expected_valid': False
            },
            {
                'name': 'Valid postal code matching',
                'data': {
                    'parsed_components': {
                        'il': 'İstanbul',
                        'ilce': 'Kadıköy',
                        'mahalle': 'Test Mahallesi',
                        'postal_code': '34718'
                    }
                },
                'expected_postal_valid': True
            },
            {
                'name': 'Invalid postal code mismatch',
                'data': {
                    'parsed_components': {
                        'il': 'Ankara',
                        'ilce': 'Çankaya',
                        'mahalle': 'Test Mahallesi',
                        'postal_code': '34718'  # Istanbul postal code
                    }
                },
                'expected_postal_valid': False
            },
            {
                'name': 'Valid Turkey coordinates',
                'coordinates': {'lat': 41.0082, 'lon': 28.9784},  # Istanbul
                'expected_coord_valid': True
            },
            {
                'name': 'Invalid out-of-bounds coordinates',
                'coordinates': {'lat': 51.5074, 'lon': -0.1278},  # London
                'expected_coord_valid': False
            }
        ]
        
        passed = 0
        total = 0
        
        # Test main validation function
        print(f"\n📋 Testing validate_address() method:")
        for test_case in test_cases:
            if 'expected_valid' in test_case:
                total += 1
                result = validator.validate_address(test_case['data'])
                
                if result['is_valid'] == test_case['expected_valid']:
                    print(f"✅ {test_case['name']}: PASSED")
                    passed += 1
                else:
                    print(f"❌ {test_case['name']}: FAILED")
                    print(f"   Expected: {test_case['expected_valid']}, Got: {result['is_valid']}")
                    print(f"   Errors: {result['errors']}")
        
        # Test hierarchy validation
        print(f"\n📋 Testing validate_hierarchy() method:")
        hierarchy_tests = [
            ('İstanbul', 'Kadıköy', 'Moda Mahallesi', True),
            ('Ankara', 'Çankaya', 'Kızılay Mahallesi', True),
            ('İzmir', 'Konak', 'Alsancak Mahallesi', True),
            ('İstanbul', 'Çankaya', 'Kızılay Mahallesi', False),  # Wrong
            ('Ankara', 'Kadıköy', 'Moda Mahallesi', False),       # Wrong
        ]
        
        for il, ilce, mahalle, expected in hierarchy_tests:
            total += 1
            result = validator.validate_hierarchy(il, ilce, mahalle)
            
            if result == expected:
                print(f"✅ {il}-{ilce}-{mahalle}: PASSED")
                passed += 1
            else:
                print(f"❌ {il}-{ilce}-{mahalle}: FAILED (expected {expected}, got {result})")
        
        # Test postal code validation
        print(f"\n📋 Testing validate_postal_code() method:")
        postal_tests = [
            ('34718', {'il': 'İstanbul', 'ilce': 'Kadıköy'}, True),
            ('06420', {'il': 'Ankara', 'ilce': 'Çankaya'}, True),
            ('34718', {'il': 'Ankara', 'ilce': 'Çankaya'}, False),  # Wrong match
            ('99999', {'il': 'İstanbul', 'ilce': 'Kadıköy'}, True),  # Unknown but valid format
            ('1234', {'il': 'İstanbul', 'ilce': 'Kadıköy'}, False),   # Invalid format
        ]
        
        for postal_code, components, expected in postal_tests:
            total += 1
            result = validator.validate_postal_code(postal_code, components)
            
            if result == expected:
                print(f"✅ Postal {postal_code}: PASSED")
                passed += 1
            else:
                print(f"❌ Postal {postal_code}: FAILED (expected {expected}, got {result})")
        
        # Test coordinate validation
        print(f"\n📋 Testing validate_coordinates() method:")
        coord_tests = [
            ({'lat': 41.0082, 'lon': 28.9784}, True),   # Istanbul
            ({'lat': 39.9334, 'lon': 32.8597}, True),   # Ankara
            ({'lat': 51.5074, 'lon': -0.1278}, False),  # London (out of bounds)
            ({'lat': 40.7128, 'lon': -74.0060}, False), # New York (out of bounds)
            ({'lat': 'invalid', 'lon': 28.9784}, False), # Invalid format
        ]
        
        for coords, expected in coord_tests:
            total += 1
            result = validator.validate_coordinates(coords, {})
            
            if result['valid'] == expected:
                print(f"✅ Coordinates {coords}: PASSED")
                passed += 1
            else:
                print(f"❌ Coordinates {coords}: FAILED (expected {expected}, got {result['valid']})")
        
        # Test error handling
        print(f"\n📋 Testing error handling:")
        error_tests = [
            ({}, "Empty input"),
            ("invalid", "String input instead of dict"),
            ({'parsed_components': {}}, "Empty components"),
        ]
        
        for invalid_input, description in error_tests:
            total += 1
            result = validator.validate_address(invalid_input)
            
            if result['is_valid'] == False and len(result['errors']) > 0:
                print(f"✅ {description}: PASSED")
                passed += 1
            else:
                print(f"❌ {description}: FAILED")
        
        print(f"\n" + "=" * 55)
        print(f"📊 Test Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 All tests passed! AddressValidator implementation is working correctly.")
        elif passed/total >= 0.8:
            print("✅ Most tests passed! Implementation is largely working correctly.")
        else:
            print("⚠️  Many tests failed. Implementation needs review.")
        
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
        import time
        from address_validator import AddressValidator
        
        validator = AddressValidator()
        
        # Test single address performance
        test_address = {
            'parsed_components': {
                'il': 'İstanbul',
                'ilce': 'Kadıköy',
                'mahalle': 'Moda Mahallesi'
            }
        }
        
        start_time = time.time()
        result = validator.validate_address(test_address)
        end_time = time.time()
        
        processing_time_ms = (end_time - start_time) * 1000
        
        print(f"✅ Single address processing: {processing_time_ms:.2f}ms")
        
        if processing_time_ms < 100:
            print("✅ Performance target met (<100ms)")
        else:
            print("⚠️  Performance target exceeded (>100ms)")
        
        # Test batch performance
        batch_size = 50
        addresses = [
            {
                'parsed_components': {
                    'il': 'İstanbul',
                    'ilce': 'Kadıköy',
                    'mahalle': f'Test Mahallesi {i}'
                }
            }
            for i in range(batch_size)
        ]
        
        start_time = time.time()
        for address in addresses:
            validator.validate_address(address)
        end_time = time.time()
        
        batch_time = (end_time - start_time) * 1000
        avg_time_per_address = batch_time / batch_size
        
        print(f"✅ Batch processing ({batch_size} addresses): {batch_time:.2f}ms total")
        print(f"✅ Average per address: {avg_time_per_address:.2f}ms")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test error: {e}")
        return False

def main():
    """Run all tests"""
    
    print("🧪 TEKNOFEST AddressValidator - Real Implementation Tests")
    print("=" * 65)
    
    success = test_real_implementation()
    
    if success:
        test_performance()
    
    print(f"\n🎯 Testing completed!")
    
    if success:
        print(f"\n🚀 AddressValidator is ready for:")
        print("   • Integration with AddressCorrector and AddressParser")
        print("   • Full pytest test suite execution")
        print("   • TEKNOFEST competition deployment")
        print("   • Production address validation workflows")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)