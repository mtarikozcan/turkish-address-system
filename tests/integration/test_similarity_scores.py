#!/usr/bin/env python3
"""
Test similarity scores for identical addresses after all fixes
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def test_similarity_scores():
    """Test if identical addresses still get low similarity scores"""
    
    print("🎯 SIMILARITY SCORE TEST - After All Fixes")
    print("=" * 60)
    
    # Try to find address matcher/duplicate detector
    try:
        from address_matcher import HybridAddressMatcher
        matcher_available = True
        matcher = HybridAddressMatcher()
        print("✅ Using HybridAddressMatcher")
    except ImportError:
        try:
            from address_matcher import AddressMatcher
            matcher_available = True
            matcher = AddressMatcher()
            print("✅ Using AddressMatcher")
        except ImportError:
            try:
                from duplicate_detector import DuplicateDetector  
                matcher_available = True
                matcher = DuplicateDetector()
                print("✅ Using DuplicateDetector")
            except ImportError:
                print("❌ No address matcher/duplicate detector found")
                matcher_available = False
    
    if not matcher_available:
        print("Checking what matcher files exist...")
        # List files to see what's available
        import glob
        matcher_files = glob.glob(str(src_dir / "*match*")) + glob.glob(str(src_dir / "*duplicate*"))
        print(f"Found files: {matcher_files}")
        return
    
    # User's test case - identical addresses in different formats
    test_cases = [
        {
            'address1': "Ank. Çank. Kızılay Mh. Atatürk Blv. No:25/A Daire:3",
            'address2': "Ankara Çankaya Kızılay Mahallesi Atatürk Bulvarı Numara:25/A Daire:3",
            'description': "User's test case - identical after normalization",
            'expected': ">0.85"
        },
        {
            'address1': "İst. Kadıköy Moda Mh. Caferağa Sk. 10/A",
            'address2': "İstanbul Kadıköy Moda Mahallesi Caferağa Sokak 10/A", 
            'description': "İstanbul abbreviation test",
            'expected': ">0.85"
        },
        {
            'address1': "İzm. Konak Alsancak",
            'address2': "İzmir Konak Alsancak",
            'description': "İzmir abbreviation test",
            'expected': ">0.85"
        }
    ]
    
    print(f"\n🧪 TESTING {len(test_cases)} IDENTICAL ADDRESS PAIRS:")
    
    issue_found = False
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. {test['description']}")
        print(f"   Address 1: '{test['address1']}'")
        print(f"   Address 2: '{test['address2']}'")
        print(f"   Expected: {test['expected']} similarity")
        
        try:
            # Try different method names that might exist
            similarity = None
            
            if hasattr(matcher, 'calculate_hybrid_similarity'):
                result = matcher.calculate_hybrid_similarity(test['address1'], test['address2'])
                similarity = result.get('overall_similarity', result.get('final_similarity', result.get('similarity', result.get('score'))))
            elif hasattr(matcher, 'calculate_similarity'):
                similarity = matcher.calculate_similarity(test['address1'], test['address2'])
            elif hasattr(matcher, 'compare_addresses'):
                result = matcher.compare_addresses(test['address1'], test['address2'])
                similarity = result.get('similarity', result.get('score'))
            elif hasattr(matcher, 'match_addresses'):
                result = matcher.match_addresses(test['address1'], test['address2'])
                similarity = result.get('similarity', result.get('score'))
            elif hasattr(matcher, 'find_similarity'):
                similarity = matcher.find_similarity(test['address1'], test['address2'])
                
            if similarity is not None:
                print(f"   Result: {similarity:.3f}")
                
                if similarity >= 0.85:
                    print(f"   ✅ EXCELLENT: High similarity as expected")
                elif similarity >= 0.75:
                    print(f"   ✅ GOOD: Decent similarity")
                elif similarity >= 0.60:
                    print(f"   ⚠️  MODERATE: Could be better")
                else:
                    print(f"   ❌ LOW: Need to fix similarity calculation")
                    issue_found = True
            else:
                print(f"   ❌ Could not calculate similarity - method not found")
                issue_found = True
                
        except Exception as e:
            print(f"   ❌ Error calculating similarity: {e}")
            issue_found = True
    
    print(f"\n" + "=" * 60)
    
    if issue_found:
        print(f"❌ SIMILARITY ISSUE CONFIRMED - Need to apply fix")
        print(f"   Some identical addresses getting <0.75 similarity")
        return True  # Issue exists, need to fix
    else:
        print(f"✅ NO SIMILARITY ISSUE - All identical addresses >0.75")
        return False  # No issue, skip fix

if __name__ == "__main__":
    needs_fix = test_similarity_scores()
    if needs_fix:
        print(f"\n🔧 RECOMMENDATION: Apply similarity calculation fix")
    else:
        print(f"\n🎉 RECOMMENDATION: Skip fix - similarity working well")