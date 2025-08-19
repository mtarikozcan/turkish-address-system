#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EMERGENCY: Verify critical failures in Turkish address parsing
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from address_parser import AddressParser

def test_critical_failures():
    """Test all critical failures reported"""
    
    print("🚨 EMERGENCY FAILURE VERIFICATION TEST")
    print("=" * 70)
    
    parser = AddressParser()
    
    critical_tests = [
        {
            "name": "TURKISH CHARACTER CORRUPTION",
            "tests": [
                {
                    "input": "istanbul istiklal caddesi",
                    "expected": {"cadde": "İstiklal Caddesi"},
                    "issue": "İstiklal becomes 'I Stiklal'"
                },
                {
                    "input": "ankara kızılay",
                    "expected": {"mahalle": "Kızılay"},
                    "issue": "Kızılay becomes 'Kizilay'"
                }
            ]
        },
        {
            "name": "STREET NAME CORRUPTION",
            "tests": [
                {
                    "input": "ankara tunali hilmi caddesi",
                    "expected": {"cadde": "Tunalı Hilmi Caddesi"},
                    "issue": "Tunalı Hilmi → Tuna Hilmi"
                },
                {
                    "input": "ankara çankaya tunalı hilmi caddesi",
                    "expected": {"cadde": "Tunalı Hilmi Caddesi"},
                    "issue": "Historical street name corruption"
                }
            ]
        },
        {
            "name": "NO CONTEXT INTELLIGENCE",
            "tests": [
                {
                    "input": "istanbul istiklal caddesi",
                    "expected": {"mahalle": "Beyoğlu", "ilce": "Beyoğlu"},
                    "issue": "No Beyoğlu inference from İstiklal"
                },
                {
                    "input": "istiklal caddesi",
                    "expected": {"il": "İstanbul", "ilce": "Beyoğlu", "mahalle": "Beyoğlu"},
                    "issue": "No smart completion"
                }
            ]
        },
        {
            "name": "APARTMENT PARSING BROKEN",
            "tests": [
                {
                    "input": "istanbul bagdat caddesi 127/A",
                    "expected": {"bina_no": "127", "daire_no": "A"},
                    "issue": "127/A → daire_no missing"
                },
                {
                    "input": "ankara tunali 25-B",
                    "expected": {"bina_no": "25", "daire_no": "B"},
                    "issue": "25-B format not working"
                }
            ]
        },
        {
            "name": "GEOGRAPHIC VALIDATION MISSING",
            "tests": [
                {
                    "input": "istanbul tunali hilmi caddesi",
                    "expected": {"error": "Geographic conflict"},
                    "issue": "Should detect Tunalı is in Ankara, not Istanbul"
                },
                {
                    "input": "ankara bagdat caddesi",
                    "expected": {"error": "Geographic conflict"},
                    "issue": "Should detect Bağdat is in Istanbul, not Ankara"
                }
            ]
        }
    ]
    
    total_failures = 0
    
    for category in critical_tests:
        print(f"\n🔴 {category['name']}")
        print("-" * 60)
        
        for test in category['tests']:
            address = test['input']
            expected = test['expected']
            issue = test['issue']
            
            print(f"\n   Input: '{address}'")
            print(f"   Issue: {issue}")
            
            result = parser.parse_address(address)
            components = result.get('components', {})
            
            # Check each expected field
            failures = []
            for field, expected_value in expected.items():
                if field == "error":
                    # Check if geographic validation caught the error (using validation_error field)
                    if 'validation_error' not in components:
                        failures.append(f"No geographic validation error detected")
                    else:
                        # Geographic validation is working - check if it mentions conflict
                        error_msg = components.get('validation_error', '')
                        if 'conflict' not in error_msg.lower():
                            failures.append(f"Geographic validation error exists but doesn't mention conflict: {error_msg}")
                else:
                    actual_value = components.get(field, 'MISSING')
                    if actual_value != expected_value:
                        failures.append(f"{field}: got '{actual_value}', expected '{expected_value}'")
            
            if failures:
                print(f"   ❌ FAILED: {'; '.join(failures)}")
                total_failures += 1
            else:
                print(f"   ✅ PASSED")
            
            print(f"   Actual: {components}")
    
    print(f"\n🚨 TOTAL FAILURES: {total_failures}")
    return total_failures

if __name__ == "__main__":
    failures = test_critical_failures()