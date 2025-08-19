"""
Advanced Pattern Recognition Engine
Phase 3: Comprehensive Turkish Address Pattern Handling

This module provides advanced pattern recognition for:
- Building hierarchy components (kat, blok, apartman, site)
- Complex building patterns with multiple components
- Regional variations (köy, belde, mevkii)
- Edge case handling for problematic inputs
"""

import logging
import re
import time
from typing import Dict, List, Tuple, Any, Optional, Set
from pathlib import Path

class AdvancedPatternEngine:
    """
    Advanced Pattern Engine
    
    Handles comprehensive Turkish address patterns including:
    - Building hierarchy: site, apartman, blok, kat
    - Regional variations: köy, belde, mevkii
    - Complex patterns: multiple streets, compound buildings
    - Edge cases: abbreviated, missing punctuation, very long/short
    """
    
    def __init__(self):
        """
        Initialize Advanced Pattern Engine
        
        Compiles patterns for building hierarchy, regional variations,
        and edge case handling
        """
        self.logger = logging.getLogger(__name__)
        
        # Compile pattern sets
        self.building_hierarchy_patterns = self._compile_building_hierarchy_patterns()
        self.regional_patterns = self._compile_regional_patterns()
        self.complex_patterns = self._compile_complex_patterns()
        self.abbreviation_expansions = self._load_abbreviation_expansions()
        
        # Performance tracking
        self.stats = {
            'total_queries': 0,
            'successful_extractions': 0,
            'building_hierarchy_found': 0,
            'regional_variations_found': 0,
            'edge_cases_handled': 0,
            'average_processing_time_ms': 0.0
        }
        
        self.logger.info(f"AdvancedPatternEngine initialized with {len(self.building_hierarchy_patterns)} building patterns")
    
    def extract_advanced_components(self, address_text: str) -> Dict[str, Any]:
        """
        Main method: Extract all advanced patterns from address text
        
        Args:
            address_text: Raw address string to analyze
            
        Returns:
            {
                'components': {'kat': str, 'blok': str, 'site': str, ...},
                'confidence': float,
                'processing_time_ms': float,
                'matched_patterns': List[str],
                'extraction_methods': List[str]
            }
        """
        start_time = time.time()
        self.stats['total_queries'] += 1
        
        if not address_text or not isinstance(address_text, str):
            return self._create_empty_result(0.0, "invalid_input")
        
        # Initialize result containers
        found_components = {}
        matched_patterns = []
        extraction_methods = []
        confidence_scores = []
        
        try:
            # Phase 1: Extract building hierarchy components
            building_result = self.extract_building_hierarchy(address_text)
            if building_result['components']:
                found_components.update(building_result['components'])
                matched_patterns.extend(building_result['patterns'])
                confidence_scores.append(building_result['confidence'])
                extraction_methods.append('building_hierarchy')
                self.stats['building_hierarchy_found'] += 1
            
            # Phase 2: Handle complex building patterns
            complex_result = self.handle_complex_buildings(address_text)
            if complex_result['components']:
                # Smart merge to avoid overwriting
                for component, value in complex_result['components'].items():
                    if component not in found_components:
                        found_components[component] = value
                matched_patterns.extend(complex_result['patterns'])
                confidence_scores.append(complex_result['confidence'])
                extraction_methods.append('complex_building')
            
            # Phase 3: Detect regional variations
            regional_result = self.detect_regional_variations(address_text)
            if regional_result['components']:
                found_components.update(regional_result['components'])
                matched_patterns.extend(regional_result['patterns'])
                confidence_scores.append(regional_result['confidence'])
                extraction_methods.append('regional_variation')
                self.stats['regional_variations_found'] += 1
            
            # Phase 4: Handle edge cases
            edge_case_result = self.handle_edge_cases(address_text, found_components)
            if edge_case_result['components']:
                for component, value in edge_case_result['components'].items():
                    if component not in found_components:
                        found_components[component] = value
                matched_patterns.extend(edge_case_result['patterns'])
                confidence_scores.append(edge_case_result['confidence'])
                extraction_methods.append('edge_case_handling')
                self.stats['edge_cases_handled'] += 1
            
            # Calculate overall confidence
            overall_confidence = max(confidence_scores) if confidence_scores else 0.0
            
            # Track successful extractions
            if found_components:
                self.stats['successful_extractions'] += 1
            
        except Exception as e:
            self.logger.error(f"Error in advanced pattern extraction for '{address_text}': {e}")
            found_components = {}
            overall_confidence = 0.0
            matched_patterns = []
            extraction_methods = ['error']
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000
        self.stats['average_processing_time_ms'] = (
            (self.stats['average_processing_time_ms'] * (self.stats['total_queries'] - 1) + processing_time) / 
            self.stats['total_queries']
        )
        
        return {
            'components': found_components,
            'confidence': overall_confidence,
            'processing_time_ms': processing_time,
            'matched_patterns': matched_patterns,
            'extraction_methods': extraction_methods
        }
    
    def extract_building_hierarchy(self, address_text: str) -> Dict[str, Any]:
        """
        Extract building hierarchy components (kat, blok, apartman, site)
        
        Handles patterns:
        - "A blok 3. kat daire 12" → {'blok': 'A', 'kat': '3', 'daire': '12'}
        - "Gül Apartmanı B blok" → {'apartman': 'Gül Apartmanı', 'blok': 'B'}
        - "Çiçek Sitesi" → {'site': 'Çiçek Sitesi'}
        - "zemin kat", "3. kat", "kat 5" → {'kat': 'zemin'/'3'/'5'}
        """
        found_components = {}
        matched_patterns = []
        
        # Extract site names
        site_patterns = [
            r'([A-ZÇĞİÖŞÜa-zçğıiöşü]+(?:\s+[A-ZÇĞİÖŞÜa-zçğıiöşü]+){0,2})\s+[Ss]itesi\b',
            r'([A-ZÇĞİÖŞÜa-zçğıiöşü]+(?:\s+[A-ZÇĞİÖŞÜa-zçğıiöşü]+){0,2})\s+[Kk]onut\s+[Ss]itesi\b',
        ]
        
        for pattern in site_patterns:
            match = re.search(pattern, address_text, re.IGNORECASE)
            if match:
                site_name = match.group(1).strip()
                if site_name and len(site_name.split()) <= 3:
                    found_components['site'] = f"{site_name.title()} Sitesi"
                    matched_patterns.append(match.group(0))
                    break
        
        # Extract apartman names
        apartman_patterns = [
            r'([A-ZÇĞİÖŞÜa-zçğıiöşü]+(?:\s+[A-ZÇĞİÖŞÜa-zçğıiöşü]+){0,2})\s+[Aa]partman[ıi]\b',
            r'([A-ZÇĞİÖŞÜa-zçğıiöşü]+(?:\s+[A-ZÇĞİÖŞÜa-zçğıiöşü]+){0,2})\s+[Aa]pt\.?\b',
        ]
        
        for pattern in apartman_patterns:
            match = re.search(pattern, address_text, re.IGNORECASE)
            if match:
                apt_name = match.group(1).strip()
                if apt_name and len(apt_name.split()) <= 3:
                    found_components['apartman'] = f"{apt_name.title()} Apartmanı"
                    matched_patterns.append(match.group(0))
                    break
        
        # Extract blok (A blok, blok B, 1. blok)
        blok_patterns = [
            r'\b([A-Za-z])\s+[Bb]lok\b',           # A blok
            r'\b[Bb]lok\s+([A-Za-z])\b',           # blok B
            r'\b(\d+)\.?\s+[Bb]lok\b',             # 1. blok
            r'\b[Bb]lok\s*:\s*([A-Za-z0-9]+)\b',   # blok: A
        ]
        
        for pattern in blok_patterns:
            match = re.search(pattern, address_text, re.IGNORECASE)
            if match:
                blok_value = match.group(1).upper()
                found_components['blok'] = blok_value
                matched_patterns.append(match.group(0))
                break
        
        # Extract kat (floor) - preserve original case
        kat_patterns = [
            r'\b(\d+)\.?\s+[Kk]at\b',              # 3. kat, 5 kat
            r'\b[Kk]at\s*:?\s*(\d+)\b',            # kat 3, kat: 5
            r'\b([Zz]emin)\s+[Kk]at\b',            # zemin kat
            r'\b([Bb]odrum)\s+[Kk]at\b',           # bodrum kat
            r'\b([Gg]iriş)\s+[Kk]at\b',            # giriş kat
        ]
        
        for pattern in kat_patterns:
            match = re.search(pattern, address_text, re.IGNORECASE)
            if match:
                kat_value = match.group(1)
                # Preserve case for special floor names
                if kat_value.lower() in ['zemin', 'bodrum', 'giriş']:
                    found_components['kat'] = kat_value.title()
                else:
                    found_components['kat'] = kat_value
                matched_patterns.append(match.group(0))
                break
        
        # Extract simple daire patterns (standalone)
        if 'daire' not in found_components:
            daire_patterns = [
                r'\bdaire\s+(\d+)\b',
                r'\bdaire\s*:\s*(\d+)\b',
                r'\bd\.\s*(\d+)\b',
            ]
            
            for pattern in daire_patterns:
                match = re.search(pattern, address_text, re.IGNORECASE)
                if match:
                    daire_value = match.group(1)
                    found_components['daire'] = daire_value
                    matched_patterns.append(match.group(0))
                    break
        
        # Extract plaza names
        plaza_patterns = [
            r'([A-ZÇĞİÖŞÜa-zçğıiöşü]+(?:\s+[A-ZÇĞİÖŞÜa-zçğıiöşü]+){0,2})\s+[Pp]laza\b',
            r'([A-ZÇĞİÖŞÜa-zçğıiöşü]+(?:\s+[A-ZÇĞİÖŞÜa-zçğıiöşü]+){0,2})\s+[İi]ş\s+[Mm]erkezi\b',
        ]
        
        for pattern in plaza_patterns:
            match = re.search(pattern, address_text, re.IGNORECASE)
            if match:
                plaza_name = match.group(1).strip()
                if plaza_name and len(plaza_name.split()) <= 3:
                    found_components['plaza'] = f"{plaza_name.title()} Plaza"
                    matched_patterns.append(match.group(0))
                    break
        
        # Calculate confidence based on pattern completeness
        confidence = 0.95 if len(found_components) >= 2 else 0.85 if found_components else 0.0
        
        return {
            'components': found_components,
            'confidence': confidence,
            'patterns': matched_patterns
        }
    
    def handle_complex_buildings(self, address_text: str) -> Dict[str, Any]:
        """
        Parse complex building descriptions with multiple components
        
        Handles patterns:
        - "no:25/A kat:3 daire:12" → complete building hierarchy
        - "A blok 5. kat daire 8" → compound building description
        - "Gül Apt. B blok no:15/C" → mixed patterns
        """
        found_components = {}
        matched_patterns = []
        
        # Pattern for colon-separated format (no:25/A kat:3 daire:12)
        colon_patterns = [
            r'\bno\s*:\s*([0-9]+(?:[/\-][A-Za-z0-9]+)?)\b',
            r'\bkat\s*:\s*([0-9]+|[Zz]emin|[Bb]odrum)\b',
            r'\bdaire\s*:\s*([0-9]+(?:[/\-][A-Za-z0-9]+)?)\b',
            r'\bblok\s*:\s*([A-Za-z0-9]+)\b',
        ]
        
        for pattern in colon_patterns:
            match = re.search(pattern, address_text, re.IGNORECASE)
            if match:
                value = match.group(1)
                if 'no' in pattern:
                    found_components['bina_no'] = value
                elif 'kat' in pattern:
                    found_components['kat'] = value.title() if value.lower() in ['zemin', 'bodrum'] else value
                elif 'daire' in pattern:
                    found_components['daire'] = value
                elif 'blok' in pattern:
                    found_components['blok'] = value.upper()
                matched_patterns.append(match.group(0))
        
        # Pattern for compound descriptions (A blok 5. kat daire 8)
        compound_pattern = r'([A-Za-z])\s+blok\s+(\d+)\.?\s+kat\s+(?:daire\s+)?(\d+)'
        match = re.search(compound_pattern, address_text, re.IGNORECASE)
        if match and not found_components:
            found_components['blok'] = match.group(1).upper()
            found_components['kat'] = match.group(2)
            found_components['daire'] = match.group(3)
            matched_patterns.append(match.group(0))
        
        # Pattern for kesişim (intersection) handling  
        intersection_patterns = [
            r'([A-ZÇĞİÖŞÜa-zçğıiöşü]+(?:\s+[A-ZÇĞİÖŞÜa-zçğıiöşü]+)?)\s+(?:cad|cadde|caddesi)\.?\s+(?:ile\s+)?([A-ZÇĞİÖŞÜa-zçğıiöşü]+(?:\s+[A-ZÇĞİÖŞÜa-zçğıiöşü]+)?)\s+(?:sk|sokak|sokağı)\.?\s+kesişimi',
            r'([A-ZÇĞİÖŞÜa-zçğıiöşü]+(?:\s+[A-ZÇĞİÖŞÜa-zçğıiöşü]+)?)\s+(?:blv|bulvar|bulvarı)\.?\s+ile\s+([A-ZÇĞİÖŞÜa-zçğıiöşü]+(?:\s+[A-ZÇĞİÖŞÜa-zçğıiöşü]+)?)\s+(?:cd|cad|cadde|caddesi)\.?\s+arası',
            # More flexible pattern for "Atatürk Cad. ile Barış Sk. kesişimi"
            r'([A-ZÇĞİÖŞÜa-zçğıiöşü]+)\s+[Cc]ad\.\s+ile\s+([A-ZÇĞİÖŞÜa-zçğıiöşü]+)\s+[Ss]k\.\s+kesişimi',
        ]
        
        for pattern in intersection_patterns:
            match = re.search(pattern, address_text, re.IGNORECASE)
            if match:
                street1 = match.group(1).strip()
                street2 = match.group(2).strip()
                if 'cad' in pattern.lower():
                    found_components['cadde'] = f"{street1.title()} Caddesi"
                    found_components['sokak'] = f"{street2.title()} Sokak"
                elif 'blv' in pattern.lower():
                    found_components['bulvar'] = f"{street1.title()} Bulvarı"
                    found_components['cadde'] = f"{street2.title()} Caddesi"
                found_components['kesişim'] = 'true'
                matched_patterns.append(match.group(0))
                break
        
        # Calculate confidence
        confidence = 0.9 if len(found_components) >= 3 else 0.8 if found_components else 0.0
        
        return {
            'components': found_components,
            'confidence': confidence,
            'patterns': matched_patterns
        }
    
    def detect_regional_variations(self, address_text: str) -> Dict[str, Any]:
        """
        Handle regional Turkish address patterns
        
        Detects:
        - "Çiçekli köyü" → {'köy': 'Çiçekli'}
        - "Merkez belde" → {'belde': 'Merkez'}
        - "Yeşiltepe mevkii" → {'mevkii': 'Yeşiltepe'}
        - "Sanayi bölgesi" → {'bölge': 'Sanayi'}
        """
        found_components = {}
        matched_patterns = []
        
        # Köy (village) patterns
        köy_patterns = [
            r'([A-ZÇĞİÖŞÜa-zçğıiöşü]+(?:\s+[A-ZÇĞİÖŞÜa-zçğıiöşü]+){0,1})\s+[Kk]öy[üu]\b',
            r'([A-ZÇĞİÖŞÜa-zçğıiöşü]+(?:\s+[A-ZÇĞİÖŞÜa-zçğıiöşü]+){0,1})\s+[Kk]öy\b',
        ]
        
        for pattern in köy_patterns:
            match = re.search(pattern, address_text, re.IGNORECASE)
            if match:
                köy_name = match.group(1).strip()
                if köy_name and köy_name.lower() not in ['merkez', 'yeni', 'eski']:
                    found_components['köy'] = köy_name.title()
                    matched_patterns.append(match.group(0))
                    break
        
        # Belde (small town) patterns
        belde_patterns = [
            r'([A-ZÇĞİÖŞÜa-zçğıiöşü]+(?:\s+[A-ZÇĞİÖŞÜa-zçğıiöşü]+){0,1})\s+[Bb]elde(?:si)?\b',
            r'\b[Mm]erkez\s+[Bb]elde\b',
        ]
        
        for pattern in belde_patterns:
            match = re.search(pattern, address_text, re.IGNORECASE)
            if match:
                if 'merkez belde' in match.group(0).lower():
                    found_components['belde'] = 'Merkez'
                else:
                    belde_name = match.group(1).strip()
                    if belde_name:
                        found_components['belde'] = belde_name.title()
                matched_patterns.append(match.group(0))
                break
        
        # Mevkii (location/area) patterns
        mevkii_patterns = [
            r'([A-ZÇĞİÖŞÜa-zçğıiöşü]+(?:\s+[A-ZÇĞİÖŞÜa-zçğıiöşü]+){0,1})\s+[Mm]evkii?\b',
            r'([A-ZÇĞİÖŞÜa-zçğıiöşü]+(?:\s+[A-ZÇĞİÖŞÜa-zçğıiöşü]+){0,1})\s+[Mm]evki\b',
        ]
        
        for pattern in mevkii_patterns:
            match = re.search(pattern, address_text, re.IGNORECASE)
            if match:
                mevkii_name = match.group(1).strip()
                if mevkii_name:
                    found_components['mevkii'] = mevkii_name.title()
                    matched_patterns.append(match.group(0))
                    break
        
        # Bölge (region/zone) patterns
        bölge_patterns = [
            r'([A-ZÇĞİÖŞÜa-zçğıiöşü]+(?:\s+[A-ZÇĞİÖŞÜa-zçğıiöşü]+){0,1})\s+[Bb]ölge(?:si)?\b',
            r'\b[Ss]anayi\s+[Bb]ölgesi\b',
            r'\b[Oo]rganize\s+[Ss]anayi\s+[Bb]ölgesi\b',
        ]
        
        for pattern in bölge_patterns:
            match = re.search(pattern, address_text, re.IGNORECASE)
            if match:
                if 'organize sanayi' in match.group(0).lower():
                    found_components['bölge'] = 'Organize Sanayi Bölgesi'
                elif 'sanayi bölgesi' in match.group(0).lower():
                    found_components['bölge'] = 'Sanayi Bölgesi'
                else:
                    bölge_name = match.group(1).strip()
                    if bölge_name:
                        found_components['bölge'] = f"{bölge_name.title()} Bölgesi"
                matched_patterns.append(match.group(0))
                break
        
        # Calculate confidence
        confidence = 0.9 if found_components else 0.0
        
        return {
            'components': found_components,
            'confidence': confidence,
            'patterns': matched_patterns
        }
    
    def handle_edge_cases(self, address_text: str, existing_components: Dict) -> Dict[str, Any]:
        """
        Handle problematic input formats and edge cases
        
        Handles:
        - Very short addresses: "Ankara Çankaya"
        - Abbreviated formats: "ist kad mod caf 15"
        - Missing punctuation: "istanbul kadikoy moda caferaga 15"
        - Multiple formats mixed: "İst./Kad./Moda Mah. Caferağa Sk."
        """
        found_components = {}
        matched_patterns = []
        
        # Handle very short addresses (just expand abbreviations)
        if len(address_text) < 20:
            expanded = self._expand_abbreviations(address_text.lower())
            if expanded != address_text.lower():
                matched_patterns.append(f"expanded: {address_text} → {expanded}")
                # Re-analyze expanded text (would need to call other methods)
                found_components['_expanded'] = expanded
        
        # Handle abbreviated/informal input (ist kad mod caf 15)
        if not existing_components and len(address_text.split()) <= 6:
            # Common abbreviations
            abbrev_map = {
                'ist': 'İstanbul',
                'ank': 'Ankara',
                'izm': 'İzmir',
                'kad': 'Kadıköy',
                'beş': 'Beşiktaş',
                'şiş': 'Şişli',
                'mod': 'Moda',
                'caf': 'Caferağa',
                'ata': 'Atatürk',
                'cum': 'Cumhuriyet'
            }
            
            words = address_text.lower().split()
            expanded_words = []
            
            for word in words:
                # Check if it's a number (potential building number)
                if word.isdigit():
                    found_components['bina_no'] = word
                    expanded_words.append(word)
                elif word in abbrev_map:
                    expanded_words.append(abbrev_map[word])
                    matched_patterns.append(f"{word} → {abbrev_map[word]}")
                else:
                    expanded_words.append(word)
            
            if matched_patterns:
                found_components['_expanded'] = ' '.join(expanded_words)
        
        # Handle missing punctuation by detecting component boundaries
        if '.' not in address_text and ',' not in address_text and len(address_text) > 30:
            # Try to detect component boundaries based on keywords
            component_keywords = {
                'mahalle': ['mah', 'mahalle', 'mahallesi'],
                'cadde': ['cad', 'cadde', 'caddesi'],
                'sokak': ['sk', 'sok', 'sokak', 'sokağı'],
                'bina': ['no', 'numara'],
                'site': ['sitesi', 'konut'],
                'apartman': ['apt', 'apartman', 'apartmanı']
            }
            
            text_lower = address_text.lower()
            for component_type, keywords in component_keywords.items():
                for keyword in keywords:
                    if keyword in text_lower and component_type not in existing_components:
                        # Mark potential component boundary
                        matched_patterns.append(f"detected {component_type} boundary")
        
        # Handle mixed formats (İst./Kad./Moda Mah.)
        if '/' in address_text and '.' in address_text:
            # Split by common delimiters
            parts = re.split(r'[/.]', address_text)
            if len(parts) > 2:
                matched_patterns.append(f"mixed format with {len(parts)} parts")
                found_components['_format'] = 'mixed_delimiters'
        
        # Handle very long addresses (200+ chars) by focusing on key components
        if len(address_text) > 200:
            found_components['_format'] = 'very_long'
            matched_patterns.append("very long address - focused extraction")
        
        # Calculate confidence (lower for edge cases)
        confidence = 0.6 if found_components else 0.3
        
        return {
            'components': found_components,
            'confidence': confidence,
            'patterns': matched_patterns
        }
    
    def _compile_building_hierarchy_patterns(self) -> List[Dict[str, Any]]:
        """Compile building hierarchy pattern rules"""
        return [
            {
                'name': 'site_pattern',
                'pattern': r'([A-ZÇĞİÖŞÜa-zçğıiöşü]+(?:\s+[A-ZÇĞİÖŞÜa-zçğıiöşü]+){0,2})\s+[Ss]itesi',
                'confidence': 0.95,
                'component': 'site'
            },
            {
                'name': 'apartman_pattern',
                'pattern': r'([A-ZÇĞİÖŞÜa-zçğıiöşü]+(?:\s+[A-ZÇĞİÖŞÜa-zçğıiöşü]+){0,2})\s+[Aa]partman[ıi]',
                'confidence': 0.95,
                'component': 'apartman'
            },
            {
                'name': 'blok_pattern',
                'pattern': r'([A-Za-z])\s+[Bb]lok',
                'confidence': 0.9,
                'component': 'blok'
            },
            {
                'name': 'kat_pattern',
                'pattern': r'(\d+)\.?\s+[Kk]at',
                'confidence': 0.9,
                'component': 'kat'
            }
        ]
    
    def _compile_regional_patterns(self) -> List[Dict[str, Any]]:
        """Compile regional variation pattern rules"""
        return [
            {
                'name': 'köy_pattern',
                'pattern': r'([A-ZÇĞİÖŞÜa-zçğıiöşü]+(?:\s+[A-ZÇĞİÖŞÜa-zçğıiöşü]+)?)\s+[Kk]öy[üu]?',
                'confidence': 0.9,
                'component': 'köy'
            },
            {
                'name': 'belde_pattern',
                'pattern': r'([A-ZÇĞİÖŞÜa-zçğıiöşü]+(?:\s+[A-ZÇĞİÖŞÜa-zçğıiöşü]+)?)\s+[Bb]elde',
                'confidence': 0.9,
                'component': 'belde'
            },
            {
                'name': 'mevkii_pattern',
                'pattern': r'([A-ZÇĞİÖŞÜa-zçğıiöşü]+(?:\s+[A-ZÇĞİÖŞÜa-zçğıiöşü]+)?)\s+[Mm]evki[i]?',
                'confidence': 0.85,
                'component': 'mevkii'
            }
        ]
    
    def _compile_complex_patterns(self) -> List[Dict[str, Any]]:
        """Compile complex building pattern rules"""
        return [
            {
                'name': 'colon_format',
                'pattern': r'no\s*:\s*([0-9]+(?:[/\-][A-Za-z0-9]+)?)',
                'confidence': 0.95,
                'component': 'bina_no'
            },
            {
                'name': 'compound_building',
                'pattern': r'([A-Za-z])\s+blok\s+(\d+)\.?\s+kat\s+(?:daire\s+)?(\d+)',
                'confidence': 0.9,
                'components': ['blok', 'kat', 'daire']
            },
            {
                'name': 'intersection',
                'pattern': r'kesişimi|arası|köşesi',
                'confidence': 0.85,
                'component': 'kesişim'
            }
        ]
    
    def _load_abbreviation_expansions(self) -> Dict[str, str]:
        """Load common Turkish address abbreviation expansions"""
        return {
            # Cities
            'ist': 'istanbul',
            'ank': 'ankara',
            'izm': 'izmir',
            'ant': 'antalya',
            'bur': 'bursa',
            # Districts
            'kad': 'kadıköy',
            'beş': 'beşiktaş',
            'şiş': 'şişli',
            'bak': 'bakırköy',
            'üsk': 'üsküdar',
            # Common street names
            'ata': 'atatürk',
            'cum': 'cumhuriyet',
            'ist': 'istiklal',
            # Components
            'mah': 'mahallesi',
            'cad': 'caddesi',
            'sk': 'sokak',
            'apt': 'apartmanı',
            'blk': 'blok'
        }
    
    def _expand_abbreviations(self, text: str) -> str:
        """Expand common abbreviations in text"""
        expanded = text
        for abbrev, expansion in self.abbreviation_expansions.items():
            # Use word boundaries to avoid partial replacements
            pattern = r'\b' + re.escape(abbrev) + r'\b'
            expanded = re.sub(pattern, expansion, expanded, flags=re.IGNORECASE)
        return expanded
    
    def _create_empty_result(self, confidence: float, method: str) -> Dict[str, Any]:
        """Create empty result structure"""
        return {
            'components': {},
            'confidence': confidence,
            'processing_time_ms': 0.0,
            'matched_patterns': [],
            'extraction_methods': [method]
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get performance statistics"""
        success_rate = (self.stats['successful_extractions'] / self.stats['total_queries'] 
                       if self.stats['total_queries'] > 0 else 0.0)
        
        return {
            'total_queries': self.stats['total_queries'],
            'successful_extractions': self.stats['successful_extractions'],
            'success_rate': success_rate,
            'building_hierarchy_found': self.stats['building_hierarchy_found'],
            'regional_variations_found': self.stats['regional_variations_found'],
            'edge_cases_handled': self.stats['edge_cases_handled'],
            'average_processing_time_ms': self.stats['average_processing_time_ms']
        }


def test_advanced_pattern_engine():
    """Test function for Advanced Pattern Engine"""
    print("🧪 Testing Advanced Pattern Engine - Phase 3")
    print("=" * 70)
    
    # Initialize engine
    try:
        advanced_engine = AdvancedPatternEngine()
        print(f"✅ Advanced Pattern Engine initialized")
        print(f"   Building patterns: {len(advanced_engine.building_hierarchy_patterns)}")
        print(f"   Regional patterns: {len(advanced_engine.regional_patterns)}")
        print(f"   Complex patterns: {len(advanced_engine.complex_patterns)}")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return
    
    # Critical test cases for Phase 3
    test_cases = [
        {
            'name': 'Complex Building Test',
            'input': "Çiçek Sitesi A blok 3. kat daire 12 Atatürk Cad. Ankara",
            'expected': {
                'site': 'Çiçek Sitesi',
                'blok': 'A',
                'kat': '3',
                'daire': '12'
            }
        },
        {
            'name': 'Regional Variation Test',
            'input': "Yeşilköy beldesi merkez mah. çiçek sk. no:5",
            'expected': {
                'belde': 'Yeşilköy'
            }
        },
        {
            'name': 'Colon Format Test',
            'input': "no:25/A kat:3 daire:12",
            'expected': {
                'bina_no': '25/A',
                'kat': '3',
                'daire': '12'
            }
        },
        {
            'name': 'Apartman + Blok Test',
            'input': "Gül Apartmanı B blok 5. kat",
            'expected': {
                'apartman': 'Gül Apartmanı',
                'blok': 'B',
                'kat': '5'
            }
        },
        {
            'name': 'Köy Pattern Test',
            'input': "Çiçekli köyü merkez",
            'expected': {
                'köy': 'Çiçekli'
            }
        },
        {
            'name': 'Edge Case - Abbreviated',
            'input': "ist kad mod 15",
            'expected_expanded': True
        },
        {
            'name': 'Intersection Test',
            'input': "Atatürk Cad. ile Barış Sk. kesişimi",
            'expected': {
                'cadde': 'Atatürk Caddesi',
                'sokak': 'Barış Sokak',
                'kesişim': 'true'
            }
        },
        {
            'name': 'Floor Variations',
            'input': "zemin kat daire 1",
            'expected': {
                'kat': 'Zemin',
                'daire': '1'
            }
        }
    ]
    
    print(f"\n🧪 Running {len(test_cases)} Phase 3 test cases:")
    
    passed_tests = 0
    failed_tests = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Input: '{test_case['input']}'")
        
        try:
            result = advanced_engine.extract_advanced_components(test_case['input'])
            components = result['components']
            confidence = result['confidence']
            processing_time = result['processing_time_ms']
            
            print(f"   Result: {components}")
            print(f"   Confidence: {confidence:.2f}")
            print(f"   Processing time: {processing_time:.2f}ms")
            
            # Check if expected components are found
            test_passed = True
            if 'expected' in test_case:
                for expected_component, expected_value in test_case['expected'].items():
                    actual_value = components.get(expected_component)
                    if actual_value != expected_value:
                        print(f"   ❌ {expected_component}: expected '{expected_value}', got '{actual_value}'")
                        test_passed = False
            elif 'expected_expanded' in test_case:
                # Check if abbreviations were expanded
                if '_expanded' in components:
                    print(f"   ✅ Abbreviations expanded: {components['_expanded']}")
                    test_passed = True
                else:
                    print(f"   ❌ No abbreviation expansion detected")
                    test_passed = False
            
            if test_passed and components:
                print(f"   ✅ PASS")
                passed_tests += 1
            else:
                print(f"   ❌ FAIL")
                failed_tests += 1
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            failed_tests += 1
    
    # Display statistics
    stats = advanced_engine.get_statistics()
    print(f"\nPerformance Statistics:")
    print(f"   Total queries: {stats['total_queries']}")
    print(f"   Successful extractions: {stats['successful_extractions']}")
    print(f"   Success rate: {stats['success_rate']:.1%}")
    print(f"   Building hierarchy found: {stats['building_hierarchy_found']}")
    print(f"   Regional variations found: {stats['regional_variations_found']}")
    print(f"   Edge cases handled: {stats['edge_cases_handled']}")
    print(f"   Average time: {stats['average_processing_time_ms']:.2f}ms")
    
    # Summary
    total_tests = passed_tests + failed_tests
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n" + "=" * 70)
    print(f"PHASE 3 TEST SUMMARY:")
    print(f"   Total tests: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {failed_tests}")
    print(f"   Success rate: {success_rate:.1f}%")
    
    if success_rate >= 85:
        print(f"\n🎉 PHASE 3 IMPLEMENTATION SUCCESSFUL!")
        print(f"✅ Advanced pattern recognition working")
        print(f"✅ Building hierarchy detection operational")
        print(f"✅ Regional variations supported")
        print(f"✅ Edge case handling functional")
        return True
    else:
        print(f"\n🔧 PHASE 3 NEEDS IMPROVEMENTS:")
        print(f"❌ Success rate below 85% target")
        print(f"🔧 Review failed cases and improve pattern logic")
        return False


if __name__ == "__main__":
    test_advanced_pattern_engine()