"""
TEKNOFEST 2025 - Geographic Intelligence Engine
Phase 1: Position-Independent Geographic Component Detection

This module provides intelligent geographic anchor detection using Turkey's
administrative hierarchy database (55,955 records) to identify il/ilçe/mahalle
components regardless of their position in the address text.

Key Features:
- Detects geographic components anywhere in address text
- Handles "district city" patterns (e.g., "keçiören ankara")
- Fills missing hierarchy levels using database relationships
- Supports Turkish character variations and common misspellings
"""

import logging
import pandas as pd
import re
from typing import Dict, List, Tuple, Any, Set, Optional
from pathlib import Path
from difflib import SequenceMatcher
import time

class GeographicIntelligence:
    """
    TEKNOFEST Geographic Intelligence Engine
    
    Detects and enriches geographic components using Turkey's complete
    administrative hierarchy database with position-independent matching.
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize Geographic Intelligence Engine
        
        Args:
            data_path: Path to enhanced_turkish_neighborhoods.csv
        """
        self.logger = logging.getLogger(__name__)
        
        # Determine data path
        if data_path is None:
            current_dir = Path(__file__).parent.parent
            data_path = current_dir / "database" / "enhanced_turkish_neighborhoods.csv"
        
        # Build Turkish character normalization first
        self.turkish_char_map = self._build_turkish_char_map()
        
        # Load and index administrative database
        self.admin_hierarchy = self.load_administrative_database(data_path)
        
        # Build fast lookup indexes
        self.city_lookup = self.build_city_lookup_index()
        self.district_lookup = self.build_district_lookup_index()
        self.neighborhood_lookup = self.build_neighborhood_lookup_index()
        
        # Performance tracking
        self.stats = {
            'total_queries': 0,
            'successful_detections': 0,
            'hierarchy_enrichments': 0,
            'average_processing_time_ms': 0.0
        }
        
        self.logger.info(f"GeographicIntelligence initialized with {len(self.admin_hierarchy)} administrative records")
        self.logger.info(f"Indexes built: {len(self.city_lookup)} cities, {len(self.district_lookup)} districts, {len(self.neighborhood_lookup)} neighborhoods")
    
    def detect_geographic_anchors(self, address_text: str) -> Dict[str, Any]:
        """
        Main method: Find il/ilçe/mahalle anywhere in address text
        
        Args:
            address_text: Raw address string to analyze
            
        Returns:
            {
                'components': {'il': str, 'ilçe': str, 'mahalle': str},
                'confidence': float,
                'detection_method': str,
                'processing_time_ms': float,
                'matched_patterns': List[str]
            }
            
        Test Cases:
            "keçiören ankara" → {'il': 'Ankara', 'ilçe': 'Keçiören'}
            "istanbul kadıköy" → {'il': 'İstanbul', 'ilçe': 'Kadıköy'}
            "moda mahallesi" → {'mahalle': 'Moda', 'ilçe': 'Kadıköy', 'il': 'İstanbul'}
        """
        
        start_time = time.time()
        self.stats['total_queries'] += 1
        
        if not address_text or not isinstance(address_text, str):
            print(f"   ❌ Invalid input - returning empty result")
            return self._create_empty_result(0.0, "invalid_input")
        
        # Normalize address text for better matching
        normalized_text = self._normalize_turkish_text(address_text.lower().strip())
        
        # Initialize result structure
        found_components = {}
        matched_patterns = []
        confidence_scores = []
        detection_methods = []
        
        try:
            # Phase 1: Detect explicit geographic patterns
            city_district_patterns = self._detect_city_district_patterns(normalized_text)
            if city_district_patterns:
                found_components.update(city_district_patterns['components'])
                matched_patterns.extend(city_district_patterns['patterns'])
                confidence_scores.append(city_district_patterns['confidence'])
                detection_methods.append('city_district_pattern')
            
            # Phase 2: Detect standalone cities
            if 'il' not in found_components:
                city_matches = self._detect_standalone_cities(normalized_text)
                if city_matches:
                    found_components.update(city_matches['components'])
                    matched_patterns.extend(city_matches['patterns'])
                    confidence_scores.append(city_matches['confidence'])
                    detection_methods.append('standalone_city')
            
            # Phase 3: Detect standalone districts (with city lookup)
            if 'ilçe' not in found_components:
                district_matches = self._detect_standalone_districts(normalized_text)
                if district_matches:
                    found_components.update(district_matches['components'])
                    matched_patterns.extend(district_matches['patterns'])
                    confidence_scores.append(district_matches['confidence'])
                    detection_methods.append('standalone_district')
            
            # Phase 4: Detect neighborhoods (with full hierarchy lookup)
            if 'mahalle' not in found_components:
                neighborhood_matches = self._detect_neighborhoods(normalized_text)
                if neighborhood_matches:
                    # Only add components that don't already exist (preserve higher-confidence matches)
                    for component, value in neighborhood_matches['components'].items():
                        if component not in found_components:
                            found_components[component] = value
                    matched_patterns.extend(neighborhood_matches['patterns'])
                    confidence_scores.append(neighborhood_matches['confidence'])
                    detection_methods.append('neighborhood_lookup')
            
            # Phase 5: Build hierarchical context for missing levels
            if found_components:
                enriched_components = self.build_hierarchical_context(found_components)
                if len(enriched_components) > len(found_components):
                    self.stats['hierarchy_enrichments'] += 1
                    found_components = enriched_components
                    detection_methods.append('hierarchy_enrichment')
            
            # Calculate overall confidence and method
            overall_confidence = max(confidence_scores) if confidence_scores else 0.0
            primary_method = detection_methods[0] if detection_methods else 'no_detection'
            
            # Track successful detections
            if found_components:
                self.stats['successful_detections'] += 1
            
        except Exception as e:
            self.logger.error(f"Error in geographic detection for '{address_text}': {e}")
            found_components = {}
            overall_confidence = 0.0
            primary_method = 'error'
            matched_patterns = []
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000
        self.stats['average_processing_time_ms'] = (
            (self.stats['average_processing_time_ms'] * (self.stats['total_queries'] - 1) + processing_time) / 
            self.stats['total_queries']
        )
        
        return {
            'components': found_components,
            'confidence': overall_confidence,
            'detection_method': primary_method,
            'processing_time_ms': processing_time,
            'matched_patterns': matched_patterns,
            'detection_methods': detection_methods
        }
    
    def build_hierarchical_context(self, found_components: Dict[str, str]) -> Dict[str, str]:
        """
        Fill missing hierarchy levels using database relationships
        
        Args:
            found_components: Partially detected components
            
        Returns:
            Complete hierarchy with missing levels filled
            
        Example:
            Input: {'ilçe': 'Keçiören'}
            Output: {'ilçe': 'Keçiören', 'il': 'Ankara'}
        """
        enriched_components = found_components.copy()
        
        try:
            # If we have mahalle, try to find its ilçe and il
            if 'mahalle' in found_components:
                mahalle_name = self._normalize_turkish_text(found_components['mahalle'])
                if mahalle_name in self.neighborhood_lookup:
                    neighborhood_info = self.neighborhood_lookup[mahalle_name]
                    if 'ilçe' not in enriched_components and neighborhood_info['ilçe']:
                        enriched_components['ilçe'] = neighborhood_info['ilçe']
                    if 'il' not in enriched_components and neighborhood_info['il']:
                        enriched_components['il'] = neighborhood_info['il']
            
            # If we have ilçe, try to find its il
            if 'ilçe' in found_components and 'il' not in enriched_components:
                district_name = self._normalize_turkish_text(found_components['ilçe'])
                if district_name in self.district_lookup:
                    district_info = self.district_lookup[district_name]
                    if district_info['il']:
                        enriched_components['il'] = district_info['il']
            
        except Exception as e:
            self.logger.warning(f"Error building hierarchical context: {e}")
        
        return enriched_components
    
    def _detect_city_district_patterns(self, normalized_text: str) -> Optional[Dict[str, Any]]:
        """
        Detect "city district" and "district city" patterns
        
        Examples:
        - "ankara keçiören" → Ankara (il) + Keçiören (ilçe)
        - "keçiören ankara" → Ankara (il) + Keçiören (ilçe)
        - "istanbul kadıköy" → İstanbul (il) + Kadıköy (ilçe)
        """
        patterns = [
            # Pattern 1: "city district" (ankara keçiören)
            r'\b(' + '|'.join(re.escape(city) for city in self.city_lookup.keys()) + r')\s+(' + '|'.join(re.escape(district) for district in self.district_lookup.keys()) + r')\b',
            
            # Pattern 2: "district city" (keçiören ankara)  
            r'\b(' + '|'.join(re.escape(district) for district in self.district_lookup.keys()) + r')\s+(' + '|'.join(re.escape(city) for city in self.city_lookup.keys()) + r')\b',
            
            # Pattern 3: "city/district" or "district/city"
            r'\b(' + '|'.join(re.escape(city) for city in self.city_lookup.keys()) + r')[/\-](' + '|'.join(re.escape(district) for district in self.district_lookup.keys()) + r')\b',
            r'\b(' + '|'.join(re.escape(district) for district in self.district_lookup.keys()) + r')[/\-](' + '|'.join(re.escape(city) for city in self.city_lookup.keys()) + r')\b'
        ]
        
        for i, pattern in enumerate(patterns):
            matches = re.finditer(pattern, normalized_text, re.IGNORECASE)
            for match in matches:
                word1, word2 = match.groups()
                word1_norm = self._normalize_turkish_text(word1)
                word2_norm = self._normalize_turkish_text(word2)
                
                # Determine which is city and which is district
                if i == 0:  # city district
                    city_name = word1_norm
                    district_name = word2_norm
                elif i == 1:  # district city
                    city_name = word2_norm
                    district_name = word1_norm
                elif i == 2:  # city/district
                    city_name = word1_norm
                    district_name = word2_norm
                else:  # district/city
                    city_name = word2_norm
                    district_name = word1_norm
                
                # Validate the combination exists in our database
                if (city_name in self.city_lookup and 
                    district_name in self.district_lookup and
                    self._validate_city_district_relationship(city_name, district_name)):
                    
                    return {
                        'components': {
                            'il': self.city_lookup[city_name]['proper_name'],
                            'ilçe': self.district_lookup[district_name]['proper_name']
                        },
                        'confidence': 0.95,
                        'patterns': [f"{word1} {word2}"]
                    }
                elif city_name in self.city_lookup or district_name in self.district_lookup:
                    # Debug: At least one component found, return partial match
                    components = {}
                    if city_name in self.city_lookup:
                        components['il'] = self.city_lookup[city_name]['proper_name']
                    if district_name in self.district_lookup:
                        components['ilçe'] = self.district_lookup[district_name]['proper_name']
                    
                    return {
                        'components': components,
                        'confidence': 0.85,
                        'patterns': [f"{word1} {word2}"]
                    }
        
        return None
    
    def _detect_standalone_cities(self, normalized_text: str) -> Optional[Dict[str, Any]]:
        """Detect standalone city names"""
        city_matches = []
        
        # Create word boundary pattern for all cities
        city_names = list(self.city_lookup.keys())
        
        # Sort by length (longest first) to prioritize longer matches
        city_names.sort(key=len, reverse=True)
        
        for city_name in city_names:
            # Use word boundary pattern
            pattern = r'\b' + re.escape(city_name) + r'\b'
            if re.search(pattern, normalized_text, re.IGNORECASE):
                if city_name in self.city_lookup:  # Additional safety check
                    city_info = self.city_lookup[city_name]
                    city_matches.append({
                        'name': city_name,
                        'proper_name': city_info['proper_name'],
                        'confidence': 0.90
                    })
                    break  # Take the first (longest) match
        
        if city_matches:
            return {
                'components': {'il': city_matches[0]['proper_name']},
                'confidence': city_matches[0]['confidence'],
                'patterns': [city_matches[0]['name']]
            }
        
        return None
    
    def _detect_standalone_districts(self, normalized_text: str) -> Optional[Dict[str, Any]]:
        """Detect standalone district names and lookup their cities"""
        district_names = list(self.district_lookup.keys())
        district_names.sort(key=len, reverse=True)
        
        for district_name in district_names:
            pattern = r'\b' + re.escape(district_name) + r'\b'
            if re.search(pattern, normalized_text, re.IGNORECASE):
                if district_name in self.district_lookup:  # Additional safety check
                    district_info = self.district_lookup[district_name]
                    components = {'ilçe': district_info['proper_name']}
                    
                    # Add city if available
                    if district_info['il']:
                        components['il'] = district_info['il']
                    
                    return {
                        'components': components,
                        'confidence': 0.85,
                        'patterns': [district_name]
                    }
        
        return None
    
    def _detect_neighborhoods(self, normalized_text: str) -> Optional[Dict[str, Any]]:
        """Detect neighborhood names and lookup their full hierarchy"""
        # Look for neighborhood patterns
        neighborhood_patterns = [
            r'\b([a-züçğıöş]+(?:\s+[a-züçğıöş]+){0,2})\s+mah(?:allesi?)?\b',
            r'\bmah(?:alle)?\s+([a-züçğıöş]+(?:\s+[a-züçğıöş]+){0,2})\b'
        ]
        
        for pattern in neighborhood_patterns:
            matches = re.finditer(pattern, normalized_text, re.IGNORECASE)
            for match in matches:
                # First try the extracted neighborhood name
                neighborhood_name = self._normalize_turkish_text(match.group(1))
                full_match = self._normalize_turkish_text(match.group(0))
                
                # Try both the extracted name and the full match
                lookup_candidates = [neighborhood_name, full_match]
                
                for candidate in lookup_candidates:
                    if candidate in self.neighborhood_lookup:
                        neighborhood_info = self.neighborhood_lookup[candidate]
                        components = {'mahalle': neighborhood_info['proper_name']}
                        
                        # Add higher levels if available
                        if neighborhood_info['ilçe']:
                            components['ilçe'] = neighborhood_info['ilçe']
                        if neighborhood_info['il']:
                            components['il'] = neighborhood_info['il']
                        
                        return {
                            'components': components,
                            'confidence': 0.80,
                            'patterns': [match.group(0)]
                        }
                        break  # Found a match, stop trying candidates
        
        return None
    
    def load_administrative_database(self, data_path: Path) -> List[Dict[str, Any]]:
        """
        Load existing 55,955 administrative records and build lookup structures
        
        Args:
            data_path: Path to enhanced_turkish_neighborhoods.csv
            
        Returns:
            List of administrative records
        """
        try:
            if isinstance(data_path, str):
                data_path = Path(data_path)
            
            if not data_path.exists():
                self.logger.error(f"Administrative database not found: {data_path}")
                return []
            
            # Load CSV data
            df = pd.read_csv(data_path, encoding='utf-8')
            
            # Convert to list of dictionaries
            admin_records = []
            for _, row in df.iterrows():
                record = {
                    'il': str(row.get('il_adi', '')).strip() if pd.notna(row.get('il_adi')) else '',
                    'ilçe': str(row.get('ilce_adi', '')).strip() if pd.notna(row.get('ilce_adi')) else '',
                    'mahalle': str(row.get('mahalle_adi', '')).strip() if pd.notna(row.get('mahalle_adi')) else '',
                    'latitude': float(row.get('latitude', 0)) if pd.notna(row.get('latitude')) and row.get('latitude', 0) != 0 else None,
                    'longitude': float(row.get('longitude', 0)) if pd.notna(row.get('longitude')) and row.get('longitude', 0) != 0 else None
                }
                
                # Only add records with valid data
                if record['il'] or record['ilçe'] or record['mahalle']:
                    admin_records.append(record)
            
            self.logger.info(f"Loaded {len(admin_records)} administrative records from {data_path}")
            return admin_records
            
        except Exception as e:
            self.logger.error(f"Error loading administrative database: {e}")
            return []
    
    def build_city_lookup_index(self) -> Dict[str, Dict[str, Any]]:
        """Create fast lookup: city_name → province info"""
        city_lookup = {}
        
        for record in self.admin_hierarchy:
            if record['il'] and record['il'] != 'Unknown':
                city_name = self._normalize_turkish_text(record['il'])
                if city_name not in city_lookup:
                    city_lookup[city_name] = {
                        'proper_name': record['il'],
                        'districts': set(),
                        'neighborhoods': set()
                    }
                
                # Add district and neighborhood info
                if record['ilçe']:
                    city_lookup[city_name]['districts'].add(record['ilçe'])
                if record['mahalle']:
                    city_lookup[city_name]['neighborhoods'].add(record['mahalle'])
        
        # Convert sets to lists for JSON serialization
        for city_info in city_lookup.values():
            city_info['districts'] = list(city_info['districts'])
            city_info['neighborhoods'] = list(city_info['neighborhoods'])
        
        return city_lookup
    
    def build_district_lookup_index(self) -> Dict[str, Dict[str, Any]]:
        """Create fast lookup: district_name → city info"""
        district_lookup = {}
        
        for record in self.admin_hierarchy:
            if record['ilçe'] and record['il'] != 'Unknown' and record['ilçe'] != 'Unknown':
                district_name = self._normalize_turkish_text(record['ilçe'])
                if district_name not in district_lookup:
                    district_lookup[district_name] = {
                        'proper_name': record['ilçe'],
                        'il': record['il'],
                        'neighborhoods': set()
                    }
                
                # Add neighborhood info
                if record['mahalle']:
                    district_lookup[district_name]['neighborhoods'].add(record['mahalle'])
        
        # Convert sets to lists
        for district_info in district_lookup.values():
            district_info['neighborhoods'] = list(district_info['neighborhoods'])
        
        return district_lookup
    
    def build_neighborhood_lookup_index(self) -> Dict[str, Dict[str, Any]]:
        """Create fast lookup: neighborhood_name → full hierarchy"""
        neighborhood_lookup = {}
        
        for record in self.admin_hierarchy:
            if record['mahalle'] and record['il'] != 'Unknown' and record['ilçe'] != 'Unknown':
                neighborhood_name = self._normalize_turkish_text(record['mahalle'])
                if neighborhood_name not in neighborhood_lookup:
                    neighborhood_lookup[neighborhood_name] = {
                        'proper_name': record['mahalle'],
                        'ilçe': record['ilçe'],
                        'il': record['il'],
                        'coordinates': []
                    }
                
                # Add coordinate info if available
                if record['latitude'] and record['longitude']:
                    neighborhood_lookup[neighborhood_name]['coordinates'].append({
                        'latitude': record['latitude'],
                        'longitude': record['longitude']
                    })
        
        return neighborhood_lookup
    
    def _validate_city_district_relationship(self, city_name: str, district_name: str) -> bool:
        """Validate that a district actually belongs to a city"""
        if city_name in self.city_lookup and district_name in self.district_lookup:
            district_info = self.district_lookup[district_name]
            city_info = self.city_lookup[city_name]
            return district_info['il'] == city_info['proper_name']
        return False
    
    def _normalize_turkish_text(self, text: str) -> str:
        """Normalize Turkish text for consistent matching"""
        if not text:
            return ""
        
        # First apply Turkish character normalization before lowercasing
        normalized = text
        for char, replacement in self.turkish_char_map.items():
            normalized = normalized.replace(char, replacement)
        
        # Then lowercase after character replacement
        normalized = normalized.lower()
        
        # Remove extra spaces and punctuation
        normalized = re.sub(r'[^\w\s]', ' ', normalized)
        normalized = re.sub(r'\s+', ' ', normalized)
        
        return normalized.strip()
    
    def _build_turkish_char_map(self) -> Dict[str, str]:
        """Build Turkish character normalization map"""
        return {
            'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
            'Ç': 'c', 'Ğ': 'g', 'I': 'i', 'İ': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u',
            # Handle combining characters
            'i̇': 'i'  # Dotted i combining character
        }
    
    def _create_empty_result(self, confidence: float, method: str) -> Dict[str, Any]:
        """Create empty result structure"""
        return {
            'components': {},
            'confidence': confidence,
            'detection_method': method,
            'processing_time_ms': 0.0,
            'matched_patterns': [],
            'detection_methods': []
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get performance statistics"""
        success_rate = (self.stats['successful_detections'] / self.stats['total_queries'] 
                       if self.stats['total_queries'] > 0 else 0.0)
        
        return {
            'total_queries': self.stats['total_queries'],
            'successful_detections': self.stats['successful_detections'],
            'success_rate': success_rate,
            'hierarchy_enrichments': self.stats['hierarchy_enrichments'],
            'average_processing_time_ms': self.stats['average_processing_time_ms'],
            'database_size': len(self.admin_hierarchy),
            'city_count': len(self.city_lookup),
            'district_count': len(self.district_lookup),
            'neighborhood_count': len(self.neighborhood_lookup)
        }
    
    def _critical_debug_database_lookups(self, original_text: str, normalized_text: str):
        """Debug method to analyze database lookups"""
        print(f"\n📂 DEBUG Database Lookup Analysis:")
        
        # Test specific keywords we expect
        test_terms = ['keçiören', 'ankara', 'etlik']
        
        for term in test_terms:
            print(f"\n   Testing term: '{term}'")
            term_norm = self._normalize_turkish_text(term)
            print(f"   Normalized: '{term_norm}'")
            
            # Check in each lookup
            city_found = term_norm in self.city_lookup
            district_found = term_norm in self.district_lookup  
            neighborhood_found = term_norm in self.neighborhood_lookup
            
            print(f"   In city_lookup: {city_found}")
            print(f"   In district_lookup: {district_found}")
            print(f"   In neighborhood_lookup: {neighborhood_found}")
            
            if city_found:
                print(f"   City data: {self.city_lookup[term_norm]['proper_name']}")
            if district_found:
                print(f"   District data: {self.district_lookup[term_norm]['proper_name']}")
            if neighborhood_found:
                print(f"   Neighborhood data: {self.neighborhood_lookup[term_norm]['proper_name']}")
        
        # Test pattern matching
        print(f"\n🔍 DEBUG Pattern Analysis:")
        
        # Test if our target patterns exist in text
        patterns_to_test = [
            'keçiören ankara',
            'ankara keçiören', 
            'keciören ankara',
            'ankara keciören'
        ]
        
        for pattern in patterns_to_test:
            pattern_norm = self._normalize_turkish_text(pattern)
            found_in_text = pattern_norm in normalized_text
            found_in_original = pattern.lower() in original_text.lower()
            
            print(f"   Pattern '{pattern}' → '{pattern_norm}'")
            print(f"     In normalized text: {found_in_text}")
            print(f"     In original text: {found_in_original}")
        
        # Debug city and district lists  
        print(f"\n📋 DEBUG Database Content Sample:")
        city_sample = list(self.city_lookup.keys())[:10]
        district_sample = list(self.district_lookup.keys())[:10] 
        print(f"   First 10 cities: {city_sample}")
        print(f"   First 10 districts: {district_sample}")


def test_geographic_intelligence():
    """Test function for Geographic Intelligence Engine"""
    print("🧪 Testing Geographic Intelligence Engine")
    print("=" * 50)
    
    # Initialize engine
    try:
        geo_intel = GeographicIntelligence()
        print(f"✅ Geographic Intelligence Engine initialized")
        print(f"   Database: {len(geo_intel.admin_hierarchy)} records")
        print(f"   Cities: {len(geo_intel.city_lookup)}")
        print(f"   Districts: {len(geo_intel.district_lookup)}")
        print(f"   Neighborhoods: {len(geo_intel.neighborhood_lookup)}")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return
    
    # Critical test cases
    test_cases = [
        {
            'name': 'District + City at end',
            'input': "Etlik mah Süleymaniye Cad 231.sk no3 / 12 keçiören ankara",
            'expected_components': ['il', 'ilçe'],
            'expected_il': 'Ankara',
            'expected_ilçe': 'Keçiören'
        },
        {
            'name': 'City only',
            'input': "moda mahallesi caferağa sokak istanbul",
            'expected_components': ['il'],
            'expected_il': 'İstanbul'
        },
        {
            'name': 'District only (should find city)',
            'input': "etlik mahallesi keçiören",
            'expected_components': ['il', 'ilçe'],
            'expected_il': 'Ankara',
            'expected_ilçe': 'Keçiören'
        },
        {
            'name': 'Neighborhood (should find district + city)',
            'input': "moda mahallesi caferağa sokak",
            'expected_components': ['mahalle'],  # May also find il, ilçe
            'expected_mahalle': 'Moda'
        }
    ]
    
    print(f"\\n🧪 Running {len(test_cases)} critical test cases:")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\\n{i}. {test_case['name']}")
        print(f"   Input: '{test_case['input']}'")
        
        try:
            result = geo_intel.detect_geographic_anchors(test_case['input'])
            components = result['components']
            
            print(f"   Result: {components}")
            print(f"   Confidence: {result['confidence']:.2f}")
            print(f"   Method: {result['detection_method']}")
            print(f"   Time: {result['processing_time_ms']:.2f}ms")
            
            # Check expected components
            success = True
            for component in test_case['expected_components']:
                if component not in components:
                    print(f"   ❌ Missing component: {component}")
                    success = False
            
            # Check specific values if provided
            for key in ['expected_il', 'expected_ilçe', 'expected_mahalle']:
                if key in test_case:
                    component_type = key.replace('expected_', '')
                    expected_value = test_case[key]
                    actual_value = components.get(component_type)
                    
                    if actual_value != expected_value:
                        print(f"   ❌ {component_type}: Expected '{expected_value}', got '{actual_value}'")
                        success = False
            
            if success and components:
                print(f"   ✅ Test passed")
            elif not components:
                print(f"   ⚠️  No components detected")
            else:
                print(f"   ❌ Test failed")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Display statistics
    stats = geo_intel.get_statistics()
    print(f"\\n📊 Performance Statistics:")
    print(f"   Total queries: {stats['total_queries']}")
    print(f"   Successful detections: {stats['successful_detections']}")
    print(f"   Success rate: {stats['success_rate']:.1%}")
    print(f"   Average time: {stats['average_processing_time_ms']:.2f}ms")
    print(f"   Hierarchy enrichments: {stats['hierarchy_enrichments']}")


if __name__ == "__main__":
    test_geographic_intelligence()