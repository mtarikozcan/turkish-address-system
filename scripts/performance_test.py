#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRITICAL: Performance and Validation Test
Measure current issues and verify fixes needed
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_performance_and_validation():
    """Test current performance and validation issues"""
    
    print("🚨 CRITICAL: Performance and Validation Analysis")
    print("=" * 60)
    
    # Test 1: System startup performance
    print("1. Testing System Startup Performance...")
    start_time = time.time()
    
    try:
        from address_validator import AddressValidator
        from address_parser import AddressParser
        
        validator = AddressValidator()
        parser = AddressParser()
        
        startup_time = time.time() - start_time
        print(f"   ⏱️  Startup time: {startup_time*1000:.0f}ms")
        
        if startup_time > 1.0:  # > 1 second
            print(f"   ❌ SLOW: Startup takes {startup_time:.1f}s (target: <1s)")
        else:
            print(f"   ✅ Startup performance acceptable")
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return
    
    # Test 2: Processing time per address
    print(f"\n2. Testing Address Processing Performance...")
    
    test_addresses = [
        "ankara cankaya kizilay",
        "izmir konak alsancak", 
        "istanbul kadikoy moda",
        "istanbul mecidiyekoy",
        "bursa osmangazi"
    ]
    
    total_time = 0
    validation_results = []
    
    for address in test_addresses:
        print(f"\n   Testing: {address}")
        
        # Test parsing performance
        start_time = time.time()
        parse_result = parser.parse_address(address)
        parse_time = time.time() - start_time
        
        # Test validation performance  
        start_time = time.time()
        components = parse_result.get('components', {})
        
        if all(k in components for k in ['il', 'ilce', 'mahalle']):
            is_valid = validator.validate_hierarchy(
                components['il'], 
                components['ilce'], 
                components['mahalle']
            )
        else:
            is_valid = False
            
        validation_time = time.time() - start_time
        
        total_time = parse_time + validation_time
        
        print(f"      📍 Components: {components}")
        print(f"      ⏱️  Parse time: {parse_time*1000:.0f}ms")
        print(f"      ⏱️  Validation time: {validation_time*1000:.0f}ms")  
        print(f"      ⏱️  Total time: {total_time*1000:.0f}ms")
        print(f"      ✅ Valid: {is_valid}")
        
        validation_results.append({
            'address': address,
            'components': components,
            'is_valid': is_valid,
            'total_time_ms': total_time * 1000
        })
        
        if total_time > 0.1:  # > 100ms
            print(f"      ❌ SLOW: Processing takes {total_time*1000:.0f}ms (target: <100ms)")
        else:
            print(f"      ✅ Performance acceptable")
    
    # Test 3: Validation logic analysis
    print(f"\n3. Validation Logic Analysis...")
    
    valid_count = sum(1 for r in validation_results if r['is_valid'])
    total_count = len(validation_results)
    
    print(f"   📊 Validation Results: {valid_count}/{total_count} addresses valid")
    
    # Critical test cases that should be valid
    critical_cases = [
        ("ankara cankaya kizilay", "Ankara-Çankaya-Kızılay should be VALID"),
        ("izmir konak alsancak", "İzmir-Konak-Alsancak should be VALID")
    ]
    
    validation_issues = []
    for address, expected in critical_cases:
        result = next((r for r in validation_results if r['address'] == address), None)
        if result and not result['is_valid']:
            validation_issues.append(f"❌ {expected} but marked INVALID")
            print(f"   ❌ {expected} but marked INVALID")
        elif result and result['is_valid']:
            print(f"   ✅ {expected} - CORRECT")
    
    # Test 4: Memory usage check
    print(f"\n4. Data Loading Analysis...")
    
    hierarchy_count = len(validator.admin_hierarchy) if hasattr(validator, 'admin_hierarchy') else 0
    neighborhood_count = len(parser.turkish_locations.get('all_neighborhoods', [])) if hasattr(parser, 'turkish_locations') else 0
    
    print(f"   📊 AddressValidator hierarchy combinations: {hierarchy_count:,}")
    print(f"   📊 AddressParser neighborhood count: {neighborhood_count:,}")
    
    if hierarchy_count < 1000:
        print(f"   ⚠️  Hierarchy validation may be incomplete ({hierarchy_count:,} combinations)")
    
    # Summary
    print(f"\n🎯 CRITICAL ISSUES SUMMARY:")
    
    avg_time = sum(r['total_time_ms'] for r in validation_results) / len(validation_results)
    print(f"   ⏱️  Average processing time: {avg_time:.0f}ms (target: <100ms)")
    
    if avg_time > 100:
        print(f"   ❌ PERFORMANCE ISSUE: Processing too slow")
    
    if validation_issues:
        print(f"   ❌ VALIDATION ISSUES: {len(validation_issues)} critical cases failing")
        for issue in validation_issues:
            print(f"      {issue}")
    
    if hierarchy_count < 10000:
        print(f"   ❌ VALIDATION SCOPE: Only {hierarchy_count:,} valid combinations (expected 27,000+)")
    
    print(f"\n   📋 FIXES NEEDED:")
    if avg_time > 100:
        print(f"      1. Optimize performance (cache data, avoid reloading)")
    if validation_issues:
        print(f"      2. Fix validation logic for OSM neighborhoods")  
    if hierarchy_count < 10000:
        print(f"      3. Expand hierarchy validation to include OSM data")

if __name__ == "__main__":
    test_performance_and_validation()