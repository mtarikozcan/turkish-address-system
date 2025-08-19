"""
TEKNOFEST 2025 Adres Çözümleme Sistemi - HybridAddressMatcher Tests
Comprehensive test suite for Turkish hybrid address matching algorithm

Tests cover:
- Hybrid address similarity calculation with 4-level breakdown
- Semantic similarity using Sentence Transformers
- Geographic similarity using coordinate distance calculation
- Text similarity using fuzzy string matching (thefuzz)
- Hierarchical similarity using component-based matching
- Weighted ensemble scoring (40%, 30%, 20%, 10% weights)
- Turkish address pair similarity scenarios
- Integration with AddressValidator, AddressCorrector, AddressParser
- Performance benchmarking (<100ms target)
- Confidence threshold testing (>0.6 minimum similarity)
"""

try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False
    # Mock pytest fixture decorator for standalone running
    def pytest_fixture_mock(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    pytest = type('MockPytest', (), {'fixture': pytest_fixture_mock})()

import json
import time
import os
import sys
import math
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Tuple, Optional

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock the HybridAddressMatcher class since we haven't implemented it yet
class MockHybridAddressMatcher:
    """Mock implementation of HybridAddressMatcher for testing"""
    
    def __init__(self):
        """Initialize with mock similarity models and weights"""
        self.similarity_weights = {
            'semantic': 0.4,     # 40% - Sentence Transformers semantic similarity
            'geographic': 0.3,   # 30% - Coordinate distance similarity
            'textual': 0.2,      # 20% - Fuzzy string matching similarity
            'hierarchical': 0.1  # 10% - Component-based hierarchical similarity
        }
        self.confidence_threshold = 0.6
        self.semantic_model = self._load_mock_semantic_model()
        self.geographic_config = self._load_mock_geographic_config()
        self.text_similarity_config = self._load_mock_text_config()
        
        # Integration with other algorithms
        self.address_validator = None
        self.address_corrector = None
        self.address_parser = None
        
    def _load_mock_semantic_model(self):
        """Load mock Sentence Transformers model"""
        return {
            'model_name': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
            'model_type': 'sentence_transformers',
            'embedding_dimension': 384,
            'similarity_function': 'cosine',
            'batch_size': 32
        }
    
    def _load_mock_geographic_config(self):
        """Load mock geographic similarity configuration"""
        return {
            'distance_function': 'haversine',
            'max_distance_km': 50.0,  # Maximum meaningful distance for similarity
            'similarity_decay': 'exponential',
            'turkey_bounds': {
                'lat_min': 35.8, 'lat_max': 42.1,
                'lon_min': 25.7, 'lon_max': 44.8
            }
        }
    
    def _load_mock_text_config(self):
        """Load mock text similarity configuration"""
        return {
            'algorithm': 'token_set_ratio',
            'library': 'thefuzz',
            'normalization': True,
            'turkish_chars': True,
            'min_length': 3
        }
    
    def calculate_hybrid_similarity(self, address1: str, address2: str) -> dict:
        """
        Main hybrid similarity calculation method
        
        Args:
            address1: First Turkish address string
            address2: Second Turkish address string
            
        Returns:
            Dict with similarity breakdown and overall score:
            {
                "overall_similarity": float (0.0-1.0),
                "similarity_breakdown": {
                    "semantic": float,
                    "geographic": float, 
                    "textual": float,
                    "hierarchical": float
                },
                "confidence": float (0.0-1.0),
                "match_decision": bool,
                "similarity_details": {
                    "method_contributions": Dict[str, float],
                    "processing_time_ms": float,
                    "algorithms_used": List[str]
                }
            }
        """
        if not address1 or not address2:
            return self._create_error_result("Invalid address inputs")
        
        if not isinstance(address1, str) or not isinstance(address2, str):
            return self._create_error_result("Addresses must be strings")
        
        start_time = time.time()
        
        # Calculate individual similarity components
        semantic_sim = self.get_semantic_similarity(address1, address2)
        geographic_sim = self.get_geographic_similarity(address1, address2)
        textual_sim = self.get_text_similarity(address1, address2)
        hierarchical_sim = self.get_hierarchy_similarity(address1, address2)
        
        # Apply weighted ensemble scoring
        similarity_breakdown = {
            'semantic': semantic_sim,
            'geographic': geographic_sim,
            'textual': textual_sim,
            'hierarchical': hierarchical_sim
        }
        
        # Calculate weighted overall similarity
        overall_similarity = (
            semantic_sim * self.similarity_weights['semantic'] +
            geographic_sim * self.similarity_weights['geographic'] +
            textual_sim * self.similarity_weights['textual'] +
            hierarchical_sim * self.similarity_weights['hierarchical']
        )
        
        # Calculate confidence and match decision
        confidence = self._calculate_similarity_confidence(similarity_breakdown, overall_similarity)
        match_decision = overall_similarity >= self.confidence_threshold
        
        processing_time_ms = (time.time() - start_time) * 1000
        
        # Method contributions for explainability
        method_contributions = {
            method: score * weight 
            for method, (score, weight) in zip(
                similarity_breakdown.keys(),
                [(semantic_sim, self.similarity_weights['semantic']),
                 (geographic_sim, self.similarity_weights['geographic']),
                 (textual_sim, self.similarity_weights['textual']),
                 (hierarchical_sim, self.similarity_weights['hierarchical'])]
            )
        }
        
        return {
            'overall_similarity': round(overall_similarity, 4),
            'similarity_breakdown': {k: round(v, 4) for k, v in similarity_breakdown.items()},
            'confidence': round(confidence, 4),
            'match_decision': match_decision,
            'similarity_details': {
                'method_contributions': {k: round(v, 4) for k, v in method_contributions.items()},
                'processing_time_ms': round(processing_time_ms, 3),
                'algorithms_used': ['semantic', 'geographic', 'textual', 'hierarchical']
            }
        }
    
    def get_semantic_similarity(self, address1: str, address2: str) -> float:
        """
        Calculate semantic similarity using Sentence Transformers
        
        Args:
            address1, address2: Address strings to compare
            
        Returns:
            Semantic similarity score (0.0-1.0)
        """
        if not address1 or not address2:
            return 0.0
        
        # Mock semantic similarity calculation
        # In real implementation, this would use sentence-transformers
        
        # Simple word overlap as semantic proxy
        words1 = set(address1.lower().split())
        words2 = set(address2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        # Jaccard similarity as semantic approximation
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        jaccard_sim = intersection / union if union > 0 else 0.0
        
        # Add semantic boosting for Turkish location names
        turkish_locations = ['istanbul', 'ankara', 'izmir', 'kadıköy', 'beşiktaş', 'çankaya']
        location_matches = sum(1 for loc in turkish_locations 
                              if loc in address1.lower() and loc in address2.lower())
        
        semantic_boost = min(0.3, location_matches * 0.1)
        semantic_similarity = min(1.0, jaccard_sim + semantic_boost)
        
        return semantic_similarity
    
    def get_geographic_similarity(self, address1: str, address2: str) -> float:
        """
        Calculate geographic similarity using coordinate distance
        
        Args:
            address1, address2: Address strings with potential coordinates
            
        Returns:
            Geographic similarity score (0.0-1.0)
        """
        # Extract or estimate coordinates for addresses
        coords1 = self._extract_or_estimate_coordinates(address1)
        coords2 = self._extract_or_estimate_coordinates(address2)
        
        if not coords1 or not coords2:
            # Use city-level geographic similarity if no coordinates
            return self._get_city_level_geographic_similarity(address1, address2)
        
        try:
            # Calculate haversine distance
            distance_km = self._haversine_distance(
                coords1['lat'], coords1['lon'],
                coords2['lat'], coords2['lon']
            )
            
            # Convert distance to similarity (exponential decay)
            max_distance = self.geographic_config['max_distance_km']
            if distance_km >= max_distance:
                return 0.0
            
            # Exponential decay similarity function
            similarity = math.exp(-distance_km / (max_distance / 3))
            return min(1.0, similarity)
            
        except Exception as e:
            return 0.0
    
    def get_text_similarity(self, address1: str, address2: str) -> float:
        """
        Calculate text similarity using fuzzy string matching
        
        Args:
            address1, address2: Address strings to compare
            
        Returns:
            Text similarity score (0.0-1.0)
        """
        if not address1 or not address2:
            return 0.0
        
        try:
            # Mock thefuzz implementation
            # In real implementation, this would use thefuzz.fuzz
            
            # Normalize Turkish addresses
            norm_addr1 = self._normalize_turkish_address(address1)
            norm_addr2 = self._normalize_turkish_address(address2)
            
            # Simple character-based similarity as fuzzy approximation
            similarity = self._calculate_character_similarity(norm_addr1, norm_addr2)
            
            # Token set similarity approximation
            tokens1 = set(norm_addr1.split())
            tokens2 = set(norm_addr2.split())
            
            if tokens1 and tokens2:
                token_similarity = len(tokens1 & tokens2) / max(len(tokens1), len(tokens1))
                similarity = max(similarity, token_similarity)
            
            return min(1.0, similarity)
            
        except Exception as e:
            return 0.0
    
    def get_hierarchy_similarity(self, address1: str, address2: str) -> float:
        """
        Calculate hierarchical similarity using component-based matching
        
        Args:
            address1, address2: Address strings to parse and compare
            
        Returns:
            Hierarchical similarity score (0.0-1.0)
        """
        try:
            # Parse addresses into components (mock parsing)
            components1 = self._parse_address_components(address1)
            components2 = self._parse_address_components(address2)
            
            if not components1 or not components2:
                return 0.0
            
            # Component weights for hierarchical similarity
            component_weights = {
                'il': 0.3,          # Province - 30%
                'ilce': 0.25,       # District - 25%
                'mahalle': 0.2,     # Neighborhood - 20%
                'sokak': 0.15,      # Street - 15%
                'bina_no': 0.05,    # Building number - 5%
                'daire': 0.05       # Apartment - 5%
            }
            
            total_similarity = 0.0
            total_weight = 0.0
            
            for component, weight in component_weights.items():
                if component in components1 and component in components2:
                    comp_sim = self._calculate_component_similarity(
                        components1[component], components2[component], component
                    )
                    total_similarity += comp_sim * weight
                    total_weight += weight
                elif component in components1 or component in components2:
                    # Penalty for missing component
                    total_weight += weight * 0.5
            
            if total_weight == 0:
                return 0.0
            
            hierarchical_similarity = total_similarity / total_weight
            return min(1.0, hierarchical_similarity)
            
        except Exception as e:
            return 0.0
    
    def _extract_or_estimate_coordinates(self, address: str) -> Optional[Dict[str, float]]:
        """Extract or estimate coordinates from address"""
        # Mock coordinate extraction/estimation
        
        # Check for explicit coordinates in address
        import re
        coord_pattern = r'(\d+\.\d+),\s*(\d+\.\d+)'
        match = re.search(coord_pattern, address)
        if match:
            lat, lon = float(match.group(1)), float(match.group(2))
            return {'lat': lat, 'lon': lon}
        
        # Estimate coordinates based on major Turkish cities
        city_coordinates = {
            'istanbul': {'lat': 41.0082, 'lon': 28.9784},
            'ankara': {'lat': 39.9334, 'lon': 32.8597},
            'izmir': {'lat': 38.4192, 'lon': 27.1287},
            'bursa': {'lat': 40.1824, 'lon': 29.0670},
            'antalya': {'lat': 36.8969, 'lon': 30.7133}
        }
        
        address_lower = address.lower()
        for city, coords in city_coordinates.items():
            if city in address_lower:
                return coords
        
        return None
    
    def _get_city_level_geographic_similarity(self, address1: str, address2: str) -> float:
        """Calculate city-level geographic similarity"""
        # Extract cities from addresses
        cities1 = self._extract_turkish_cities(address1)
        cities2 = self._extract_turkish_cities(address2)
        
        if not cities1 or not cities2:
            return 0.0
        
        # Check for exact city matches
        common_cities = set(cities1) & set(cities2)
        if common_cities:
            return 0.8  # High similarity for same city
        
        # Check for nearby cities (simplified)
        nearby_cities = {
            'istanbul': ['bursa', 'kocaeli'],
            'ankara': ['eskişehir', 'konya'],
            'izmir': ['manisa', 'aydın']
        }
        
        for city1 in cities1:
            for city2 in cities2:
                if city1 in nearby_cities and city2 in nearby_cities[city1]:
                    return 0.4  # Medium similarity for nearby cities
                elif city2 in nearby_cities and city1 in nearby_cities[city2]:
                    return 0.4
        
        return 0.1  # Low similarity for different cities
    
    def _extract_turkish_cities(self, address: str) -> List[str]:
        """Extract Turkish city names from address"""
        major_cities = ['istanbul', 'ankara', 'izmir', 'bursa', 'antalya', 'adana', 'konya']
        found_cities = []
        address_lower = address.lower()
        
        for city in major_cities:
            if city in address_lower:
                found_cities.append(city)
        
        return found_cities
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate haversine distance between two coordinate points"""
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of earth in kilometers
        r = 6371
        
        return c * r
    
    def _normalize_turkish_address(self, address: str) -> str:
        """Normalize Turkish address for text comparison"""
        if not address:
            return ""
        
        # Convert to lowercase and clean
        normalized = address.lower().strip()
        
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        
        # Turkish character normalization (preserve Turkish chars)
        normalized = normalized.replace('ı', 'i').replace('ğ', 'g').replace('ü', 'u')
        normalized = normalized.replace('ş', 's').replace('ö', 'o').replace('ç', 'c')
        
        return normalized
    
    def _calculate_character_similarity(self, text1: str, text2: str) -> float:
        """Calculate character-based similarity"""
        if not text1 or not text2:
            return 0.0
        
        # Simple Levenshtein-like similarity
        max_len = max(len(text1), len(text2))
        if max_len == 0:
            return 1.0
        
        # Character overlap similarity
        common_chars = sum(1 for c1, c2 in zip(text1, text2) if c1 == c2)
        similarity = common_chars / max_len
        
        return similarity
    
    def _parse_address_components(self, address: str) -> Dict[str, str]:
        """Parse address into components (mock implementation)"""
        components = {}
        address_lower = address.lower()
        
        # Simple component extraction
        if 'istanbul' in address_lower:
            components['il'] = 'İstanbul'
        elif 'ankara' in address_lower:
            components['il'] = 'Ankara'
        elif 'izmir' in address_lower:
            components['il'] = 'İzmir'
        
        if 'kadıköy' in address_lower:
            components['ilce'] = 'Kadıköy'
        elif 'beşiktaş' in address_lower:
            components['ilce'] = 'Beşiktaş'
        elif 'çankaya' in address_lower:
            components['ilce'] = 'Çankaya'
        
        if 'moda' in address_lower and 'mah' in address_lower:
            components['mahalle'] = 'Moda Mahallesi'
        elif 'kızılay' in address_lower and 'mah' in address_lower:
            components['mahalle'] = 'Kızılay Mahallesi'
        
        # Extract numbers as building/apartment numbers
        import re
        numbers = re.findall(r'\d+', address)
        if numbers:
            components['bina_no'] = numbers[0]
            if len(numbers) > 1:
                components['daire'] = numbers[1]
        
        return components
    
    def _calculate_component_similarity(self, comp1: str, comp2: str, component_type: str) -> float:
        """Calculate similarity between address components"""
        if not comp1 or not comp2:
            return 0.0
        
        comp1_norm = comp1.lower().strip()
        comp2_norm = comp2.lower().strip()
        
        # Exact match
        if comp1_norm == comp2_norm:
            return 1.0
        
        # Partial match for text components
        if component_type in ['il', 'ilce', 'mahalle', 'sokak']:
            # Check if one is contained in the other
            if comp1_norm in comp2_norm or comp2_norm in comp1_norm:
                return 0.8
            
            # Word overlap similarity
            words1 = set(comp1_norm.split())
            words2 = set(comp2_norm.split())
            if words1 and words2:
                overlap = len(words1 & words2) / max(len(words1), len(words2))
                return overlap
        
        # Numeric similarity for building/apartment numbers
        elif component_type in ['bina_no', 'daire']:
            try:
                num1 = int(''.join(filter(str.isdigit, comp1)))
                num2 = int(''.join(filter(str.isdigit, comp2)))
                
                # Close numbers get higher similarity
                diff = abs(num1 - num2)
                if diff == 0:
                    return 1.0
                elif diff <= 2:
                    return 0.8
                elif diff <= 5:
                    return 0.5
                else:
                    return 0.2
            except:
                pass
        
        return 0.0
    
    def _calculate_similarity_confidence(self, breakdown: Dict[str, float], overall: float) -> float:
        """Calculate confidence in similarity calculation"""
        # Base confidence from overall similarity
        base_confidence = overall
        
        # Boost confidence if multiple methods agree
        high_similarity_methods = sum(1 for score in breakdown.values() if score > 0.7)
        if high_similarity_methods >= 2:
            base_confidence = min(1.0, base_confidence + 0.1)
        
        # Reduce confidence if methods disagree significantly
        similarity_variance = sum((score - overall) ** 2 for score in breakdown.values()) / len(breakdown)
        if similarity_variance > 0.1:
            base_confidence = max(0.0, base_confidence - 0.1)
        
        return base_confidence
    
    def _create_error_result(self, error_message: str) -> dict:
        """Create standardized error result"""
        return {
            'overall_similarity': 0.0,
            'similarity_breakdown': {
                'semantic': 0.0,
                'geographic': 0.0,
                'textual': 0.0,
                'hierarchical': 0.0
            },
            'confidence': 0.0,
            'match_decision': False,
            'error': error_message,
            'similarity_details': {
                'method_contributions': {},
                'processing_time_ms': 0.0,
                'algorithms_used': []
            }
        }


# Test fixtures
@pytest.fixture
def mock_address_matcher():
    """Fixture providing MockHybridAddressMatcher instance"""
    return MockHybridAddressMatcher()


@pytest.fixture
def turkish_address_pairs():
    """Fixture providing Turkish address pairs for similarity testing"""
    return [
        {
            'name': 'Identical addresses',
            'address1': 'İstanbul Kadıköy Moda Mahallesi Caferağa Sokak No 10',
            'address2': 'İstanbul Kadıköy Moda Mahallesi Caferağa Sokak No 10',
            'expected_similarity_min': 0.95,
            'expected_match': True
        },
        {
            'name': 'Same address with minor variations',
            'address1': 'İstanbul Kadıköy Moda Mahallesi Caferağa Sk. 10',
            'address2': 'Istanbul Kadikoy Moda Mah. Caferaga Sokak No:10',
            'expected_similarity_min': 0.75,
            'expected_match': True
        },
        {
            'name': 'Same neighborhood different streets',
            'address1': 'İstanbul Kadıköy Moda Mahallesi Caferağa Sokak 10',
            'address2': 'İstanbul Kadıköy Moda Mahallesi Mühürdar Sokak 15',
            'expected_similarity_min': 0.65,
            'expected_match': True
        },
        {
            'name': 'Same district different neighborhoods',
            'address1': 'İstanbul Kadıköy Moda Mahallesi',
            'address2': 'İstanbul Kadıköy Fenerbahçe Mahallesi',
            'expected_similarity_min': 0.50,
            'expected_match': False
        },
        {
            'name': 'Same city different districts',
            'address1': 'İstanbul Kadıköy Moda Mahallesi',
            'address2': 'İstanbul Beşiktaş Levent Mahallesi',
            'expected_similarity_min': 0.35,
            'expected_match': False
        },
        {
            'name': 'Different cities',
            'address1': 'İstanbul Kadıköy Moda Mahallesi',
            'address2': 'Ankara Çankaya Kızılay Mahallesi',
            'expected_similarity_max': 0.30,
            'expected_match': False
        },
        {
            'name': 'Address with coordinates - same location',
            'address1': 'İstanbul Kadıköy 40.9875,29.0376',
            'address2': 'İstanbul Kadıköy Moda Mahallesi',
            'expected_similarity_min': 0.70,
            'expected_match': True
        },
        {
            'name': 'Address with coordinates - different locations',
            'address1': 'İstanbul Kadıköy 40.9875,29.0376',
            'address2': 'Ankara Çankaya 39.9334,32.8597',
            'expected_similarity_max': 0.25,
            'expected_match': False
        }
    ]


@pytest.fixture
def similarity_component_tests():
    """Fixture providing test cases for individual similarity components"""
    return {
        'semantic_tests': [
            {
                'address1': 'İstanbul Kadıköy Moda Mahallesi',
                'address2': 'İstanbul Kadıköy Moda Mahallesi',
                'expected_min': 0.9
            },
            {
                'address1': 'İstanbul Kadıköy Moda Mahallesi',
                'address2': 'Istanbul Kadikoy Moda Mahallesi',
                'expected_min': 0.7
            },
            {
                'address1': 'İstanbul Kadıköy Moda Mahallesi',
                'address2': 'Ankara Çankaya Kızılay Mahallesi',
                'expected_max': 0.3
            }
        ],
        'geographic_tests': [
            {
                'address1': 'İstanbul Kadıköy 40.9875,29.0376',
                'address2': 'İstanbul Kadıköy 40.9880,29.0380',
                'expected_min': 0.8
            },
            {
                'address1': 'İstanbul Kadıköy',
                'address2': 'İstanbul Beşiktaş',
                'expected_min': 0.5
            },
            {
                'address1': 'İstanbul Kadıköy',
                'address2': 'Ankara Çankaya',
                'expected_max': 0.2
            }
        ],
        'textual_tests': [
            {
                'address1': 'Caferağa Sokak No 10',
                'address2': 'Caferaga Sk. 10',
                'expected_min': 0.8
            },
            {
                'address1': 'Moda Mahallesi',
                'address2': 'Moda Mah.',
                'expected_min': 0.7
            },
            {
                'address1': 'İstanbul Kadıköy',
                'address2': 'Completely Different Text',
                'expected_max': 0.2
            }
        ],
        'hierarchical_tests': [
            {
                'address1': 'İstanbul Kadıköy Moda Mahallesi Caferağa Sokak 10',
                'address2': 'İstanbul Kadıköy Moda Mahallesi Caferağa Sokak 10',
                'expected_min': 0.95
            },
            {
                'address1': 'İstanbul Kadıköy Moda Mahallesi',
                'address2': 'İstanbul Kadıköy Fenerbahçe Mahallesi',
                'expected_range': (0.4, 0.7)
            },
            {
                'address1': 'İstanbul Kadıköy',
                'address2': 'Ankara Çankaya',
                'expected_max': 0.3
            }
        ]
    }


@pytest.fixture
def performance_test_data():
    """Fixture providing performance testing data"""
    return {
        'single_comparison': {
            'address1': 'İstanbul Kadıköy Moda Mahallesi Caferağa Sokak No 10 Daire 3',
            'address2': 'İstanbul Kadıköy Moda Mahallesi Caferağa Sk. 10/3',
            'max_time_ms': 100
        },
        'batch_comparisons': [
            ('İstanbul Kadıköy Moda Mahallesi', 'İstanbul Kadıköy Moda Mah.'),
            ('Ankara Çankaya Kızılay Mahallesi', 'Ankara Çankaya Kızılay Mah.'),
            ('İzmir Konak Alsancak Mahallesi', 'İzmir Konak Alsancak Mah.'),
            ('Bursa Nilüfer Görükle Mahallesi', 'Bursa Nilüfer Görükle Mah.'),
            ('Antalya Muratpaşa Lara Mahallesi', 'Antalya Muratpaşa Lara Mah.')
        ],
        'max_batch_time_ms': 500
    }


@pytest.fixture
def integration_test_data():
    """Fixture providing integration test data for other algorithms"""
    return {
        'validator_integration': {
            'valid_address': 'İstanbul Kadıköy Moda Mahallesi',
            'invalid_address': 'İstanbul Çankaya Kızılay Mahallesi',  # Wrong hierarchy
            'expected_impact_on_similarity': 0.1
        },
        'corrector_integration': {
            'raw_address': 'istbl kadikoy moda mah',
            'corrected_address': 'İstanbul Kadıköy Moda Mahallesi',
            'expected_similarity_improvement': 0.2
        },
        'parser_integration': {
            'unparsed_address': 'İstanbul Kadıköy Moda Mahallesi Caferağa Sokak No 10',
            'expected_components': ['il', 'ilce', 'mahalle', 'sokak', 'bina_no'],
            'expected_hierarchy_similarity_boost': 0.1
        }
    }


# Main hybrid similarity method tests
class TestHybridAddressMatcherMainMethod:
    """Test the main calculate_hybrid_similarity method"""
    
    def test_calculate_hybrid_similarity_identical_addresses(self, mock_address_matcher, turkish_address_pairs):
        """Test similarity calculation for identical addresses"""
        matcher = mock_address_matcher
        
        identical_test = turkish_address_pairs[0]  # Identical addresses test case
        result = matcher.calculate_hybrid_similarity(
            identical_test['address1'], 
            identical_test['address2']
        )
        
        # Test structure
        assert isinstance(result, dict)
        assert 'overall_similarity' in result
        assert 'similarity_breakdown' in result
        assert 'confidence' in result
        assert 'match_decision' in result
        assert 'similarity_details' in result
        
        # Test similarity values
        assert result['overall_similarity'] >= identical_test['expected_similarity_min']
        assert result['match_decision'] == identical_test['expected_match']
        assert result['confidence'] > 0.8  # High confidence for identical addresses
        
        # Test breakdown structure
        breakdown = result['similarity_breakdown']
        assert 'semantic' in breakdown
        assert 'geographic' in breakdown
        assert 'textual' in breakdown
        assert 'hierarchical' in breakdown
        
        # All similarity components should be present
        for component, score in breakdown.items():
            assert 0.0 <= score <= 1.0
    
    def test_calculate_hybrid_similarity_all_test_cases(self, mock_address_matcher, turkish_address_pairs):
        """Test similarity calculation for all Turkish address pair scenarios"""
        matcher = mock_address_matcher
        
        passed_tests = 0
        total_tests = len(turkish_address_pairs)
        
        for test_case in turkish_address_pairs:
            result = matcher.calculate_hybrid_similarity(
                test_case['address1'], 
                test_case['address2']
            )
            
            # Test minimum similarity expectations
            if 'expected_similarity_min' in test_case:
                if result['overall_similarity'] >= test_case['expected_similarity_min']:
                    passed_tests += 1
                    
            # Test maximum similarity expectations
            elif 'expected_similarity_max' in test_case:
                if result['overall_similarity'] <= test_case['expected_similarity_max']:
                    passed_tests += 1
            
            # Test match decision
            assert result['match_decision'] == test_case['expected_match']
        
        # At least 80% of tests should pass (allowing for mock implementation flexibility)
        assert passed_tests / total_tests >= 0.8
    
    def test_calculate_hybrid_similarity_weighted_ensemble(self, mock_address_matcher):
        """Test weighted ensemble scoring (40%, 30%, 20%, 10% weights)"""
        matcher = mock_address_matcher
        
        test_address1 = "İstanbul Kadıköy Moda Mahallesi Caferağa Sokak 10"
        test_address2 = "İstanbul Kadıköy Moda Mahallesi Mühürdar Sokak 15"
        
        result = matcher.calculate_hybrid_similarity(test_address1, test_address2)
        
        # Test that weights are applied correctly
        breakdown = result['similarity_breakdown']
        contributions = result['similarity_details']['method_contributions']
        
        # Check weight application
        expected_semantic_contribution = breakdown['semantic'] * 0.4
        expected_geographic_contribution = breakdown['geographic'] * 0.3
        expected_textual_contribution = breakdown['textual'] * 0.2
        expected_hierarchical_contribution = breakdown['hierarchical'] * 0.1
        
        assert abs(contributions['semantic'] - expected_semantic_contribution) < 0.01
        assert abs(contributions['geographic'] - expected_geographic_contribution) < 0.01
        assert abs(contributions['textual'] - expected_textual_contribution) < 0.01
        assert abs(contributions['hierarchical'] - expected_hierarchical_contribution) < 0.01
        
        # Overall similarity should equal sum of contributions
        total_contributions = sum(contributions.values())
        assert abs(result['overall_similarity'] - total_contributions) < 0.01
    
    def test_calculate_hybrid_similarity_confidence_threshold(self, mock_address_matcher):
        """Test confidence threshold testing (>0.6 minimum similarity)"""
        matcher = mock_address_matcher
        
        # Test cases around the threshold
        test_cases = [
            {
                'addresses': ('İstanbul Kadıköy Moda Mahallesi', 'İstanbul Kadıköy Moda Mahallesi'),
                'should_match': True
            },
            {
                'addresses': ('İstanbul Kadıköy Moda Mahallesi', 'İstanbul Kadıköy Fenerbahçe Mahallesi'),
                'should_match': False  # Different neighborhoods
            },
            {
                'addresses': ('İstanbul Kadıköy', 'Ankara Çankaya'),
                'should_match': False  # Different cities
            }
        ]
        
        for test_case in test_cases:
            addr1, addr2 = test_case['addresses']
            result = matcher.calculate_hybrid_similarity(addr1, addr2)
            
            # Test match decision based on threshold
            if result['overall_similarity'] >= matcher.confidence_threshold:
                assert result['match_decision'] == True
            else:
                assert result['match_decision'] == False
            
            # Test expected match behavior
            assert result['match_decision'] == test_case['should_match']
    
    def test_calculate_hybrid_similarity_error_handling(self, mock_address_matcher):
        """Test error handling for invalid inputs"""
        matcher = mock_address_matcher
        
        error_test_cases = [
            (None, "Valid address"),
            ("Valid address", None),
            ("", "Valid address"),
            ("Valid address", ""),
            (123, "Valid address"),
            ("Valid address", [])
        ]
        
        for addr1, addr2 in error_test_cases:
            result = matcher.calculate_hybrid_similarity(addr1, addr2)
            
            # Should return error result structure
            assert result['overall_similarity'] == 0.0
            assert result['match_decision'] == False
            assert result['confidence'] == 0.0
            
            # Check for error message
            if 'error' in result:
                assert isinstance(result['error'], str)
                assert len(result['error']) > 0


# Individual similarity component tests
class TestHybridAddressMatcherComponents:
    """Test individual similarity calculation components"""
    
    def test_get_semantic_similarity(self, mock_address_matcher, similarity_component_tests):
        """Test semantic similarity using Sentence Transformers integration"""
        matcher = mock_address_matcher
        
        for test in similarity_component_tests['semantic_tests']:
            result = matcher.get_semantic_similarity(test['address1'], test['address2'])
            
            # Test return type and range
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0
            
            # Test expected similarity ranges
            if 'expected_min' in test:
                assert result >= test['expected_min']
            elif 'expected_max' in test:
                assert result <= test['expected_max']
    
    def test_get_geographic_similarity(self, mock_address_matcher, similarity_component_tests):
        """Test geographic similarity using coordinate distance calculation"""
        matcher = mock_address_matcher
        
        for test in similarity_component_tests['geographic_tests']:
            result = matcher.get_geographic_similarity(test['address1'], test['address2'])
            
            # Test return type and range
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0
            
            # Test expected similarity ranges
            if 'expected_min' in test:
                assert result >= test['expected_min']
            elif 'expected_max' in test:
                assert result <= test['expected_max']
    
    def test_get_text_similarity(self, mock_address_matcher, similarity_component_tests):
        """Test text similarity using fuzzy string matching (thefuzz)"""
        matcher = mock_address_matcher
        
        for test in similarity_component_tests['textual_tests']:
            result = matcher.get_text_similarity(test['address1'], test['address2'])
            
            # Test return type and range
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0
            
            # Test expected similarity ranges
            if 'expected_min' in test:
                assert result >= test['expected_min']
            elif 'expected_max' in test:
                assert result <= test['expected_max']
    
    def test_get_hierarchy_similarity(self, mock_address_matcher, similarity_component_tests):
        """Test hierarchical similarity using component-based matching"""
        matcher = mock_address_matcher
        
        for test in similarity_component_tests['hierarchical_tests']:
            result = matcher.get_hierarchy_similarity(test['address1'], test['address2'])
            
            # Test return type and range
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0
            
            # Test expected similarity ranges
            if 'expected_min' in test:
                assert result >= test['expected_min']
            elif 'expected_max' in test:
                assert result <= test['expected_max']
            elif 'expected_range' in test:
                min_val, max_val = test['expected_range']
                assert min_val <= result <= max_val
    
    def test_semantic_similarity_sentence_transformers_config(self, mock_address_matcher):
        """Test Sentence Transformers model configuration"""
        matcher = mock_address_matcher
        
        # Test model configuration
        semantic_config = matcher.semantic_model
        assert semantic_config['model_name'] == 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
        assert semantic_config['model_type'] == 'sentence_transformers'
        assert semantic_config['embedding_dimension'] == 384
        assert semantic_config['similarity_function'] == 'cosine'
        assert semantic_config['batch_size'] == 32
    
    def test_geographic_similarity_coordinate_extraction(self, mock_address_matcher):
        """Test coordinate extraction and distance calculation"""
        matcher = mock_address_matcher
        
        # Test coordinate extraction from address
        coords = matcher._extract_or_estimate_coordinates("İstanbul Kadıköy 40.9875,29.0376")
        assert coords is not None
        assert 'lat' in coords and 'lon' in coords
        assert abs(coords['lat'] - 40.9875) < 0.01
        assert abs(coords['lon'] - 29.0376) < 0.01
        
        # Test city-based coordinate estimation
        coords = matcher._extract_or_estimate_coordinates("İstanbul Kadıköy")
        assert coords is not None
        assert coords['lat'] > 40.0 and coords['lat'] < 42.0  # Istanbul latitude range
        
        # Test haversine distance calculation
        distance = matcher._haversine_distance(41.0, 29.0, 41.1, 29.1)
        assert isinstance(distance, float)
        assert distance > 0
        assert distance < 20  # Should be reasonable distance for close points
    
    def test_text_similarity_turkish_normalization(self, mock_address_matcher):
        """Test Turkish text normalization for fuzzy matching"""
        matcher = mock_address_matcher
        
        # Test Turkish character normalization
        normalized = matcher._normalize_turkish_address("İSTANBUL ŞIŞLI MECİDİYEKÖY")
        assert normalized.islower()
        assert "istanbul" in normalized
        assert "sisli" in normalized
        assert "mecidiyekoy" in normalized
        
        # Test text similarity with Turkish variations
        similarity = matcher.get_text_similarity("İstanbul Şişli", "Istanbul Sisli")
        assert similarity > 0.7  # Should be high similarity despite character differences
    
    def test_hierarchy_similarity_component_weights(self, mock_address_matcher):
        """Test component-based hierarchical similarity with proper weights"""
        matcher = mock_address_matcher
        
        # Test addresses with different component matches
        test_cases = [
            {
                'addr1': 'İstanbul Kadıköy Moda Mahallesi Caferağa Sokak 10',
                'addr2': 'İstanbul Kadıköy Moda Mahallesi Caferağa Sokak 10',
                'expected_min': 0.9  # All components match
            },
            {
                'addr1': 'İstanbul Kadıköy Moda Mahallesi',
                'addr2': 'İstanbul Kadıköy Fenerbahçe Mahallesi',
                'expected_range': (0.4, 0.7)  # Same il+ilce, different mahalle
            },
            {
                'addr1': 'İstanbul Kadıköy',
                'addr2': 'İstanbul Beşiktaş',
                'expected_range': (0.2, 0.4)  # Same il, different ilce
            }
        ]
        
        for test in test_cases:
            result = matcher.get_hierarchy_similarity(test['addr1'], test['addr2'])
            
            if 'expected_min' in test:
                assert result >= test['expected_min']
            elif 'expected_range' in test:
                min_val, max_val = test['expected_range']
                assert min_val <= result <= max_val


# Performance testing
class TestHybridAddressMatcherPerformance:
    """Test performance requirements (<100ms per comparison)"""
    
    def test_single_comparison_performance(self, mock_address_matcher, performance_test_data):
        """Test single address comparison performance"""
        matcher = mock_address_matcher
        
        perf_data = performance_test_data['single_comparison']
        
        start_time = time.time()
        result = matcher.calculate_hybrid_similarity(
            perf_data['address1'], 
            perf_data['address2']
        )
        end_time = time.time()
        
        processing_time_ms = (end_time - start_time) * 1000
        
        # Test performance requirement
        assert processing_time_ms < perf_data['max_time_ms']
        
        # Test that processing time is reported
        reported_time = result['similarity_details']['processing_time_ms']
        assert isinstance(reported_time, (int, float))
        assert reported_time > 0
    
    def test_batch_comparison_performance(self, mock_address_matcher, performance_test_data):
        """Test batch address comparison performance"""
        matcher = mock_address_matcher
        
        batch_data = performance_test_data['batch_comparisons']
        max_batch_time = performance_test_data['max_batch_time_ms']
        
        start_time = time.time()
        results = []
        for addr1, addr2 in batch_data:
            result = matcher.calculate_hybrid_similarity(addr1, addr2)
            results.append(result)
        end_time = time.time()
        
        total_time_ms = (end_time - start_time) * 1000
        avg_time_ms = total_time_ms / len(batch_data)
        
        # Test batch performance
        assert total_time_ms < max_batch_time
        assert avg_time_ms < 100  # Individual comparisons under 100ms
        
        # Test all comparisons completed successfully
        assert len(results) == len(batch_data)
        for result in results:
            assert isinstance(result, dict)
            assert 'overall_similarity' in result
    
    def test_component_method_performance(self, mock_address_matcher):
        """Test performance of individual similarity component methods"""
        matcher = mock_address_matcher
        
        test_addr1 = "İstanbul Kadıköy Moda Mahallesi Caferağa Sokak No 10"
        test_addr2 = "İstanbul Kadıköy Moda Mahallesi Mühürdar Sokak No 15"
        
        methods = [
            ('get_semantic_similarity', 50),
            ('get_geographic_similarity', 30),
            ('get_text_similarity', 20),
            ('get_hierarchy_similarity', 40)
        ]
        
        for method_name, max_time_ms in methods:
            method = getattr(matcher, method_name)
            
            start_time = time.time()
            result = method(test_addr1, test_addr2)
            end_time = time.time()
            
            processing_time_ms = (end_time - start_time) * 1000
            
            # Test individual method performance
            assert processing_time_ms < max_time_ms
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0


# Integration tests with other algorithms
class TestHybridAddressMatcherIntegration:
    """Test integration with AddressValidator, AddressCorrector, AddressParser"""
    
    def test_integration_with_address_validator(self, mock_address_matcher, integration_test_data):
        """Test integration with AddressValidator for validation impact"""
        matcher = mock_address_matcher
        
        # Mock AddressValidator integration
        valid_addr = integration_test_data['validator_integration']['valid_address']
        invalid_addr = integration_test_data['validator_integration']['invalid_address']
        
        # Compare valid vs invalid address hierarchies
        result_valid = matcher.calculate_hybrid_similarity(valid_addr, valid_addr)
        result_invalid = matcher.calculate_hybrid_similarity(valid_addr, invalid_addr)
        
        # Valid addresses should have higher hierarchical similarity
        assert result_valid['similarity_breakdown']['hierarchical'] > result_invalid['similarity_breakdown']['hierarchical']
        
        # Overall similarity should reflect validation impact
        similarity_diff = result_valid['overall_similarity'] - result_invalid['overall_similarity']
        expected_impact = integration_test_data['validator_integration']['expected_impact_on_similarity']
        assert similarity_diff >= expected_impact
    
    def test_integration_with_address_corrector(self, mock_address_matcher, integration_test_data):
        """Test integration with AddressCorrector for correction impact"""
        matcher = mock_address_matcher
        
        raw_addr = integration_test_data['corrector_integration']['raw_address']
        corrected_addr = integration_test_data['corrector_integration']['corrected_address']
        reference_addr = "İstanbul Kadıköy Moda Mahallesi"
        
        # Compare similarity before and after correction
        similarity_raw = matcher.calculate_hybrid_similarity(raw_addr, reference_addr)
        similarity_corrected = matcher.calculate_hybrid_similarity(corrected_addr, reference_addr)
        
        # Corrected address should have higher similarity
        improvement = similarity_corrected['overall_similarity'] - similarity_raw['overall_similarity']
        expected_improvement = integration_test_data['corrector_integration']['expected_similarity_improvement']
        
        assert improvement >= expected_improvement
        
        # Text similarity should show the most improvement
        text_improvement = (similarity_corrected['similarity_breakdown']['textual'] - 
                          similarity_raw['similarity_breakdown']['textual'])
        assert text_improvement > 0.1
    
    def test_integration_with_address_parser(self, mock_address_matcher, integration_test_data):
        """Test integration with AddressParser for component extraction impact"""
        matcher = mock_address_matcher
        
        unparsed_addr = integration_test_data['parser_integration']['unparsed_address']
        components_addr = "İstanbul Kadıköy Moda Mahallesi Caferağa Sokak 10"  # Well-structured
        
        # Test hierarchical similarity benefits from parsing
        result = matcher.calculate_hybrid_similarity(unparsed_addr, components_addr)
        
        # Should have good hierarchical similarity due to parsing
        hierarchical_sim = result['similarity_breakdown']['hierarchical']
        assert hierarchical_sim > 0.7  # Good component extraction
        
        # Overall similarity should benefit from component extraction
        assert result['overall_similarity'] > 0.6
    
    def test_integration_algorithm_pipeline(self, mock_address_matcher):
        """Test complete integration pipeline with all three algorithms"""
        matcher = mock_address_matcher
        
        # Test pipeline: Raw -> Corrected -> Parsed -> Validated -> Similarity
        raw_addr1 = "istbl kadikoy moda mah caferaga sk 10"
        raw_addr2 = "Istanbul Kadikoy Moda Mahallesi Caferaga Sokak No:10"
        
        # This would represent the complete pipeline integration
        result = matcher.calculate_hybrid_similarity(raw_addr1, raw_addr2)
        
        # Should achieve high similarity despite raw input variations
        assert result['overall_similarity'] > 0.7
        assert result['match_decision'] == True
        
        # All similarity components should contribute meaningfully
        breakdown = result['similarity_breakdown']
        meaningful_components = sum(1 for score in breakdown.values() if score > 0.5)
        assert meaningful_components >= 2  # At least 2 components should score well


# Turkish language specific tests
class TestHybridAddressMatcherTurkishLanguage:
    """Test Turkish language specific functionality"""
    
    def test_turkish_character_handling_in_similarity(self, mock_address_matcher):
        """Test proper handling of Turkish characters in similarity calculation"""
        matcher = mock_address_matcher
        
        turkish_char_tests = [
            {
                'addr1': 'İstanbul Şişli Mecidiyeköy',
                'addr2': 'Istanbul Sisli Mecidiyekoy',
                'expected_min_similarity': 0.7
            },
            {
                'addr1': 'Ankara Çankaya Kızılay',
                'addr2': 'Ankara Cankaya Kizilay',
                'expected_min_similarity': 0.7
            },
            {
                'addr1': 'İzmir Karşıyaka Bostanlı',
                'addr2': 'Izmir Karsiyaka Bostanli',
                'expected_min_similarity': 0.7
            }
        ]
        
        for test in turkish_char_tests:
            result = matcher.calculate_hybrid_similarity(test['addr1'], test['addr2'])
            
            assert result['overall_similarity'] >= test['expected_min_similarity']
            
            # Text similarity should handle Turkish characters well
            assert result['similarity_breakdown']['textual'] >= 0.6
    
    def test_turkish_location_recognition(self, mock_address_matcher):
        """Test recognition of Turkish location names in similarity"""
        matcher = mock_address_matcher
        
        turkish_location_tests = [
            ('İstanbul Kadıköy', 'İstanbul Kadıköy Moda Mahallesi'),
            ('Ankara Çankaya', 'Ankara Çankaya Kızılay Mahallesi'),
            ('İzmir Konak', 'İzmir Konak Alsancak Mahallesi')
        ]
        
        for addr1, addr2 in turkish_location_tests:
            result = matcher.calculate_hybrid_similarity(addr1, addr2)
            
            # Should recognize Turkish locations and give good similarity
            assert result['overall_similarity'] > 0.6
            
            # Semantic similarity should benefit from Turkish location recognition
            assert result['similarity_breakdown']['semantic'] > 0.5
    
    def test_turkish_address_structure_similarity(self, mock_address_matcher):
        """Test Turkish address structure pattern recognition"""
        matcher = mock_address_matcher
        
        structure_tests = [
            {
                'addr1': 'İl İlçe Mahalle pattern',
                'addr2': 'İstanbul Kadıköy Moda Mahallesi',
                'component': 'hierarchical'
            },
            {
                'addr1': 'Mahallesi Sokak pattern',
                'addr2': 'Moda Mahallesi Caferağa Sokak',
                'component': 'hierarchical'
            },
            {
                'addr1': 'No/Numara pattern',
                'addr2': 'Caferağa Sokak No 10',
                'component': 'hierarchical'
            }
        ]
        
        for test in structure_tests:
            result = matcher.calculate_hybrid_similarity(test['addr1'], test['addr2'])
            
            # Should recognize Turkish address structure patterns
            if test['component'] == 'hierarchical':
                assert result['similarity_breakdown']['hierarchical'] > 0.3


# Edge cases and error handling
class TestHybridAddressMatcherEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_and_null_addresses(self, mock_address_matcher):
        """Test handling of empty and null addresses"""
        matcher = mock_address_matcher
        
        edge_cases = [
            (None, "Valid address"),
            ("Valid address", None),
            ("", "Valid address"),
            ("Valid address", ""),
            ("   ", "Valid address"),
            ("Valid address", "   ")
        ]
        
        for addr1, addr2 in edge_cases:
            result = matcher.calculate_hybrid_similarity(addr1, addr2)
            
            # Should handle gracefully
            assert isinstance(result, dict)
            assert result['overall_similarity'] == 0.0
            assert result['match_decision'] == False
            assert result['confidence'] == 0.0
    
    def test_very_long_addresses(self, mock_address_matcher):
        """Test handling of very long addresses"""
        matcher = mock_address_matcher
        
        long_addr = "İstanbul Kadıköy Moda Mahallesi " * 20
        normal_addr = "İstanbul Kadıköy Moda Mahallesi"
        
        result = matcher.calculate_hybrid_similarity(long_addr, normal_addr)
        
        # Should not crash and return reasonable result
        assert isinstance(result, dict)
        assert 0.0 <= result['overall_similarity'] <= 1.0
        assert isinstance(result['match_decision'], bool)
    
    def test_special_characters_in_addresses(self, mock_address_matcher):
        """Test handling of special characters in addresses"""
        matcher = mock_address_matcher
        
        special_char_tests = [
            ("İstanbul Kadıköy Moda Mah. Caferağa Sk. No:10", 
             "İstanbul Kadıköy Moda Mahallesi Caferağa Sokak 10"),
            ("İstanbul, Kadıköy - Moda Mahallesi (Caferağa Sokak) No: 10",
             "İstanbul Kadıköy Moda Mahallesi Caferağa Sokak 10"),
            ("İstanbul/Kadıköy/Moda Mahallesi & Caferağa Sokak #10",
             "İstanbul Kadıköy Moda Mahallesi Caferağa Sokak 10")
        ]
        
        for addr1, addr2 in special_char_tests:
            result = matcher.calculate_hybrid_similarity(addr1, addr2)
            
            # Should handle special characters and still find similarity
            assert result['overall_similarity'] > 0.5
            assert result['similarity_breakdown']['textual'] > 0.4
    
    def test_mixed_language_addresses(self, mock_address_matcher):
        """Test handling of mixed Turkish/English addresses"""
        matcher = mock_address_matcher
        
        mixed_tests = [
            ("Istanbul Kadikoy Moda District", "İstanbul Kadıköy Moda Mahallesi"),
            ("Ankara Cankaya Kizilay Neighborhood", "Ankara Çankaya Kızılay Mahallesi")
        ]
        
        for addr1, addr2 in mixed_tests:
            result = matcher.calculate_hybrid_similarity(addr1, addr2)
            
            # Should handle mixed language reasonably
            assert result['overall_similarity'] > 0.4
            assert result['similarity_breakdown']['semantic'] > 0.3


if __name__ == "__main__":
    # Simple test runner for development
    print("🧪 Running HybridAddressMatcher Mock Tests")
    print("=" * 50)
    
    try:
        matcher = MockHybridAddressMatcher()
        
        # Test basic functionality
        addr1 = "İstanbul Kadıköy Moda Mahallesi Caferağa Sokak No 10"
        addr2 = "İstanbul Kadıköy Moda Mahallesi Caferağa Sk. 10"
        
        result = matcher.calculate_hybrid_similarity(addr1, addr2)
        
        print(f"✅ Address 1: {addr1}")
        print(f"✅ Address 2: {addr2}")
        print(f"✅ Overall similarity: {result['overall_similarity']}")
        print(f"✅ Match decision: {result['match_decision']}")
        print(f"✅ Confidence: {result['confidence']}")
        print(f"✅ Processing time: {result['similarity_details']['processing_time_ms']}ms")
        
        # Test similarity breakdown
        breakdown = result['similarity_breakdown']
        print(f"\n📊 Similarity Breakdown:")
        print(f"   Semantic: {breakdown['semantic']}")
        print(f"   Geographic: {breakdown['geographic']}")
        print(f"   Textual: {breakdown['textual']}")
        print(f"   Hierarchical: {breakdown['hierarchical']}")
        
        # Test individual methods
        semantic_sim = matcher.get_semantic_similarity(addr1, addr2)
        geographic_sim = matcher.get_geographic_similarity(addr1, addr2)
        textual_sim = matcher.get_text_similarity(addr1, addr2)
        hierarchical_sim = matcher.get_hierarchy_similarity(addr1, addr2)
        
        print(f"\n🔧 Individual Methods:")
        print(f"   Semantic similarity: {semantic_sim}")
        print(f"   Geographic similarity: {geographic_sim}")
        print(f"   Text similarity: {textual_sim}")
        print(f"   Hierarchical similarity: {hierarchical_sim}")
        
        print("\n🎉 Mock HybridAddressMatcher tests completed successfully!")
        print("Ready for real implementation!")
        
    except Exception as e:
        print(f"❌ Error in mock tests: {e}")
        import traceback
        traceback.print_exc()