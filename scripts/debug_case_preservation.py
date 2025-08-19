#!/usr/bin/env python3
"""
Debug case preservation in semantic pattern engine
"""

import re

def test_case_preservation():
    address = "15.sk no 25/A kat 3"
    
    print(f"Testing address: '{address}'")
    
    # Test original pattern
    no_slash_pattern = r'no\s*(\d+(?:[/\-][a-zA-Z0-9]+)?)\s*[/\-]\s*(\d+)'
    
    for match in re.finditer(no_slash_pattern, address, re.IGNORECASE):
        print(f"\nFound match: '{match.group(0)}'")
        print(f"Groups: {match.groups()}")
        print(f"Group 1: '{match.group(1)}' (building)")
        print(f"Group 2: '{match.group(2)}' (apartment)")
        
        # Test case preservation
        start, end = match.span()
        original_segment = address[start:end]
        print(f"Original segment: '{original_segment}'")
        
        # Re-extract from original case-preserved segment
        case_match = re.search(no_slash_pattern, original_segment, re.IGNORECASE)
        if case_match:
            print(f"Case-preserved groups: {case_match.groups()}")
            print(f"Building (case-preserved): '{case_match.group(1)}'")
        break

def test_building_patterns():
    test_cases = [
        "no 25/A kat 3",
        "numara 5-B daire 7",
        "15-C blok 2"
    ]
    
    building_patterns = [
        r'no\s+(\\d+[/\\-][a-zA-Z0-9]+)(?:\s+kat\s+(\\d+))?',
        r'(?:no\\.?\s*|numara\s*)?(\d+[/\-][a-zA-Z0-9]+)(?:\s+(?:daire|kat)\s+(\d+))?',
        r'(?:no\\.?\s*|numara\s*)?(\d+)(?:\s+(?:blok|block)\s+([a-zA-Z]))(?:\s+(?:daire|kat)\s+(\d+))?',
    ]
    
    for test_case in test_cases:
        print(f"\nTesting: '{test_case}'")
        
        for i, pattern in enumerate(building_patterns):
            for match in re.finditer(pattern, test_case, re.IGNORECASE):
                print(f"  Pattern {i}: match='{match.group(0)}', groups={match.groups()}")
                
                # Test case preservation
                start, end = match.span()
                original_segment = test_case[start:end]
                print(f"  Original segment: '{original_segment}'")
                
                case_match = re.search(pattern, original_segment, re.IGNORECASE)
                if case_match:
                    print(f"  Case-preserved groups: {case_match.groups()}")
                break

if __name__ == "__main__":
    test_case_preservation()
    test_building_patterns()