#!/usr/bin/env python3
"""
Debug specific case preservation issue for "15.sk no 25/A kat 3"
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def debug_specific_case():
    try:
        from address_parser import AddressParser
        parser = AddressParser()
        
        test_input = "15.sk no 25/A kat 3"
        print(f"Testing: '{test_input}'")
        
        # Test the full pipeline
        result = parser.parse_address(test_input)
        components = result['components']
        
        print(f"Final result: {components}")
        print(f"Building number: '{components.get('bina_no', 'NOT FOUND')}'")
        
        # Let's also test the semantic parser directly
        print("\n--- Direct semantic test ---")
        from semantic_parser import SemanticPatternEngine
        semantic = SemanticPatternEngine()
        semantic_result = semantic.classify_semantic_components(test_input)
        print(f"Semantic result: {semantic_result['components']}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_specific_case()