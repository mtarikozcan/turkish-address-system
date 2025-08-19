#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Turkish Address System - Turkish Text Utilities

Centralized Turkish character normalization and text processing utilities
for consistent handling across all system components.
"""

import re
import unicodedata
from typing import Dict, List, Optional, Union


class TurkishTextNormalizer:
    """
    Centralized Turkish text normalization utility for consistent character handling
    """
    
    # Turkish character mappings for different normalization scenarios
    TURKISH_TO_ASCII = {
        'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
        'Ç': 'C', 'Ğ': 'G', 'I': 'I', 'İ': 'I', 'Ö': 'O', 'Ş': 'S', 'Ü': 'U'
    }
    
    TURKISH_LOWERCASE_MAP = {
        'İ': 'i',   # Turkish capital I with dot
        'I': 'ı',   # Latin capital I (becomes Turkish dotless i)
        'Ç': 'ç', 'Ğ': 'ğ', 'Ö': 'ö', 'Ş': 'ş', 'Ü': 'ü'
    }
    
    TURKISH_UPPERCASE_MAP = {
        'i': 'İ',   # Turkish lowercase i (becomes capital I with dot)
        'ı': 'I',   # Turkish dotless i (becomes Latin capital I)
        'ç': 'Ç', 'ğ': 'Ğ', 'ö': 'Ö', 'ş': 'Ş', 'ü': 'Ü'
    }
    
    @classmethod
    def normalize_for_comparison(cls, text: str) -> str:
        """
        Normalize Turkish text for fuzzy matching while PRESERVING Turkish characters
        
        Args:
            text: Input text to normalize
            
        Returns:
            Normalized text suitable for comparison operations with Turkish chars preserved
        """
        if not isinstance(text, str):
            return str(text)
        
        # Remove extra whitespace
        normalized = ' '.join(text.split())
        
        # CRITICAL FIX: DO NOT convert Turkish characters to ASCII
        # Keep Turkish characters intact for proper matching
        
        # Use proper Turkish lowercase conversion
        normalized = cls.turkish_lower(normalized)
        
        # Remove punctuation but preserve Turkish characters, spaces and hyphens
        normalized = re.sub(r'[^\w\sçğıİöşüÇĞIÖŞÜ\-]', '', normalized)
        
        # Clean up multiple spaces
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    @classmethod
    def turkish_lower(cls, text: str) -> str:
        """
        Convert text to lowercase using Turkish locale rules
        
        Args:
            text: Input text
            
        Returns:
            Lowercase text with proper Turkish character handling
        """
        if not isinstance(text, str):
            return str(text)
        
        # Apply Turkish-specific lowercase mappings first
        result = text
        for upper, lower in cls.TURKISH_LOWERCASE_MAP.items():
            result = result.replace(upper, lower)
        
        # Apply standard lowercase to remaining characters
        result = result.lower()
        
        return result
    
    @classmethod
    def turkish_upper(cls, text: str) -> str:
        """
        Convert text to uppercase using Turkish locale rules
        
        Args:
            text: Input text
            
        Returns:
            Uppercase text with proper Turkish character handling
        """
        if not isinstance(text, str):
            return str(text)
        
        # Apply standard uppercase first
        result = text.upper()
        
        # Apply Turkish-specific uppercase mappings
        for lower, upper in cls.TURKISH_UPPERCASE_MAP.items():
            result = result.replace(lower.upper(), upper)
        
        return result
    
    @classmethod
    def turkish_title(cls, text: str) -> str:
        """
        Convert text to title case using Turkish locale rules
        
        Args:
            text: Input text
            
        Returns:
            Title case text with proper Turkish character handling
        """
        if not isinstance(text, str):
            return str(text)
        
        words = text.split()
        title_words = []
        
        for word in words:
            if word:
                # Capitalize first character using Turkish rules
                first_char = word[0]
                if first_char in cls.TURKISH_UPPERCASE_MAP:
                    capitalized = cls.TURKISH_UPPERCASE_MAP[first_char] + cls.turkish_lower(word[1:])
                else:
                    capitalized = first_char.upper() + cls.turkish_lower(word[1:])
                title_words.append(capitalized)
        
        return ' '.join(title_words)
    
    @classmethod
    def normalize_address_component(cls, component: str, component_type: str = None) -> str:
        """
        Normalize address component with type-specific formatting
        
        Args:
            component: Address component text
            component_type: Type of component ('il', 'ilce', 'mahalle', etc.)
            
        Returns:
            Properly formatted address component
        """
        if not isinstance(component, str) or not component.strip():
            return ""
        
        # Basic normalization
        normalized = ' '.join(component.strip().split())
        
        # Apply Turkish title case
        normalized = cls.turkish_title(normalized)
        
        # Component-specific formatting
        if component_type == 'mahalle':
            # Ensure mahalle components don't have redundant suffixes
            if normalized.lower().endswith(' mahallesi mahallesi'):
                normalized = normalized[:-11]  # Remove one " mahallesi"
            elif not normalized.lower().endswith(' mahallesi') and not normalized.lower().endswith(' mh'):
                # Don't automatically add suffix - let other components handle this
                pass
        
        return normalized
    
    @classmethod
    def clean_text(cls, text: str) -> str:
        """
        Clean and normalize text for general processing
        
        Args:
            text: Input text to clean
            
        Returns:
            Cleaned text
        """
        if not isinstance(text, str):
            return str(text)
        
        # Remove extra whitespace
        cleaned = ' '.join(text.split())
        
        # Remove control characters
        cleaned = ''.join(char for char in cleaned if unicodedata.category(char)[0] != 'C')
        
        # Normalize Unicode characters
        cleaned = unicodedata.normalize('NFC', cleaned)
        
        return cleaned.strip()
    
    @classmethod
    def is_turkish_text(cls, text: str) -> bool:
        """
        Check if text contains Turkish characters
        
        Args:
            text: Text to check
            
        Returns:
            True if text contains Turkish-specific characters
        """
        if not isinstance(text, str):
            return False
        
        turkish_chars = set('çğıöşüÇĞIİÖŞÜ')
        return any(char in turkish_chars for char in text)
    
    @classmethod
    def get_character_variants(cls, char: str) -> List[str]:
        """
        Get common variants of a Turkish character
        
        Args:
            char: Character to get variants for
            
        Returns:
            List of character variants
        """
        variants_map = {
            'i': ['ı', 'í', 'î', 'ì', 'İ'],
            'ı': ['i', 'í', 'î', 'ì', 'I'],
            'İ': ['I', 'Í', 'Î', 'Ì', 'i'],
            'I': ['İ', 'Í', 'Î', 'Ì', 'ı'],
            'c': ['ç', 'ć', 'č', 'ĉ'],
            'ç': ['c', 'ć', 'č', 'ĉ', 'Ç'],
            'g': ['ğ', 'ģ', 'ġ'],
            'ğ': ['g', 'ģ', 'ġ', 'Ğ'],
            'o': ['ö', 'ó', 'ô', 'ò', 'ő'],
            'ö': ['o', 'ó', 'ô', 'ò', 'ő', 'Ö'],
            's': ['ş', 'ś', 'š', 'ŝ'],
            'ş': ['s', 'ś', 'š', 'ŝ', 'Ş'],
            'u': ['ü', 'ú', 'û', 'ù', 'ű'],
            'ü': ['u', 'ú', 'û', 'ù', 'ű', 'Ü']
        }
        
        # Add uppercase variants
        if char.lower() in variants_map:
            variants = variants_map[char.lower()]
            if char.isupper():
                variants = [v.upper() if v.islower() else v for v in variants]
            return variants
        
        return [char]


# Convenience functions for backward compatibility
def normalize_turkish_text(text: str) -> str:
    """Convenience function for text normalization"""
    return TurkishTextNormalizer.normalize_for_comparison(text)

def turkish_title_case(text: str) -> str:
    """Convenience function for Turkish title case"""
    return TurkishTextNormalizer.turkish_title(text)

def clean_turkish_text(text: str) -> str:
    """Convenience function for text cleaning"""
    return TurkishTextNormalizer.clean_text(text)