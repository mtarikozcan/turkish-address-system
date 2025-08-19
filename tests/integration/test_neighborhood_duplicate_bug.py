#!/usr/bin/env python3
"""
Test different neighborhoods being detected as duplicates bug
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def test_neighborhood_duplicate_bug():
    """Test the specific bug with different neighborhoods detected as duplicates"""
    
    print("🎯 NEIGHBORHOOD DUPLICATE DETECTION BUG TEST")
    print("=" * 70)
    
    try:
        from duplicate_detector import DuplicateAddressDetector
        print("✅ DuplicateAddressDetector loaded successfully")
    except ImportError as e:
        print(f"❌ Error importing detector: {e}")
        return False
    
    # Initialize detector with standard threshold
    detector = DuplicateAddressDetector(similarity_threshold=0.75)
    print(f"✅ Detector initialized with threshold {detector.similarity_threshold}")
    
    # Test case from user report
    test_addresses = [
        "Ankara Çankaya Büklüm Sokak Mahallesi Atatürk Cad",
        "Ankara Çankaya Kavaklıdere Mahallesi Atatürk Caddesi"
    ]
    
    print(f"\n🧪 TESTING USER-REPORTED BUG:")
    print(f"Address 1: '{test_addresses[0]}'")  
    print(f"Address 2: '{test_addresses[1]}'")
    print(f"Expected: NOT duplicates (different neighborhoods: Büklüm ≠ Kavaklıdere)")
    
    # Test pair comparison
    pair_result = detector.detect_duplicate_pairs(test_addresses[0], test_addresses[1])
    
    print(f"\n📊 PAIR COMPARISON RESULT:")
    print(f"   Is Duplicate: {pair_result['is_duplicate']}")
    print(f"   Similarity Score: {pair_result['similarity_score']:.3f}")
    print(f"   Confidence: {pair_result['confidence']:.3f}")
    print(f"   Breakdown: {pair_result['similarity_breakdown']}")
    
    # Test group detection
    groups = detector.find_duplicate_groups(test_addresses)
    
    print(f"\n📊 GROUP DETECTION RESULT:")
    print(f"   Total groups: {len(groups)}")
    
    bug_detected = False
    for i, group in enumerate(groups):
        print(f"   Group {i+1}: {group}")
        if len(group) > 1:
            print(f"      ❌ BUG: Different neighborhoods grouped as duplicates!")
            for idx in group:
                print(f"         - {test_addresses[idx]}")
            bug_detected = True
        else:
            print(f"      ✅ Correctly identified as unique: {test_addresses[group[0]]}")
    
    # Additional test cases with more neighborhood pairs
    print(f"\n🧪 EXTENDED TEST CASES:")
    
    extended_test_cases = [
        ("Ankara Çankaya Kızılay Mahallesi Atatürk Cad", "Ankara Çankaya Bahçelievler Mahallesi Atatürk Cad"),
        ("İstanbul Kadıköy Moda Mahallesi Bahariye Cad", "İstanbul Kadıköy Fenerbahçe Mahallesi Bahariye Cad"),
        ("İzmir Konak Alsancak Mahallesi Cumhuriyet Cad", "İzmir Konak Kemeraltı Mahallesi Cumhuriyet Cad"),
    ]
    
    extended_bug_count = 0
    
    for i, (addr1, addr2) in enumerate(extended_test_cases, 1):
        print(f"\n   Test Case {i}:")
        print(f"   Address 1: {addr1}")
        print(f"   Address 2: {addr2}")
        
        # Extract neighborhood names for verification
        mah1 = addr1.split("Mahallesi")[0].split()[-1] if "Mahallesi" in addr1 else "Unknown"
        mah2 = addr2.split("Mahallesi")[0].split()[-1] if "Mahallesi" in addr2 else "Unknown"
        print(f"   Neighborhoods: {mah1} vs {mah2}")
        
        result = detector.detect_duplicate_pairs(addr1, addr2)
        print(f"   Is Duplicate: {result['is_duplicate']}")
        print(f"   Similarity: {result['similarity_score']:.3f}")
        
        if result['is_duplicate']:
            print(f"   ❌ BUG: Different neighborhoods detected as duplicates!")
            extended_bug_count += 1
        else:
            print(f"   ✅ Correctly identified as different")
    
    # Summary
    total_bug_count = (1 if bug_detected else 0) + extended_bug_count
    total_tests = 1 + len(extended_test_cases)
    
    print(f"\n" + "=" * 70)
    print(f"📊 BUG TEST SUMMARY:")
    print(f"   Total test cases: {total_tests}")
    print(f"   Bug instances found: {total_bug_count}")
    print(f"   Tests passed: {total_tests - total_bug_count}")
    
    if total_bug_count == 0:
        print(f"   ✅ SUCCESS: No neighborhood duplicate bugs detected")
        return True
    else:
        print(f"   ❌ BUG CONFIRMED: {total_bug_count} cases incorrectly detected as duplicates")
        print(f"   🔧 ANALYSIS: Different neighborhoods sharing same street names are incorrectly grouped")
        return False

if __name__ == "__main__":
    success = test_neighborhood_duplicate_bug()
    if not success:
        print(f"\n🔧 BUG REPRODUCTION SUCCESSFUL - Now implementing fix...")
    else:
        print(f"\n✅ No bugs detected - system working correctly")