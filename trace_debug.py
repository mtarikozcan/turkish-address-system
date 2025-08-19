#!/usr/bin/env python3
"""
Trace the Turkish character issue step by step
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from address_corrector import AddressCorrector

def trace_correction_steps():
    print("🔍 TRACING CORRECTION STEPS")
    print("=" * 60)
    
    corrector = AddressCorrector()
    
    # Test cases
    test_cases = ["10/A", "çankaya"]
    
    for test_input in test_cases:
        print(f"\n📝 Testing: '{test_input}'")
        print("-" * 40)
        
        # Step 1: Initial normalization
        step1 = corrector._preserve_turkish_normalization(test_input)
        print(f"1. After _preserve_turkish_normalization: '{step1}'")
        
        # Step 2: Expansion (should do nothing for these)
        step2 = corrector.expand_abbreviations(step1)
        print(f"2. After expand_abbreviations: '{step2}'")
        
        # Step 3: Spelling corrections (should do nothing for these) 
        step3 = corrector.correct_spelling_errors(step2)
        print(f"3. After correct_spelling_errors: '{step3}'")
        
        # Step 4: Turkish capitalization
        step4 = corrector._apply_turkish_capitalization(step3)
        print(f"4. After _apply_turkish_capitalization: '{step4}'")
        
        # Full pipeline
        full_result = corrector.correct_address(test_input)
        print(f"5. Full pipeline result: '{full_result['corrected_address']}'")

if __name__ == "__main__":
    trace_correction_steps()