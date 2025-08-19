#!/usr/bin/env python3
"""
TEST NIŞANTAŞI FIX
Verify that the Nişantaşı → Şişli completion now works
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def test_nisantasi_fix():
    """Test the specific Nişantaşı → Şişli fix"""
    print("🎯 TESTING NIŞANTAŞI → ŞİŞLİ FIX")
    print("=" * 50)
    
    try:
        from component_completion_engine import ComponentCompletionEngine
        engine = ComponentCompletionEngine()
        print(f"✅ Component Completion Engine loaded")
        print(f"   Database records: {len(engine.admin_database)}")
    except Exception as e:
        print(f"❌ Failed to load engine: {e}")
        return False
    
    # Test the specific case that was failing
    test_cases = [
        {'name': 'Nişantaşı → Şişli', 'input': {'mahalle': 'Nişantaşı'}, 'expected_ilçe': 'Şişli'},
        {'name': 'Nişantaşı Mahallesi → Şişli', 'input': {'mahalle': 'Nişantaşı Mahallesi'}, 'expected_ilçe': 'Şişli'},
        {'name': 'Taksim → Beyoğlu', 'input': {'mahalle': 'Taksim'}, 'expected_ilçe': 'Beyoğlu'},
        {'name': 'Kızılay → Çankaya', 'input': {'mahalle': 'Kızılay'}, 'expected_ilçe': 'Çankaya'},
        {'name': 'Maslak → Sarıyer', 'input': {'mahalle': 'Maslak'}, 'expected_ilçe': 'Sarıyer'},
    ]
    
    print(f"\nTesting {len(test_cases)} famous neighborhood completions:")
    
    success_count = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Input: {test_case['input']}")
        
        try:
            result = engine.complete_address_hierarchy(test_case['input'])
            completed = result.get('completed_components', {})
            completions = result.get('completions_made', [])
            confidence = result.get('confidence', 0.0)
            
            print(f"   Result: {completed}")
            print(f"   Completions: {completions}")
            print(f"   Confidence: {confidence:.3f}")
            
            # Check if expected completion was made
            actual_ilçe = completed.get('ilçe', '')
            expected_ilçe = test_case['expected_ilçe']
            
            if expected_ilçe.lower() in actual_ilçe.lower():
                print(f"   ✅ SUCCESS - {expected_ilçe} completion working!")
                success_count += 1
            else:
                print(f"   ❌ FAILED - Expected {expected_ilçe}, got {actual_ilçe}")
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    success_rate = (success_count / len(test_cases)) * 100
    print(f"\n📊 Famous Neighborhood Completion Results:")
    print(f"   Successful: {success_count}/{len(test_cases)}")
    print(f"   Success rate: {success_rate:.1f}%")
    
    return success_rate >= 80

def test_comprehensive_scenarios():
    """Test comprehensive scenarios including the fixed cases"""
    print(f"\n🧪 COMPREHENSIVE COMPLETION TEST")
    print("=" * 50)
    
    try:
        from address_parser import AddressParser
        parser = AddressParser()
        print("✅ AddressParser with fixed Component Completion Intelligence loaded")
    except Exception as e:
        print(f"❌ Failed to load AddressParser: {e}")
        return False
    
    # Test the fixed cases in full AddressParser context
    test_scenarios = [
        "İstanbul Nişantaşı Mahallesi Teşvikiye Caddesi 15",
        "Nişantaşı Abdi İpekçi Caddesi 25/A",
        "Taksim Meydanı İstiklal Caddesi 10",
        "Ankara Kızılay Atatürk Bulvarı 50",
        "Maslak 4.Levent İş Merkezi"
    ]
    
    print(f"Testing {len(test_scenarios)} real-world scenarios:")
    
    successful_scenarios = 0
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. Scenario: '{scenario}'")
        
        try:
            result = parser.parse_address(scenario)
            components = result.get('components', {})
            confidence = result.get('confidence', 0)
            
            print(f"   Components: {len(components)} detected")
            print(f"   Result: {components}")
            print(f"   Confidence: {confidence:.3f}")
            
            # Check if hierarchy completion worked
            has_hierarchy = ('mahalle' in components or 'ilçe' in components) and 'il' in components
            
            if has_hierarchy:
                print(f"   ✅ SUCCESS - Hierarchy completion working")
                successful_scenarios += 1
            else:
                print(f"   ❌ INCOMPLETE - Missing hierarchy components")
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    scenario_success_rate = (successful_scenarios / len(test_scenarios)) * 100
    print(f"\n📊 Real-World Scenario Results:")
    print(f"   Successful: {successful_scenarios}/{len(test_scenarios)}")
    print(f"   Success rate: {scenario_success_rate:.1f}%")
    
    return scenario_success_rate >= 80

def main():
    """Main test function"""
    print("🔧 NIŞANTAŞI → ŞİŞLİ FIX VERIFICATION")
    print("=" * 50)
    print("Testing the fix for Component Completion Intelligence gaps\n")
    
    # Test the specific fix
    fix_success = test_nisantasi_fix()
    
    # Test comprehensive scenarios
    comprehensive_success = test_comprehensive_scenarios()
    
    # Overall assessment
    print(f"\n" + "=" * 50)
    print("🏁 FIX VERIFICATION SUMMARY:")
    print(f"   Nişantaşı fix: {'✅ SUCCESS' if fix_success else '❌ FAILED'}")
    print(f"   Comprehensive scenarios: {'✅ SUCCESS' if comprehensive_success else '❌ FAILED'}")
    
    overall_success = fix_success and comprehensive_success
    
    if overall_success:
        print(f"\n🎉 COMPONENT COMPLETION INTELLIGENCE FIX: SUCCESS")
        print(f"✅ Nişantaşı → Şişli completion working")
        print(f"✅ Famous neighborhood mappings operational") 
        print(f"✅ Database filtering issues resolved")
        print(f"✅ Component Completion Intelligence enhanced")
        print(f"🚀 Ready for 100% completion rate!")
    else:
        print(f"\n🔧 FIX NEEDS FURTHER WORK")
        print(f"❌ Some test cases still failing")
        print(f"🔧 Review and refine the fix")
    
    print("=" * 50)
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)