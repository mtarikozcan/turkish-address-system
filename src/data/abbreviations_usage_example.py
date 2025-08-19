"""
TEKNOFEST 2025 Adres Çözümleme Sistemi
Turkish Address Abbreviations Dictionary Usage Example

This example demonstrates how to use the abbreviations.json file
in the AddressCorrector algorithm for expanding Turkish address abbreviations.
"""

import json
import re
from typing import Dict, List, Tuple


class TurkishAbbreviationExpander:
    """Example implementation of Turkish abbreviation expansion for addresses"""
    
    def __init__(self, abbreviations_path: str = "src/data/abbreviations.json"):
        """Load abbreviations dictionary from JSON file"""
        with open(abbreviations_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Filter out comment keys and create lookup dictionary
        self.abbreviations = {
            k: v for k, v in data['abbreviations'].items() 
            if not k.startswith('_comment')
        }
        
        self.metadata = data['metadata']
        print(f"Loaded {len(self.abbreviations)} abbreviations in {len(self.metadata['categories'])} categories")
    
    def expand_abbreviations(self, address_text: str) -> Tuple[str, List[Dict]]:
        """
        Expand abbreviations in Turkish address text
        
        Args:
            address_text: Raw address string with potential abbreviations
            
        Returns:
            Tuple of (expanded_text, list_of_expansions_applied)
        """
        expanded_text = address_text
        expansions_applied = []
        
        # Split address into tokens (words)
        tokens = re.findall(r'\b\w+\.?\b', address_text)
        
        for token in tokens:
            # Try exact match first
            if token in self.abbreviations:
                replacement = self.abbreviations[token]
                expanded_text = expanded_text.replace(token, replacement)
                expansions_applied.append({
                    'original': token,
                    'expanded': replacement,
                    'type': 'exact_match'
                })
            
            # Try lowercase match
            elif token.lower() in self.abbreviations:
                replacement = self.abbreviations[token.lower()]
                expanded_text = expanded_text.replace(token, replacement)
                expansions_applied.append({
                    'original': token,
                    'expanded': replacement,
                    'type': 'case_insensitive_match'
                })
        
        return expanded_text, expansions_applied
    
    def get_category_abbreviations(self, category: str) -> Dict[str, str]:
        """Get all abbreviations for a specific category"""
        category_abbrevs = {}
        comment_key = f"_comment_{category}"
        
        # Find abbreviations that come after the category comment
        found_category = False
        for key, value in self.abbreviations.items():
            if key == comment_key:
                found_category = True
                continue
            if found_category and key.startswith('_comment_'):
                break  # Next category started
            if found_category:
                category_abbrevs[key] = value
        
        return category_abbrevs
    
    def demonstrate_expansions(self):
        """Demonstrate abbreviation expansion with example addresses"""
        
        test_addresses = [
            "Istanbul Bagcilar Mh. 1234 Sk. No:15 Apt:A",
            "Ankara Çankaya Kızılay Mah. Atatürk Blv. 25/3",
            "İzmir Konak Alsancak Mah. Kıbrıs Şehitleri Cd. 15/A",
            "Bursa Osmangazi Heykel Mah. Atatürk Cd. 100 Kat:2 D:5",
            "Antalya Muratpaşa Lara Mah. Kenan Evren Blv. 50 Site:B Bl:3"
        ]
        
        print("\n" + "="*80)
        print("TURKISH ADDRESS ABBREVIATION EXPANSION EXAMPLES")
        print("="*80)
        
        for i, address in enumerate(test_addresses, 1):
            print(f"\n{i}. Original Address:")
            print(f"   {address}")
            
            expanded, expansions = self.expand_abbreviations(address)
            print(f"   Expanded Address:")
            print(f"   {expanded}")
            
            if expansions:
                print(f"   Expansions Applied:")
                for exp in expansions:
                    print(f"   - {exp['original']} → {exp['expanded']} ({exp['type']})")
            else:
                print("   No abbreviations found to expand")
    
    def show_category_examples(self):
        """Show examples from each category"""
        print("\n" + "="*80)
        print("ABBREVIATION CATEGORIES AND EXAMPLES")
        print("="*80)
        
        for category in self.metadata['categories']:
            abbrevs = self.get_category_abbreviations(category)
            if abbrevs:
                print(f"\n{category.upper()} ({len(abbrevs)} abbreviations):")
                # Show first 5 examples
                for i, (abbrev, expansion) in enumerate(list(abbrevs.items())[:5]):
                    print(f"  {abbrev} → {expansion}")
                if len(abbrevs) > 5:
                    print(f"  ... and {len(abbrevs) - 5} more")


def main():
    """Main function to demonstrate abbreviation expansion"""
    try:
        # Initialize the expander
        expander = TurkishAbbreviationExpander()
        
        # Show statistics
        print(f"Dictionary Statistics:")
        print(f"- Total abbreviations: {len(expander.abbreviations)}")
        print(f"- Categories: {len(expander.metadata['categories'])}")
        print(f"- Features: {', '.join(expander.metadata['features'].keys())}")
        
        # Demonstrate expansions
        expander.demonstrate_expansions()
        
        # Show category examples
        expander.show_category_examples()
        
        print("\n" + "="*80)
        print("INTEGRATION WITH ADDRESSCORRECTOR")
        print("="*80)
        print("""
The abbreviations.json file can be integrated into the AddressCorrector class:

```python
class AddressCorrector:
    def __init__(self):
        # Load abbreviations dictionary
        with open('src/data/abbreviations.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.abbreviation_dict = {
            k: v for k, v in data['abbreviations'].items() 
            if not k.startswith('_comment')
        }
    
    def expand_abbreviations(self, text: str) -> tuple:
        # Implementation similar to example above
        pass
```

Performance: O(n*m) where n=tokens, m=avg_abbreviation_length
Memory: ~25KB for full dictionary in memory
Turkish Character Support: Full support for ç, ğ, ı, ö, ş, ü
        """)
        
    except FileNotFoundError:
        print("Error: abbreviations.json file not found!")
        print("Make sure the file exists at: src/data/abbreviations.json")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format: {e}")


if __name__ == "__main__":
    main()