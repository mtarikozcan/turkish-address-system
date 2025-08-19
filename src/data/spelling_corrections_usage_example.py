"""
Address Resolution System
Turkish Address Spelling Corrections Usage Example

This example demonstrates how to use the spelling_corrections.json file
in the AddressCorrector algorithm for fixing Turkish address misspellings.
"""

import json
import re
from typing import Dict, List, Tuple, Optional
from difflib import SequenceMatcher


class TurkishSpellingCorrector:
    """Example implementation of Turkish spelling correction for addresses"""
    
    def __init__(self, corrections_path: str = "src/data/spelling_corrections.json"):
        """Load spelling corrections dictionary from JSON file"""
        with open(corrections_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Load different correction types
        self.spelling_corrections = {
            k: v for k, v in data['spelling_corrections'].items() 
            if not k.startswith('_comment')
        }
        
        self.character_mappings = data['character_mappings']
        self.pattern_corrections = data['pattern_corrections']
        self.contextual_corrections = data['contextual_corrections']
        self.frequency_corrections = data['frequency_corrections']
        self.metadata = data['metadata']
        
        print(f"Loaded {len(self.spelling_corrections)} spelling corrections")
        print(f"Categories: {len(self.metadata['categories'])}")
    
    def correct_spelling_errors(self, address_text: str, city_context: str = None) -> Tuple[str, List[Dict]]:
        """
        Correct spelling errors in Turkish address text
        
        Args:
            address_text: Raw address string with potential spelling errors
            city_context: Optional city context for contextual corrections
            
        Returns:
            Tuple of (corrected_text, list_of_corrections_applied)
        """
        corrected_text = address_text.lower()
        corrections_applied = []
        
        # Step 1: Direct spelling corrections (highest priority)
        for wrong, correct in self.spelling_corrections.items():
            if wrong in corrected_text:
                corrected_text = corrected_text.replace(wrong, correct)
                corrections_applied.append({
                    'type': 'direct_spelling',
                    'original': wrong,
                    'corrected': correct,
                    'confidence': 0.95
                })
        
        # Step 2: Character mapping corrections
        corrected_text, char_corrections = self._apply_character_mappings(corrected_text)
        corrections_applied.extend(char_corrections)
        
        # Step 3: Pattern-based corrections
        corrected_text, pattern_corrections = self._apply_pattern_corrections(corrected_text)
        corrections_applied.extend(pattern_corrections)
        
        # Step 4: Contextual corrections (if city context provided)
        if city_context:
            corrected_text, context_corrections = self._apply_contextual_corrections(
                corrected_text, city_context.lower()
            )
            corrections_applied.extend(context_corrections)
        
        # Step 5: Fuzzy matching for remaining errors
        corrected_text, fuzzy_corrections = self._apply_fuzzy_corrections(corrected_text)
        corrections_applied.extend(fuzzy_corrections)
        
        return corrected_text, corrections_applied
    
    def _apply_character_mappings(self, text: str) -> Tuple[str, List[Dict]]:
        """Apply Turkish character substitution mappings"""
        corrected_text = text
        corrections = []
        
        # Apply character mappings
        char_map = {
            'i': 'ı', 'g': 'ğ', 'u': 'ü', 'o': 'ö', 's': 'ş', 'c': 'ç'
        }
        
        # Apply contextual character corrections (simplified)
        for wrong_char, correct_char in char_map.items():
            # This is a simplified version - in practice, you'd use context
            # to determine when to apply these corrections
            pass
        
        return corrected_text, corrections
    
    def _apply_pattern_corrections(self, text: str) -> Tuple[str, List[Dict]]:
        """Apply regex pattern-based corrections"""
        corrected_text = text
        corrections = []
        
        # Fix double letters
        double_letter_pattern = r'([bcdfghjklmnpqrstvwxyz])\1+'
        matches = re.finditer(double_letter_pattern, text)
        for match in matches:
            original = match.group()
            corrected = match.group(1)
            corrected_text = corrected_text.replace(original, corrected)
            corrections.append({
                'type': 'pattern_double_letter',
                'original': original,
                'corrected': corrected,
                'confidence': 0.80
            })
        
        # Apply missing Turkish character patterns
        missing_patterns = self.pattern_corrections.get('missing_turkish_chars', {}).get('patterns', {})
        for wrong, correct in missing_patterns.items():
            if wrong in corrected_text:
                corrected_text = corrected_text.replace(wrong, correct)
                corrections.append({
                    'type': 'pattern_missing_char',
                    'original': wrong,
                    'corrected': correct,
                    'confidence': 0.85
                })
        
        return corrected_text, corrections
    
    def _apply_contextual_corrections(self, text: str, city_context: str) -> Tuple[str, List[Dict]]:
        """Apply city-specific contextual corrections"""
        corrected_text = text
        corrections = []
        
        # Get contextual corrections for the city
        context_key = f"{city_context}_context"
        if context_key in self.contextual_corrections:
            context_corrections = self.contextual_corrections[context_key]
            
            for wrong, correct in context_corrections.items():
                if wrong in corrected_text:
                    corrected_text = corrected_text.replace(wrong, correct)
                    corrections.append({
                        'type': 'contextual',
                        'original': wrong,
                        'corrected': correct,
                        'context': city_context,
                        'confidence': 0.90
                    })
        
        return corrected_text, corrections
    
    def _apply_fuzzy_corrections(self, text: str) -> Tuple[str, List[Dict]]:
        """Apply fuzzy matching for remaining errors"""
        corrected_text = text
        corrections = []
        
        # Split into words and check each word
        words = text.split()
        corrected_words = []
        
        for word in words:
            best_match = self._find_best_fuzzy_match(word)
            if best_match and best_match['similarity'] > 0.75:
                corrected_words.append(best_match['correction'])
                corrections.append({
                    'type': 'fuzzy_match',
                    'original': word,
                    'corrected': best_match['correction'],
                    'confidence': best_match['similarity']
                })
            else:
                corrected_words.append(word)
        
        corrected_text = ' '.join(corrected_words)
        return corrected_text, corrections
    
    def _find_best_fuzzy_match(self, word: str) -> Optional[Dict]:
        """Find best fuzzy match for a word using similarity scoring"""
        best_match = None
        best_similarity = 0
        
        # Check against high-frequency corrections first
        for correct_word, misspellings in self.frequency_corrections.get('very_common', {}).items():
            for misspelling in misspellings:
                similarity = SequenceMatcher(None, word, misspelling).ratio()
                if similarity > best_similarity and similarity > 0.75:
                    best_similarity = similarity
                    best_match = {
                        'correction': correct_word,
                        'similarity': similarity,
                        'type': 'high_frequency'
                    }
        
        # Check against all spelling corrections
        for wrong, correct in self.spelling_corrections.items():
            similarity = SequenceMatcher(None, word, wrong).ratio()
            if similarity > best_similarity and similarity > 0.70:
                best_similarity = similarity
                best_match = {
                    'correction': correct,
                    'similarity': similarity,
                    'type': 'spelling_correction'
                }
        
        return best_match
    
    def demonstrate_corrections(self):
        """Demonstrate spelling correction with example addresses"""
        
        test_addresses = [
            ("istbl kadikoy moda mah.", "istanbul"),
            ("ankara cankaya kızılay mah. atatuk cd.", "ankara"), 
            ("izmır karsiyaka bostanli mah.", "izmir"),
            ("bursa osmangazi heykel mah. atatuk cd.", "bursa"),
            ("antalya muratpasa lara mah. kenan evren blv.", "antalya"),
            ("istanbul besiktas levent mah. büyukdere cd.", "istanbul"),
            ("ankara kecioren etlik mah. cumhurıyet cd.", "ankara"),
            ("izmir bornova erzene mah. kazimdirik cd.", "izmir")
        ]
        
        print("\n" + "="*80)
        print("TURKISH ADDRESS SPELLING CORRECTION EXAMPLES")
        print("="*80)
        
        for i, (address, city) in enumerate(test_addresses, 1):
            print(f"\n{i}. Original Address:")
            print(f"   {address}")
            print(f"   City Context: {city}")
            
            corrected, corrections = self.correct_spelling_errors(address, city)
            print(f"   Corrected Address:")
            print(f"   {corrected}")
            
            if corrections:
                print(f"   Corrections Applied:")
                for corr in corrections:
                    print(f"   - {corr['original']} → {corr['corrected']} "
                          f"({corr['type']}, confidence: {corr.get('confidence', 'N/A'):.2f})")
            else:
                print("   No corrections needed")
    
    def show_correction_categories(self):
        """Show examples from each correction category"""
        print("\n" + "="*80)
        print("SPELLING CORRECTION CATEGORIES AND EXAMPLES")
        print("="*80)
        
        # Show character mappings
        print(f"\nCHARACTER MAPPINGS:")
        for char, alternatives in self.character_mappings.items():
            if not char.startswith('_'):
                print(f"  {char} ↔ {alternatives}")
        
        # Show frequency corrections
        print(f"\nHIGH-FREQUENCY CORRECTIONS:")
        for correct, misspellings in list(self.frequency_corrections.get('very_common', {}).items())[:5]:
            print(f"  {correct}: {', '.join(misspellings)}")
        
        # Show contextual corrections
        print(f"\nCONTEXTUAL CORRECTIONS (Istanbul):")
        istanbul_corrections = self.contextual_corrections.get('istanbul_context', {})
        for wrong, correct in list(istanbul_corrections.items())[:5]:
            print(f"  {wrong} → {correct}")


def main():
    """Main function to demonstrate spelling corrections"""
    try:
        # Initialize the corrector
        corrector = TurkishSpellingCorrector()
        
        # Show statistics
        print(f"Dictionary Statistics:")
        print(f"- Total spelling corrections: {len(corrector.spelling_corrections)}")
        print(f"- Character mappings: {len([k for k in corrector.character_mappings.keys() if not k.startswith('_')])}")
        print(f"- Categories: {len(corrector.metadata['categories'])}")
        
        # Demonstrate corrections
        corrector.demonstrate_corrections()
        
        # Show category examples
        corrector.show_correction_categories()
        
        print("\n" + "="*80)
        print("INTEGRATION WITH ADDRESSCORRECTOR")
        print("="*80)
        print("""
The spelling_corrections.json file can be integrated into the AddressCorrector class:

```python
class AddressCorrector:
    def __init__(self):
        # Load spelling corrections dictionary
        with open('src/data/spelling_corrections.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.spelling_corrections = data['spelling_corrections']
        self.character_mappings = data['character_mappings']
        self.contextual_corrections = data['contextual_corrections']
    
    def correct_spelling_errors(self, text: str, city_context: str = None) -> tuple:
        # Multi-level correction approach:
        # 1. Direct spelling corrections (highest confidence)
        # 2. Character mapping corrections
        # 3. Pattern-based corrections  
        # 4. Contextual corrections (city-specific)
        # 5. Fuzzy matching (lowest confidence)
        pass
```

Features:
- 285+ spelling corrections for Turkish addresses
- Character substitution mappings (ı↔i, ğ↔g, ü↔u, ö↔o, ş↔s, ç↔c)
- City-specific contextual corrections
- Pattern-based corrections (double letters, missing chars)
- Frequency-based prioritization
- Confidence scoring for each correction type

Performance: O(n) for direct lookups, O(n*m) for fuzzy matching
Memory: ~45KB for full correction dictionary
        """)
        
    except FileNotFoundError:
        print("Error: spelling_corrections.json file not found!")
        print("Make sure the file exists at: src/data/spelling_corrections.json")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format: {e}")


if __name__ == "__main__":
    main()