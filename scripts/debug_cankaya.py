#!/usr/bin/env python3
"""
Debug the specific çankaya -> ÇÇankaya issue
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from turkish_character_fix import TurkishCharacterHandler
from address_corrector import AddressCorrector

def debug_cankaya():
    print("🔍 DEBUGGING ÇANKAYA ISSUE")
    print("=" * 60)
    
    test_input = "çankaya"
    
    # Step 1: Test turkish_character_fix directly
    print(f"Original input: '{test_input}'")
    
    handler = TurkishCharacterHandler()
    
    # Test normalization
    normalized = handler.normalize_turkish_text(test_input)
    print(f"1. After normalize_turkish_text: '{normalized}'")
    
    # Test fix_common_corruptions
    fixed_corruptions = handler.fix_common_corruptions(normalized)
    print(f"2. After fix_common_corruptions: '{fixed_corruptions}'")
    
    # Test turkish_title_case
    titled = handler.turkish_title_case(fixed_corruptions)
    print(f"3. After turkish_title_case: '{titled}'")
    
    # Test full address corrector pipeline
    corrector = AddressCorrector()
    full_result = corrector.correct_address(test_input)
    print(f"4. Full pipeline result: '{full_result['corrected_address']}'")

if __name__ == "__main__":
    debug_cankaya()