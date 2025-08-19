"""
CRITICAL FIX: Turkish Character Handling for Address System
Fixes the character corruption issues in address processing
"""

import re
import unicodedata
from typing import Dict, Optional

class TurkishCharacterHandler:
    """
    Proper Turkish character handling without corruption
    Fixes issues like "İstiklal" → "I Stiklal" and "Tunalı" → "Tuna"
    """
    
    # Turkish character mappings
    TURKISH_LOWER_MAP = {
        'İ': 'i', 'I': 'ı', 
        'Ş': 'ş', 'Ğ': 'ğ', 
        'Ü': 'ü', 'Ö': 'ö', 
        'Ç': 'ç'
    }
    
    TURKISH_UPPER_MAP = {
        'i': 'İ', 'ı': 'I',
        'ş': 'Ş', 'ğ': 'Ğ',
        'ü': 'Ü', 'ö': 'Ö',
        'ç': 'Ç'
    }
    
    # Protected famous Turkish street/place names
    PROTECTED_NAMES = [
        'İstiklal', 'Tunalı Hilmi', 'Bağdat', 'Atatürk', 
        'Cumhuriyet', 'İnönü', 'Kızılay', 'Çankaya',
        'Beşiktaş', 'Kadıköy', 'Üsküdar', 'Şişli',
        'Bakırköy', 'Beyoğlu', 'Sarıyer', 'Büyükdere',
        'Nişantaşı', 'Etiler', 'Bebek', 'Ortaköy',
        'Çengelköy', 'Kanlıca', 'Paşabahçe', 'Beykoz',
        'Taksim', 'Galata', 'Karaköy', 'Eminönü',
        'Sultanahmet', 'Beyazıt', 'Çemberlitaş', 'Aksaray',
        'Laleli', 'Topkapı', 'Yenikapı', 'Bakırköy',
        'Ataköy', 'Yeşilköy', 'Florya', 'Yeşilyurt',
        'Pendik', 'Tuzla', 'Kartal', 'Maltepe',
        'Bostancı', 'Göztepe', 'Fenerbahçe', 'Moda',
        'Bahariye', 'Altıyol', 'Acıbadem', 'Kozyatağı',
        'Suadiye', 'Caddebostan', 'Erenköy', 'Küçükyalı'
    ]
    
    @staticmethod
    def turkish_lower(text: str) -> str:
        """
        Convert to lowercase with proper Turkish character handling
        İ → i, I → ı (Turkish specific rules)
        """
        if not text:
            return ""
            
        result = []
        for char in text:
            if char in TurkishCharacterHandler.TURKISH_LOWER_MAP:
                result.append(TurkishCharacterHandler.TURKISH_LOWER_MAP[char])
            else:
                result.append(char.lower())
        return ''.join(result)
    
    @staticmethod
    def turkish_upper(text: str) -> str:
        """
        Convert to uppercase with proper Turkish character handling
        i → İ, ı → I (Turkish specific rules)
        """
        if not text:
            return ""
            
        result = []
        for char in text:
            if char in TurkishCharacterHandler.TURKISH_UPPER_MAP:
                result.append(TurkishCharacterHandler.TURKISH_UPPER_MAP[char])
            else:
                result.append(char.upper())
        return ''.join(result)
    
    @staticmethod
    def turkish_title_case(text: str, preserve_protected: bool = True) -> str:
        """
        Apply title case with proper Turkish character handling
        Preserves protected names like "İstiklal", "Tunalı Hilmi"
        Also preserves building numbers like "10/A" correctly
        """
        if not text:
            return ""
        
        # First check if any protected names exist
        if preserve_protected:
            for protected_name in TurkishCharacterHandler.PROTECTED_NAMES:
                # Case-insensitive search but preserve original protected form
                pattern = re.compile(re.escape(protected_name), re.IGNORECASE)
                text = pattern.sub(protected_name, text)
        
        # Split into words and handle each
        words = text.split()
        result = []
        
        for word in words:
            # Check if word is a building number (e.g., "10/a", "5B", "23/A")
            if re.match(r'^\d+[/\-]?[A-Za-z]?$', word):
                # Preserve building number case - make sure letter part is uppercase
                if re.search(r'[a-zA-Z]', word):
                    # Has letter component - ensure it's uppercase
                    building_num = re.sub(r'([a-zA-Z])', lambda m: m.group(1).upper(), word)
                else:
                    # Just numbers - keep as is
                    building_num = word
                result.append(building_num)
                continue
            
            # Check if word is protected
            is_protected = False
            for protected_name in TurkishCharacterHandler.PROTECTED_NAMES:
                if TurkishCharacterHandler.turkish_lower(word) == TurkishCharacterHandler.turkish_lower(protected_name):
                    result.append(protected_name)
                    is_protected = True
                    break
            
            if not is_protected:
                # Apply Turkish title case
                if len(word) > 0:
                    # Convert to lowercase first to avoid double capitalization
                    lower_word = TurkishCharacterHandler.turkish_lower(word)
                    
                    # First character uppercase (Turkish aware)
                    first_char = lower_word[0]
                    if first_char in ['i', 'ı', 'ş', 'ğ', 'ü', 'ö', 'ç']:
                        first_upper = TurkishCharacterHandler.TURKISH_UPPER_MAP.get(first_char, first_char.upper())
                    else:
                        first_upper = first_char.upper()
                    
                    # Rest stays lowercase
                    rest = lower_word[1:] if len(lower_word) > 1 else ""
                    result.append(first_upper + rest)
                else:
                    result.append(word)
        
        return ' '.join(result)
    
    @staticmethod
    def normalize_turkish_text(text: str, preserve_protected: bool = True) -> str:
        """
        Normalize Turkish text while preserving character integrity
        Does NOT corrupt İ to I or remove dots
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # DO NOT normalize unicode - it corrupts Turkish characters!
        # Keep original Turkish characters intact
        
        return text
    
    @staticmethod
    def fix_common_corruptions(text: str) -> str:
        """
        Fix common Turkish character corruptions
        """
        if not text:
            return ""
        
        # Fix common corruptions
        corrections = {
            'I Stiklal': 'İstiklal',
            'I Stanbul': 'İstanbul',
            'I Zmir': 'İzmir',
            'Tuna Hilmi': 'Tunalı Hilmi',
            'Tunal Hilmi': 'Tunalı Hilmi',
            'Kadky': 'Kadıköy',
            'Sisli': 'Şişli',
            'Uskudar': 'Üsküdar',
            'Bakrky': 'Bakırköy',
            'Beyolu': 'Beyoğlu',
            'Ataky': 'Ataköy',
            'Yesilyurt': 'Yeşilyurt',
            'Gztepe': 'Göztepe',
            'Kk': 'Küçük',
            'Byk': 'Büyük',
            'Atatrk': 'Atatürk',
            'ankaya': 'Çankaya',
            'Ataşehir': 'Ataşehir'
        }
        
        # Apply corrections with word boundaries to avoid partial matches
        for wrong, correct in corrections.items():
            # Use word boundary regex to avoid corrupting partial matches
            # Only replace if it's a complete word, not a substring
            pattern = r'\b' + re.escape(wrong) + r'\b'
            text = re.sub(pattern, correct, text, flags=re.IGNORECASE)
        
        return text


class ImprovedAddressCorrector:
    """
    Improved address corrector with proper Turkish character handling
    """
    
    def __init__(self):
        self.char_handler = TurkishCharacterHandler()
        
        # Safe abbreviations that won't corrupt Turkish text
        self.safe_abbreviations = {
            'mh': 'mahallesi',
            'mah': 'mahallesi',
            'cd': 'caddesi',
            'cad': 'caddesi',
            'sk': 'sokak',
            'sok': 'sokak',
            'blv': 'bulvarı',
            'apt': 'apartmanı',
            'no': 'numara',
            'kat': 'kat',
            'blok': 'blok'
        }
        
        # Harmful corrections to REMOVE
        self.harmful_corrections = [
            'tunali', 'tuna',  # Corrupts Tunalı Hilmi
            'istanbul', 'istanbol',  # Wrong
            'hilmi', 'hi',  # Corrupts names
        ]
    
    def correct_address(self, raw_address: str) -> Dict:
        """
        Correct address with proper Turkish character preservation
        """
        if not raw_address:
            return {
                "original_address": "",
                "corrected_address": "",
                "corrections_applied": [],
                "confidence": 0.0
            }
        
        corrections_applied = []
        
        # Step 1: Normalize (but preserve Turkish chars!)
        working_address = self.char_handler.normalize_turkish_text(raw_address)
        if working_address != raw_address:
            corrections_applied.append("Normalized whitespace")
        
        # Step 2: Fix known corruptions
        fixed_address = self.char_handler.fix_common_corruptions(working_address)
        if fixed_address != working_address:
            corrections_applied.append("Fixed character corruptions")
            working_address = fixed_address
        
        # Step 3: Expand abbreviations safely
        words = working_address.split()
        expanded_words = []
        for word in words:
            word_lower = self.char_handler.turkish_lower(word)
            # Remove trailing dots for abbreviation matching
            word_clean = word_lower.rstrip('.')
            
            if word_clean in self.safe_abbreviations:
                expanded_words.append(self.safe_abbreviations[word_clean])
                if word_clean != word_lower:
                    corrections_applied.append(f"Expanded {word} to {self.safe_abbreviations[word_clean]}")
            else:
                expanded_words.append(word)
        
        working_address = ' '.join(expanded_words)
        
        # Step 4: Apply proper Turkish title case
        final_address = self.char_handler.turkish_title_case(working_address, preserve_protected=True)
        if final_address != working_address:
            corrections_applied.append("Applied Turkish title case")
        
        # Calculate confidence
        confidence = min(1.0, 0.7 + (len(corrections_applied) * 0.1))
        
        return {
            "original_address": raw_address,
            "corrected_address": final_address,
            "corrections_applied": corrections_applied,
            "confidence": confidence
        }


# Test the fix
if __name__ == "__main__":
    corrector = ImprovedAddressCorrector()
    
    # Test cases that were failing
    test_cases = [
        "istanbul kadikoy moda mh",
        "İstiklal Caddesi",
        "istiklal caddesi", 
        "ankara tunali hilmi caddesi",
        "TUNALI HİLMİ CADDESİ",
        "şişli mecidiyeköy büyükdere cd.",
        "üsküdar bağlarbaşı mah.",
        "beyoğlu istiklal cd no:127/A"
    ]
    
    print("🔧 TESTING TURKISH CHARACTER FIX")
    print("=" * 60)
    
    for test_address in test_cases:
        result = corrector.correct_address(test_address)
        print(f"\n📍 Input:  {test_address}")
        print(f"✅ Output: {result['corrected_address']}")
        if result['corrections_applied']:
            print(f"📝 Corrections: {', '.join(result['corrections_applied'])}")
        print(f"🎯 Confidence: {result['confidence']:.2f}")
    
    print("\n" + "=" * 60)
    print("✅ Turkish character handling test complete!")