#!/usr/bin/env python3
"""
Test semantic pattern engine directly to debug case preservation
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def test_semantic_direct():
    try:
        from semantic_parser import SemanticPatternEngine
        engine = SemanticPatternEngine()
        
        test_cases = [
            "15.sk no 25/A kat 3",
            "no5-B daire 7",
            "231.sk no3 / 12"
        ]
        
        for test_case in test_cases:
            print(f"\nTesting: '{test_case}'")
            result = engine.classify_semantic_components(test_case)
            components = result['components']
            print(f"Result: {components}")
            
            # Check specific components
            if 'bina_no' in components:
                print(f"Building number: '{components['bina_no']}'")
                print(f"Case preserved?: {'A' in components['bina_no'] or 'B' in components['bina_no']}")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_semantic_direct()