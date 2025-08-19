#!/usr/bin/env python3
"""
TEKNOFEST 2025 - Critical Bug Fixes Verification
Test that the specific critical bugs have been resolved

Focus on:
1. Duplicate detection properly detecting identical addresses
2. Geocoding returning different coordinates for different cities  
3. Pipeline integration working without method signature errors
"""

import sys
import time
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def test_duplicate_detection_fixes():
    """Test that duplicate detection fixes are working"""
    print("🔍 TESTING DUPLICATE DETECTION FIXES")
    print("=" * 60)
    
    from duplicate_detector import DuplicateAddressDetector
    
    # Test the specific failing case from the bug report
    detector = DuplicateAddressDetector(similarity_threshold=0.75)
    
    addr1 = 'Istanbul Kadıköy Moda Mahallesi Caferağa Sokak 10'
    addr2 = 'İstanbul Kadıköy Moda Mah. Caferağa Sk. 10'
    
    result = detector.detect_duplicate_pairs(addr1, addr2)
    
    print(f"Testing critical pair:")
    print(f"  Address 1: {addr1}")
    print(f"  Address 2: {addr2}")
    print(f"  Is duplicate: {result['is_duplicate']}")
    print(f"  Similarity: {result['similarity_score']:.3f}")
    print(f"  Confidence: {result['confidence']:.3f}")
    
    # Success criteria: Should now detect as duplicate or high similarity
    if result['is_duplicate'] or result['similarity_score'] > 0.7:
        print("✅ FIXED: Duplicate detection now working correctly")
        return True
    else:
        print("❌ STILL BROKEN: Duplicate detection not improved enough")
        return False

def test_geocoding_fixes():
    """Test that geocoding fixes are working"""
    print("\n🌍 TESTING GEOCODING FIXES")
    print("=" * 60)
    
    from address_geocoder import AddressGeocoder
    
    geocoder = AddressGeocoder()
    
    test_addresses = [
        ("Istanbul Beyoglu Taksim", "Istanbul"),
        ("Ankara Cankaya Kizilay", "Ankara"), 
        ("Izmir Konak Alsancak", "Izmir"),
        ("Bursa Osmangazi Merkez", "Bursa")
    ]
    
    results = []
    coordinates_unique = set()
    
    print("Testing geocoding for different cities:")
    for address, expected_city in test_addresses:
        result = geocoder.geocode_turkish_address(address)
        
        lat = result.get('latitude')
        lon = result.get('longitude')
        method = result.get('method', 'unknown')
        confidence = result.get('confidence', 0)
        
        print(f"  {expected_city:8}: ({lat}, {lon}) - {method} (conf: {confidence:.3f})")
        
        results.append(result)
        if lat is not None and lon is not None:
            coordinates_unique.add((round(lat, 3), round(lon, 3)))
    
    # Success criteria: Should have different coordinates, not all Turkey center
    unique_coords = len(coordinates_unique)
    no_turkey_center_fallback = all(r.get('method') != 'turkey_center' for r in results)
    
    print(f"\nResults:")
    print(f"  Unique coordinates: {unique_coords}/4")
    print(f"  No Turkey center fallback: {no_turkey_center_fallback}")
    
    if unique_coords >= 3 and no_turkey_center_fallback:
        print("✅ FIXED: Geocoding now returns different coordinates for different cities")
        return True
    else:
        print("❌ STILL BROKEN: Geocoding still falling back to same coordinates")
        return False

def test_pipeline_integration_fixes():
    """Test that pipeline integration fixes are working"""
    print("\n🔧 TESTING PIPELINE INTEGRATION FIXES")
    print("=" * 60)
    
    import asyncio
    from geo_integrated_pipeline import GeoIntegratedPipeline
    
    async def test_pipeline():
        pipeline = GeoIntegratedPipeline("postgresql://localhost/test")
        
        test_addresses = ["Istanbul Kadıköy", "Ankara Çankaya"]
        
        # Test all three new integration methods
        try:
            print("Testing process_for_duplicate_detection()...")
            result1 = await pipeline.process_for_duplicate_detection(test_addresses)
            success1 = result1['status'] == 'completed'
            print(f"  Status: {result1['status']} - {'✅' if success1 else '❌'}")
            
            print("Testing process_with_geocoding()...")  
            result2 = await pipeline.process_with_geocoding(test_addresses)
            success2 = result2['status'] == 'completed'
            print(f"  Status: {result2['status']} - {'✅' if success2 else '❌'}")
            
            print("Testing format_for_kaggle_submission()...")
            result3 = await pipeline.format_for_kaggle_submission(test_addresses)
            success3 = result3['status'] == 'completed'
            print(f"  Status: {result3['status']} - {'✅' if success3 else '❌'}")
            
            return success1 and success2 and success3
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False
    
    success = asyncio.run(test_pipeline())
    
    if success:
        print("✅ FIXED: Pipeline integration methods working without signature errors")
    else:
        print("❌ STILL BROKEN: Pipeline integration still has errors")
    
    return success

def main():
    """Run critical bug fix verification tests"""
    print("🚨 TEKNOFEST 2025 - CRITICAL BUG FIXES VERIFICATION")
    print("=" * 80)
    print("Testing specific critical bugs that were identified...")
    
    tests = [
        ("Duplicate Detection Fixes", test_duplicate_detection_fixes),
        ("Geocoding Fixes", test_geocoding_fixes),
        ("Pipeline Integration Fixes", test_pipeline_integration_fixes),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
            results.append((test_name, False))
    
    # Final summary
    print("\n" + "=" * 80)
    print("🏁 CRITICAL BUG FIX VERIFICATION RESULTS")
    print("=" * 80)
    
    fixed_bugs = sum(1 for _, success in results if success)
    total_bugs = len(results)
    
    for test_name, success in results:
        status = "✅ FIXED" if success else "❌ STILL BROKEN"
        print(f"  {status} {test_name}")
    
    print(f"\nBugs Fixed: {fixed_bugs}/{total_bugs}")
    print(f"Fix Rate: {fixed_bugs/total_bugs:.1%}")
    
    if fixed_bugs == total_bugs:
        print("\n🎉 ALL CRITICAL BUGS FIXED!")
        print("✅ System genuinely ready for TEKNOFEST 2025 competition")
        return True
    else:
        print(f"\n⚠️  {total_bugs - fixed_bugs} critical bug(s) still need fixing")
        print("❌ System not yet ready for competition")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)