#!/usr/bin/env python3
"""
Debug what methods are available in HybridAddressMatcher
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def debug_matcher_methods():
    """Debug available methods in matcher"""
    
    print("🔍 DEBUGGING MATCHER METHODS")
    print("=" * 50)
    
    try:
        from address_matcher import HybridAddressMatcher
        matcher = HybridAddressMatcher()
        print("✅ HybridAddressMatcher loaded successfully")
        
        # List all methods
        print(f"\n📋 AVAILABLE METHODS:")
        methods = [method for method in dir(matcher) if not method.startswith('_') and callable(getattr(matcher, method))]
        for method in methods:
            print(f"   - {method}")
        
        # Test the main method directly
        print(f"\n🧪 TESTING calculate_hybrid_similarity METHOD:")
        address1 = "Ank. Çank. Kızılay Mh."
        address2 = "Ankara Çankaya Kızılay Mahallesi"
        
        print(f"   Address 1: '{address1}'")
        print(f"   Address 2: '{address2}'")
        
        try:
            result = matcher.calculate_hybrid_similarity(address1, address2)
            print(f"   Raw result: {result}")
            print(f"   Type: {type(result)}")
            
            if isinstance(result, dict):
                print(f"   Keys: {result.keys()}")
                for key, value in result.items():
                    print(f"     {key}: {value}")
                    
        except Exception as e:
            print(f"   ❌ Error calling calculate_hybrid_similarity: {e}")
            import traceback
            traceback.print_exc()
            
    except ImportError as e:
        print(f"❌ Could not import HybridAddressMatcher: {e}")
    except Exception as e:
        print(f"❌ Error creating matcher: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_matcher_methods()