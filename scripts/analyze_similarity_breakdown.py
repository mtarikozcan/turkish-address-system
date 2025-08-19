#!/usr/bin/env python3
"""
Analyze why identical addresses get low similarity scores
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def analyze_similarity_breakdown():
    """Analyze detailed similarity breakdown"""
    
    print("🔍 SIMILARITY BREAKDOWN ANALYSIS")
    print("=" * 60)
    
    from address_matcher import HybridAddressMatcher
    matcher = HybridAddressMatcher()
    
    # User's test case
    address1 = "Ank. Çank. Kızılay Mh. Atatürk Blv. No:25/A Daire:3"
    address2 = "Ankara Çankaya Kızılay Mahallesi Atatürk Bulvarı Numara:25/A Daire:3"
    
    print(f"Address 1: '{address1}'")
    print(f"Address 2: '{address2}'")
    print(f"These should be IDENTICAL after normalization!")
    print("-" * 60)
    
    result = matcher.calculate_hybrid_similarity(address1, address2)
    
    print(f"📊 DETAILED RESULTS:")
    print(f"   Overall Similarity: {result['overall_similarity']:.3f}")
    print(f"   Match Decision: {result['match_decision']}")
    print(f"   Confidence: {result['confidence']:.3f}")
    
    print(f"\n🔍 COMPONENT BREAKDOWN:")
    breakdown = result['similarity_breakdown']
    for component, score in breakdown.items():
        print(f"   {component.capitalize()}: {score:.3f}")
    
    print(f"\n⚖️ WEIGHTED CONTRIBUTIONS:")
    contributions = result['similarity_details']['method_contributions']
    for method, contribution in contributions.items():
        print(f"   {method.capitalize()}: {contribution:.3f}")
    
    # Test individual components to see which is failing
    print(f"\n🧪 INDIVIDUAL COMPONENT ANALYSIS:")
    
    semantic_score = matcher.get_semantic_similarity(address1, address2)
    print(f"   Semantic: {semantic_score:.3f}")
    
    geographic_score = matcher.get_geographic_similarity(address1, address2)
    print(f"   Geographic: {geographic_score:.3f}")
    
    text_score = matcher.get_text_similarity(address1, address2)
    print(f"   Text: {text_score:.3f}")
    
    hierarchy_score = matcher.get_hierarchy_similarity(address1, address2)
    print(f"   Hierarchy: {hierarchy_score:.3f}")
    
    # Analyze the problem
    print(f"\n🔍 PROBLEM ANALYSIS:")
    if semantic_score < 0.7:
        print(f"   ❌ SEMANTIC ISSUE: Score {semantic_score:.3f} - not recognizing semantic equivalence")
    if geographic_score < 0.7:
        print(f"   ❌ GEOGRAPHIC ISSUE: Score {geographic_score:.3f} - geographic matching problem")
    if text_score < 0.7:
        print(f"   ❌ TEXT ISSUE: Score {text_score:.3f} - text normalization not working")
    if hierarchy_score < 0.7:
        print(f"   ❌ HIERARCHY ISSUE: Score {hierarchy_score:.3f} - component parsing problem")
    
    # The issue is likely that the matcher isn't using the corrected/normalized addresses
    print(f"\n💡 LIKELY ISSUE: Matcher not using corrected/normalized addresses")
    print(f"   Should apply abbreviation expansion and Turkish char normalization BEFORE similarity")

if __name__ == "__main__":
    analyze_similarity_breakdown()