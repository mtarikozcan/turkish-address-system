#!/usr/bin/env python3
"""
Debug why neighborhood penalty is not being applied correctly
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def debug_neighborhood_penalty():
    """Debug the neighborhood penalty application"""
    
    print("🔍 DEBUGGING NEIGHBORHOOD PENALTY APPLICATION")
    print("=" * 70)
    
    try:
        from duplicate_detector import DuplicateAddressDetector
        print("✅ DuplicateAddressDetector loaded successfully")
    except ImportError as e:
        print(f"❌ Error importing detector: {e}")
        return False
    
    # Initialize detector
    detector = DuplicateAddressDetector(similarity_threshold=0.75)
    print(f"✅ Detector initialized with threshold {detector.similarity_threshold}")
    
    # Test case from user report
    address1 = "Ankara Çankaya Büklüm Sokak Mahallesi Atatürk Cad"
    address2 = "Ankara Çankaya Kavaklıdere Mahallesi Atatürk Caddesi"
    
    print(f"\n🧪 TEST ADDRESSES:")
    print(f"   Address 1: '{address1}'")
    print(f"   Address 2: '{address2}'")
    
    # Step 1: Check address parsing
    print(f"\n📊 STEP 1: ADDRESS PARSING")
    if hasattr(detector, 'parser') and detector.parser:
        try:
            components1 = detector.parser.parse_address(address1)
            components2 = detector.parser.parse_address(address2)
            
            print(f"   Address 1 components: {components1.get('components', {})}")
            print(f"   Address 2 components: {components2.get('components', {})}")
            
            mah1 = components1.get('components', {}).get('mahalle', 'NOT_FOUND')
            mah2 = components2.get('components', {}).get('mahalle', 'NOT_FOUND')
            
            print(f"   Parsed mahalle 1: '{mah1}'")
            print(f"   Parsed mahalle 2: '{mah2}'")
            
        except Exception as e:
            print(f"   ❌ Error parsing addresses: {e}")
    else:
        print(f"   ⚠️ Parser not available, using fallback")
    
    # Step 2: Test neighborhood penalty calculation directly
    print(f"\n📊 STEP 2: NEIGHBORHOOD PENALTY CALCULATION")
    try:
        penalty = detector._calculate_neighborhood_difference_penalty(address1, address2)
        print(f"   Neighborhood penalty: {penalty:.3f}")
        
        # Test neighborhood extraction methods
        if hasattr(detector, '_get_address_components'):
            comp1 = detector._get_address_components(address1)
            comp2 = detector._get_address_components(address2)
            print(f"   Components 1: {comp1}")
            print(f"   Components 2: {comp2}")
            
        if hasattr(detector, '_extract_neighborhood_fallback'):
            fb1 = detector._extract_neighborhood_fallback(address1)
            fb2 = detector._extract_neighborhood_fallback(address2)
            print(f"   Fallback extraction 1: '{fb1}'")
            print(f"   Fallback extraction 2: '{fb2}'")
        
    except Exception as e:
        print(f"   ❌ Error calculating penalty: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 3: Test basic similarity (should have penalty applied)
    print(f"\n📊 STEP 3: BASIC SIMILARITY CALCULATION")
    try:
        basic_similarity = detector._calculate_basic_similarity(address1, address2)
        print(f"   Basic similarity (with penalty): {basic_similarity:.3f}")
        
    except Exception as e:
        print(f"   ❌ Error calculating basic similarity: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 4: Test hybrid similarity
    print(f"\n📊 STEP 4: HYBRID SIMILARITY CALCULATION")
    try:
        if hasattr(detector, 'hybrid_matcher') and detector.hybrid_matcher:
            hybrid_result = detector.hybrid_matcher.calculate_hybrid_similarity(address1, address2)
            hybrid_similarity = hybrid_result.get('overall_similarity', 0.0)
            print(f"   Raw hybrid similarity: {hybrid_similarity:.3f}")
            
            # Apply penalty manually to see expected result
            penalty = detector._calculate_neighborhood_difference_penalty(address1, address2)
            hybrid_adjusted = max(0.0, hybrid_similarity - penalty)
            print(f"   Expected adjusted hybrid: {hybrid_adjusted:.3f}")
            
        else:
            print(f"   ⚠️ Hybrid matcher not available")
            
    except Exception as e:
        print(f"   ❌ Error calculating hybrid similarity: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 5: Test final similarity calculation
    print(f"\n📊 STEP 5: FINAL SIMILARITY CALCULATION")
    try:
        result = detector.detect_duplicate_pairs(address1, address2)
        
        print(f"   Final result:")
        print(f"     Is Duplicate: {result['is_duplicate']}")
        print(f"     Similarity Score: {result['similarity_score']:.3f}")
        print(f"     Confidence: {result['confidence']:.3f}")
        
        if 'similarity_breakdown' in result:
            breakdown = result['similarity_breakdown']
            print(f"     Breakdown:")
            for key, value in breakdown.items():
                if isinstance(value, (int, float)):
                    print(f"       {key}: {value:.3f}")
                else:
                    print(f"       {key}: {value}")
        
    except Exception as e:
        print(f"   ❌ Error in final calculation: {e}")
        import traceback
        traceback.print_exc()
    
    # Summary
    print(f"\n" + "=" * 70)
    print(f"🎯 DEBUGGING SUMMARY:")
    print(f"   Expected behavior: Different neighborhoods should get ~0.35 penalty")
    print(f"   Expected similarity: ~0.50 (raw ~0.85 - penalty 0.35)")
    print(f"   Expected result: NOT duplicates (< 0.75 threshold)")
    
    return True

if __name__ == "__main__":
    debug_neighborhood_penalty()