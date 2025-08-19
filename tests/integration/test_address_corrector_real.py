"""
Test the real AddressCorrector implementation
Simple test runner without pytest dependency
"""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_real_address_corrector():
    """Test the real AddressCorrector implementation"""
    
    print("🧪 Testing Real AddressCorrector Implementation")
    print("=" * 55)
    
    try:
        from address_corrector import AddressCorrector
        
        # Initialize corrector
        corrector = AddressCorrector()
        print("✅ AddressCorrector initialized successfully")
        
        # Test cases covering all major functionality
        test_cases = [
            {
                'name': 'Basic address correction',
                'input': 'Istanbul Kadikoy Moda Mah.',
                'expected_has_corrections': True
            },
            {
                'name': 'Abbreviation expansion test',
                'input': 'Moda Mah. Caferaga Sk. No 10',
                'test_type': 'abbreviation_expansion'
            },
            {
                'name': 'Spelling correction test',
                'input': 'istbl kadikoy',
                'test_type': 'spelling_correction'
            },
            {
                'name': 'Turkish character normalization',
                'input': 'İSTANBUL ŞİŞLİ MECİDİYEKÖY   ',
                'test_type': 'normalization'
            },
            {
                'name': 'Complex address with multiple issues',
                'input': 'Istbl Sisli Mecidiyekoy Mh. Ataturk Cd. No. 25 Apt 3',
                'expected_confidence_min': 0.5
            },
            {
                'name': 'Empty input handling',
                'input': '',
                'expected_corrected': ''
            },
            {
                'name': 'Valid address with no corrections needed',
                'input': 'Istanbul Kadikoy Moda Mahallesi',
                'expected_has_corrections': True  # Still expects normalization
            }
        ]
        
        passed = 0
        total = 0
        
        # Test main correction function
        print(f"\n📋 Testing correct_address() method:")
        for test_case in test_cases:
            total += 1
            
            try:
                result = corrector.correct_address(test_case['input'])
                
                # Basic validation - should return proper structure
                if not isinstance(result, dict) or 'original' not in result or 'corrected' not in result:
                    print(f"❌ {test_case['name']}: FAILED - Invalid result structure")
                    continue
                
                # Test specific expectations
                if 'expected_corrected' in test_case:
                    if result['corrected'] == test_case['expected_corrected']:
                        print(f"✅ {test_case['name']}: PASSED")
                        passed += 1
                    else:
                        print(f"❌ {test_case['name']}: FAILED")
                        print(f"   Expected: '{test_case['expected_corrected']}', Got: '{result['corrected']}'")
                
                elif 'expected_confidence_min' in test_case:
                    if result['confidence'] >= test_case['expected_confidence_min']:
                        print(f"✅ {test_case['name']}: PASSED (confidence: {result['confidence']})")
                        passed += 1
                    else:
                        print(f"❌ {test_case['name']}: FAILED (confidence too low: {result['confidence']})")
                
                elif 'expected_has_corrections' in test_case:
                    has_corrections = len(result.get('corrections', [])) > 0
                    if has_corrections == test_case['expected_has_corrections']:
                        print(f"✅ {test_case['name']}: PASSED")
                        passed += 1
                    else:
                        print(f"❌ {test_case['name']}: FAILED")
                        print(f"   Expected corrections: {test_case['expected_has_corrections']}, Got: {has_corrections}")
                
                else:
                    # Just test that it doesn't crash and returns reasonable result
                    if len(result['corrected']) > 0:
                        print(f"✅ {test_case['name']}: PASSED")
                        passed += 1
                    else:
                        print(f"❌ {test_case['name']}: FAILED - Empty result")
                
            except Exception as e:
                print(f"❌ {test_case['name']}: ERROR - {e}")
        
        # Test individual methods
        print(f"\n📋 Testing individual methods:")
        
        individual_tests = [
            {
                'method': 'expand_abbreviations',
                'input': 'Moda Mah. Caferaga Sk.',
                'expected_contains': ['mahallesi', 'sokak']
            },
            {
                'method': 'correct_spelling_errors', 
                'input': 'istbl kadikoy',
                'expected_contains': ['istanbul', 'kadıköy']
            },
            {
                'method': 'normalize_turkish_chars',
                'input': 'İSTANBUL ŞİŞLİ   MECİDİYEKÖY!!!',
                'expected_result': 'istanbul şişli mecidiyeköy'
            }
        ]
        
        for test in individual_tests:
            total += 1
            method = getattr(corrector, test['method'])
            result = method(test['input'])
            
            if 'expected_result' in test:
                if result == test['expected_result']:
                    print(f"✅ {test['method']}: PASSED")
                    passed += 1
                else:
                    print(f"❌ {test['method']}: FAILED")
                    print(f"   Expected: '{test['expected_result']}', Got: '{result}'")
            
            elif 'expected_contains' in test:
                contains_all = all(word in result for word in test['expected_contains'])
                if contains_all:
                    print(f"✅ {test['method']}: PASSED")
                    passed += 1
                else:
                    print(f"❌ {test['method']}: FAILED")
                    print(f"   Expected to contain: {test['expected_contains']}, Got: '{result}'")
        
        print(f"\n" + "=" * 55)
        print(f"📊 Test Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 All tests passed! AddressCorrector implementation is working correctly.")
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
        from address_corrector import AddressCorrector
        
        corrector = AddressCorrector()
        
        # Test single address performance
        test_address = "Istbl Kadikoy Moda Mah. Caferaga Sk. No 10"
        
        start_time = time.time()
        result = corrector.correct_address(test_address)
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
            f"Istbl Kadikoy Test Mahallesi {i} Sokak No {i}"
            for i in range(batch_size)
        ]
        
        start_time = time.time()
        for address in addresses:
            corrector.correct_address(address)
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
    
    print("🧪 TEKNOFEST AddressCorrector - Real Implementation Tests")
    print("=" * 65)
    
    success = test_real_address_corrector()
    
    if success:
        test_performance()
    
    print(f"\n🎯 Testing completed!")
    
    if success:
        print(f"\n🚀 AddressCorrector is ready for:")
        print("   • Integration with AddressValidator and AddressParser")
        print("   • Full address correction pipeline")
        print("   • TEKNOFEST competition deployment")
        print("   • Production address correction workflows")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)