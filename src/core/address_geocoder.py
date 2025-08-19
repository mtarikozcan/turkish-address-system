"""
Address Resolution System - Address Geocoding System
Algorithm 6: Address Geocoder

REQUIREMENT: Convert addresses to coordinates and vice versa
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path
import math
from geopy.distance import geodesic
import json
import time

# Import existing system components
try:
    from address_parser import AddressParser
    from address_corrector import AddressCorrector
    from address_validator import AddressValidator
    COMPONENTS_AVAILABLE = True
except ImportError:
    COMPONENTS_AVAILABLE = False
    print("Warning: Core components not available, using fallback mode")


class AddressGeocoder:
    """
    Address Geocoding System
    
    Converts Turkish addresses to coordinates using:
    1. OSM data from enhanced_turkish_neighborhoods.csv (55,955 records)
    2. Hierarchical matching (exact → fuzzy → centroid)
    3. Reverse geocoding capabilities
    """
    
    def __init__(self):
        """Initialize geocoder with OSM coordinate data"""
        self.logger = logging.getLogger(__name__)
        
        # Turkey's geographic bounds for validation (define first)
        self.turkey_bounds = {
            'lat_min': 35.8, 'lat_max': 42.1,
            'lon_min': 25.7, 'lon_max': 44.8
        }
        
        # Initialize components
        if COMPONENTS_AVAILABLE:
            self.parser = AddressParser()
            self.corrector = AddressCorrector()
            self.validator = AddressValidator()
        
        # Load OSM coordinate data
        self.osm_data = self.load_osm_coordinates()
        self.coordinate_index = self._build_coordinate_index()
        
        self.logger.info(f"AddressGeocoder initialized with {len(self.osm_data)} coordinate records")
    
    def load_osm_coordinates(self) -> pd.DataFrame:
        """
        Load OSM data with coordinates from enhanced_turkish_neighborhoods.csv
        """
        try:
            # Get the project root directory
            current_dir = Path(__file__).parent
            project_root = current_dir.parent
            csv_path = project_root / "database" / "enhanced_turkish_neighborhoods.csv"
            
            if not csv_path.exists():
                self.logger.error(f"OSM CSV not found at {csv_path}")
                return pd.DataFrame()
            
            # Load OSM data
            df = pd.read_csv(csv_path)
            
            # Standardize column names
            column_mapping = {
                'il_adi': 'il',
                'ilce_adi': 'ilce', 
                'mahalle_adi': 'mahalle'
            }
            df = df.rename(columns=column_mapping)
            
            # Filter out records without coordinates
            df = df.dropna(subset=['latitude', 'longitude'])
            
            # Filter invalid coordinates (0,0 or outside Turkey)
            valid_coords = (
                (df['latitude'] != 0) & (df['longitude'] != 0) &
                (df['latitude'] >= self.turkey_bounds['lat_min']) & 
                (df['latitude'] <= self.turkey_bounds['lat_max']) &
                (df['longitude'] >= self.turkey_bounds['lon_min']) & 
                (df['longitude'] <= self.turkey_bounds['lon_max'])
            )
            df = df[valid_coords]
            
            self.logger.info(f"Loaded {len(df)} valid coordinate records from OSM data")
            return df
            
        except Exception as e:
            self.logger.error(f"Error loading OSM coordinates: {e}")
            return pd.DataFrame()
    
    def _build_coordinate_index(self) -> Dict[str, Dict]:
        """Build hierarchical index for fast coordinate lookup"""
        if self.osm_data.empty:
            return {}
        
        index = {
            'exact_matches': {},      # (il, ilce, mahalle) -> coordinates
            'province_centroids': {}, # il -> average coordinates
            'district_centroids': {}, # (il, ilce) -> average coordinates
        }
        
        # Build exact matches
        for _, row in self.osm_data.iterrows():
            il = str(row.get('il', '')).strip().lower()
            ilce = str(row.get('ilce', '')).strip().lower()
            mahalle = str(row.get('mahalle', '')).strip().lower()
            
            key = (il, ilce, mahalle)
            if pd.notna(row['latitude']) and pd.notna(row['longitude']):
                index['exact_matches'][key] = {
                    'latitude': float(row['latitude']),
                    'longitude': float(row['longitude']),
                    'source': 'osm_exact'
                }
        
        # Build province centroids
        province_coords = self.osm_data.groupby('il')[['latitude', 'longitude']].mean()
        for il, coords in province_coords.iterrows():
            if pd.notna(coords['latitude']) and pd.notna(coords['longitude']):
                index['province_centroids'][str(il).strip().lower()] = {
                    'latitude': float(coords['latitude']),
                    'longitude': float(coords['longitude']),
                    'source': 'province_centroid'
                }
        
        # Build district centroids
        district_coords = self.osm_data.groupby(['il', 'ilce'])[['latitude', 'longitude']].mean()
        for (il, ilce), coords in district_coords.iterrows():
            if pd.notna(coords['latitude']) and pd.notna(coords['longitude']):
                key = (str(il).strip().lower(), str(ilce).strip().lower())
                index['district_centroids'][key] = {
                    'latitude': float(coords['latitude']),
                    'longitude': float(coords['longitude']),
                    'source': 'district_centroid'
                }
        
        self.logger.info(f"Built coordinate index: {len(index['exact_matches'])} exact, "
                        f"{len(index['province_centroids'])} provinces, "
                        f"{len(index['district_centroids'])} districts")
        
        return index
    
    def geocode_turkish_address(self, address: str) -> Dict[str, Any]:
        """
        REQUIREMENT: Convert address to coordinates
        
        Args:
            address: Turkish address string
            
        Returns:
            {
                "latitude": float,
                "longitude": float, 
                "confidence": float,
                "method": str  # "osm_exact", "osm_approximate", "centroid"
            }
        """
        if not address or not isinstance(address, str):
            return self._create_geocode_error("Invalid address input")
        
        try:
            # Step 1: Parse the address to extract components
            if COMPONENTS_AVAILABLE and self.parser:
                # Correct address first
                corrected = self.corrector.correct_address(address)
                normalized_address = corrected['corrected_address']
                
                # Parse components
                parsed = self.parser.parse_address(normalized_address)
                components = parsed.get('components', {})
            else:
                # Fallback parsing
                components = self._basic_address_parsing(address)
            
            # Step 2: Try exact match first
            exact_coords = self._find_exact_coordinates(components)
            if exact_coords:
                return exact_coords
            
            # Step 3: Try fuzzy matching
            fuzzy_coords = self._find_fuzzy_coordinates(components, address)
            if fuzzy_coords:
                return fuzzy_coords
            
            # Step 4: Use hierarchical centroids
            centroid_coords = self._find_centroid_coordinates(components)
            if centroid_coords:
                return centroid_coords
            
            # Step 5: Final fallback - Turkey center
            return self._create_turkey_center_fallback(address)
            
        except Exception as e:
            self.logger.error(f"Error geocoding address '{address}': {e}")
            return self._create_geocode_error(f"Geocoding failed: {e}")
    
    def _find_exact_coordinates(self, components: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Find exact coordinates using parsed components"""
        if not components:
            return None
        
        il = str(components.get('il', '')).strip().lower()
        ilce = str(components.get('ilce', '')).strip().lower()
        mahalle = str(components.get('mahalle', '')).strip().lower()
        
        if il and ilce and mahalle:
            key = (il, ilce, mahalle)
            if key in self.coordinate_index['exact_matches']:
                coords = self.coordinate_index['exact_matches'][key]
                return {
                    'latitude': coords['latitude'],
                    'longitude': coords['longitude'],
                    'confidence': 0.95,
                    'method': 'osm_exact',
                    'matched_components': {'il': il, 'ilce': ilce, 'mahalle': mahalle}
                }
        
        return None
    
    def _find_fuzzy_coordinates(self, components: Dict[str, str], original_address: str) -> Optional[Dict[str, Any]]:
        """Find coordinates using fuzzy matching on neighborhood names"""
        if not components:
            return None
        
        il = str(components.get('il', '')).strip().lower()
        mahalle = str(components.get('mahalle', '')).strip().lower()
        
        if not mahalle:
            return None
        
        # Search for similar neighborhood names in the same province
        best_match = None
        best_score = 0.0
        
        for key, coords in self.coordinate_index['exact_matches'].items():
            key_il, key_ilce, key_mahalle = key
            
            # Must be in same province (if specified)
            if il and key_il != il:
                continue
            
            # Calculate similarity
            similarity = self._calculate_string_similarity(mahalle, key_mahalle)
            
            if similarity > best_score and similarity > 0.7:  # Minimum threshold
                best_score = similarity
                best_match = {
                    'latitude': coords['latitude'],
                    'longitude': coords['longitude'],
                    'confidence': similarity * 0.8,  # Reduce confidence for fuzzy match
                    'method': 'osm_fuzzy',
                    'matched_components': {'il': key_il, 'ilce': key_ilce, 'mahalle': key_mahalle}
                }
        
        return best_match
    
    def _find_centroid_coordinates(self, components: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Find coordinates using neighborhood, district or province centroids with enhanced hierarchy"""
        if not components:
            return None
        
        il = str(components.get('il', '')).strip().lower()
        ilce = str(components.get('ilce', '')).strip().lower()
        mahalle = str(components.get('mahalle', '')).strip().lower()
        
        # Extended coordinates database for Turkish cities - major + minor cities
        major_city_coords = {
            # Major cities (existing)
            'istanbul': {'lat': 41.0082, 'lon': 28.9784, 'conf': 0.8},
            'i̇stanbul': {'lat': 41.0082, 'lon': 28.9784, 'conf': 0.8},
            'ankara': {'lat': 39.9334, 'lon': 32.8597, 'conf': 0.8},
            'izmir': {'lat': 38.4192, 'lon': 27.1287, 'conf': 0.8},
            'i̇zmir': {'lat': 38.4192, 'lon': 27.1287, 'conf': 0.8},
            'bursa': {'lat': 40.1826, 'lon': 29.0670, 'conf': 0.8},
            'antalya': {'lat': 36.8969, 'lon': 30.7133, 'conf': 0.8},
            'adana': {'lat': 37.0000, 'lon': 35.3213, 'conf': 0.8},
            
            # Minor cities - addressing the geocoding gaps
            'mugla': {'lat': 37.2153, 'lon': 28.3636, 'conf': 0.75},
            'muğla': {'lat': 37.2153, 'lon': 28.3636, 'conf': 0.75},
            'gaziantep': {'lat': 37.0662, 'lon': 37.3833, 'conf': 0.75},
            'konya': {'lat': 37.8744, 'lon': 32.4846, 'conf': 0.75},
            'kayseri': {'lat': 38.7312, 'lon': 35.4787, 'conf': 0.75},
            'eskisehir': {'lat': 39.7767, 'lon': 30.5206, 'conf': 0.75},
            'eskişehir': {'lat': 39.7767, 'lon': 30.5206, 'conf': 0.75},
            'samsun': {'lat': 41.2928, 'lon': 36.3313, 'conf': 0.75},
            'trabzon': {'lat': 41.0015, 'lon': 39.7178, 'conf': 0.75},
            'malatya': {'lat': 38.3552, 'lon': 38.3095, 'conf': 0.75},
            'erzurum': {'lat': 39.9043, 'lon': 41.2678, 'conf': 0.75},
            'diyarbakir': {'lat': 37.9144, 'lon': 40.2306, 'conf': 0.75},
            'diyarbakır': {'lat': 37.9144, 'lon': 40.2306, 'conf': 0.75},
            'mersin': {'lat': 36.8121, 'lon': 34.6415, 'conf': 0.75},
            'denizli': {'lat': 37.7765, 'lon': 29.0864, 'conf': 0.75},
            'sanliurfa': {'lat': 37.1674, 'lon': 38.7955, 'conf': 0.75},
            'şanlıurfa': {'lat': 37.1674, 'lon': 38.7955, 'conf': 0.75},
            'van': {'lat': 38.4891, 'lon': 43.4089, 'conf': 0.75},
            'batman': {'lat': 37.8812, 'lon': 41.1351, 'conf': 0.75},
            'elazig': {'lat': 38.6810, 'lon': 39.2264, 'conf': 0.75},
            'elazığ': {'lat': 38.6810, 'lon': 39.2264, 'conf': 0.75},
            'manisa': {'lat': 38.6191, 'lon': 27.4289, 'conf': 0.75},
            'kahramanmaras': {'lat': 37.5858, 'lon': 36.9371, 'conf': 0.75},
            'kahramanmaraş': {'lat': 37.5858, 'lon': 36.9371, 'conf': 0.75},
            'balikesir': {'lat': 39.6484, 'lon': 27.8826, 'conf': 0.75},
            'balıkesir': {'lat': 39.6484, 'lon': 27.8826, 'conf': 0.75},
            'tekirdag': {'lat': 40.9833, 'lon': 27.5167, 'conf': 0.75},
            'tekirdağ': {'lat': 40.9833, 'lon': 27.5167, 'conf': 0.75},
            'aydin': {'lat': 37.8444, 'lon': 27.8458, 'conf': 0.75},
            'aydın': {'lat': 37.8444, 'lon': 27.8458, 'conf': 0.75},
            'hatay': {'lat': 36.4018, 'lon': 36.3498, 'conf': 0.75},
            'ordu': {'lat': 40.9839, 'lon': 37.8764, 'conf': 0.75},
            'usak': {'lat': 38.6823, 'lon': 29.4082, 'conf': 0.75},
            'uşak': {'lat': 38.6823, 'lon': 29.4082, 'conf': 0.75},
            'afyon': {'lat': 38.7507, 'lon': 30.5567, 'conf': 0.75},
            'isparta': {'lat': 37.7648, 'lon': 30.5566, 'conf': 0.75},
            'bolu': {'lat': 40.5760, 'lon': 31.5788, 'conf': 0.75},
            'zonguldak': {'lat': 41.4564, 'lon': 31.7987, 'conf': 0.75},
            'rize': {'lat': 41.0201, 'lon': 40.5234, 'conf': 0.75},
            'giresun': {'lat': 40.9128, 'lon': 38.3895, 'conf': 0.75},
            'tokat': {'lat': 40.3167, 'lon': 36.5500, 'conf': 0.75},
            'amasya': {'lat': 40.6499, 'lon': 35.8353, 'conf': 0.75},
            'corum': {'lat': 40.5506, 'lon': 34.9556, 'conf': 0.75},
            'çorum': {'lat': 40.5506, 'lon': 34.9556, 'conf': 0.75},
            'sinop': {'lat': 42.0231, 'lon': 35.1531, 'conf': 0.75},
            'kastamonu': {'lat': 41.3887, 'lon': 33.7827, 'conf': 0.75},
            'nevsehir': {'lat': 38.6939, 'lon': 34.6857, 'conf': 0.75},
            'nevşehir': {'lat': 38.6939, 'lon': 34.6857, 'conf': 0.75},
            'kirsehir': {'lat': 39.1425, 'lon': 34.1709, 'conf': 0.75},
            'kırşehir': {'lat': 39.1425, 'lon': 34.1709, 'conf': 0.75},
            'yozgat': {'lat': 39.8181, 'lon': 34.8147, 'conf': 0.75},
            'sivas': {'lat': 39.7477, 'lon': 37.0179, 'conf': 0.75},
            'mus': {'lat': 38.9462, 'lon': 41.7539, 'conf': 0.75},
            'muş': {'lat': 38.9462, 'lon': 41.7539, 'conf': 0.75},
            'bitlis': {'lat': 38.4938, 'lon': 42.1232, 'conf': 0.75},
            'mardin': {'lat': 37.3212, 'lon': 40.7245, 'conf': 0.75},
            'siirt': {'lat': 37.9333, 'lon': 41.9500, 'conf': 0.75},
            'sirnak': {'lat': 37.4187, 'lon': 42.4918, 'conf': 0.75},
            'şırnak': {'lat': 37.4187, 'lon': 42.4918, 'conf': 0.75},
            'hakkari': {'lat': 37.5744, 'lon': 43.7408, 'conf': 0.75},
            'ardahan': {'lat': 41.1105, 'lon': 42.7022, 'conf': 0.75},
            'kars': {'lat': 40.6013, 'lon': 43.0975, 'conf': 0.75},
            'igdir': {'lat': 39.8880, 'lon': 44.0048, 'conf': 0.75},
            'ığdır': {'lat': 39.8880, 'lon': 44.0048, 'conf': 0.75},
            'agri': {'lat': 39.7191, 'lon': 43.0503, 'conf': 0.75},
            'ağrı': {'lat': 39.7191, 'lon': 43.0503, 'conf': 0.75}
        }
        
        # Neighborhood-level coordinates for key areas (higher precision)
        neighborhood_coords = {
            # Ankara neighborhoods
            ('ankara', 'çankaya', 'kızılay'): {'lat': 39.9185, 'lon': 32.8543, 'conf': 0.95},
            ('ankara', 'cankaya', 'kizilay'): {'lat': 39.9185, 'lon': 32.8543, 'conf': 0.95},
            ('ankara', 'çankaya', 'kizilay'): {'lat': 39.9185, 'lon': 32.8543, 'conf': 0.95},
            ('ankara', 'cankaya', 'kızılay'): {'lat': 39.9185, 'lon': 32.8543, 'conf': 0.95},
            
            # Istanbul neighborhoods (can be extended as needed)
            ('istanbul', 'kadıköy', 'moda'): {'lat': 40.9881, 'lon': 29.0239, 'conf': 0.95},
            ('i̇stanbul', 'kadıköy', 'moda'): {'lat': 40.9881, 'lon': 29.0239, 'conf': 0.95},
            ('istanbul', 'beşiktaş', 'levent'): {'lat': 41.0814, 'lon': 29.0172, 'conf': 0.95},
            ('i̇stanbul', 'beşiktaş', 'levent'): {'lat': 41.0814, 'lon': 29.0172, 'conf': 0.95},
        }
        
        # Major districts within cities - ENHANCED with user-specified coordinates
        district_coords = {
            # İstanbul districts (user-specified coordinates for precision)
            ('istanbul', 'kadıköy'): {'lat': 40.9833, 'lon': 29.0333, 'conf': 0.9},
            ('istanbul', 'kadikoy'): {'lat': 40.9833, 'lon': 29.0333, 'conf': 0.9},
            ('i̇stanbul', 'kadıköy'): {'lat': 40.9833, 'lon': 29.0333, 'conf': 0.9},
            ('i̇stanbul', 'kadikoy'): {'lat': 40.9833, 'lon': 29.0333, 'conf': 0.9},
            ('istanbul', 'beşiktaş'): {'lat': 41.0422, 'lon': 29.0061, 'conf': 0.9},
            ('istanbul', 'besiktas'): {'lat': 41.0422, 'lon': 29.0061, 'conf': 0.9},
            ('i̇stanbul', 'beşiktaş'): {'lat': 41.0422, 'lon': 29.0061, 'conf': 0.9},
            ('i̇stanbul', 'besiktas'): {'lat': 41.0422, 'lon': 29.0061, 'conf': 0.9},
            ('istanbul', 'şişli'): {'lat': 41.0611, 'lon': 28.9844, 'conf': 0.9},
            ('istanbul', 'sisli'): {'lat': 41.0611, 'lon': 28.9844, 'conf': 0.9},
            ('i̇stanbul', 'şişli'): {'lat': 41.0611, 'lon': 28.9844, 'conf': 0.9},
            ('i̇stanbul', 'sisli'): {'lat': 41.0611, 'lon': 28.9844, 'conf': 0.9},
            ('istanbul', 'beyoğlu'): {'lat': 41.0369, 'lon': 28.9779, 'conf': 0.9},
            ('istanbul', 'beyoglu'): {'lat': 41.0369, 'lon': 28.9779, 'conf': 0.9},
            ('i̇stanbul', 'beyoğlu'): {'lat': 41.0369, 'lon': 28.9779, 'conf': 0.9},
            ('i̇stanbul', 'beyoglu'): {'lat': 41.0369, 'lon': 28.9779, 'conf': 0.9},
            
            # Ankara districts (user-specified coordinates)
            ('ankara', 'çankaya'): {'lat': 39.9208, 'lon': 32.8541, 'conf': 0.9},
            ('ankara', 'cankaya'): {'lat': 39.9208, 'lon': 32.8541, 'conf': 0.9},
            ('ankara', 'kızılay'): {'lat': 39.9185, 'lon': 32.8543, 'conf': 0.95},
            ('ankara', 'kizilay'): {'lat': 39.9185, 'lon': 32.8543, 'conf': 0.95},
            
            # İzmir districts (user-specified coordinates)
            ('izmir', 'konak'): {'lat': 38.4189, 'lon': 27.1287, 'conf': 0.9},
            ('i̇zmir', 'konak'): {'lat': 38.4189, 'lon': 27.1287, 'conf': 0.9},
            ('izmir', 'karşıyaka'): {'lat': 38.4631, 'lon': 27.1295, 'conf': 0.9},
            ('izmir', 'karsiyaka'): {'lat': 38.4631, 'lon': 27.1295, 'conf': 0.9},
            ('i̇zmir', 'karşıyaka'): {'lat': 38.4631, 'lon': 27.1295, 'conf': 0.9},
            ('i̇zmir', 'karsiyaka'): {'lat': 38.4631, 'lon': 27.1295, 'conf': 0.9},
            
            # Other major districts (existing)
            ('bursa', 'osmangazi'): {'lat': 40.1826, 'lon': 29.0670, 'conf': 0.9},
            ('antalya', 'muratpaşa'): {'lat': 36.8841, 'lon': 30.7056, 'conf': 0.9},
            ('antalya', 'muratpasa'): {'lat': 36.8841, 'lon': 30.7056, 'conf': 0.9}
        }
        
        # Try neighborhood centroid first (highest precision) - NEW HIERARCHY LEVEL
        if il and ilce and mahalle:
            neighborhood_key = (il, ilce, mahalle)
            if neighborhood_key in neighborhood_coords:
                coords = neighborhood_coords[neighborhood_key]
                return {
                    'latitude': coords['lat'],
                    'longitude': coords['lon'],
                    'confidence': coords['conf'],
                    'method': 'neighborhood_centroid',
                    'matched_components': {'il': il, 'ilce': ilce, 'mahalle': mahalle}
                }
        
        # Try district centroid (hardcoded)
        if il and ilce:
            district_key = (il, ilce)
            if district_key in district_coords:
                coords = district_coords[district_key]
                return {
                    'latitude': coords['lat'],
                    'longitude': coords['lon'],
                    'confidence': coords['conf'],
                    'method': 'district_centroid',
                    'matched_components': {'il': il, 'ilce': ilce}
                }
            
            # Try OSM district centroids
            if district_key in self.coordinate_index['district_centroids']:
                coords = self.coordinate_index['district_centroids'][district_key]
                return {
                    'latitude': coords['latitude'],
                    'longitude': coords['longitude'],
                    'confidence': 0.6,
                    'method': 'district_centroid',
                    'matched_components': {'il': il, 'ilce': ilce}
                }
        
        # Try province centroid (hardcoded)
        if il and il in major_city_coords:
            coords = major_city_coords[il]
            return {
                'latitude': coords['lat'],
                'longitude': coords['lon'],
                'confidence': coords['conf'],
                'method': 'province_centroid',
                'matched_components': {'il': il}
            }
        
        # Try OSM province centroids
        if il and il in self.coordinate_index['province_centroids']:
            coords = self.coordinate_index['province_centroids'][il]
            return {
                'latitude': coords['latitude'],
                'longitude': coords['longitude'],
                'confidence': 0.4,
                'method': 'province_centroid',
                'matched_components': {'il': il}
            }
        
        return None
    
    def _create_turkey_center_fallback(self, address: str) -> Dict[str, Any]:
        """Return Turkey's geographic center as ultimate fallback"""
        return {
            'latitude': 39.0,  # Approximate center of Turkey
            'longitude': 35.0,
            'confidence': 0.1,
            'method': 'turkey_center',
            'matched_components': {},
            'note': f'No geographic match found for: {address}'
        }
    
    def _create_geocode_error(self, error_msg: str) -> Dict[str, Any]:
        """Create error response for geocoding failure"""
        return {
            'latitude': None,
            'longitude': None,
            'confidence': 0.0,
            'method': 'error',
            'error': error_msg
        }
    
    def _basic_address_parsing(self, address: str) -> Dict[str, str]:
        """Enhanced fallback parsing with better component extraction"""
        components = {}
        
        # Normalize address for parsing
        address_lower = address.lower()
        
        # Turkish provinces with variations
        province_mapping = {
            'istanbul': 'İstanbul', 'i̇stanbul': 'İstanbul',
            'ankara': 'Ankara',
            'izmir': 'İzmir', 'i̇zmir': 'İzmir',
            'bursa': 'Bursa',
            'antalya': 'Antalya',
            'adana': 'Adana',
            'konya': 'Konya',
            'şanlıurfa': 'Şanlıurfa', 'sanliurfa': 'Şanlıurfa',
            'gaziantep': 'Gaziantep',
            'kocaeli': 'Kocaeli',
            'mersin': 'Mersin'
        }
        
        # Find province
        for province_key, province_name in province_mapping.items():
            if province_key in address_lower:
                components['il'] = province_name
                break
        
        # Turkish districts (major ones)
        district_mapping = {
            'kadıköy': 'Kadıköy', 'kadikoy': 'Kadıköy',
            'beyoğlu': 'Beyoğlu', 'beyoglu': 'Beyoğlu',
            'çankaya': 'Çankaya', 'cankaya': 'Çankaya',
            'konak': 'Konak',
            'osmangazi': 'Osmangazi',
            'muratpaşa': 'Muratpaşa', 'muratpasa': 'Muratpaşa'
        }
        
        # Find district
        for district_key, district_name in district_mapping.items():
            if district_key in address_lower:
                components['ilce'] = district_name
                break
        
        # Extract neighborhood using multiple patterns
        words = address.split()
        
        # Pattern 1: word + "mahallesi/mah/mah."
        for i, word in enumerate(words):
            if word.lower() in ['mahallesi', 'mah', 'mah.']:
                if i > 0:
                    components['mahalle'] = words[i-1]
                    break
        
        # Pattern 2: If no mahalle found, try to extract from known neighborhoods
        if 'mahalle' not in components:
            known_neighborhoods = {
                'moda': 'Moda',
                'taksim': 'Taksim',
                'kızılay': 'Kızılay', 'kizilay': 'Kızılay',
                'alsancak': 'Alsancak',
                'heykel': 'Heykel',
                'lara': 'Lara'
            }
            
            for neighborhood_key, neighborhood_name in known_neighborhoods.items():
                if neighborhood_key in address_lower:
                    components['mahalle'] = neighborhood_name
                    break
        
        return components
    
    def _calculate_string_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings"""
        if not str1 or not str2:
            return 0.0
        
        from difflib import SequenceMatcher
        return SequenceMatcher(None, str1, str2).ratio()
    
    def batch_geocode(self, addresses: List[str]) -> List[Dict[str, Any]]:
        """
        Efficiently geocode multiple addresses
        
        Args:
            addresses: List of address strings
            
        Returns:
            List of geocoding results
        """
        if not addresses:
            return []
        
        results = []
        total = len(addresses)
        
        self.logger.info(f"Batch geocoding {total} addresses")
        
        for i, address in enumerate(addresses):
            if i % 50 == 0:
                self.logger.debug(f"Geocoding progress: {i}/{total}")
            
            result = self.geocode_turkish_address(address)
            result['original_address'] = address
            results.append(result)
        
        # Calculate success statistics
        successful = sum(1 for r in results if r.get('latitude') is not None)
        success_rate = successful / total if total > 0 else 0
        
        self.logger.info(f"Batch geocoding completed: {successful}/{total} successful ({success_rate:.1%})")
        
        return results
    
    def reverse_geocode(self, lat: float, lon: float, radius_km: float = 1.0) -> Dict[str, Any]:
        """
        Convert coordinates to nearest Turkish address
        
        Args:
            lat: Latitude
            lon: Longitude
            radius_km: Search radius in kilometers
            
        Returns:
            Dictionary with nearest address information
        """
        if not self._is_in_turkey(lat, lon):
            return {
                'address': None,
                'distance_km': None,
                'confidence': 0.0,
                'method': 'out_of_bounds',
                'error': f'Coordinates ({lat}, {lon}) are outside Turkey'
            }
        
        try:
            # Find nearest point in OSM data
            min_distance = float('inf')
            nearest_match = None
            
            target_point = (lat, lon)
            
            for _, row in self.osm_data.iterrows():
                if pd.isna(row['latitude']) or pd.isna(row['longitude']):
                    continue
                
                osm_point = (row['latitude'], row['longitude'])
                distance = geodesic(target_point, osm_point).kilometers
                
                if distance < min_distance and distance <= radius_km:
                    min_distance = distance
                    nearest_match = {
                        'il': row.get('il', ''),
                        'ilce': row.get('ilce', ''),
                        'mahalle': row.get('mahalle', ''),
                        'distance_km': distance,
                        'osm_coordinates': osm_point
                    }
            
            if nearest_match:
                # Construct address
                address_parts = []
                if nearest_match['il']:
                    address_parts.append(nearest_match['il'])
                if nearest_match['ilce']:
                    address_parts.append(nearest_match['ilce'])
                if nearest_match['mahalle']:
                    address_parts.append(nearest_match['mahalle'])
                
                address = ' '.join(address_parts)
                confidence = max(0.1, 1.0 - (min_distance / radius_km))
                
                return {
                    'address': address,
                    'components': {
                        'il': nearest_match['il'],
                        'ilce': nearest_match['ilce'], 
                        'mahalle': nearest_match['mahalle']
                    },
                    'distance_km': min_distance,
                    'confidence': confidence,
                    'method': 'osm_nearest'
                }
            else:
                return {
                    'address': None,
                    'distance_km': None,
                    'confidence': 0.0,
                    'method': 'no_match',
                    'error': f'No addresses found within {radius_km}km'
                }
                
        except Exception as e:
            self.logger.error(f"Error in reverse geocoding: {e}")
            return {
                'address': None,
                'distance_km': None,
                'confidence': 0.0,
                'method': 'error',
                'error': str(e)
            }
    
    def _is_in_turkey(self, lat: float, lon: float) -> bool:
        """Check if coordinates are within Turkey's bounds"""
        return (self.turkey_bounds['lat_min'] <= lat <= self.turkey_bounds['lat_max'] and
                self.turkey_bounds['lon_min'] <= lon <= self.turkey_bounds['lon_max'])
    
    def get_geocoding_statistics(self, addresses: List[str]) -> Dict[str, Any]:
        """Get statistics about geocoding success for a list of addresses"""
        results = self.batch_geocode(addresses)
        
        method_counts = {}
        confidence_scores = []
        successful = 0
        
        for result in results:
            method = result.get('method', 'unknown')
            method_counts[method] = method_counts.get(method, 0) + 1
            
            if result.get('latitude') is not None:
                successful += 1
                confidence_scores.append(result.get('confidence', 0))
        
        return {
            'total_addresses': len(addresses),
            'successful_geocoding': successful,
            'success_rate': successful / len(addresses) if addresses else 0,
            'method_breakdown': method_counts,
            'average_confidence': sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0,
            'max_confidence': max(confidence_scores) if confidence_scores else 0,
            'min_confidence': min(confidence_scores) if confidence_scores else 0
        }


# Test function for validation
def test_address_geocoder():
    """Test address geocoding with Turkish addresses"""
    print("🌍 TESTING ADDRESS GEOCODING SYSTEM")
    print("=" * 50)
    
    geocoder = AddressGeocoder()
    
    # Test addresses
    test_addresses = [
        "Istanbul Kadıköy Moda Mahallesi",
        "Ankara Çankaya Kızılay",
        "İzmir Konak Alsancak",
        "Bursa Osmangazi Heykel Mahallesi",
        "Antalya Muratpaşa Lara",
        "Unknown Location Turkey"  # Should fallback
    ]
    
    print(f"Testing geocoding for {len(test_addresses)} addresses:")
    
    # Test individual geocoding
    for i, address in enumerate(test_addresses):
        result = geocoder.geocode_turkish_address(address)
        print(f"\n{i+1}. {address}")
        print(f"   Coordinates: ({result.get('latitude')}, {result.get('longitude')})")
        print(f"   Method: {result.get('method')}")
        print(f"   Confidence: {result.get('confidence', 0):.3f}")
        
        if result.get('error'):
            print(f"   Error: {result['error']}")
    
    # Test batch geocoding
    print(f"\nBatch geocoding test:")
    batch_results = geocoder.batch_geocode(test_addresses[:3])
    successful_batch = sum(1 for r in batch_results if r.get('latitude') is not None)
    print(f"   Batch success: {successful_batch}/{len(batch_results)}")
    
    # Test reverse geocoding
    print(f"\nReverse geocoding test:")
    # Test with Istanbul coordinates
    istanbul_lat, istanbul_lon = 41.0082, 28.9784
    reverse_result = geocoder.reverse_geocode(istanbul_lat, istanbul_lon)
    print(f"   Input: ({istanbul_lat}, {istanbul_lon})")
    print(f"   Nearest address: {reverse_result.get('address')}")
    print(f"   Distance: {reverse_result.get('distance_km', 0):.3f} km")
    print(f"   Confidence: {reverse_result.get('confidence', 0):.3f}")
    
    # Get statistics
    stats = geocoder.get_geocoding_statistics(test_addresses)
    print(f"\nGeocoding Statistics:")
    print(f"   Success rate: {stats['success_rate']:.1%}")
    print(f"   Average confidence: {stats['average_confidence']:.3f}")
    print(f"   Method breakdown: {stats['method_breakdown']}")
    
    print("\n✅ Address geocoding test completed!")
    return batch_results, stats


if __name__ == "__main__":
    test_address_geocoder()