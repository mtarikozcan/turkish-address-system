#!/usr/bin/env python3
"""
DEBUG: Turkish Character Preservation Issue
Test to verify and fix Turkish character loss in address_corrector.py
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from address_corrector import AddressCorrector


def test_turkish_character_preservation():
    """Test Turkish character preservation in address correction"""
    print("🔍 DEBUGGING TURKISH CHARACTER PRESERVATION")
    print("=" * 60)
    
    corrector = AddressCorrector()
    
    # Test cases that are currently failing
    test_cases = [
        "Kadıköy",
        "Caferağa",
        "10/A",
        "çankaya",
        "Müdür Sokak",
        "Üsküdar",
        "Şişli",
        "Göztepe"
    ]
    
    print("Testing each address:")
    for test_address in test_cases:
        print(f"\nInput: '{test_address}'")
        
        # Test the correction
        result = corrector.correct_address(test_address)
        output = result['corrected_address']
        
        print(f"Output: '{output}'")
        
        # Check for character loss - account for case changes
        turkish_chars_input = set(char.lower() for char in test_address if char.lower() in 'çğıiöşü')
        turkish_chars_output = set(char.lower() for char in output if char.lower() in 'çğıiöşü')
        
        if turkish_chars_input != turkish_chars_output:
            print(f"❌ TURKISH CHARACTERS LOST!")
            print(f"   Lost: {turkish_chars_input - turkish_chars_output}")
            print(f"   Added: {turkish_chars_output - turkish_chars_input}")
        else:
            print(f"✅ Turkish characters preserved")
        
        # Check for unwanted case changes
        if test_address == "10/A" and output != "10/A":
            print(f"❌ BUILDING NUMBER CASE BROKEN: '{output}' should be '10/A'")


def debug_normalization_methods():
    """Debug the normalization methods step by step"""
    print("\n🔧 DEBUGGING NORMALIZATION METHODS")
    print("=" * 60)
    
    corrector = AddressCorrector()
    test_input = "Kadıköy Caferağa 10/A"
    
    print(f"Original input: '{test_input}'")
    
    # Test step by step
    print("\nStep-by-step debugging:")
    
    # Step 1: Initial normalization  
    step1 = test_input.lower()  # This is the problematic line
    print(f"1. After .lower(): '{step1}'")
    
    # Step 2: Try _normalize_turkish_chars if available
    if hasattr(corrector, '_normalize_turkish_chars'):
        step2 = corrector._normalize_turkish_chars(test_input)
        print(f"2. After _normalize_turkish_chars(): '{step2}'")
    
    # Step 3: Full correction
    result = corrector.correct_address(test_input)
    print(f"3. Final result: '{result['corrected_address']}'")


def test_character_mappings():
    """Test the character mappings in the corrector"""
    print("\n📋 TESTING CHARACTER MAPPINGS")
    print("=" * 60)
    
    corrector = AddressCorrector()
    
    print("Character mappings loaded:")
    for char, variants in corrector.character_mappings.items():
        print(f"  {char} -> {variants}")


if __name__ == "__main__":
    test_turkish_character_preservation()
    debug_normalization_methods()
    test_character_mappings()