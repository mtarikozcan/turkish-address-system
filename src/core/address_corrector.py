"""
Address Resolution System - Address Corrector Algorithm

Algorithm 2: Address Corrector
Turkish address spelling error correction and normalization algorithm

Purpose: Correct Turkish address spelling errors, expand abbreviations,
and normalize text for improved parsing and validation accuracy.
"""

import json
import os
import logging
import re
import unicodedata
from typing import Dict, List, Optional, Tuple, Any, Set
from pathlib import Path
import difflib

# Import centralized Turkish text utilities
try:
    from turkish_text_utils import TurkishTextNormalizer
    TURKISH_UTILS_AVAILABLE = True
except ImportError:
    TURKISH_UTILS_AVAILABLE = False
    # Fallback class if utils not available
    class TurkishTextNormalizer:
        @staticmethod
        def turkish_title(text): return text.title()
        @staticmethod
        def normalize_for_comparison(text): return text.lower()

# Import the fixed Turkish character handler
try:
    from turkish_character_fix import TurkishCharacterHandler, ImprovedAddressCorrector
    TURKISH_FIX_AVAILABLE = True
except ImportError:
    TURKISH_FIX_AVAILABLE = False


class AddressCorrector:
    """
    Turkish Address Corrector Algorithm
    
    Corrects spelling errors, expands abbreviations, and normalizes
    Turkish address text according to system specifications.
    """
    
    def __init__(self):
        """
        Initialize AddressCorrector with Turkish correction data
        
        Loads:
        - Turkish abbreviations dictionary
        - Common spelling corrections
        - Character mappings for Turkish characters
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Initialize Turkish character handler if available
        self.turkish_handler = TurkishCharacterHandler() if TURKISH_FIX_AVAILABLE else None
        
        # Create console handler if none exists
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        # Initialize correction data structures
        self.abbreviation_dict = {}
        self.common_errors = {}
        self.character_mappings = {}
        self.reverse_abbreviations = {}
        self.error_patterns = {}
        
        # Load correction data
        try:
            self.abbreviation_dict = self.load_abbreviations()
            self.common_errors = self.load_spelling_corrections()
            self.character_mappings = self.load_character_mappings()
            self._build_indexes()
            self.logger.info("AddressCorrector initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize AddressCorrector: {e}")
            raise
    
    def load_abbreviations(self) -> Dict[str, str]:
        """
        Load Turkish abbreviations dictionary from JSON file
        
        Returns:
            Dict mapping abbreviations to full forms
            
        Raises:
            FileNotFoundError: If abbreviations.json file not found
            json.JSONDecodeError: If JSON file is malformed
        """
        try:
            # Get the project root directory
            current_dir = Path(__file__).parent
            json_path = current_dir / "data" / "abbreviations.json"
            
            if not json_path.exists():
                self.logger.warning(f"Abbreviations JSON not found at {json_path}, using fallback data")
                return self._get_fallback_abbreviations()
            
            # Load JSON data
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Flatten the nested structure
            abbreviations = {}
            for category, abbrev_list in data.items():
                if isinstance(abbrev_list, dict):
                    for abbrev, full_form in abbrev_list.items():
                        # Skip comment entries
                        if abbrev.startswith('_comment'):
                            continue
                        
                        # Ensure both abbrev and full_form are strings
                        abbrev_str = str(abbrev).lower()
                        full_form_str = str(full_form).lower()
                        
                        # Store both with and without periods
                        abbreviations[abbrev_str] = full_form_str
                        if not abbrev_str.endswith('.'):
                            abbreviations[f"{abbrev_str}."] = full_form_str
                elif isinstance(abbrev_list, list):
                    # Handle list format
                    for item in abbrev_list:
                        if isinstance(item, dict) and 'abbreviation' in item and 'full_form' in item:
                            abbrev_str = str(item['abbreviation']).lower()
                            full_form_str = str(item['full_form']).lower()
                            abbreviations[abbrev_str] = full_form_str
                            if not abbrev_str.endswith('.'):
                                abbreviations[f"{abbrev_str}."] = full_form_str
            
            self.logger.info(f"Loaded {len(abbreviations)} abbreviations from JSON")
            return abbreviations
            
        except FileNotFoundError:
            self.logger.warning("Abbreviations JSON file not found, using fallback data")
            return self._get_fallback_abbreviations()
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing abbreviations JSON: {e}")
            return self._get_fallback_abbreviations()
        except Exception as e:
            self.logger.error(f"Error loading abbreviations: {e}")
            return self._get_fallback_abbreviations()
    
    def load_spelling_corrections(self) -> Dict[str, str]:
        """
        Load Turkish spelling corrections dictionary from JSON file
        
        Returns:
            Dict mapping common errors to correct spellings
            
        Raises:
            FileNotFoundError: If spelling_corrections.json file not found
            json.JSONDecodeError: If JSON file is malformed
        """
        try:
            # Get the project root directory
            current_dir = Path(__file__).parent
            json_path = current_dir / "data" / "spelling_corrections.json"
            
            if not json_path.exists():
                self.logger.warning(f"Spelling corrections JSON not found at {json_path}, using fallback data")
                return self._get_fallback_spelling_corrections()
            
            # Load JSON data
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Flatten the nested structure  
            corrections = {}
            for category, correction_list in data.items():
                # Skip metadata categories
                if category in ['character_mappings', 'pattern_corrections', 'contextual_corrections', 'categories']:
                    continue
                    
                if isinstance(correction_list, dict):
                    for error, correct in correction_list.items():
                        # Skip comment entries and character mappings
                        if error.startswith('_comment') or error in ['character_mappings', 'pattern_corrections', 'contextual_corrections']:
                            continue
                        
                        # Skip entries where the correction is a list (character mappings)
                        if isinstance(correct, list):
                            continue
                        
                        error_str = str(error).lower()
                        correct_str = str(correct).lower()
                        corrections[error_str] = correct_str
                elif isinstance(correction_list, list):
                    # Handle list format
                    for item in correction_list:
                        if isinstance(item, dict) and 'error' in item and 'correction' in item:
                            error_str = str(item['error']).lower()
                            correct_str = str(item['correction']).lower()
                            corrections[error_str] = correct_str
            
            self.logger.info(f"Loaded {len(corrections)} spelling corrections from JSON")
            return corrections
            
        except FileNotFoundError:
            self.logger.warning("Spelling corrections JSON file not found, using fallback data")
            return self._get_fallback_spelling_corrections()
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing spelling corrections JSON: {e}")
            return self._get_fallback_spelling_corrections()
        except Exception as e:
            self.logger.error(f"Error loading spelling corrections: {e}")
            return self._get_fallback_spelling_corrections()
    
    def load_character_mappings(self) -> Dict[str, List[str]]:
        """
        Load Turkish character mappings ONLY for encoding corrections
        
        Returns:
            Dict mapping corrupted characters to their correct forms
        """
        try:
            # CRITICAL FIX: Only map encoding errors, NOT legitimate Turkish characters
            # These mappings should NOT be used for automatic character replacement
            # They are reference data only for specific correction contexts
            mappings = {
                # Only encoding corruption fixes - NOT character replacement
                'i̇': ['i'],     # Combining dot above (encoding issue)
                'ı̇': ['i'],     # Dotless i with combining dot (encoding issue)
                'â': ['a'],     # Circumflex accent (not Turkish)
                'î': ['i'],     # Circumflex accent (not Turkish) 
                'û': ['u'],     # Circumflex accent (not Turkish)
                'ê': ['e'],     # Circumflex accent (not Turkish)
                'ô': ['o'],     # Circumflex accent (not Turkish)
            }
            
            self.logger.info(f"Loaded {len(mappings)} character mappings")
            return mappings
            
        except Exception as e:
            self.logger.error(f"Error loading character mappings: {e}")
            return {}
    
    def _build_indexes(self):
        """Build reverse indexes and patterns for efficient correction"""
        try:
            # Build reverse abbreviation index
            self.reverse_abbreviations = {v: k for k, v in self.abbreviation_dict.items()}
            
            # Build error patterns for faster matching
            self.error_patterns = {}
            for error, correction in self.common_errors.items():
                pattern = re.compile(re.escape(error), re.IGNORECASE)
                self.error_patterns[pattern] = correction
            
            self.logger.debug("Built correction indexes successfully")
            
        except Exception as e:
            self.logger.error(f"Error building indexes: {e}")
    
    def correct_address(self, raw_address: str) -> dict:
        """
        Main correction function for Turkish addresses
        
        Args:
            raw_address: Original address string to correct
            
        Returns:
            Dictionary with correction results:
            {
                "original_address": str,
                "corrected_address": str, 
                "corrections_applied": List[str],
                "confidence": float
            }
        """
        try:
            # Input validation
            if not raw_address or not isinstance(raw_address, str):
                return {
                    "original_address": raw_address,
                    "corrected_address": raw_address,
                    "corrections_applied": [],
                    "confidence": 0.0
                }
            
            corrections_applied = []
            
            # Step 1: Normalize while preserving Turkish characters
            working_address = self._preserve_turkish_normalization(raw_address)
            
            # Step 1: Expand abbreviations
            expanded_address = self.expand_abbreviations(working_address)
            if expanded_address != working_address:
                corrections_applied.append(f"Expanded abbreviations")
                working_address = expanded_address
            
            # Step 2: Fix spelling errors
            corrected_address = self.correct_spelling_errors(working_address)
            if corrected_address != working_address:
                corrections_applied.append(f"Fixed spelling errors")
                working_address = corrected_address
            
            # Step 3: Proper Turkish capitalization
            if TURKISH_FIX_AVAILABLE and self.turkish_handler:
                # Use the fixed Turkish title case
                final_address = self.turkish_handler.turkish_title_case(working_address, preserve_protected=True)
                # Fix any known corruptions
                final_address = self.turkish_handler.fix_common_corruptions(final_address)
            else:
                final_address = self._apply_turkish_capitalization(working_address)
            
            if final_address != working_address:
                corrections_applied.append(f"Applied Turkish capitalization")
            
            # Calculate confidence based on corrections applied
            confidence = min(1.0, 0.7 + (len(corrections_applied) * 0.1))
            
            return {
                "original_address": raw_address,
                "corrected_address": final_address,
                "corrections_applied": corrections_applied,
                "confidence": confidence
            }
            
        except Exception as e:
            self.logger.error(f"Error in correct_address: {e}")
            return {
                "original_address": raw_address,
                "corrected_address": raw_address,
                "corrections_applied": [f"Error: {str(e)}"],
                "confidence": 0.0
            }
    
    def expand_abbreviations(self, address: str) -> str:
        """
        Expand Turkish address abbreviations
        
        Args:
            address: Address string with abbreviations
            
        Returns:
            Address string with expanded abbreviations
        """
        try:
            if not address:
                return ""
            
            # Split address into words for processing
            words = address.split()
            expanded_words = []
            
            for word in words:
                # Clean word for matching but preserve original Turkish characters
                clean_word = re.sub(r'[^\w]', '', word)
                clean_word_lower = clean_word.lower()
                
                # Check for exact abbreviation match
                if clean_word_lower in self.abbreviation_dict:
                    expanded_words.append(self.abbreviation_dict[clean_word_lower])
                    self.logger.debug(f"Expanded abbreviation: {word} → {self.abbreviation_dict[clean_word_lower]}")
                # Check for abbreviation with period
                elif f"{clean_word_lower}." in self.abbreviation_dict:
                    expanded_words.append(self.abbreviation_dict[f"{clean_word_lower}."])
                    self.logger.debug(f"Expanded abbreviation: {word} → {self.abbreviation_dict[f'{clean_word_lower}.']}")
                else:
                    # Keep original word with Turkish characters preserved
                    expanded_words.append(word)
            
            return ' '.join(expanded_words)
            
        except Exception as e:
            self.logger.error(f"Error expanding abbreviations: {e}")
            return address
    
    def correct_spelling_errors(self, address: str) -> str:
        """
        Correct common Turkish spelling errors in addresses with fuzzy matching
        
        This is CRITICAL FIX #2 for improving success rate from 20% to 80%+
        
        Args:
            address: Address string with potential spelling errors
            
        Returns:
            Address string with corrected spelling
        """
        try:
            if not address:
                return ""
            
            corrected_address = address
            words = corrected_address.split()
            corrected_words = []
            
            for word in words:
                # Check exact match in common errors first
                if word in self.common_errors:
                    corrected_word = self.common_errors[word]
                    corrected_words.append(corrected_word)
                    self.logger.debug(f"Exact spelling correction: {word} → {corrected_word}")
                else:
                    # Try fuzzy matching for administrative names (CRITICAL FIX #2)
                    fuzzy_corrected = self._fuzzy_correct_administrative_name(word)
                    if fuzzy_corrected and fuzzy_corrected != word:
                        corrected_words.append(fuzzy_corrected)
                        self.logger.debug(f"Fuzzy correction: {word} → {fuzzy_corrected}")
                    else:
                        corrected_words.append(word)
            
            return ' '.join(corrected_words)
            
        except Exception as e:
            self.logger.error(f"Error correcting spelling: {e}")
            return address
    
    def _apply_turkish_capitalization(self, address: str) -> str:
        """
        Apply proper Turkish capitalization while preserving building numbers and Turkish chars
        
        Args:
            address: Address string to capitalize
            
        Returns:
            Address string with proper Turkish capitalization
        """
        try:
            if not address:
                return ""
            
            # Split into words to handle each separately
            words = address.split()
            capitalized_words = []
            
            for word in words:
                if not word:
                    continue
                
                # Check if word is a building number (e.g., "10/a", "5B", "23/A")
                if re.match(r'^\d+[/\-]?[A-Za-z]?$', word):
                    # Preserve building number case - make sure letter part is uppercase
                    if re.search(r'[a-zA-Z]', word):
                        # Has letter component - ensure it's uppercase
                        capitalized_word = re.sub(r'([a-zA-Z])', lambda m: m.group(1).upper(), word)
                    else:
                        # Just numbers - keep as is
                        capitalized_word = word
                    capitalized_words.append(capitalized_word)
                    continue
                
                # Apply Turkish title case to other words
                if hasattr(TurkishTextNormalizer, 'turkish_title'):
                    capitalized_word = TurkishTextNormalizer.turkish_title(word)
                else:
                    # Fallback Turkish capitalization
                    capitalized_word = self._turkish_title_case_fallback(word)
                
                capitalized_words.append(capitalized_word)
            
            return ' '.join(capitalized_words)
            
        except Exception as e:
            self.logger.error(f"Error applying Turkish capitalization: {e}")
            return address
    
    def _turkish_title_case_fallback(self, word: str) -> str:
        """Fallback Turkish title case implementation"""
        if not word:
            return word
        
        # Turkish character upper case mapping
        turkish_upper_map = {
            'ç': 'Ç', 'ğ': 'Ğ', 'ı': 'I', 'İ': 'İ', 
            'ö': 'Ö', 'ş': 'Ş', 'ü': 'Ü', 'i': 'İ'
        }
        
        # Convert to proper Turkish lowercase first to avoid double capitalization
        if hasattr(TurkishTextNormalizer, 'turkish_lower'):
            lower_word = TurkishTextNormalizer.turkish_lower(word)
        else:
            lower_word = word.lower()
        
        # Capitalize first character with Turkish rules
        first_char = lower_word[0]
        if first_char in turkish_upper_map:
            first_upper = turkish_upper_map[first_char]
        else:
            first_upper = first_char.upper()
        
        # Rest of word stays lowercase
        return first_upper + lower_word[1:]
    
    def _fuzzy_correct_administrative_name(self, word: str) -> str:
        """
        Apply fuzzy matching to correct misspelled administrative names
        
        This is CRITICAL FIX #2 implementation for Turkish administrative names
        
        Args:
            word: Potentially misspelled administrative name
            
        Returns:
            Corrected administrative name or original word if no match
        """
        try:
            if not word or len(word) < 3:
                return word
            
            # Load administrative names from CSV data if available
            administrative_names = self._get_administrative_names()
            if not administrative_names:
                return word
                
            # Normalize word for comparison
            normalized_word = TurkishTextNormalizer.normalize_for_comparison(word)
            
            # Use difflib for fuzzy matching with threshold ≥0.8
            matches = difflib.get_close_matches(
                normalized_word, 
                administrative_names, 
                n=1,  # Get only the best match
                cutoff=0.8  # Similarity threshold ≥0.8
            )
            
            if matches:
                best_match = matches[0]
                # Find the original case version of the match
                original_match = self._find_original_case(best_match, administrative_names)
                if original_match:
                    return TurkishTextNormalizer.turkish_title(original_match)
            
            return word
            
        except Exception as e:
            self.logger.error(f"Error in fuzzy correction: {e}")
            return word
    
    def _get_administrative_names(self) -> List[str]:
        """
        Get list of all Turkish administrative names for fuzzy matching
        
        Returns:
            List of normalized administrative names (il, ilce, mahalle)
        """
        try:
            # Try to load from CSV file
            current_dir = Path(__file__).parent
            project_root = current_dir.parent
            csv_path = project_root / "database" / "turkey_admin_hierarchy.csv"
            
            administrative_names = []
            
            if csv_path.exists():
                import csv
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Add province names
                        if row.get('il_adi'):
                            name = row['il_adi'].strip()
                            if name:
                                administrative_names.append(TurkishTextNormalizer.normalize_for_comparison(name))
                        
                        # Add district names  
                        if row.get('ilce_adi'):
                            name = row['ilce_adi'].strip()
                            if name and name != 'Merkez':  # Skip generic 'Merkez'
                                administrative_names.append(TurkishTextNormalizer.normalize_for_comparison(name))
                        
                        # Add neighborhood names
                        if row.get('mahalle_adi'):
                            name = row['mahalle_adi'].strip()
                            if name:
                                # Remove 'Mahallesi' suffix for fuzzy matching
                                clean_name = name.replace(' Mahallesi', '').replace(' mahallesi', '')
                                if clean_name and clean_name != 'Merkez':
                                    administrative_names.append(TurkishTextNormalizer.normalize_for_comparison(clean_name))
            
            # Remove duplicates and return
            return list(set(administrative_names))
            
        except Exception as e:
            self.logger.error(f"Error loading administrative names: {e}")
            return []
    
    def _find_original_case(self, normalized_name: str, all_names: List[str]) -> str:
        """
        Find the original case version of a normalized name
        
        Args:
            normalized_name: Normalized name to find
            all_names: List of all normalized names
            
        Returns:
            Original case name or normalized name if not found
        """
        try:
            # This is a simplified implementation
            # In a full implementation, we'd maintain a mapping
            return normalized_name
            
        except Exception as e:
            self.logger.error(f"Error finding original case: {e}")
            return normalized_name
    
    def normalize_turkish_chars(self, text: str) -> str:
        """
        Normalize Turkish characters and text formatting
        
        Args:
            text: Input text to normalize
            
        Returns:
            Normalized text with proper Turkish character usage
        """
        try:
            if not text or not isinstance(text, str):
                return ""
            
            # Convert to lowercase while preserving Turkish characters
            normalized = text.lower()
            
            # Remove extra whitespace
            normalized = re.sub(r'\s+', ' ', normalized).strip()
            
            # Remove unwanted punctuation but preserve Turkish chars
            normalized = re.sub(r'[^\w\sçğıöşü\-]', '', normalized)
            
            # Fix common character issues
            normalized = self._fix_turkish_characters(normalized)
            
            return normalized
            
        except Exception as e:
            self.logger.error(f"Error normalizing Turkish characters: {e}")
            return text
    
    def _preserve_turkish_normalization(self, text: str) -> str:
        """
        Normalize text while preserving ALL Turkish characters
        
        Args:
            text: Input text to normalize
            
        Returns:
            Normalized text with Turkish characters preserved
        """
        try:
            if not text:
                return ""
            
            # Clean up whitespace only - DO NOT change case or characters yet
            normalized = re.sub(r'\s+', ' ', text.strip())
            
            # Only remove truly unwanted punctuation, preserve Turkish chars and case info
            # Keep alphanumeric, Turkish chars, spaces, hyphens, slashes, and basic punctuation
            normalized = re.sub(r'[^\w\sçğıİöşüÇĞIÖŞÜ\-/:.()0-9A-Za-z]', '', normalized)
            
            return normalized
            
        except Exception as e:
            self.logger.error(f"Error in Turkish normalization: {e}")
            return text

    def _apply_character_corrections(self, text: str) -> str:
        """
        Apply Turkish character corrections ONLY when necessary
        
        Args:
            text: Text to apply character corrections to
            
        Returns:
            Text with minimal character corrections applied
        """
        try:
            corrected_text = text
            
            # CRITICAL FIX: DO NOT apply automatic character replacements
            # Turkish characters should be PRESERVED, not replaced
            # Only fix encoding issues, not legitimate Turkish characters
            
            # Fix only encoding corruption issues
            encoding_fixes = {
                'i̇': 'i',      # Combining dot above (encoding issue)
                'ı̇': 'i',      # Dotless i with combining dot (encoding issue)  
                'â': 'a',      # Circumflex accent (not Turkish)
                'î': 'i',      # Circumflex accent (not Turkish)
                'û': 'u',      # Circumflex accent (not Turkish)
            }
            
            for corrupted, fixed in encoding_fixes.items():
                if corrupted in corrected_text:
                    corrected_text = corrected_text.replace(corrupted, fixed)
            
            return corrected_text
            
        except Exception as e:
            self.logger.error(f"Error applying character corrections: {e}")
            return text
    
    def _contextual_character_replace(self, text: str, old_char: str, new_char: str) -> str:
        """
        Apply contextual character replacement for Turkish text
        
        Args:
            text: Text to process
            old_char: Character to replace
            new_char: Replacement character
            
        Returns:
            Text with contextual replacements
        """
        try:
            # Simple replacement for now
            # In production, this could include more sophisticated rules
            return text.replace(old_char, new_char)
            
        except Exception as e:
            self.logger.error(f"Error in contextual character replacement: {e}")
            return text
    
    def _fix_turkish_characters(self, text: str) -> str:
        """
        Fix common Turkish character encoding issues
        
        Args:
            text: Text with potential character issues
            
        Returns:
            Text with fixed Turkish characters
        """
        try:
            # Common character fixes
            fixes = {
                'i̇': 'i',  # Combining dot above
                'ı̇': 'i',  # Dotless i with combining dot
                'ğ': 'ğ',  # Ensure proper soft g
                'ş': 'ş',  # Ensure proper s with cedilla
                'ç': 'ç',  # Ensure proper c with cedilla
                'ö': 'ö',  # Ensure proper o with umlaut
                'ü': 'ü',  # Ensure proper u with umlaut
            }
            
            fixed_text = text
            for problem, solution in fixes.items():
                fixed_text = fixed_text.replace(problem, solution)
            
            return fixed_text
            
        except Exception as e:
            self.logger.error(f"Error fixing Turkish characters: {e}")
            return text
    
    def _final_cleanup(self, address: str) -> str:
        """
        Perform final cleanup and formatting
        
        Args:
            address: Address string to clean up
            
        Returns:
            Final cleaned address string
        """
        try:
            if not address:
                return ""
            
            # Remove extra spaces
            cleaned = re.sub(r'\s+', ' ', address).strip()
            
            # Ensure proper case for first letters of words
            words = cleaned.split()
            cleaned_words = []
            
            for word in words:
                if word:
                    # Capitalize first letter while preserving Turkish characters
                    if word[0] in 'çğıöşü':
                        # Turkish characters that have different uppercase forms
                        turkish_upper = {
                            'ç': 'Ç', 'ğ': 'Ğ', 'ı': 'I', 
                            'ö': 'Ö', 'ş': 'Ş', 'ü': 'Ü'
                        }
                        capitalized = turkish_upper.get(word[0], word[0].upper()) + word[1:]
                    else:
                        capitalized = word[0].upper() + word[1:]
                    
                    cleaned_words.append(capitalized)
            
            return ' '.join(cleaned_words)
            
        except Exception as e:
            self.logger.error(f"Error in final cleanup: {e}")
            return address
    
    def _calculate_correction_confidence(self, original: str, corrected: str, 
                                       corrections: List[dict], factors: List[float]) -> float:
        """
        Calculate overall confidence score for corrections
        
        Args:
            original: Original address string
            corrected: Corrected address string
            corrections: List of applied corrections
            factors: List of confidence factors
            
        Returns:
            Overall confidence score (0.0-1.0)
        """
        try:
            if not corrections:
                return 1.0  # No corrections needed
            
            # Base confidence from individual corrections
            if factors:
                base_confidence = sum(factors) / len(factors)
            else:
                base_confidence = 0.5
            
            # Adjust based on amount of change
            similarity = difflib.SequenceMatcher(None, original, corrected).ratio()
            
            # More changes = lower confidence
            change_penalty = (1.0 - similarity) * 0.2
            adjusted_confidence = max(0.0, base_confidence - change_penalty)
            
            # Boost confidence if corrections are common/expected
            if len(corrections) <= 2:
                adjusted_confidence = min(1.0, adjusted_confidence + 0.1)
            
            return round(adjusted_confidence, 3)
            
        except Exception as e:
            self.logger.error(f"Error calculating confidence: {e}")
            return 0.5
    
    def _get_fallback_abbreviations(self) -> Dict[str, str]:
        """
        Provide fallback abbreviations when JSON is not available
        
        Returns:
            Dict with basic Turkish address abbreviations
        """
        fallback = {
            'mh.': 'mahallesi', 'mah.': 'mahallesi', 'mah': 'mahallesi',
            'sk.': 'sokak', 'sok.': 'sokak', 'sk': 'sokak',
            'cd.': 'caddesi', 'cad.': 'caddesi', 'cd': 'caddesi',
            'blv.': 'bulvarı', 'bulv.': 'bulvarı', 'blv': 'bulvarı',
            'no.': 'numara', 'no': 'numara', 'num.': 'numara',
            'apt.': 'apartmanı', 'ap.': 'apartmanı', 'apt': 'apartmanı',
            'bl.': 'blok', 'blok': 'blok', 'bl': 'blok',
            'st.': 'sitesi', 'site': 'sitesi', 'st': 'sitesi',
            'km.': 'kilometre', 'km': 'kilometre',
            'pl.': 'plaza', 'plz.': 'plaza', 'plaza': 'plaza'
        }
        
        self.logger.info(f"Using fallback abbreviations with {len(fallback)} entries")
        return fallback
    
    def _get_fallback_spelling_corrections(self) -> Dict[str, str]:
        """
        Provide fallback spelling corrections when JSON is not available
        
        Returns:
            Dict with basic Turkish spelling corrections
        """
        fallback = {
            'istbl': 'istanbul', 'istanbull': 'istanbul', 'stanbul': 'istanbul',
            'mcidiyeköy': 'mecidiyeköy', 'mecıdıyeköy': 'mecidiyeköy',
            'kadikoy': 'kadıköy', 'kadıkoy': 'kadıköy',
            'besiktas': 'beşiktaş', 'besıktas': 'beşiktaş',
            'sisli': 'şişli', 'şisli': 'şişli',
            'ataturk': 'atatürk', 'atatuk': 'atatürk',
            'cumhurıyet': 'cumhuriyet', 'cumhuriyet': 'cumhuriyet',
            'bagcilar': 'bağcılar', 'bağcılarr': 'bağcılar',
            'ankara': 'ankara', 'ankarra': 'ankara',
            'cankaya': 'çankaya', 'çankayaa': 'çankaya',
            'izmir': 'izmir', 'izmır': 'izmir',
            'karsiyaka': 'karşıyaka', 'karşıyakaa': 'karşıyaka'
        }
        
        self.logger.info(f"Using fallback spelling corrections with {len(fallback)} entries")
        return fallback
    
    def _create_error_result(self, error_message: str) -> dict:
        """
        Create standardized error result dictionary
        
        Args:
            error_message: Error description
            
        Returns:
            Error result dictionary
        """
        return {
            'original': "",
            'corrected': "",
            'corrections': [],
            'confidence': 0.0,
            'error': error_message
        }


# Utility functions for external use
def correct_turkish_address(address: str) -> str:
    """
    Utility function to correct Turkish address text
    
    Args:
        address: Raw address string
        
    Returns:
        Corrected address string
    """
    corrector = AddressCorrector()
    result = corrector.correct_address(address)
    return result['corrected']


def expand_turkish_abbreviations(address: str) -> str:
    """
    Utility function to expand Turkish abbreviations in address
    
    Args:
        address: Address string with abbreviations
        
    Returns:
        Address string with expanded abbreviations
    """
    corrector = AddressCorrector()
    return corrector.expand_abbreviations(address)


# Example usage and testing
if __name__ == "__main__":
    # Example usage
    corrector = AddressCorrector()
    
    # Test address correction
    test_addresses = [
        "İstbl Kadikoy Moda Mah. Caferağa Sk. No 10",
        "Ankara Cankaya Kızılay Mh. Atatuk Bulv. 25",
        "İzmir Karsiyaka Bostanli Mah. Cumhurıyet Cd. 45 Apt. 3"
    ]
    
    for address in test_addresses:
        result = corrector.correct_address(address)
        print(f"\nOriginal: {result['original']}")
        print(f"Corrected: {result['corrected']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Corrections: {len(result['corrections'])}")