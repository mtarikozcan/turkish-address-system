#!/usr/bin/env python3
"""
Debug Pattern 4 specifically
"""

import re

def debug_pattern4():
    """Debug the specific pattern that should match 10/A but isn't working"""
    
    pattern = r'\b(\d+[\/\-][a-zA-Z]+)(?:\s+|$)'
    test_cases = [
        "10/A Daire:3",
        "15/C Daire:5", 
        "Sokak 20/D"
    ]
    
    print("🔍 DEBUGGING PATTERN 4")
    print("=" * 60)
    print(f"Pattern: {pattern}")
    print()
    
    for address in test_cases:
        print(f"Testing: '{address}'")
        match = re.search(pattern, address, re.IGNORECASE)
        if match:
            print(f"  ✅ MATCH: '{match.group(1)}'")
            print(f"  Full match: '{match.group(0)}'")
            print(f"  Match span: {match.span()}")
        else:
            print(f"  ❌ NO MATCH")
        
        # Test if the issue is with the (?:\s+|$) part
        simple_pattern = r'\b(\d+[\/\-][a-zA-Z]+)'
        match2 = re.search(simple_pattern, address, re.IGNORECASE)
        if match2:
            print(f"  Simple pattern match: '{match2.group(1)}'")
        print()

if __name__ == "__main__":
    debug_pattern4()