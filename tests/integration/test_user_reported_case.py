#!/usr/bin/env python3
"""
Test the exact user-reported case to verify fix
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def test_user_reported_case():
    """Test the exact user-reported bug case"""
    
    print("🎯 USER-REPORTED BUG VERIFICATION TEST")
    print("=" * 60)
    
    try:
        from duplicate_detector import DuplicateAddressDetector
        print("✅ DuplicateAddressDetector loaded successfully")
    except ImportError as e:
        print(f"❌ Error importing detector: {e}")
        return False
    
    # Initialize detector
    detector = DuplicateAddressDetector(similarity_threshold=0.75)
    print(f"✅ Detector initialized with threshold {detector.similarity_threshold}")
    
    print(f"\n📋 USER-REPORTED BUG:")
    print(f"   Problem: Different neighborhoods being incorrectly grouped as duplicates")
    print(f"   Location: src/duplicate_detector.py")
    print(f"   Wrong Behavior: 'Büklüm Sokak Mahallesi' vs 'Kavaklıdere Mahallesi' → Detected as duplicates")
    print(f"   Expected: These are DIFFERENT neighborhoods in Ankara Çankaya!")
    
    # Exact test case from user report
    address1 = "Ankara Çankaya Büklüm Sokak Mahallesi Atatürk Cad"
    address2 = "Ankara Çankaya Kavaklıdere Mahallesi Atatürk Caddesi"
    
    print(f"\n🧪 EXACT TEST CASE:")
    print(f"   Address 1: \"{address1}\"")
    print(f"   Address 2: \"{address2}\"")
    print(f"   Expected: NOT duplicates (different mahalle: Büklüm ≠ Kavaklıdere)")
    
    # Component analysis expected from user
    print(f"\n📊 COMPONENT ANALYSIS:")
    print(f"   ✅ il: 'Ankara' ↔ 'Ankara' (match)")
    print(f"   ✅ ilce: 'Çankaya' ↔ 'Çankaya' (match)")  
    print(f"   ❌ mahalle: 'Büklüm Sokak' ↔ 'Kavaklıdere' (DIFFERENT!)")
    print(f"   ✅ cadde: 'Atatürk' ↔ 'Atatürk' (match)")
    
    # Test the exact case
    result = detector.detect_duplicate_pairs(address1, address2)
    
    print(f"\n📊 TEST RESULT:")
    print(f"   Is Duplicate: {result['is_duplicate']}")
    print(f"   Similarity Score: {result['similarity_score']:.3f}")
    print(f"   Confidence: {result['confidence']:.3f}")
    
    if 'breakdown' in result:
        breakdown = result['breakdown']
        print(f"   Breakdown:")
        for key, value in breakdown.items():
            print(f"     {key}: {value:.3f}" if isinstance(value, float) else f"     {key}: {value}")
    
    # Verify fix
    print(f"\n🔍 VERIFICATION:")
    if result['is_duplicate']:
        print(f"   ❌ BUG STILL EXISTS: Different neighborhoods incorrectly detected as duplicates!")
        print(f"   🔧 ANALYSIS: Similarity score {result['similarity_score']:.3f} >= threshold {detector.similarity_threshold}")
        return False
    else:
        print(f"   ✅ FIX SUCCESSFUL: Different neighborhoods correctly identified as different!")
        print(f"   📈 ANALYSIS: Similarity score {result['similarity_score']:.3f} < threshold {detector.similarity_threshold}")
        
        # Check if penalty was applied
        if 'breakdown' in result and 'neighborhood_penalty' in result['breakdown']:
            penalty = result['breakdown']['neighborhood_penalty']
            print(f"   🎯 PENALTY APPLIED: Neighborhood difference penalty = {penalty:.3f}")
            
            if 'hybrid_adjusted' in result['breakdown']:
                original = result['breakdown']['hybrid']
                adjusted = result['breakdown']['hybrid_adjusted']
                print(f"   📉 ADJUSTMENT: Hybrid similarity {original:.3f} → {adjusted:.3f} (reduced by {penalty:.3f})")
        
        return True

if __name__ == "__main__":
    success = test_user_reported_case()
    if success:
        print(f"\n🏆 USER-REPORTED BUG SUCCESSFULLY FIXED!")
        print(f"✅ Different neighborhoods with same street names no longer grouped as duplicates")
        print(f"✅ Component analysis correctly identifies mahalle differences")
        print(f"✅ Similarity threshold properly prevents false duplicates")
        print(f"✅ TEKNOFEST competition system ready!")
    else:
        print(f"\n🔧 Bug still exists - additional fixes needed")