#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test current street-level and building-level parsing issues
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from address_parser import AddressParser

def test_current_parsing_issues():
    """Test the current parsing issues with street and building level addresses"""
    
    print("🧪 TESTING CURRENT PARSING ISSUES")
    print("=" * 60)
    
    parser = AddressParser()
    
    test_cases = [
        {
            "address": "bursa osmangazi emek gazi caddesi",
            "issue": "Mahalle/sokak confusion",
            "expected": {
                "il": "Bursa",
                "ilce": "Osmangazi", 
                "mahalle": "Emek",
                "sokak": "Gazi Caddesi"
            }
        },
        {
            "address": "istanbul bagdat caddesi 127/A",
            "issue": "Missing building-level parsing",
            "expected": {
                "il": "İstanbul",
                "sokak": "Bağdat Caddesi",
                "bina_no": "127",
                "daire": "A"
            }
        },
        {
            "address": "ankara tunali hilmi caddesi 25/A",
            "issue": "Missing building-level parsing",
            "expected": {
                "il": "Ankara",
                "sokak": "Tunalı Hilmi Caddesi", 
                "bina_no": "25",
                "daire": "A"
            }
        },
        {
            "address": "izmir kordon boyu 15 B blok",
            "issue": "Missing building-level parsing",
            "expected": {
                "il": "İzmir",
                "sokak": "Kordon Boyu",
                "bina_no": "15",
                "blok": "B"
            }
        },
        {
            "address": "bursa osmangazi emek gazi caddesi 127",
            "issue": "Complete parsing test",
            "expected": {
                "il": "Bursa",
                "ilce": "Osmangazi",
                "mahalle": "Emek", 
                "sokak": "Gazi Caddesi",
                "bina_no": "127"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        address = test_case["address"]
        issue = test_case["issue"]
        expected = test_case["expected"]
        
        print(f"\n🧪 Test {i}: {address}")
        print(f"   Issue: {issue}")
        print(f"   Expected: {expected}")
        
        result = parser.parse_address(address)
        components = result.get('components', {})
        confidence = result.get('confidence', 0)
        
        print(f"   📍 Actual: {components}")
        print(f"   🎯 Confidence: {confidence:.2f}")
        
        # Check for issues
        issues_found = []
        
        for key, expected_value in expected.items():
            if key not in components:
                issues_found.append(f"Missing {key}")
            elif components[key] != expected_value:
                issues_found.append(f"{key}: got '{components[key]}', expected '{expected_value}'")
        
        if issues_found:
            print(f"   ❌ Issues found: {', '.join(issues_found)}")
        else:
            print(f"   ✅ All components correct")
        
        if confidence < 0.8:
            print(f"   ⚠️  Low confidence: {confidence:.2f} (target: 0.8+)")

if __name__ == "__main__":
    test_current_parsing_issues()