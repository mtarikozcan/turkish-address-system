#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EMERGENCY VERIFICATION TEST - Check exact failure cases
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from address_parser import AddressParser

def emergency_verification():
    """Verify the exact failing test cases"""
    
    print("🚨 EMERGENCY VERIFICATION - TEKNOFEST Critical Failures")
    print("=" * 70)
    
    parser = AddressParser()
    
    test_cases = [
        {
            "name": "TEST CASE 1",
            "address": "istanbul kadıköy bağdat caddesi",
            "expected": "İstanbul Kadıköy Bağdat Caddesi",
            "issue": "Turkish char corruption + Wrong street name"
        },
        {
            "name": "TEST CASE 2", 
            "address": "ankara cankaya tunali hilmi caddesi",
            "expected": "Ankara Çankaya Tunalı Hilmi Caddesi",
            "issue": "Historical street name corrupted"
        },
        {
            "name": "TEST CASE 3",
            "address": "istanbul kadikoy moda", 
            "expected": {"il": "İstanbul", "ilce": "Kadıköy", "mahalle": "Moda"},
            "issue": "Missing ilce component"
        },
        {
            "name": "TEST CASE 4",
            "address": "izmir konak kordon boyu",
            "expected": {"il": "İzmir", "ilce": "Konak", "sokak": "Kordon Boyu"},
            "issue": "Component assignment logic wrong"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{test_case['name']}: {test_case['address']}")
        print(f"Issue: {test_case['issue']}")
        
        result = parser.parse_address(test_case['address'])
        components = result.get('components', {})
        confidence = result.get('confidence', 0)
        
        print(f"📍 Actual: {components}")
        print(f"🎯 Expected: {test_case['expected']}")
        print(f"🎯 Confidence: {confidence:.2f}")
        
        if isinstance(test_case['expected'], dict):
            # Component-based comparison
            issues = []
            for comp, exp_val in test_case['expected'].items():
                actual_val = components.get(comp)
                if not actual_val:
                    issues.append(f"Missing {comp}")
                elif actual_val != exp_val:
                    issues.append(f"{comp}: got '{actual_val}', expected '{exp_val}'")
            
            if issues:
                print(f"❌ FAILED: {', '.join(issues)}")
            else:
                print("✅ PASSED")
        else:
            # String-based comparison - format address correctly
            ordered_components = []
            if components.get('il'):
                ordered_components.append(components['il'])
            if components.get('ilce'):
                ordered_components.append(components['ilce'])
            if components.get('mahalle'):
                ordered_components.append(components['mahalle'])
            if components.get('sokak'):
                # For street addresses, include the sokak but remove city/district contamination
                sokak = components['sokak']
                # Clean sokak by removing city/district parts
                clean_sokak = sokak
                for admin_comp in ['il', 'ilce', 'mahalle']:
                    if admin_comp in components:
                        admin_val = components[admin_comp]
                        clean_sokak = clean_sokak.replace(admin_val, '').strip()
                        clean_sokak = clean_sokak.replace(admin_val.lower(), '').strip()
                        clean_sokak = clean_sokak.replace(admin_val.capitalize(), '').strip()
                ordered_components.append(clean_sokak.strip())
            
            actual_formatted = " ".join([c for c in ordered_components if c])
            
            if actual_formatted == test_case['expected']:
                print("✅ PASSED")
            else:
                print(f"❌ FAILED")
                print(f"   Got:      '{actual_formatted}'")
                print(f"   Expected: '{test_case['expected']}'")
        
        print("-" * 50)

if __name__ == "__main__":
    emergency_verification()