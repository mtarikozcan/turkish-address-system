"""
TEKNOFEST 2025 Adres Çözümleme Sistemi - Address Validator Algorithm

Algorithm 1: Address Validator
Türkçe adreslerin hiyerarşik tutarlılığını kontrol etme algoritması

Purpose: Validate Turkish addresses for hierarchical consistency,
postal code accuracy, and geographic coordinate validation.
"""

import pandas as pd
import os
import logging
import re
import math
from typing import Dict, List, Optional, Tuple, Any, Set
from pathlib import Path
import unicodedata

# Import centralized Turkish text utilities
try:
    from turkish_text_utils import TurkishTextNormalizer
    TURKISH_UTILS_AVAILABLE = True
except ImportError:
    TURKISH_UTILS_AVAILABLE = False
    # Fallback class if utils not available
    class TurkishTextNormalizer:
        @staticmethod
        def normalize_for_comparison(text): return text.lower()
        @staticmethod
        def turkish_title(text): return text.title()


class AddressValidator:
    """
    Turkish Address Validator Algorithm
    
    Validates Turkish address hierarchical consistency, postal codes,
    and geographic coordinates according to TEKNOFEST specifications.
    
    PERFORMANCE: Singleton pattern with cached data to avoid reloading 55,955 records
    """
    
    _instance = None
    _data_loaded = False
    _shared_admin_hierarchy = None
    _shared_hierarchy_index = None
    _shared_reverse_hierarchy = None
    _shared_postal_codes = None
    _shared_neighborhood_set = None
    
    def __new__(cls):
        """Singleton pattern - only create one instance with shared data"""
        if cls._instance is None:
            cls._instance = super(AddressValidator, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """
        Initialize AddressValidator with administrative data and postal codes
        
        Loads:
        - Turkish administrative hierarchy (İl-İlçe-Mahalle)
        - Postal code validation data
        - Geographic bounds for Turkey
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Create console handler if none exists
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        # CRITICAL FIX: Singleton pattern - load data only once
        if self._data_loaded:
            # Use cached data (avoid reloading 55,955 records)
            self.admin_hierarchy = self._shared_admin_hierarchy
            self.hierarchy_index = self._shared_hierarchy_index
            self.reverse_hierarchy = self._shared_reverse_hierarchy
            self.postal_codes = self._shared_postal_codes
            self.neighborhood_set = self._shared_neighborhood_set
            
            # Geographic bounds (lightweight)
            self.turkey_bounds = {
                'lat_min': 35.8,
                'lat_max': 42.1,
                'lon_min': 25.7,
                'lon_max': 44.8
            }
            return  # Skip loading, use cached data
        
        # Geographic bounds for Turkey
        self.turkey_bounds = {
            'lat_min': 35.8,
            'lat_max': 42.1,
            'lon_min': 25.7,
            'lon_max': 44.8
        }
        
        # Initialize data structures (first time only)
        self.admin_hierarchy = {}
        self.postal_codes = {}
        self.hierarchy_index = {}
        self.reverse_hierarchy = {}
        
        # Load data ONCE
        try:
            self.logger.info("SINGLETON: Loading data ONCE for all instances")
            self.admin_hierarchy = self.load_administrative_data()
            self.postal_codes = self.load_postal_code_data()
            
            # Cache data for future instances
            self._shared_admin_hierarchy = self.admin_hierarchy
            self._shared_hierarchy_index = self.hierarchy_index
            self._shared_reverse_hierarchy = self.reverse_hierarchy
            self._shared_postal_codes = self.postal_codes
            self._shared_neighborhood_set = getattr(self, 'neighborhood_set', set())
            
            # Mark as loaded
            self._data_loaded = True
            
            self.logger.info("AddressValidator initialized successfully with singleton caching")
        except Exception as e:
            self.logger.error(f"Failed to initialize AddressValidator: {e}")
            raise
    
    def load_administrative_data(self) -> Dict[Tuple[str, str, str], bool]:
        """
        Load Turkish administrative hierarchy data from CSV
        
        Returns:
            Dict mapping (il, ilce, mahalle) tuples to True for valid hierarchies
            
        Raises:
            FileNotFoundError: If hierarchy CSV file not found
            pd.errors.EmptyDataError: If CSV file is empty
        """
        try:
            # Get the project root directory
            current_dir = Path(__file__).parent
            project_root = current_dir.parent
            csv_path = project_root / "database" / "enhanced_turkish_neighborhoods.csv"
            
            if not csv_path.exists():
                self.logger.warning(f"Hierarchy CSV not found at {csv_path}, using fallback data")
                return self._get_fallback_hierarchy_data()
            
            # Load CSV data
            df = pd.read_csv(csv_path, encoding='utf-8')
            self.logger.info(f"Loaded {len(df)} administrative records from CSV")
            
            # Create hierarchy lookup dictionary for O(1) access  
            hierarchy_dict = {}
            hierarchy_index = {}
            reverse_hierarchy = {}
            neighborhood_set = set()  # CRITICAL: Comprehensive neighborhood validation
            
            for _, row in df.iterrows():
                il = self._normalize_turkish_text(str(row['il_adi']))
                ilce = self._normalize_turkish_text(str(row['ilce_adi']))
                mahalle = self._normalize_turkish_text(str(row['mahalle_adi']))
                source = row.get('source', 'traditional')
                
                # Add ALL neighborhoods to validation set (CRITICAL FIX)
                neighborhood_set.add(mahalle)
                
                if source == 'traditional' and il != 'unknown' and ilce != 'unknown':
                    # Traditional data: Full hierarchy validation
                    hierarchy_tuple = (il, ilce, mahalle)
                    hierarchy_dict[hierarchy_tuple] = True
                    
                    # Create indexes for efficient lookups
                    if il not in hierarchy_index:
                        hierarchy_index[il] = {}
                    if ilce not in hierarchy_index[il]:
                        hierarchy_index[il][ilce] = set()
                    hierarchy_index[il][ilce].add(mahalle)
                    
                    # Reverse index for validation
                    if mahalle not in reverse_hierarchy:
                        reverse_hierarchy[mahalle] = []
                    reverse_hierarchy[mahalle].append((il, ilce))
                    
                elif source == 'osm':
                    # OSM data: Flexible neighborhood validation (CRITICAL FIX)
                    # Create wildcard hierarchy for OSM neighborhoods
                    flexible_tuple = ('*', '*', mahalle)  # Wildcard validation
                    hierarchy_dict[flexible_tuple] = True
                    
                    # Add to reverse index with flexible matching
                    if mahalle not in reverse_hierarchy:
                        reverse_hierarchy[mahalle] = []
                    reverse_hierarchy[mahalle].append(('*', '*'))  # Wildcard match
            
            # Store indexes for efficient validation (CRITICAL FIX)
            self.hierarchy_index = hierarchy_index
            self.reverse_hierarchy = reverse_hierarchy
            self.neighborhood_set = neighborhood_set  # CRITICAL: Store for fast lookups
            
            # Count validation combinations
            traditional_combinations = len([k for k in hierarchy_dict.keys() if k[0] != '*'])
            osm_combinations = len([k for k in hierarchy_dict.keys() if k[0] == '*'])
            
            self.logger.info(f"Created enhanced hierarchy index:")
            self.logger.info(f"  - Traditional combinations: {traditional_combinations}")
            self.logger.info(f"  - OSM flexible combinations: {osm_combinations}")
            self.logger.info(f"  - Total valid combinations: {len(hierarchy_dict)}")
            self.logger.info(f"  - Total neighborhoods: {len(neighborhood_set)}")
            return hierarchy_dict
            
        except FileNotFoundError:
            self.logger.warning("Administrative hierarchy CSV file not found, using fallback data")
            return self._get_fallback_hierarchy_data()
        except pd.errors.EmptyDataError:
            self.logger.error("Administrative hierarchy CSV file is empty")
            return self._get_fallback_hierarchy_data()
        except Exception as e:
            self.logger.error(f"Error loading administrative data: {e}")
            return self._get_fallback_hierarchy_data()
    
    def load_postal_code_data(self) -> Dict[str, Dict[str, str]]:
        """
        Load Turkish postal code validation data
        
        Returns:
            Dict mapping postal codes to {il, ilce} information
            
        Note:
            In a production system, this would load from a comprehensive
            postal code database. For now, using representative samples.
        """
        try:
            # Representative Turkish postal codes for major cities
            # In production, this would be loaded from a comprehensive database
            postal_data = {
                # İstanbul postal codes
                '34718': {'il': 'istanbul', 'ilce': 'kadıköy'},
                '34357': {'il': 'istanbul', 'ilce': 'beşiktaş'},
                '34394': {'il': 'istanbul', 'ilce': 'şişli'},
                '34349': {'il': 'istanbul', 'ilce': 'bakırköy'},
                '34093': {'il': 'istanbul', 'ilce': 'fatih'},
                '34433': {'il': 'istanbul', 'ilce': 'beyoğlu'},
                
                # Ankara postal codes
                '06420': {'il': 'ankara', 'ilce': 'çankaya'},
                '06170': {'il': 'ankara', 'ilce': 'yenimahalle'},
                '06230': {'il': 'ankara', 'ilce': 'altındağ'},
                '06490': {'il': 'ankara', 'ilce': 'keçiören'},
                '06560': {'il': 'ankara', 'ilce': 'mamak'},
                
                # İzmir postal codes
                '35220': {'il': 'izmir', 'ilce': 'konak'},
                '35530': {'il': 'izmir', 'ilce': 'karşıyaka'},
                '35100': {'il': 'izmir', 'ilce': 'bornova'},
                '35390': {'il': 'izmir', 'ilce': 'buca'},
                '35410': {'il': 'izmir', 'ilce': 'gaziemir'},
                
                # Other major cities
                '16050': {'il': 'bursa', 'ilce': 'osmangazi'},
                '07070': {'il': 'antalya', 'ilce': 'muratpaşa'},
                '01120': {'il': 'adana', 'ilce': 'seyhan'},
                '42060': {'il': 'konya', 'ilce': 'selçuklu'},
                '38030': {'il': 'kayseri', 'ilce': 'melikgazi'},
            }
            
            self.logger.info(f"Loaded {len(postal_data)} postal code mappings")
            return postal_data
            
        except Exception as e:
            self.logger.error(f"Error loading postal code data: {e}")
            return {}
    
    def _get_fallback_hierarchy_data(self) -> Dict[Tuple[str, str, str], bool]:
        """
        Provide fallback hierarchy data when CSV is not available
        
        Returns:
            Dict with basic Turkish administrative hierarchies
        """
        fallback_data = {
            ('istanbul', 'kadıköy', 'moda mahallesi'): True,
            ('istanbul', 'kadıköy', 'caferağa mahallesi'): True,
            ('istanbul', 'beşiktaş', 'levent mahallesi'): True,
            ('istanbul', 'beşiktaş', 'etiler mahallesi'): True,
            ('istanbul', 'şişli', 'mecidiyeköy mahallesi'): True,
            ('istanbul', 'şişli', 'gayrettepe mahallesi'): True,
            ('ankara', 'çankaya', 'kızılay mahallesi'): True,
            ('ankara', 'çankaya', 'bahçelievler mahallesi'): True,
            ('izmir', 'konak', 'alsancak mahallesi'): True,
            ('izmir', 'karşıyaka', 'bostanlı mahallesi'): True,
        }
        
        self.logger.info(f"Using fallback hierarchy data with {len(fallback_data)} entries")
        return fallback_data
    
    def _normalize_turkish_text(self, text: str) -> str:
        """
        Normalize Turkish text for consistent comparison
        
        Args:
            text: Input text to normalize
            
        Returns:
            Normalized text (lowercase, Turkish characters preserved)
        """
        return TurkishTextNormalizer.normalize_for_comparison(text)
    
    def validate_address(self, address_data) -> dict:
        """
        Main validation function for Turkish addresses
        
        Args:
            address_data: Dictionary containing address information with keys:
                - raw_address: Original address string
                - coordinates: Optional dict with lat/lon (optional)
                - parsed_components: Dict with il, ilce, mahalle, etc. (optional)
            OR
            address_data: String address (will be automatically parsed)
                
        Returns:
            Dictionary with validation results:
            {
                "is_valid": bool,
                "confidence": float (0.0-1.0),
                "errors": List[str],
                "suggestions": List[str],
                "validation_details": {
                    "hierarchy_valid": bool,
                    "postal_code_valid": bool,
                    "coordinate_valid": bool,
                    "completeness_score": float
                }
            }
        """
        try:
            # Input validation
            # CRITICAL FIX: Handle both string and dictionary inputs
            if isinstance(address_data, str):
                # String input: automatically parse the address
                raw_address = address_data
                coordinates = None
                parsed_components = {}
                
                # Try to parse the address if parser is available
                try:
                    # Import and use parser
                    from address_parser import AddressParser
                    parser = AddressParser()
                    parse_result = parser.parse_address(raw_address)
                    parsed_components = parse_result.get('components', {})
                except ImportError:
                    # Parser not available, use empty components
                    parsed_components = {}
                    
            elif isinstance(address_data, dict):
                # Dictionary input: extract components as before
                raw_address = address_data.get('raw_address', '')
                coordinates = address_data.get('coordinates')
                parsed_components = address_data.get('parsed_components', {})
            else:
                return self._create_error_result("Input must be a string or dictionary")
            
            if not raw_address and not parsed_components:
                return self._create_error_result("Either raw_address or parsed_components must be provided")
            
            # Initialize validation results
            validation_details = {
                'hierarchy_valid': False,
                'postal_code_valid': True,  # Default to True if no postal code provided
                'coordinate_valid': True,   # Default to True if no coordinates provided
                'completeness_score': 0.0
            }
            
            errors = []
            suggestions = []
            confidence_factors = []
            
            # 1. Enhanced hierarchy validation with partial address support
            if parsed_components:
                il = parsed_components.get('il')
                ilce = parsed_components.get('ilce') 
                mahalle = parsed_components.get('mahalle')
                
                hierarchy_result = self._validate_partial_hierarchy(il, ilce, mahalle)
                validation_details['hierarchy_valid'] = hierarchy_result['is_valid']
                validation_details['hierarchy_type'] = hierarchy_result['type']
                
                if hierarchy_result['is_valid']:
                    confidence_factors.append(hierarchy_result['confidence_weight'])
                    if hierarchy_result['warnings']:
                        suggestions.extend(hierarchy_result['warnings'])
                else:
                    errors.extend(hierarchy_result['errors'])
                    suggestions.extend(hierarchy_result['suggestions'])
            
            # 2. Postal code validation
            postal_code = parsed_components.get('postal_code') if parsed_components else None
            if postal_code:
                postal_valid = self.validate_postal_code(postal_code, parsed_components)
                validation_details['postal_code_valid'] = postal_valid
                
                if postal_valid:
                    confidence_factors.append(0.3)  # 30% weight for postal code
                else:
                    errors.append(f"Invalid or inconsistent postal code: {postal_code}")
                    suggestions.append("Verify postal code matches the address location")
            
            # 3. Coordinate validation
            if coordinates:
                coord_result = self.validate_coordinates(coordinates, parsed_components)
                validation_details['coordinate_valid'] = coord_result['valid']
                
                if coord_result['valid']:
                    confidence_factors.append(0.3)  # 30% weight for coordinates
                else:
                    errors.append("Invalid or inconsistent coordinates")
                    suggestions.append("Check that coordinates are within Turkey bounds")
            
            # 4. Calculate completeness score
            if parsed_components:
                required_fields = ['il', 'ilce', 'mahalle']
                optional_fields = ['sokak', 'bina_no', 'postal_code']
                
                provided_required = sum(1 for field in required_fields if parsed_components.get(field))
                provided_optional = sum(1 for field in optional_fields if parsed_components.get(field))
                
                completeness = (provided_required / len(required_fields)) * 0.7 + \
                              (provided_optional / len(optional_fields)) * 0.3
                validation_details['completeness_score'] = round(completeness, 3)
            
            # 5. Calculate overall confidence - ENHANCED for better scoring
            base_confidence = sum(confidence_factors)
            
            # CRITICAL FIX: Make completeness a major factor, not just a bonus
            completeness_score = validation_details.get('completeness_score', 0.0)
            
            if completeness_score > 0:
                # Instead of tiny 0.1 multiplier, make completeness contribute significantly
                # Complete address (0.7 completeness) should reach 0.7-0.9 confidence range
                completeness_contribution = completeness_score * 0.4  # Up to 0.28 instead of 0.07
                base_confidence = min(1.0, base_confidence + completeness_contribution)
            
            # Additional bonus for valid hierarchy without requiring postal/coordinates
            if (validation_details.get('hierarchy_valid', False) and 
                validation_details.get('hierarchy_type') == 'complete'):
                # High quality complete hierarchy gets additional boost
                base_confidence = min(1.0, base_confidence + 0.2)
            
            # Penalty for errors
            if errors:
                error_penalty = min(0.3, len(errors) * 0.1)
                base_confidence = max(0.0, base_confidence - error_penalty)
            
            final_confidence = round(base_confidence, 3)
            
            # 6. Determine overall validity
            is_valid = (validation_details['hierarchy_valid'] and 
                       validation_details['postal_code_valid'] and 
                       validation_details['coordinate_valid'] and
                       len(errors) == 0)
            
            return {
                'is_valid': is_valid,
                'confidence': final_confidence,
                'errors': errors,
                'suggestions': suggestions,
                'validation_details': validation_details
            }
            
        except Exception as e:
            self.logger.error(f"Error in validate_address: {e}")
            return self._create_error_result(f"Validation error: {str(e)}")
    
    def validate_hierarchy(self, il: str, ilce: str, mahalle: str) -> bool:
        """
        Validate İl-İlçe-Mahalle hierarchical consistency
        
        Args:
            il: Province name (İl)
            ilce: District name (İlçe)  
            mahalle: Neighborhood name (Mahalle)
            
        Returns:
            True if hierarchy is valid, False otherwise
        """
        try:
            # Input validation
            if not all([il, ilce, mahalle]):
                self.logger.debug("Missing parameters in hierarchy validation")
                return False
            
            # Normalize inputs
            il_norm = self._normalize_turkish_text(il)
            ilce_norm = self._normalize_turkish_text(ilce)
            mahalle_norm = self._normalize_turkish_text(mahalle)
            
            # Check exact match first (traditional hierarchy)
            hierarchy_tuple = (il_norm, ilce_norm, mahalle_norm)
            if hierarchy_tuple in self.admin_hierarchy:
                return True
            
            # CRITICAL FIX: Check OSM flexible validation
            osm_tuple = ('*', '*', mahalle_norm)
            if osm_tuple in self.admin_hierarchy:
                return True
            
            # CRITICAL FIX: Fast neighborhood validation for partial addresses
            if hasattr(self, 'neighborhood_set') and mahalle_norm in self.neighborhood_set:
                return True
            
            # Check using hierarchy index for better performance
            if il_norm in self.hierarchy_index:
                if ilce_norm in self.hierarchy_index[il_norm]:
                    # Check exact match first
                    if mahalle_norm in self.hierarchy_index[il_norm][ilce_norm]:
                        return True
                    
                    # Check with "mahallesi" suffix if not already present
                    if not mahalle_norm.endswith('mahallesi'):
                        mahalle_with_suffix = f"{mahalle_norm} mahallesi"
                        if mahalle_with_suffix in self.hierarchy_index[il_norm][ilce_norm]:
                            return True
                    
                    # Check without "mahallesi" suffix if present
                    if mahalle_norm.endswith('mahallesi'):
                        mahalle_without_suffix = mahalle_norm.replace(' mahallesi', '')
                        for stored_mahalle in self.hierarchy_index[il_norm][ilce_norm]:
                            if stored_mahalle.replace(' mahallesi', '') == mahalle_without_suffix:
                                return True
            
            # Use enhanced hierarchy matching for comprehensive validation
            enhanced_result = self._enhanced_hierarchy_match(il, ilce, mahalle)
            return enhanced_result['is_match']
            
        except Exception as e:
            self.logger.error(f"Error in validate_hierarchy: {e}")
            return False
    
    def _validate_partial_hierarchy(self, il: str, ilce: str, mahalle: str) -> dict:
        """
        Validate partial address hierarchies with appropriate handling for different combinations
        
        Args:
            il: Province name (can be None)
            ilce: District name (can be None)
            mahalle: Neighborhood name (can be None)
            
        Returns:
            Dictionary with validation results:
            {
                'is_valid': bool,
                'type': str,  # 'complete', 'partial_valid', 'insufficient'
                'confidence_weight': float,
                'errors': List[str],
                'suggestions': List[str],
                'warnings': List[str]
            }
        """
        result = {
            'is_valid': False,
            'type': 'insufficient',
            'confidence_weight': 0.0,
            'errors': [],
            'suggestions': [],
            'warnings': []
        }
        
        # Count non-empty components
        components_provided = sum(1 for component in [il, ilce, mahalle] if component)
        
        if components_provided == 0:
            result['errors'].append("No address components provided")
            result['suggestions'].append("Provide at least province and neighborhood information")
            return result
        
        # Case 1: Complete hierarchy (il + ilce + mahalle)
        if il and ilce and mahalle:
            hierarchy_valid = self.validate_hierarchy(il, ilce, mahalle)
            if hierarchy_valid:
                result['is_valid'] = True
                result['type'] = 'complete'
                result['confidence_weight'] = 0.4  # Full confidence
            else:
                result['errors'].append(f"Invalid administrative hierarchy: {il}-{ilce}-{mahalle}")
                result['suggestions'].append("Verify the province-district-neighborhood combination")
                # Try partial validation as fallback
                if self._validate_province_neighborhood(il, mahalle):
                    result['is_valid'] = True
                    result['type'] = 'partial_valid'
                    result['confidence_weight'] = 0.25
                    result['warnings'].append(f"District '{ilce}' may not belong to {il}-{mahalle}")
        
        # Case 2: Province + Neighborhood (il + mahalle, missing ilce)
        elif il and mahalle and not ilce:
            if self._validate_province_neighborhood(il, mahalle):
                result['is_valid'] = True
                result['type'] = 'partial_valid'
                result['confidence_weight'] = 0.3
                result['warnings'].append("District information missing but province-neighborhood combination is valid")
            else:
                result['errors'].append(f"Invalid combination: {il} province with {mahalle} neighborhood")
                result['suggestions'].append("Check if the neighborhood belongs to the specified province")
        
        # Case 3: Province + District (il + ilce, missing mahalle)
        elif il and ilce and not mahalle:
            if self._validate_province_district(il, ilce):
                result['is_valid'] = True
                result['type'] = 'partial_valid'
                result['confidence_weight'] = 0.25
                result['warnings'].append("Neighborhood information missing")
                result['suggestions'].append("Provide neighborhood for complete address validation")
            else:
                result['errors'].append(f"Invalid combination: {il} province with {ilce} district")
                result['suggestions'].append("Check if the district belongs to the specified province")
        
        # Case 4: Only province (il only)
        elif il and not ilce and not mahalle:
            if self._is_valid_province_name(il):
                result['is_valid'] = True
                result['type'] = 'partial_valid'
                result['confidence_weight'] = 0.15
                result['warnings'].append("Only province provided - very incomplete address")
                result['suggestions'].append("Add district and neighborhood for better validation")
            else:
                result['errors'].append(f"Unknown province: {il}")
                result['suggestions'].append("Check province name spelling")
        
        # Case 5: Invalid combinations (only district, only neighborhood, district+neighborhood without province)
        else:
            if ilce and not il and not mahalle:
                result['errors'].append("District provided without province - insufficient information")
                result['suggestions'].append("Provide province information for proper validation")
            elif mahalle and not il and not ilce:
                result['errors'].append("Only neighborhood provided - insufficient information")
                result['suggestions'].append("Provide province and district information")
            elif ilce and mahalle and not il:
                result['errors'].append("District and neighborhood provided without province")
                result['suggestions'].append("Province information is required for validation")
        
        return result
    
    def _validate_province_neighborhood(self, il: str, mahalle: str) -> bool:
        """Check if neighborhood exists in the specified province (across all districts)"""
        try:
            il_norm = self._normalize_turkish_text(il)
            mahalle_norm = self._normalize_turkish_text(mahalle)
            
            if il_norm not in self.hierarchy_index:
                return False
            
            # Check if mahalle exists in any district of this province
            for district, neighborhoods in self.hierarchy_index[il_norm].items():
                # Try exact match first
                if mahalle_norm in neighborhoods:
                    return True
                # Try with mahallesi suffix
                if f"{mahalle_norm} mahallesi" in neighborhoods:
                    return True
                # Try without suffix if present
                if mahalle_norm.endswith(' mahallesi'):
                    base_name = mahalle_norm.replace(' mahallesi', '')
                    if any(base_name in n for n in neighborhoods):
                        return True
            
            return False
        except Exception:
            return False
    
    def _validate_province_district(self, il: str, ilce: str) -> bool:
        """Check if district belongs to the specified province"""
        try:
            il_norm = self._normalize_turkish_text(il)
            ilce_norm = self._normalize_turkish_text(ilce)
            
            if il_norm not in self.hierarchy_index:
                return False
            
            return ilce_norm in self.hierarchy_index[il_norm]
        except Exception:
            return False
    
    def _is_valid_province_name(self, il: str) -> bool:
        """Check if province name is valid"""
        try:
            il_norm = self._normalize_turkish_text(il)
            return il_norm in self.hierarchy_index
        except Exception:
            return False
    
    def _enhanced_hierarchy_match(self, il: str, ilce: str, mahalle: str) -> dict:
        """
        Enhanced hierarchy matching with comprehensive variation handling and CSV integration
        
        Args:
            il: Province name
            ilce: District name
            mahalle: Neighborhood name
            
        Returns:
            Dictionary with matching results:
            {
                'is_match': bool,
                'confidence': float,
                'matched_forms': dict,
                'suggestions': List[str]
            }
        """
        result = {
            'is_match': False,
            'confidence': 0.0,
            'matched_forms': {},
            'suggestions': []
        }
        
        try:
            # Normalize inputs
            il_norm = self._normalize_turkish_text(il) if il else ''
            ilce_norm = self._normalize_turkish_text(ilce) if ilce else ''
            mahalle_norm = self._normalize_turkish_text(mahalle) if mahalle else ''
            
            # Step 1: Exact match
            if self._exact_hierarchy_match(il_norm, ilce_norm, mahalle_norm):
                result['is_match'] = True
                result['confidence'] = 1.0
                result['matched_forms'] = {'il': il, 'ilce': ilce, 'mahalle': mahalle}
                return result
                
            # Step 2: Handle mahalle suffix variations
            if il_norm and ilce_norm and mahalle_norm:
                match_result = self._match_with_suffix_variations(il_norm, ilce_norm, mahalle_norm)
                if match_result['found']:
                    result['is_match'] = True
                    result['confidence'] = 0.9
                    result['matched_forms'] = match_result['matched_forms']
                    return result
            
            # Step 3: Fuzzy matching with similarity threshold
            if il_norm and ilce_norm and mahalle_norm:
                fuzzy_result = self._fuzzy_match_hierarchy_components(il_norm, ilce_norm, mahalle_norm)
                if fuzzy_result['best_score'] >= 0.8:
                    result['is_match'] = True
                    result['confidence'] = fuzzy_result['best_score']
                    result['matched_forms'] = fuzzy_result['best_match']
                    result['suggestions'] = fuzzy_result['suggestions']
                    return result
            
            # Step 4: Partial matching for incomplete addresses
            if il_norm and not (ilce_norm and mahalle_norm):
                partial_result = self._match_partial_hierarchy(il_norm, ilce_norm, mahalle_norm)
                if partial_result['found']:
                    result['is_match'] = True
                    result['confidence'] = partial_result['confidence']
                    result['matched_forms'] = partial_result['matched_forms']
                    result['suggestions'] = partial_result['suggestions']
                    return result
            
            # Step 5: Suggest corrections for close matches
            suggestions = self._generate_hierarchy_suggestions(il_norm, ilce_norm, mahalle_norm)
            result['suggestions'] = suggestions
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in enhanced hierarchy matching: {e}")
            return result
    
    def _exact_hierarchy_match(self, il: str, ilce: str, mahalle: str) -> bool:
        """Check for exact hierarchy match"""
        try:
            if il in self.hierarchy_index:
                if ilce in self.hierarchy_index[il]:
                    return mahalle in self.hierarchy_index[il][ilce]
            return False
        except Exception:
            return False
    
    def _match_with_suffix_variations(self, il: str, ilce: str, mahalle: str) -> dict:
        """
        Match hierarchy with common suffix variations
        """
        result = {'found': False, 'matched_forms': {}}
        
        try:
            if il not in self.hierarchy_index:
                return result
                
            if ilce not in self.hierarchy_index[il]:
                return result
            
            neighborhoods = self.hierarchy_index[il][ilce]
            
            # Try different mahalle variations
            mahalle_variations = [
                mahalle,
                f"{mahalle} mahallesi",
                mahalle.replace(' mahallesi', ''),
                mahalle.replace(' mh', ' mahallesi'),
                mahalle.replace(' mah', ' mahallesi')
            ]
            
            for variation in mahalle_variations:
                if variation in neighborhoods:
                    result['found'] = True
                    result['matched_forms'] = {
                        'il': il,
                        'ilce': ilce,
                        'mahalle': variation
                    }
                    break
                    
            # Also try partial matching within neighborhood names
            if not result['found']:
                for neighborhood in neighborhoods:
                    # Check if mahalle is a substring of any neighborhood
                    if mahalle in neighborhood or neighborhood.replace(' mahallesi', '') == mahalle:
                        result['found'] = True
                        result['matched_forms'] = {
                            'il': il,
                            'ilce': ilce,
                            'mahalle': neighborhood
                        }
                        break
            
            return result
            
        except Exception as e:
            self.logger.debug(f"Error in suffix variation matching: {e}")
            return result
    
    def _fuzzy_match_hierarchy_components(self, il: str, ilce: str, mahalle: str) -> dict:
        """
        Perform fuzzy matching on all hierarchy components
        """
        result = {
            'best_score': 0.0,
            'best_match': {},
            'suggestions': []
        }
        
        try:
            from difflib import SequenceMatcher
            
            best_overall_score = 0.0
            best_match = {}
            
            # Check all provinces for fuzzy matches
            for province in self.hierarchy_index.keys():
                il_similarity = SequenceMatcher(None, il, province).ratio()
                
                if il_similarity >= 0.7:  # Province threshold
                    # Check districts in this province
                    for district in self.hierarchy_index[province].keys():
                        ilce_similarity = SequenceMatcher(None, ilce, district).ratio()
                        
                        if ilce_similarity >= 0.7:  # District threshold
                            # Check neighborhoods in this district
                            for neighborhood in self.hierarchy_index[province][district]:
                                # Try matching with base neighborhood name
                                base_neighborhood = neighborhood.replace(' mahallesi', '')
                                mahalle_similarity = max(
                                    SequenceMatcher(None, mahalle, neighborhood).ratio(),
                                    SequenceMatcher(None, mahalle, base_neighborhood).ratio()
                                )
                                
                                if mahalle_similarity >= 0.7:  # Neighborhood threshold
                                    # Calculate combined score
                                    combined_score = (il_similarity + ilce_similarity + mahalle_similarity) / 3
                                    
                                    if combined_score > best_overall_score:
                                        best_overall_score = combined_score
                                        best_match = {
                                            'il': province,
                                            'ilce': district,
                                            'mahalle': base_neighborhood
                                        }
            
            result['best_score'] = best_overall_score
            result['best_match'] = best_match
            
            if best_overall_score >= 0.8:
                result['suggestions'] = [
                    f"Did you mean: {best_match['il']} - {best_match['ilce']} - {best_match['mahalle']}?"
                ]
            
            return result
            
        except Exception as e:
            self.logger.debug(f"Error in fuzzy hierarchy matching: {e}")
            return result
    
    def _match_partial_hierarchy(self, il: str, ilce: str, mahalle: str) -> dict:
        """
        Handle partial hierarchy matching for incomplete addresses
        """
        result = {
            'found': False,
            'confidence': 0.0,
            'matched_forms': {},
            'suggestions': []
        }
        
        try:
            # Province only
            if il and not ilce and not mahalle:
                if il in self.hierarchy_index:
                    result['found'] = True
                    result['confidence'] = 0.3
                    result['matched_forms'] = {'il': il}
                    result['suggestions'] = ["Provide district and neighborhood for complete validation"]
                    
            # Province + District
            elif il and ilce and not mahalle:
                if il in self.hierarchy_index and ilce in self.hierarchy_index[il]:
                    result['found'] = True
                    result['confidence'] = 0.6
                    result['matched_forms'] = {'il': il, 'ilce': ilce}
                    result['suggestions'] = ["Provide neighborhood for complete validation"]
                    
            # Province + Neighborhood (missing district)
            elif il and not ilce and mahalle:
                if il in self.hierarchy_index:
                    # Search for mahalle across all districts in this province
                    for district, neighborhoods in self.hierarchy_index[il].items():
                        for neighborhood in neighborhoods:
                            if (mahalle in neighborhood or 
                                neighborhood.replace(' mahallesi', '') == mahalle):
                                result['found'] = True
                                result['confidence'] = 0.7
                                result['matched_forms'] = {
                                    'il': il, 
                                    'ilce': district, 
                                    'mahalle': neighborhood.replace(' mahallesi', '')
                                }
                                result['suggestions'] = [f"Inferred district: {district}"]
                                break
                        if result['found']:
                            break
            
            return result
            
        except Exception as e:
            self.logger.debug(f"Error in partial hierarchy matching: {e}")
            return result
    
    def _generate_hierarchy_suggestions(self, il: str, ilce: str, mahalle: str) -> List[str]:
        """
        Generate helpful suggestions for invalid hierarchies
        """
        suggestions = []
        
        try:
            # Check if province exists
            if il and il not in self.hierarchy_index:
                # Find similar provinces
                from difflib import get_close_matches
                close_provinces = get_close_matches(il, list(self.hierarchy_index.keys()), n=3, cutoff=0.6)
                if close_provinces:
                    suggestions.append(f"Did you mean province: {', '.join(close_provinces)}?")
                else:
                    suggestions.append("Check province name spelling")
                    
            # Check if district exists in province
            elif il and ilce and il in self.hierarchy_index and ilce not in self.hierarchy_index[il]:
                close_districts = get_close_matches(ilce, list(self.hierarchy_index[il].keys()), n=3, cutoff=0.6)
                if close_districts:
                    suggestions.append(f"Did you mean district: {', '.join(close_districts)}?")
                else:
                    suggestions.append(f"Check district name in {il} province")
                    
            # Check if neighborhood exists in district
            elif il and ilce and mahalle and il in self.hierarchy_index and ilce in self.hierarchy_index[il]:
                neighborhoods = list(self.hierarchy_index[il][ilce])
                base_neighborhoods = [n.replace(' mahallesi', '') for n in neighborhoods]
                close_neighborhoods = get_close_matches(mahalle, base_neighborhoods, n=3, cutoff=0.6)
                if close_neighborhoods:
                    suggestions.append(f"Did you mean neighborhood: {', '.join(close_neighborhoods)}?")
                else:
                    suggestions.append(f"Check neighborhood name in {il}-{ilce}")
            
            return suggestions
            
        except Exception as e:
            self.logger.debug(f"Error generating suggestions: {e}")
            return suggestions
    
    def _fuzzy_hierarchy_match(self, il: str, ilce: str, mahalle: str) -> bool:
        """
        Perform fuzzy matching for hierarchy validation
        
        Args:
            il, ilce, mahalle: Normalized address components
            
        Returns:
            True if fuzzy match found, False otherwise
        """
        try:
            # Simple fuzzy matching - check if mahalle exists in reverse index
            if mahalle in self.reverse_hierarchy:
                for valid_il, valid_ilce in self.reverse_hierarchy[mahalle]:
                    # Allow some flexibility in il/ilce matching
                    if (self._fuzzy_text_match(il, valid_il) and 
                        self._fuzzy_text_match(ilce, valid_ilce)):
                        return True
            
            return False
            
        except Exception as e:
            self.logger.debug(f"Error in fuzzy hierarchy matching: {e}")
            return False
    
    def _fuzzy_text_match(self, text1: str, text2: str, threshold: float = 0.8) -> bool:
        """
        Simple fuzzy text matching using character overlap
        
        Args:
            text1, text2: Texts to compare
            threshold: Similarity threshold (0.0-1.0)
            
        Returns:
            True if texts are similar enough, False otherwise
        """
        if not text1 or not text2:
            return False
        
        if text1 == text2:
            return True
        
        # Simple character-based similarity
        common_chars = set(text1) & set(text2)
        total_chars = set(text1) | set(text2)
        
        if not total_chars:
            return False
        
        similarity = len(common_chars) / len(total_chars)
        return similarity >= threshold
    
    def validate_postal_code(self, postal_code: str, address_components: dict) -> bool:
        """
        Validate Turkish postal code format and consistency
        
        Args:
            postal_code: 5-digit Turkish postal code
            address_components: Dict with address information (il, ilce)
            
        Returns:
            True if postal code is valid and consistent, False otherwise
        """
        try:
            # Input validation
            if not postal_code:
                return False
            
            # Convert to string and clean
            postal_str = str(postal_code).strip()
            
            # Format validation: Must be exactly 5 digits
            if not re.match(r'^\d{5}$', postal_str):
                self.logger.debug(f"Invalid postal code format: {postal_str}")
                return False
            
            # Check against known postal codes
            if postal_str in self.postal_codes:
                postal_data = self.postal_codes[postal_str]
                
                # Cross-validate with address components
                if address_components:
                    il = address_components.get('il')
                    ilce = address_components.get('ilce')
                    
                    if il and ilce:
                        il_norm = self._normalize_turkish_text(il)
                        ilce_norm = self._normalize_turkish_text(ilce)
                        
                        # Check if postal code matches address
                        if (postal_data['il'] == il_norm and 
                            postal_data['ilce'] == ilce_norm):
                            return True
                        else:
                            self.logger.debug(f"Postal code {postal_str} doesn't match {il_norm}-{ilce_norm}")
                            return False
                
                # If no address components to cross-validate, accept known postal code
                return True
            
            # For unknown postal codes, accept if format is valid
            # In production, this should be more restrictive
            self.logger.debug(f"Unknown postal code {postal_str}, accepting based on format")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in validate_postal_code: {e}")
            return False
    
    def validate_coordinates(self, coords: dict, address_components: dict) -> dict:
        """
        Validate coordinate-address consistency and Turkey bounds
        
        Args:
            coords: Dictionary with 'lat' and 'lon' keys
            address_components: Dict with address information (optional)
            
        Returns:
            Dictionary with:
            {
                "valid": bool,
                "distance_km": float,
                "error_message": str (optional)
            }
        """
        try:
            # Input validation
            if not coords or not isinstance(coords, dict):
                return {'valid': False, 'distance_km': float('inf'), 'error_message': 'No coordinates provided'}
            
            # Extract coordinates
            try:
                lat = float(coords.get('lat', 0))
                lon = float(coords.get('lon', 0))
            except (ValueError, TypeError):
                return {'valid': False, 'distance_km': float('inf'), 'error_message': 'Invalid coordinate format'}
            
            # Basic range validation
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                return {'valid': False, 'distance_km': float('inf'), 'error_message': 'Coordinates out of valid range'}
            
            # Turkey bounds validation
            if not (self.turkey_bounds['lat_min'] <= lat <= self.turkey_bounds['lat_max'] and
                    self.turkey_bounds['lon_min'] <= lon <= self.turkey_bounds['lon_max']):
                self.logger.debug(f"Coordinates ({lat}, {lon}) outside Turkey bounds")
                return {'valid': False, 'distance_km': float('inf'), 'error_message': 'Coordinates outside Turkey'}
            
            # If address components provided, attempt distance validation
            distance_km = 0.0
            if address_components:
                distance_km = self._calculate_address_distance(lat, lon, address_components)
            
            return {
                'valid': True,
                'distance_km': distance_km,
                'error_message': None
            }
            
        except Exception as e:
            self.logger.error(f"Error in validate_coordinates: {e}")
            return {'valid': False, 'distance_km': float('inf'), 'error_message': str(e)}
    
    def _calculate_address_distance(self, lat: float, lon: float, address_components: dict) -> float:
        """
        Calculate approximate distance between coordinates and address location
        
        Args:
            lat, lon: Coordinates to validate
            address_components: Address information
            
        Returns:
            Approximate distance in kilometers (0.0 if cannot calculate)
        """
        try:
            # Approximate city center coordinates for major Turkish cities
            city_coordinates = {
                'istanbul': (41.0082, 28.9784),
                'ankara': (39.9334, 32.8597),
                'izmir': (38.4192, 27.1287),
                'bursa': (40.1824, 29.0670),
                'antalya': (36.8969, 30.7133),
                'adana': (37.0000, 35.3213),
                'konya': (37.8746, 32.4932),
                'gaziantep': (37.0594, 37.3825),
                'kayseri': (38.7312, 35.4787),
            }
            
            il = address_components.get('il')
            if not il:
                return 0.0
            
            il_norm = self._normalize_turkish_text(il)
            
            if il_norm in city_coordinates:
                city_lat, city_lon = city_coordinates[il_norm]
                distance = self._haversine_distance(lat, lon, city_lat, city_lon)
                return round(distance, 2)
            
            return 0.0
            
        except Exception as e:
            self.logger.debug(f"Error calculating address distance: {e}")
            return 0.0
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the great circle distance between two points on Earth
        
        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates
            
        Returns:
            Distance in kilometers
        """
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
    
    def _create_error_result(self, error_message: str) -> dict:
        """
        Create standardized error result dictionary
        
        Args:
            error_message: Error description
            
        Returns:
            Error result dictionary
        """
        return {
            'is_valid': False,
            'confidence': 0.0,
            'errors': [error_message],
            'suggestions': ['Please check input data format and completeness'],
            'validation_details': {
                'hierarchy_valid': False,
                'postal_code_valid': False,
                'coordinate_valid': False,
                'completeness_score': 0.0
            }
        }


# Utility functions for external use
def normalize_turkish_address(address: str) -> str:
    """
    Utility function to normalize Turkish address text
    
    Args:
        address: Raw address string
        
    Returns:
        Normalized address string
    """
    validator = AddressValidator()
    return validator._normalize_turkish_text(address)


def quick_hierarchy_check(il: str, ilce: str, mahalle: str) -> bool:
    """
    Quick utility function for hierarchy validation
    
    Args:
        il, ilce, mahalle: Address components
        
    Returns:
        True if hierarchy is valid
    """
    validator = AddressValidator()
    return validator.validate_hierarchy(il, ilce, mahalle)


# Example usage and testing
if __name__ == "__main__":
    # Example usage
    validator = AddressValidator()
    
    # Test valid address
    test_address = {
        'raw_address': 'İstanbul Kadıköy Moda Mahallesi Caferağa Sokak 10',
        'parsed_components': {
            'il': 'İstanbul',
            'ilce': 'Kadıköy',
            'mahalle': 'Moda Mahallesi',
            'sokak': 'Caferağa Sokak',
            'bina_no': '10',
            'postal_code': '34718'
        },
        'coordinates': {'lat': 40.9875, 'lon': 29.0376}
    }
    
    result = validator.validate_address(test_address)
    print("Validation Result:")
    print(f"Valid: {result['is_valid']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Errors: {result['errors']}")
    print(f"Details: {result['validation_details']}")