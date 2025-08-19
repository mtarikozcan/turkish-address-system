#!/usr/bin/env python3
"""
DEFINITIVE VERIFICATION TEST for GeographicIntelligence Integration
Run this script to verify that the system correctly detects il/ilçe components

Expected Result: SUCCESS for all test cases
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def test_direct_geographic_intelligence():
    """Test GeographicIntelligence directly"""
    print("🔍 TESTING GEOGRAPHIC INTELLIGENCE DIRECTLY")
    print("=" * 60)
    
    try:
        from geographic_intelligence import GeographicIntelligence
        geo = GeographicIntelligence()
        
        test_input = "Etlik Mahallesi Süleymaniye Caddesi 231.sk No3 / 12 Keçiören Ankara"
        print(f"Input: {test_input}")
        
        result = geo.detect_geographic_anchors(test_input)
        components = result.get('components', {})
        
        print(f"Result: {components}")
        print(f"Confidence: {result.get('confidence', 0):.3f}")
        
        success = 'il' in components and 'ilçe' in components
        print(f"Status: {'✅ SUCCESS' if success else '❌ FAILED'}")
        
        if success:
            print(f"   il = '{components['il']}'")
            print(f"   ilçe = '{components['ilçe']}'")
        
        return success
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_address_parser_integration():
    """Test through AddressParser integration"""
    print("\n🔗 TESTING ADDRESSPARSER INTEGRATION")
    print("=" * 60)
    
    try:
        from address_parser import AddressParser
        parser = AddressParser()
        
        test_input = "Etlik Mahallesi Süleymaniye Caddesi 231.sk No3 / 12 Keçiören Ankara"
        print(f"Input: {test_input}")
        
        result = parser.parse_address(test_input)
        components = result.get('components', {})
        
        print(f"Result: {components}")
        print(f"Confidence: {result.get('confidence', 0):.3f}")
        
        success = 'il' in components and 'ilçe' in components
        print(f"Status: {'✅ SUCCESS' if success else '❌ FAILED'}")
        
        if success:
            print(f"   il = '{components['il']}'")
            print(f"   ilçe = '{components['ilçe']}'")
        
        return success
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_multiple_cases():
    """Test multiple address patterns"""
    print("\n🧪 TESTING MULTIPLE PATTERNS")
    print("=" * 60)
    
    try:
        from address_parser import AddressParser
        parser = AddressParser()
        
        test_cases = [
            "keçiören ankara",
            "Keçiören Ankara", 
            "istanbul kadıköy",
            "çankaya ankara",
            "moda mahallesi istanbul"
        ]
        
        success_count = 0
        
        for i, test_input in enumerate(test_cases, 1):
            print(f"\n{i}. {test_input}")
            
            result = parser.parse_address(test_input)
            components = result.get('components', {})
            
            has_il = 'il' in components and components['il']
            has_ilce = 'ilçe' in components and components['ilçe']
            
            print(f"   Components: {components}")
            print(f"   il: {'✓' if has_il else '✗'}")
            print(f"   ilçe: {'✓' if has_ilce else '✗'}")
            
            if has_il and has_ilce:
                success_count += 1
                print(f"   Status: ✅ SUCCESS")
            else:
                print(f"   Status: ❌ FAILED")
        
        print(f"\nOverall: {success_count}/{len(test_cases)} successful")
        return success_count == len(test_cases)
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    """Run all verification tests"""
    print("🚀 GEOGRAPHIC INTELLIGENCE VERIFICATION TEST")
    print("=" * 60)
    print("This script verifies that GeographicIntelligence correctly detects")
    print("il/ilçe components in Turkish addresses.\n")
    
    # Run tests
    test1 = test_direct_geographic_intelligence()
    test2 = test_address_parser_integration()  
    test3 = test_multiple_cases()
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 FINAL VERIFICATION RESULTS:")
    print(f"   Direct GeographicIntelligence: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"   AddressParser Integration: {'✅ PASS' if test2 else '❌ FAIL'}")
    print(f"   Multiple Pattern Tests: {'✅ PASS' if test3 else '❌ FAIL'}")
    
    overall_success = test1 and test2 and test3
    
    print("\n" + "=" * 60)
    if overall_success:
        print("🎉 ALL TESTS PASSED!")
        print("GeographicIntelligence is working correctly.")
        print("The system successfully detects il/ilçe components.")
    else:
        print("❌ SOME TESTS FAILED!")
        print("There may be an issue with your installation or environment.")
        print("Check the error messages above for details.")
    
    print("=" * 60)
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)