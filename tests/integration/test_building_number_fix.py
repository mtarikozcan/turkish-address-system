#!/usr/bin/env python3
"""
Test building number parsing fix
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from address_parser import AddressParser

def test_building_number_parsing():
    """Test building number parsing with problematic cases"""
    print("🔍 TESTING BUILDING NUMBER PARSING - CURRENT BEHAVIOR")
    print("=" * 70)
    
    parser = AddressParser()
    
    test_cases = [
        "10/A Daire:3",
        "No:25/B Kat:2",  
        "15/C Daire:5",
        "Sokak 20/D",
        "Numara:12/A Daire:8"
    ]
    
    for address in test_cases:
        print(f"\n📍 Testing: '{address}'")
        print("-" * 50)
        
        result = parser.parse_address(address)
        
        print(f"✅ Parsed result: {result}")
        
        # Check building number related fields from components
        components = result.get('components', {})
        building_fields = ['bina_no', 'daire_no', 'daire', 'kat', 'blok']
        found_fields = {k: v for k, v in components.items() if k in building_fields and v}
        if found_fields:
            print(f"   Building fields found: {found_fields}")
        else:
            print(f"   No building fields extracted")
            
        # Check if this matches expected behavior
        if address == "10/A Daire:3":
            expected_bina = "10/A"
            expected_daire = "3"
            actual_bina = components.get('bina_no', '')
            actual_daire = components.get('daire_no', components.get('daire', ''))
            
            if actual_bina == expected_bina and actual_daire == expected_daire:
                print(f"   ✅ CORRECT: Expected bina_no='{expected_bina}', daire_no='{expected_daire}'")
            else:
                print(f"   ❌ WRONG: Expected bina_no='{expected_bina}', daire_no='{expected_daire}'")
                print(f"            Got bina_no='{actual_bina}', daire_no='{actual_daire}'")

if __name__ == "__main__":
    test_building_number_parsing()