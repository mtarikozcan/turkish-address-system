#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEKNOFEST Address Schema Test - Comprehensive Enhancement Testing
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from address_parser import AddressParser

def test_teknofest_schema():
    """Test TEKNOFEST comprehensive address schema requirements"""
    
    print("🏆 TEKNOFEST COMPREHENSIVE ADDRESS SCHEMA TEST")
    print("=" * 70)
    
    parser = AddressParser()
    
    # TEKNOFEST competition test cases
    competition_cases = [
        {
            "name": "STREET TYPE CLASSIFICATION",
            "address": "istanbul bagdat caddesi 127/A",
            "required_schema": {
                "il": "İstanbul",
                "cadde": "Bağdat Caddesi",  # NEW: Separate cadde field
                "bina_no": "127",
                "daire_no": "A"  # NEW: Separate daire_no field
            },
            "issue": "Must separate cadde from sokak, parse building components"
        },
        {
            "name": "CONTEXT INFERENCE ENGINE", 
            "address": "ankara cankaya konur sokak",
            "required_schema": {
                "il": "Ankara",
                "ilce": "Çankaya", 
                "mahalle": "Kızılay",  # INFERRED from OSM data
                "sokak": "Konur Sokak"
            },
            "issue": "Must infer mahalle='Kızılay' using OSM context"
        },
        {
            "name": "ENHANCED BUILDING PARSING",
            "address": "izmir konak kordon boyu 15 B blok 3 kat",
            "required_schema": {
                "il": "İzmir",
                "ilce": "Konak",
                "sokak": "Kordon Boyu",  # Street type: "boyu"
                "bina_no": "15",
                "blok": "B",  # NEW: Block field
                "kat": "3"    # NEW: Floor field
            },
            "issue": "Must parse complete building structure"
        },
        {
            "name": "SUFFIX CONTAMINATION FIX",
            "address": "ankara kizilay mahallesi ataturk caddesi",
            "required_schema": {
                "il": "Ankara", 
                "mahalle": "Kızılay",  # Clean, no "Mahallesi"
                "cadde": "Atatürk Caddesi"  # Clean, no contamination
            },
            "issue": "Must remove 'Mahallesi' suffix contamination"
        }
    ]
    
    for case in competition_cases:
        print(f"\n🎯 {case['name']}")
        print(f"   Address: {case['address']}")
        print(f"   Issue: {case['issue']}")
        
        # Parse with current system
        result = parser.parse_address(case['address'])
        components = result.get('components', {})
        confidence = result.get('confidence', 0)
        
        print(f"   📍 Current Result: {components}")
        print(f"   🎯 Required Schema: {case['required_schema']}")
        print(f"   🎯 Confidence: {confidence:.2f}")
        
        # Check schema compliance
        missing_fields = []
        incorrect_fields = []
        
        for field, expected_value in case['required_schema'].items():
            if field not in components:
                missing_fields.append(f"{field}='{expected_value}'")
            elif components[field] != expected_value:
                incorrect_fields.append(f"{field}: got '{components[field]}', expected '{expected_value}'")
        
        if missing_fields or incorrect_fields:
            issues = missing_fields + incorrect_fields
            print(f"   ❌ NEEDS ENHANCEMENT: {', '.join(issues)}")
        else:
            print(f"   ✅ TEKNOFEST COMPLIANT")
        
        print("-" * 50)
    
    # Schema analysis
    print(f"\n📋 CURRENT SCHEMA ANALYSIS:")
    print(f"   Current fields: il, ilce, mahalle, sokak, bina_no")
    print(f"   TEKNOFEST Required: il, ilce, mahalle, cadde, sokak, bina_no, daire_no, blok, kat, site")
    print(f"   Missing fields: cadde, daire_no, blok, kat, site")
    print(f"   Required: Street type classification, OSM inference, enhanced building parsing")

if __name__ == "__main__":
    test_teknofest_schema()