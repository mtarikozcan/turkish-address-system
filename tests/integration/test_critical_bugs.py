#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRITICAL BUG ISOLATION TEST
Isolate and verify the exact component overwriting and confidence issues
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from address_parser import AddressParser

def test_critical_bugs():
    """Test the specific critical bugs identified"""
    
    print("🚨 CRITICAL BUG ISOLATION TEST")
    print("=" * 60)
    
    parser = AddressParser()
    
    critical_test_cases = [
        {
            "bug": "MAHALLE OVERWRITING BUG",
            "address": "istanbul kadikoy moda",
            "expected": {
                "il": "İstanbul",
                "ilce": "Kadıköy", 
                "mahalle": "Moda"
            },
            "issue": "mahalle should be 'Moda' not 'Kadıköy'"
        },
        {
            "bug": "SYSTEMATIC COMPONENT CONFUSION - Case 1",
            "address": "ankara cankaya kizilay",
            "expected": {
                "il": "Ankara",
                "ilce": "Çankaya",
                "mahalle": "Kızılay"
            },
            "issue": "mahalle should be 'Kızılay' not 'Çankaya'"
        },
        {
            "bug": "SYSTEMATIC COMPONENT CONFUSION - Case 2", 
            "address": "bursa osmangazi emek",
            "expected": {
                "il": "Bursa",
                "ilce": "Osmangazi",
                "mahalle": "Emek"
            },
            "issue": "mahalle should be 'Emek' not 'Osmangazi'"
        },
        {
            "bug": "STREET CONTAMINATION",
            "address": "istanbul moda bagdat caddesi",
            "expected": {
                "il": "İstanbul",
                "mahalle": "Moda",
                "sokak": "Bağdat Caddesi"
            },
            "issue": "sokak should be clean 'Bağdat Caddesi' without city/neighborhood"
        }
    ]
    
    print("Testing component extraction order and overwriting issues...")
    
    for i, test_case in enumerate(critical_test_cases, 1):
        bug = test_case["bug"]
        address = test_case["address"]
        expected = test_case["expected"]
        issue = test_case["issue"]
        
        print(f"\n🐛 Bug Test {i}: {bug}")
        print(f"   Address: {address}")
        print(f"   Issue: {issue}")
        print(f"   Expected: {expected}")
        
        # Parse and analyze
        result = parser.parse_address(address)
        components = result.get('components', {})
        confidence = result.get('confidence', 0)
        
        print(f"   📍 Actual: {components}")
        print(f"   🎯 Confidence: {confidence:.2f}")
        
        # Check each expected component
        bugs_found = []
        for component, expected_value in expected.items():
            actual_value = components.get(component)
            
            if actual_value is None:
                bugs_found.append(f"Missing {component}")
            elif actual_value != expected_value:
                bugs_found.append(f"{component}: got '{actual_value}', expected '{expected_value}'")
            else:
                print(f"   ✅ {component}: {actual_value} (correct)")
        
        if bugs_found:
            print(f"   🚨 BUGS CONFIRMED: {', '.join(bugs_found)}")
            
            # Check if this is component overwriting (wrong component in wrong field)
            all_values = set(components.values())
            expected_values = set(expected.values())
            
            for expected_val in expected_values:
                if expected_val in all_values:
                    # Find where the expected value ended up
                    for comp, val in components.items():
                        if val == expected_val and comp not in expected:
                            print(f"   🔄 OVERWRITING: '{expected_val}' in wrong field '{comp}'")
        else:
            print(f"   ✅ No bugs found in this case")
        
        # Confidence accuracy check
        correct_components = sum(1 for comp, exp_val in expected.items() 
                                if components.get(comp) == exp_val)
        expected_accuracy = correct_components / len(expected)
        
        if confidence > 0.9 and expected_accuracy < 0.7:
            print(f"   🚨 FALSE CONFIDENCE: {confidence:.2f} confidence but only {expected_accuracy*100:.1f}% accurate")
        
        print("-" * 50)
    
    print("\n🔍 COMPONENT EXTRACTION ORDER ANALYSIS:")
    
    # Test extraction order with detailed logging
    test_address = "istanbul kadikoy moda"
    print(f"\n   Analyzing: {test_address}")
    
    # This would require adding debug logging to the parser to see the order
    result = parser.extract_components_rule_based(test_address)
    components = result.get('components', {})
    
    print(f"   Rule-based result: {components}")
    
    if 'mahalle' in components and 'ilce' in components:
        if components['mahalle'] == components['ilce']:
            print(f"   🚨 CONFIRMED BUG: mahalle and ilce have same value '{components['mahalle']}'")
            print(f"   🔍 This indicates component overwriting during extraction")

if __name__ == "__main__":
    test_critical_bugs()