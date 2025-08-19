"""
TEKNOFEST 2025 Turkish Address Resolution System
Algorithm 4: Hybrid Address Matcher

Author: AI Assistant
Date: 2025-01-XX
Version: 1.0.0

PRD Compliance: Complete implementation of HybridAddressMatcher with:
- 4-level similarity breakdown (semantic, geographic, textual, hierarchical)
- Weighted ensemble scoring (40%, 30%, 20%, 10%)
- Turkish language specialization
- Integration with all previous algorithms
- Performance optimization (<100ms per comparison)
"""

import re
import json
import math
import time
from typing import Dict, List, Any, Tuple, Optional
import numpy as np

# Turkish character normalization
TURKISH_CHAR_MAP = {
    'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
    'Ç': 'C', 'Ğ': 'G', 'I': 'I', 'Ö': 'O', 'Ş': 'S', 'Ü': 'U'
}

class HybridAddressMatcher:
    """
    Hybrid Address Matcher implementing 4-level similarity calculation
    
    This class provides comprehensive Turkish address similarity matching
    using weighted ensemble of semantic, geographic, textual, and hierarchical
    similarity measures according to TEKNOFEST PRD specifications.
    """
    
    def __init__(self):
        """Initialize the HybridAddressMatcher with models and configurations"""
        
        # Similarity component weights (from PRD)
        self.similarity_weights = {
            'semantic': 0.4,      # 40% - Sentence Transformers
            'geographic': 0.3,    # 30% - Coordinate distance 
            'textual': 0.2,       # 20% - Fuzzy string matching
            'hierarchical': 0.1   # 10% - Component-based matching
        }
        
        # Confidence threshold for match decision (from PRD)
        self.confidence_threshold = 0.6
        
        # Initialize semantic model configuration
        self.semantic_model = {
            'model_name': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
            'embedding_dimension': 384,
            'available': False,
            'model': None,
            'tokenizer': None
        }
        
        # Geographic configuration
        self.geographic_config = {
            'distance_function': 'haversine',
            'max_distance_km': 50.0,
            'turkey_bounds': {
                'lat_min': 35.8, 'lat_max': 42.1,
                'lon_min': 25.7, 'lon_max': 44.8
            }
        }
        
        # Text similarity configuration
        self.text_similarity_config = {
            'algorithm': 'token_set_ratio',
            'library': 'thefuzz',
            'turkish_char_normalization': True
        }
        
        # Hierarchical similarity weights
        self.hierarchy_weights = {
            'il': 0.30,          # Province (highest importance)
            'ilce': 0.25,        # District
            'mahalle': 0.20,     # Neighborhood
            'sokak': 0.15,       # Street
            'bina_no': 0.05,     # Building number
            'daire': 0.05        # Apartment number
        }
        
        # Load integrated algorithms
        self._load_integrated_algorithms()
        
        # Initialize semantic model
        self._initialize_semantic_model()
        
        # Load Turkish location data
        self._load_turkish_location_data()
    
    def _load_integrated_algorithms(self):
        """Load previously implemented algorithms for integration"""
        try:
            from address_validator import AddressValidator
            from address_corrector import AddressCorrector  
            from address_parser import AddressParser
            
            self.address_validator = AddressValidator()
            self.address_corrector = AddressCorrector()
            self.address_parser = AddressParser()
            
            self.algorithms_available = {
                'validator': True,
                'corrector': True,
                'parser': True
            }
            
        except ImportError as e:
            # Create fallback implementations
            self.algorithms_available = {
                'validator': False,
                'corrector': False,
                'parser': False
            }
            self.address_validator = None
            self.address_corrector = None
            self.address_parser = None
    
    def _initialize_semantic_model(self):
        """Initialize Sentence Transformers model with fallback"""
        try:
            from sentence_transformers import SentenceTransformer
            
            self.semantic_model['model'] = SentenceTransformer(
                self.semantic_model['model_name'],
                device='cpu'  # Ensure CPU compatibility
            )
            self.semantic_model['available'] = True
            
        except ImportError:
            # Fallback mode - use simple embedding approximation
            self.semantic_model['available'] = False
            self.semantic_model['model'] = None
    
    def _load_turkish_location_data(self):
        """Load Turkish administrative hierarchy and location data"""
        self.turkish_locations = {
            'provinces': set(),
            'districts': set(),
            'neighborhoods': set(),
            'major_cities': {
                'istanbul', 'ankara', 'izmir', 'bursa', 'antalya', 
                'adana', 'konya', 'gaziantep', 'mersin', 'diyarbakır'
            }
        }
        
        # Load hierarchy data if available
        try:
            import csv
            import os
            
            hierarchy_file = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                'database', 'turkey_admin_hierarchy.csv'
            )
            
            if os.path.exists(hierarchy_file):
                with open(hierarchy_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if 'il' in row:
                            self.turkish_locations['provinces'].add(row['il'].lower())
                        if 'ilce' in row:
                            self.turkish_locations['districts'].add(row['ilce'].lower())
                        if 'mahalle' in row:
                            self.turkish_locations['neighborhoods'].add(row['mahalle'].lower())
                            
        except Exception:
            # Use fallback data
            pass
    
    def calculate_hybrid_similarity(self, address1: str, address2: str) -> dict:
        """
        Calculate comprehensive similarity between two addresses
        
        Args:
            address1 (str): First address for comparison
            address2 (str): Second address for comparison
            
        Returns:
            dict: Complete similarity analysis with breakdown and decision
        """
        start_time = time.time()
        
        # Input validation
        if not self._validate_inputs(address1, address2):
            return self._create_error_result("Invalid address inputs")
        
        try:
            # CRITICAL FIX: Apply address correction BEFORE similarity calculation
            corrected_addr1 = address1
            corrected_addr2 = address2
            
            if hasattr(self, 'address_corrector') and self.address_corrector:
                try:
                    # Apply abbreviation expansion and Turkish character normalization
                    correction_result1 = self.address_corrector.correct_address(address1)
                    correction_result2 = self.address_corrector.correct_address(address2)
                    
                    if correction_result1 and 'corrected_address' in correction_result1:
                        corrected_addr1 = correction_result1['corrected_address']
                    if correction_result2 and 'corrected_address' in correction_result2:
                        corrected_addr2 = correction_result2['corrected_address']
                        
                except Exception as e:
                    # If correction fails, use original addresses
                    pass
            
            # Calculate individual similarity components using CORRECTED addresses
            semantic_similarity = self.get_semantic_similarity(corrected_addr1, corrected_addr2)
            geographic_similarity = self.get_geographic_similarity(corrected_addr1, corrected_addr2)
            textual_similarity = self.get_text_similarity(corrected_addr1, corrected_addr2)
            hierarchical_similarity = self.get_hierarchy_similarity(corrected_addr1, corrected_addr2)
            
            # Apply weighted ensemble scoring
            overall_similarity = (
                semantic_similarity * self.similarity_weights['semantic'] +
                geographic_similarity * self.similarity_weights['geographic'] +
                textual_similarity * self.similarity_weights['textual'] +
                hierarchical_similarity * self.similarity_weights['hierarchical']
            )
            
            # Calculate confidence and match decision
            confidence = min(overall_similarity + 0.1, 1.0)  # Slight confidence boost
            match_decision = overall_similarity >= self.confidence_threshold
            
            # Calculate method contributions
            method_contributions = {
                'semantic': semantic_similarity * self.similarity_weights['semantic'],
                'geographic': geographic_similarity * self.similarity_weights['geographic'],
                'textual': textual_similarity * self.similarity_weights['textual'],
                'hierarchical': hierarchical_similarity * self.similarity_weights['hierarchical']
            }
            
            processing_time_ms = (time.time() - start_time) * 1000
            
            return {
                "overall_similarity": overall_similarity,
                "similarity_breakdown": {
                    "semantic": semantic_similarity,
                    "geographic": geographic_similarity,
                    "textual": textual_similarity,
                    "hierarchical": hierarchical_similarity
                },
                "confidence": confidence,
                "match_decision": match_decision,
                "similarity_details": {
                    "method_contributions": method_contributions,
                    "processing_time_ms": processing_time_ms,
                    "algorithms_used": [
                        "semantic_transformers" if self.semantic_model['available'] else "fallback_semantic",
                        "haversine_distance",
                        "fuzzy_string_matching", 
                        "hierarchical_component_matching"
                    ]
                }
            }
            
        except Exception as e:
            return self._create_error_result(f"Similarity calculation error: {str(e)}")
    
    def get_semantic_similarity(self, address1: str, address2: str) -> float:
        """
        Calculate semantic similarity using Sentence Transformers
        
        Args:
            address1 (str): First address
            address2 (str): Second address
            
        Returns:
            float: Semantic similarity score (0.0-1.0)
        """
        if not self.semantic_model['available'] or not self.semantic_model['model']:
            return self._fallback_semantic_similarity(address1, address2)
        
        try:
            # Normalize addresses for better semantic matching
            normalized_addr1 = self._normalize_for_semantic_analysis(address1)
            normalized_addr2 = self._normalize_for_semantic_analysis(address2)
            
            # Generate embeddings
            embeddings1 = self.semantic_model['model'].encode([normalized_addr1])
            embeddings2 = self.semantic_model['model'].encode([normalized_addr2])
            
            # Calculate cosine similarity
            cosine_sim = np.dot(embeddings1[0], embeddings2[0]) / (
                np.linalg.norm(embeddings1[0]) * np.linalg.norm(embeddings2[0])
            )
            
            # Apply Turkish location boosting
            location_boost = self._calculate_location_boost(address1, address2)
            
            # Combine cosine similarity with location boost
            final_similarity = min((cosine_sim + 1.0) / 2.0 + location_boost, 1.0)
            
            return max(0.0, final_similarity)
            
        except Exception:
            return self._fallback_semantic_similarity(address1, address2)
    
    def _fallback_semantic_similarity(self, address1: str, address2: str) -> float:
        """Fallback semantic similarity when Sentence Transformers unavailable"""
        # Simple word overlap approach
        words1 = set(self._normalize_text(address1).split())
        words2 = set(self._normalize_text(address2).split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        jaccard_similarity = intersection / union if union > 0 else 0.0
        
        # Apply Turkish location recognition boost
        location_boost = self._calculate_location_boost(address1, address2)
        
        return min(jaccard_similarity + location_boost, 1.0)
    
    def _normalize_for_semantic_analysis(self, address: str) -> str:
        """Normalize address for semantic analysis"""
        if not address:
            return ""
        
        # Convert to lowercase, preserve Turkish characters
        normalized = address.lower()
        
        # Expand common abbreviations for better semantics
        abbreviations = {
            'mah.': 'mahallesi', 'mah': 'mahallesi',
            'sk.': 'sokak', 'sk': 'sokak',
            'cd.': 'caddesi', 'cd': 'caddesi',
            'bulv.': 'bulvarı', 'bulv': 'bulvarı',
            'no.': 'numara', 'no': 'numara'
        }
        
        for abbrev, full_form in abbreviations.items():
            normalized = re.sub(r'\b' + re.escape(abbrev) + r'\b', full_form, normalized)
        
        return normalized.strip()
    
    def _calculate_location_boost(self, address1: str, address2: str) -> float:
        """Calculate boost for matching Turkish locations"""
        boost = 0.0
        
        addr1_lower = address1.lower()
        addr2_lower = address2.lower()
        
        # Check for major city matches
        for city in self.turkish_locations['major_cities']:
            if city in addr1_lower and city in addr2_lower:
                boost += 0.15
                break
        
        # Check for province matches
        for province in self.turkish_locations['provinces']:
            if province in addr1_lower and province in addr2_lower:
                boost += 0.1
                break
        
        return min(boost, 0.2)  # Cap boost at 0.2
    
    def get_geographic_similarity(self, address1: str, address2: str) -> float:
        """
        Calculate geographic similarity based on coordinates
        
        Args:
            address1 (str): First address (may contain coordinates)
            address2 (str): Second address (may contain coordinates)
            
        Returns:
            float: Geographic similarity score (0.0-1.0)
        """
        # Extract or estimate coordinates
        coords1 = self._extract_or_estimate_coordinates(address1)
        coords2 = self._extract_or_estimate_coordinates(address2)
        
        if not coords1 or not coords2:
            # Fallback to city-level geographic similarity
            return self._city_level_geographic_similarity(address1, address2)
        
        # Calculate Haversine distance
        distance_km = self._haversine_distance(
            coords1['lat'], coords1['lon'],
            coords2['lat'], coords2['lon']
        )
        
        # Convert distance to similarity score
        if distance_km == 0:
            return 1.0
        elif distance_km >= self.geographic_config['max_distance_km']:
            return 0.0
        else:
            # Exponential decay function
            return math.exp(-distance_km / 10.0)  # 10km half-life
    
    def _extract_or_estimate_coordinates(self, address: str) -> Optional[Dict[str, float]]:
        """Extract coordinates from address or estimate based on location"""
        # Try to extract explicit coordinates
        coord_pattern = r'(\d+\.?\d*),\s*(\d+\.?\d*)'
        coord_match = re.search(coord_pattern, address)
        
        if coord_match:
            lat, lon = float(coord_match.group(1)), float(coord_match.group(2))
            
            # Validate Turkey bounds
            bounds = self.geographic_config['turkey_bounds']
            if (bounds['lat_min'] <= lat <= bounds['lat_max'] and 
                bounds['lon_min'] <= lon <= bounds['lon_max']):
                return {'lat': lat, 'lon': lon}
        
        # Estimate coordinates based on known locations
        return self._estimate_coordinates_from_location(address)
    
    def _estimate_coordinates_from_location(self, address: str) -> Optional[Dict[str, float]]:
        """Estimate coordinates based on Turkish location names"""
        address_lower = address.lower()
        
        # Major city coordinates (approximate centers)
        city_coordinates = {
            'istanbul': {'lat': 41.0082, 'lon': 28.9784},
            'ankara': {'lat': 39.9334, 'lon': 32.8597},
            'izmir': {'lat': 38.4192, 'lon': 27.1287},
            'bursa': {'lat': 40.1826, 'lon': 29.0665},
            'antalya': {'lat': 36.8841, 'lon': 30.7056},
            'adana': {'lat': 37.0000, 'lon': 35.3213},
            'konya': {'lat': 37.8713, 'lon': 32.4846},
            'kadıköy': {'lat': 40.9875, 'lon': 29.0376},
            'beyoğlu': {'lat': 41.0370, 'lon': 28.9756},
            'çankaya': {'lat': 39.9075, 'lon': 32.8681}
        }
        
        for location, coords in city_coordinates.items():
            if location in address_lower:
                return coords
        
        return None
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate Haversine distance between two coordinates"""
        R = 6371  # Earth's radius in kilometers
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = (math.sin(dlat/2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2)
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def _city_level_geographic_similarity(self, address1: str, address2: str) -> float:
        """Calculate city-level geographic similarity without coordinates"""
        # Extract city names
        cities1 = self._extract_city_names(address1)
        cities2 = self._extract_city_names(address2)
        
        if not cities1 or not cities2:
            return 0.5  # Neutral score when cities unknown
        
        # Check for exact city matches
        common_cities = cities1.intersection(cities2)
        if common_cities:
            return 0.8  # High similarity for same city
        
        # Check for neighboring cities (simplified)
        if self._are_neighboring_cities(cities1, cities2):
            return 0.6
        
        return 0.2  # Low similarity for different cities
    
    def _extract_city_names(self, address: str) -> set:
        """Extract Turkish city names from address"""
        address_lower = address.lower()
        found_cities = set()
        
        # Check against known Turkish cities
        all_locations = (self.turkish_locations['major_cities'] | 
                        self.turkish_locations['provinces'])
        
        for city in all_locations:
            if city in address_lower:
                found_cities.add(city)
        
        return found_cities
    
    def _are_neighboring_cities(self, cities1: set, cities2: set) -> bool:
        """Check if cities are neighbors (simplified logic)"""
        # Simplified neighboring logic - can be enhanced with actual geographic data
        neighboring_pairs = {
            ('istanbul', 'bursa'), ('ankara', 'konya'), 
            ('izmir', 'manisa'), ('antalya', 'mersin')
        }
        
        for city1 in cities1:
            for city2 in cities2:
                if (city1, city2) in neighboring_pairs or (city2, city1) in neighboring_pairs:
                    return True
        
        return False
    
    def get_text_similarity(self, address1: str, address2: str) -> float:
        """
        Calculate textual similarity using fuzzy string matching
        
        Args:
            address1 (str): First address
            address2 (str): Second address
            
        Returns:
            float: Text similarity score (0.0-1.0)  
        """
        try:
            from thefuzz import fuzz
            
            # Normalize addresses for comparison
            norm_addr1 = self._normalize_text(address1)
            norm_addr2 = self._normalize_text(address2)
            
            # Use token set ratio for best Turkish text comparison
            similarity_score = fuzz.token_set_ratio(norm_addr1, norm_addr2) / 100.0
            
            # Apply Turkish-specific adjustments
            turkish_boost = self._calculate_turkish_text_boost(address1, address2)
            
            return min(similarity_score + turkish_boost, 1.0)
            
        except ImportError:
            # Fallback to simple string similarity
            return self._fallback_text_similarity(address1, address2)
    
    def _fallback_text_similarity(self, address1: str, address2: str) -> float:
        """Fallback text similarity when thefuzz unavailable"""
        norm_addr1 = self._normalize_text(address1)
        norm_addr2 = self._normalize_text(address2)
        
        if not norm_addr1 or not norm_addr2:
            return 0.0
        
        # Simple longest common subsequence ratio
        lcs_length = self._longest_common_subsequence(norm_addr1, norm_addr2)
        max_length = max(len(norm_addr1), len(norm_addr2))
        
        return lcs_length / max_length if max_length > 0 else 0.0
    
    def _longest_common_subsequence(self, str1: str, str2: str) -> int:
        """Calculate longest common subsequence length"""
        m, n = len(str1), len(str2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if str1[i-1] == str2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        
        return dp[m][n]
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison while preserving Turkish characters"""
        if not text:
            return ""
        
        # Convert to lowercase
        normalized = text.lower()
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Remove punctuation except Turkish characters
        normalized = re.sub(r'[^\w\sçğıöşüÇĞIÖŞÜ]', ' ', normalized)
        
        return normalized.strip()
    
    def _calculate_turkish_text_boost(self, address1: str, address2: str) -> float:
        """Calculate boost for Turkish-specific text patterns"""
        boost = 0.0
        
        # Check for Turkish abbreviation consistency
        abbrev_patterns = [
            (r'mah\.?', r'mahallesi?'),
            (r'sk\.?', r'sokak'),
            (r'cd\.?', r'caddesi?'),
            (r'no\.?', r'numara')
        ]
        
        for abbrev, full_form in abbrev_patterns:
            if (re.search(abbrev, address1.lower()) and re.search(full_form, address2.lower())) or \
               (re.search(full_form, address1.lower()) and re.search(abbrev, address2.lower())):
                boost += 0.02
        
        return min(boost, 0.1)  # Cap boost
    
    def get_hierarchy_similarity(self, address1: str, address2: str) -> float:
        """
        Calculate hierarchical similarity based on address components
        
        Args:
            address1 (str): First address 
            address2 (str): Second address
            
        Returns:
            float: Hierarchical similarity score (0.0-1.0)
        """
        # Parse address components using AddressParser if available
        components1 = self._extract_address_components(address1)
        components2 = self._extract_address_components(address2)
        
        return self._calculate_component_similarity(components1, components2)
    
    def _extract_address_components(self, address: str) -> Dict[str, str]:
        """Extract address components using integrated AddressParser"""
        if self.algorithms_available['parser'] and self.address_parser:
            try:
                result = self.address_parser.parse_address(address)
                return result.get('components', {})
            except Exception:
                pass
        
        # Fallback component extraction
        return self._fallback_component_extraction(address)
    
    def _fallback_component_extraction(self, address: str) -> Dict[str, str]:
        """Fallback component extraction using simple patterns"""
        components = {}
        address_lower = address.lower()
        
        # Extract province (il)
        for province in self.turkish_locations['provinces']:
            if province in address_lower:
                components['il'] = province.title()
                break
        
        # Extract major cities as potential provinces
        for city in self.turkish_locations['major_cities']:
            if city in address_lower:
                components['il'] = city.title()
                break
        
        # Extract mahalle
        mahalle_match = re.search(r'(\w+(?:\s+\w+)*)\s+mah(?:allesi?)?', address_lower)
        if mahalle_match:
            components['mahalle'] = mahalle_match.group(1).title()
        
        # Extract sokak
        sokak_match = re.search(r'(\w+(?:\s+\w+)*)\s+(?:sk|sokak)', address_lower)
        if sokak_match:
            components['sokak'] = sokak_match.group(1).title()
        
        # Extract building number
        bina_match = re.search(r'no\s*:?\s*(\d+[a-z]?)', address_lower)
        if bina_match:
            components['bina_no'] = bina_match.group(1)
        
        return components
    
    def _calculate_component_similarity(self, components1: Dict[str, str], components2: Dict[str, str]) -> float:
        """Calculate weighted similarity between address components"""
        if not components1 or not components2:
            return 0.0
        
        total_similarity = 0.0
        total_weight = 0.0
        
        # Compare each component with appropriate weight
        for component, weight in self.hierarchy_weights.items():
            if component in components1 and component in components2:
                comp_similarity = self._component_string_similarity(
                    components1[component], components2[component]
                )
                total_similarity += comp_similarity * weight
                total_weight += weight
            elif component in components1 or component in components2:
                # Partial penalty for missing component
                total_similarity += 0.0 * weight
                total_weight += weight
        
        return total_similarity / total_weight if total_weight > 0 else 0.0
    
    def _component_string_similarity(self, comp1: str, comp2: str) -> float:
        """Calculate similarity between individual components"""
        if not comp1 or not comp2:
            return 0.0
        
        comp1_norm = self._normalize_text(comp1)
        comp2_norm = self._normalize_text(comp2)
        
        if comp1_norm == comp2_norm:
            return 1.0
        
        # Use simple character-based similarity
        longer = max(len(comp1_norm), len(comp2_norm))
        shorter = min(len(comp1_norm), len(comp2_norm))
        
        if longer == 0:
            return 1.0
        
        # Calculate edit distance approximation
        common_chars = len(set(comp1_norm).intersection(set(comp2_norm)))
        unique_chars = len(set(comp1_norm).union(set(comp2_norm)))
        
        return common_chars / unique_chars if unique_chars > 0 else 0.0
    
    def _validate_inputs(self, address1: str, address2: str) -> bool:
        """Validate input addresses"""
        return (isinstance(address1, str) and isinstance(address2, str) and 
                len(address1.strip()) > 0 and len(address2.strip()) > 0)
    
    def _create_error_result(self, error_message: str) -> dict:
        """Create standardized error result"""
        return {
            "overall_similarity": 0.0,
            "similarity_breakdown": {
                "semantic": 0.0,
                "geographic": 0.0,
                "textual": 0.0,
                "hierarchical": 0.0
            },
            "confidence": 0.0,
            "match_decision": False,
            "similarity_details": {
                "method_contributions": {
                    "semantic": 0.0,
                    "geographic": 0.0,
                    "textual": 0.0,
                    "hierarchical": 0.0
                },
                "processing_time_ms": 0.0,
                "algorithms_used": [],
                "error": error_message
            }
        }


def main():
    """Demo usage of HybridAddressMatcher"""
    print("🚀 TEKNOFEST HybridAddressMatcher Demo")
    print("=" * 50)
    
    matcher = HybridAddressMatcher()
    
    # Test cases
    test_cases = [
        {
            'name': 'Identical addresses',
            'addr1': 'İstanbul Kadıköy Moda Mahallesi Caferağa Sokak No 10',
            'addr2': 'İstanbul Kadıköy Moda Mahallesi Caferağa Sokak No 10'
        },
        {
            'name': 'Address variations',
            'addr1': 'İstanbul Kadıköy Moda Mahallesi Caferağa Sk. 10',
            'addr2': 'Istanbul Kadikoy Moda Mah. Caferaga Sokak No:10'
        },
        {
            'name': 'Different neighborhoods',
            'addr1': 'İstanbul Kadıköy Moda Mahallesi',
            'addr2': 'İstanbul Kadıköy Fenerbahçe Mahallesi'
        },
        {
            'name': 'Different cities',
            'addr1': 'İstanbul Kadıköy Moda Mahallesi',
            'addr2': 'Ankara Çankaya Kızılay Mahallesi'
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📍 {test_case['name']}:")
        print(f"   Address 1: {test_case['addr1']}")
        print(f"   Address 2: {test_case['addr2']}")
        
        result = matcher.calculate_hybrid_similarity(
            test_case['addr1'], test_case['addr2']
        )
        
        print(f"   Overall Similarity: {result['overall_similarity']:.3f}")
        print(f"   Match Decision: {result['match_decision']}")
        print(f"   Breakdown: S:{result['similarity_breakdown']['semantic']:.2f} "
              f"G:{result['similarity_breakdown']['geographic']:.2f} "
              f"T:{result['similarity_breakdown']['textual']:.2f} "
              f"H:{result['similarity_breakdown']['hierarchical']:.2f}")
        print(f"   Processing Time: {result['similarity_details']['processing_time_ms']:.2f}ms")


if __name__ == "__main__":
    main()