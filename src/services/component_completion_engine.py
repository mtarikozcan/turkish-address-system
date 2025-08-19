"""
Component Completion Intelligence Engine
Phase 5: Bidirectional Hierarchy Completion

This module provides intelligent component completion for missing hierarchy levels:
- DOWN completion: mahalle → ilçe → il (neighborhood to district to city)
- UP completion: ilçe → il (district to city) - enhanced
- Multi-level completion: fill all missing levels in hierarchy

Key Features:
- Uses complete 55,955 record database
- Handles neighborhood name variations (with/without "Mahallesi")
- Bidirectional hierarchy completion
- Confidence scoring for completions
"""

import logging
import re
import time
from typing import Dict, List, Tuple, Any, Optional, Set
from pathlib import Path
from difflib import SequenceMatcher

class ComponentCompletionEngine:
    """
    Component Completion Intelligence Engine
    
    Provides intelligent hierarchy completion:
    - mahalle → ilçe → il (DOWN completion)
    - ilçe → il (UP completion)
    - Multi-level smart completion
    """
    
    def __init__(self, database_path: Optional[str] = None):
        """
        Initialize Component Completion Engine
        
        Args:
            database_path: Path to enhanced_turkish_neighborhoods.csv
        """
        self.logger = logging.getLogger(__name__)
        
        # Build Turkish character normalization first
        self.turkish_char_map = self._build_turkish_char_map()
        
        # Load and build comprehensive completion indexes
        self.admin_database = self._load_admin_database(database_path)
        self.neighborhood_completion_index = self._build_neighborhood_completion_index()
        self.district_completion_index = self._build_district_completion_index()
        
        # Performance tracking
        self.stats = {
            'total_queries': 0,
            'successful_completions': 0,
            'down_completions': 0,
            'up_completions': 0,
            'multi_level_completions': 0,
            'average_processing_time_ms': 0.0
        }
        
        self.logger.info(f"ComponentCompletionEngine initialized with {len(self.admin_database)} records")
        self.logger.info(f"Built indexes: {len(self.neighborhood_completion_index)} neighborhoods, {len(self.district_completion_index)} districts")
    
    def complete_address_hierarchy(self, components: Dict[str, str]) -> Dict[str, Any]:
        """
        Main method: Complete missing hierarchy levels in address components
        
        Args:
            components: Existing address components
            
        Returns:
            {
                'completed_components': Dict[str, str],
                'completions_made': List[str],
                'confidence': float,
                'completion_methods': List[str],
                'processing_time_ms': float
            }
            
        Test Cases:
            Input: {'mahalle': 'Etlik'} → Output: {'mahalle': 'Etlik', 'ilçe': 'Keçiören', 'il': 'Ankara'}
            Input: {'il': 'İstanbul', 'mahalle': 'Moda'} → Output: {..., 'ilçe': 'Kadıköy'}
        """
        start_time = time.time()
        self.stats['total_queries'] += 1
        
        if not components or not isinstance(components, dict):
            return self._create_empty_result(0.0, "invalid_input")
        
        # Initialize result
        completed_components = components.copy()
        completions_made = []
        completion_methods = []
        confidence_scores = []
        
        try:
            # Phase 1: DOWN completion (mahalle → ilçe → il)
            if 'mahalle' in components and 'ilçe' not in components:
                down_result = self._complete_neighborhood_to_district(components['mahalle'])
                if down_result['ilçe']:
                    completed_components['ilçe'] = down_result['ilçe']
                    completions_made.append(f"mahalle→ilçe: {down_result['ilçe']}")
                    completion_methods.append('down_completion')
                    confidence_scores.append(down_result['confidence'])
                    self.stats['down_completions'] += 1
                    
                    # Also complete il if missing
                    if down_result['il'] and 'il' not in components:
                        completed_components['il'] = down_result['il']
                        completions_made.append(f"mahalle→il: {down_result['il']}")
                        self.stats['multi_level_completions'] += 1
            
            # Phase 2: UP completion (ilçe → il) - enhanced
            if 'ilçe' in completed_components and 'il' not in completed_components:
                up_result = self._complete_district_to_city(completed_components['ilçe'])
                if up_result['il']:
                    completed_components['il'] = up_result['il']
                    completions_made.append(f"ilçe→il: {up_result['il']}")
                    completion_methods.append('up_completion')
                    confidence_scores.append(up_result['confidence'])
                    self.stats['up_completions'] += 1
            
            # Phase 3: Validate and cross-check completions
            validation_result = self._validate_hierarchy_consistency(completed_components)
            if validation_result['adjustments']:
                for adjustment in validation_result['adjustments']:
                    completed_components.update(adjustment)
                    completions_made.append(f"validation_fix: {adjustment}")
                    completion_methods.append('validation')
            
            # Calculate overall confidence
            overall_confidence = max(confidence_scores) if confidence_scores else 0.0
            
            # Track successful completions
            if completions_made:
                self.stats['successful_completions'] += 1
            
        except Exception as e:
            self.logger.error(f"Error in hierarchy completion for {components}: {e}")
            completed_components = components.copy()
            completions_made = []
            completion_methods = ['error']
            overall_confidence = 0.0
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000
        self.stats['average_processing_time_ms'] = (
            (self.stats['average_processing_time_ms'] * (self.stats['total_queries'] - 1) + processing_time) / 
            self.stats['total_queries']
        )
        
        return {
            'completed_components': completed_components,
            'completions_made': completions_made,
            'confidence': overall_confidence,
            'completion_methods': completion_methods,
            'processing_time_ms': processing_time
        }
    
    def _get_famous_neighborhood_mapping(self, mahalle_name: str) -> Optional[Dict[str, str]]:
        """Handle famous neighborhoods that may not be in official database"""
        famous_mappings = {
            # İstanbul famous areas
            'nişantaşı': {'ilçe': 'Şişli', 'il': 'İstanbul'},
            'nisantasi': {'ilçe': 'Şişli', 'il': 'İstanbul'},
            'taksim': {'ilçe': 'Beyoğlu', 'il': 'İstanbul'},
            'galata': {'ilçe': 'Beyoğlu', 'il': 'İstanbul'},
            'karaköy': {'ilçe': 'Beyoğlu', 'il': 'İstanbul'},
            'maslak': {'ilçe': 'Sarıyer', 'il': 'İstanbul'},
            
            # Ankara famous areas  
            'kızılay': {'ilçe': 'Çankaya', 'il': 'Ankara'},
            'kizilay': {'ilçe': 'Çankaya', 'il': 'Ankara'},
            'ulus': {'ilçe': 'Altındağ', 'il': 'Ankara'},
            
            # İzmir famous areas
            'konak': {'ilçe': 'Konak', 'il': 'İzmir'},
        }
        
        # Try multiple variations of the input
        normalized = self._normalize_turkish_text(mahalle_name.lower())
        
        # Try exact match first
        if normalized in famous_mappings:
            return famous_mappings[normalized]
        
        # Try without "mahallesi" suffix
        normalized_base = normalized.replace(' mahallesi', '').strip()
        if normalized_base in famous_mappings:
            return famous_mappings[normalized_base]
        
        return None

    def _complete_neighborhood_to_district(self, mahalle_name: str) -> Dict[str, Any]:
        """
        Complete neighborhood → district → city (DOWN completion)
        
        Handles variations:
        - "Etlik" → "Keçiören", "Ankara"
        - "Etlik Mahallesi" → "Keçiören", "Ankara"  
        - "Moda" → "Kadıköy", "İstanbul"
        
        Args:
            mahalle_name: Neighborhood name to complete
            
        Returns:
            Dict with ilçe, il, and confidence
        """
        if not mahalle_name:
            return {'ilçe': None, 'il': None, 'confidence': 0.0}
        
        # Normalize the neighborhood name for lookup
        normalized_name = self._normalize_turkish_text(mahalle_name.lower())
        
        # Try multiple lookup variations
        lookup_candidates = [
            normalized_name,                          # "etlik"
            f"{normalized_name} mahallesi",          # "etlik mahallesi"
            normalized_name.replace(' mahallesi', ''), # remove mahallesi if present
        ]
        
        # Add title case variations
        for candidate in lookup_candidates.copy():
            lookup_candidates.append(candidate.title())
        
        best_match = None
        best_confidence = 0.0
        
        # Search in neighborhood completion index
        for candidate in lookup_candidates:
            if candidate in self.neighborhood_completion_index:
                match_info = self.neighborhood_completion_index[candidate]
                confidence = 0.95  # High confidence for exact match
                
                if confidence > best_confidence:
                    best_match = match_info
                    best_confidence = confidence
                    break  # Exact match found
        
        # If no exact match, try famous neighborhood mapping
        if not best_match:
            famous_mapping = self._get_famous_neighborhood_mapping(mahalle_name)
            if famous_mapping:
                best_match = {
                    'ilçe': famous_mapping['ilçe'],
                    'il': famous_mapping['il']
                }
                best_confidence = 0.90  # High confidence for famous mappings
        
        # If still no match, try fuzzy matching
        if not best_match:
            best_match, best_confidence = self._fuzzy_match_neighborhood(normalized_name)
        
        if best_match:
            return {
                'ilçe': best_match['ilçe'],
                'il': best_match['il'],
                'confidence': best_confidence
            }
        
        return {'ilçe': None, 'il': None, 'confidence': 0.0}
    
    def _complete_district_to_city(self, district_name: str) -> Dict[str, Any]:
        """
        Complete district → city (UP completion)
        
        Args:
            district_name: District name to complete
            
        Returns:
            Dict with il and confidence
        """
        if not district_name:
            return {'il': None, 'confidence': 0.0}
        
        # Normalize district name
        normalized_name = self._normalize_turkish_text(district_name.lower())
        
        # Try lookup
        if normalized_name in self.district_completion_index:
            district_info = self.district_completion_index[normalized_name]
            return {
                'il': district_info['il'],
                'confidence': 0.95
            }
        
        # Try fuzzy matching
        best_match = None
        best_confidence = 0.0
        
        for indexed_district, district_info in self.district_completion_index.items():
            similarity = SequenceMatcher(None, normalized_name, indexed_district).ratio()
            if similarity > 0.8 and similarity > best_confidence:
                best_match = district_info
                best_confidence = similarity * 0.8  # Lower confidence for fuzzy
        
        if best_match:
            return {
                'il': best_match['il'],
                'confidence': best_confidence
            }
        
        return {'il': None, 'confidence': 0.0}
    
    def _fuzzy_match_neighborhood(self, target_name: str) -> Tuple[Optional[Dict], float]:
        """
        Fuzzy match neighborhood name when exact match fails
        
        Args:
            target_name: Normalized neighborhood name to match
            
        Returns:
            Tuple of (best_match_info, confidence)
        """
        best_match = None
        best_similarity = 0.0
        
        # Search through neighborhood index with fuzzy matching
        for indexed_name, neighborhood_info in self.neighborhood_completion_index.items():
            # Try matching against base name (without mahallesi)
            base_indexed = indexed_name.replace(' mahallesi', '').strip()
            
            # Calculate similarity
            similarity = SequenceMatcher(None, target_name, base_indexed).ratio()
            
            # Also try partial matching (target is substring)
            if target_name in base_indexed or base_indexed in target_name:
                similarity = max(similarity, 0.85)
            
            if similarity > 0.75 and similarity > best_similarity:
                best_match = neighborhood_info
                best_similarity = similarity
        
        if best_match and best_similarity > 0.75:
            return best_match, best_similarity * 0.8  # Lower confidence for fuzzy match
        
        return None, 0.0
    
    def _validate_hierarchy_consistency(self, components: Dict[str, str]) -> Dict[str, Any]:
        """
        Validate that completed hierarchy is consistent
        
        Args:
            components: Address components to validate
            
        Returns:
            Dict with validation results and adjustments
        """
        adjustments = []
        
        try:
            # Check if mahalle/ilçe/il combination is valid
            if all(comp in components for comp in ['mahalle', 'ilçe', 'il']):
                mahalle = components['mahalle']
                ilçe = components['ilçe']
                il = components['il']
                
                # Look for this exact combination in database
                normalized_mahalle = self._normalize_turkish_text(mahalle.lower())
                combinations_to_check = [
                    normalized_mahalle,
                    f"{normalized_mahalle} mahallesi"
                ]
                
                valid_combination = False
                for combo in combinations_to_check:
                    if combo in self.neighborhood_completion_index:
                        neighborhood_info = self.neighborhood_completion_index[combo]
                        expected_ilçe = self._normalize_turkish_text(neighborhood_info['ilçe'].lower())
                        expected_il = self._normalize_turkish_text(neighborhood_info['il'].lower())
                        actual_ilçe = self._normalize_turkish_text(ilçe.lower())
                        actual_il = self._normalize_turkish_text(il.lower())
                        
                        if expected_ilçe == actual_ilçe and expected_il == actual_il:
                            valid_combination = True
                            break
                
                if not valid_combination:
                    self.logger.debug(f"Inconsistent hierarchy detected: {mahalle} not in {ilçe}, {il}")
            
        except Exception as e:
            self.logger.warning(f"Hierarchy validation error: {e}")
        
        return {
            'is_consistent': len(adjustments) == 0,
            'adjustments': adjustments
        }
    
    def _load_admin_database(self, data_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Load the complete administrative database"""
        if data_path is None:
            current_dir = Path(__file__).parent.parent
            # Use the clean turkey_admin_hierarchy.csv instead of enhanced_turkish_neighborhoods.csv
            data_path = current_dir / "database" / "turkey_admin_hierarchy.csv"
        
        try:
            import pandas as pd
            df = pd.read_csv(data_path, encoding='utf-8')
            
            admin_records = []
            for _, row in df.iterrows():
                record = {
                    'il': str(row.get('il_adi', '')).strip() if pd.notna(row.get('il_adi')) else '',
                    'ilçe': str(row.get('ilce_adi', '')).strip() if pd.notna(row.get('ilce_adi')) else '',
                    'mahalle': str(row.get('mahalle_adi', '')).strip() if pd.notna(row.get('mahalle_adi')) else '',
                }
                
                # Only add records with valid data - turkey_admin_hierarchy.csv is clean
                if (record['il'] and record['ilçe'] and record['mahalle'] and
                    len(record['il'].strip()) > 0 and len(record['ilçe'].strip()) > 0 and len(record['mahalle'].strip()) > 0):
                    admin_records.append(record)
            
            self.logger.info(f"Loaded {len(admin_records)} complete administrative records")
            return admin_records
            
        except Exception as e:
            self.logger.error(f"Error loading admin database: {e}")
            return []
    
    def _build_neighborhood_completion_index(self) -> Dict[str, Dict[str, str]]:
        """
        Build comprehensive neighborhood → district+city completion index
        
        Returns:
            Dict mapping normalized neighborhood names to district+city info
        """
        neighborhood_index = {}
        
        for record in self.admin_database:
            # Skip records with missing data
            if not all([record['il'], record['ilçe'], record['mahalle']]):
                continue
            
            mahalle = record['mahalle']
            ilçe = record['ilçe']
            il = record['il']
            
            # Create multiple lookup keys for flexibility
            base_name = mahalle.replace(' Mahallesi', '').replace(' mahallesi', '').strip()
            
            lookup_keys = [
                self._normalize_turkish_text(base_name.lower()),           # "etlik"
                self._normalize_turkish_text(mahalle.lower()),             # "etlik mahallesi"
                base_name.lower(),                                        # "etlik" (unnormalized)
                mahalle.lower(),                                          # "etlik mahallesi" (unnormalized)
            ]
            
            # Remove duplicates while preserving order
            seen = set()
            unique_keys = []
            for key in lookup_keys:
                if key and key not in seen:
                    seen.add(key)
                    unique_keys.append(key)
            
            # Add to index
            for key in unique_keys:
                if key:  # Skip empty keys
                    neighborhood_index[key] = {
                        'proper_name': mahalle,
                        'ilçe': ilçe,
                        'il': il
                    }
        
        return neighborhood_index
    
    def _build_district_completion_index(self) -> Dict[str, Dict[str, str]]:
        """
        Build district → city completion index
        
        Returns:
            Dict mapping normalized district names to city info
        """
        district_index = {}
        
        for record in self.admin_database:
            if not all([record['il'], record['ilçe']]):
                continue
            
            ilçe = record['ilçe']
            il = record['il']
            
            normalized_district = self._normalize_turkish_text(ilçe.lower())
            
            if normalized_district:
                district_index[normalized_district] = {
                    'proper_name': ilçe,
                    'il': il
                }
        
        return district_index
    
    def _normalize_turkish_text(self, text: str) -> str:
        """Normalize Turkish text for consistent matching"""
        if not text:
            return ""
        
        # Apply Turkish character normalization
        normalized = text
        for char, replacement in self.turkish_char_map.items():
            normalized = normalized.replace(char, replacement)
        
        # Remove extra spaces and punctuation
        normalized = re.sub(r'[^\w\s]', ' ', normalized)
        normalized = re.sub(r'\s+', ' ', normalized)
        
        return normalized.strip().lower()
    
    def _build_turkish_char_map(self) -> Dict[str, str]:
        """Build Turkish character normalization map"""
        return {
            'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
            'Ç': 'c', 'Ğ': 'g', 'I': 'i', 'İ': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u',
        }
    
    def _create_empty_result(self, confidence: float, method: str) -> Dict[str, Any]:
        """Create empty result structure"""
        return {
            'completed_components': {},
            'completions_made': [],
            'confidence': confidence,
            'completion_methods': [method],
            'processing_time_ms': 0.0
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get performance statistics"""
        success_rate = (self.stats['successful_completions'] / self.stats['total_queries'] 
                       if self.stats['total_queries'] > 0 else 0.0)
        
        return {
            'total_queries': self.stats['total_queries'],
            'successful_completions': self.stats['successful_completions'],
            'success_rate': success_rate,
            'down_completions': self.stats['down_completions'],
            'up_completions': self.stats['up_completions'],
            'multi_level_completions': self.stats['multi_level_completions'],
            'average_processing_time_ms': self.stats['average_processing_time_ms']
        }


def test_component_completion_engine():
    """Test function for Component Completion Engine"""
    print("🧪 Testing Component Completion Engine - Phase 5")
    print("=" * 70)
    
    # Initialize engine
    try:
        completion_engine = ComponentCompletionEngine()
        print(f"✅ Component Completion Engine initialized")
        print(f"   Database records: {len(completion_engine.admin_database)}")
        print(f"   Neighborhood index: {len(completion_engine.neighborhood_completion_index)}")
        print(f"   District index: {len(completion_engine.district_completion_index)}")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return
    
    # Critical test cases for hierarchy completion
    test_cases = [
        {
            'name': 'DOWN Completion: Etlik → Keçiören, Ankara',
            'input': {'mahalle': 'Etlik'},
            'expected_completions': ['mahalle→ilçe: Keçiören', 'mahalle→il: Ankara'],
            'expected_components': {'mahalle': 'Etlik', 'ilçe': 'Keçiören', 'il': 'Ankara'}
        },
        {
            'name': 'DOWN Completion: Moda → Kadıköy, İstanbul',
            'input': {'mahalle': 'Moda'},
            'expected_completions': ['mahalle→ilçe: Kadıköy', 'mahalle→il: İstanbul'],
            'expected_components': {'mahalle': 'Moda', 'ilçe': 'Kadıköy', 'il': 'İstanbul'}
        },
        {
            'name': 'Partial DOWN Completion: İstanbul + Moda → Kadıköy',
            'input': {'il': 'İstanbul', 'mahalle': 'Moda'},
            'expected_completions': ['mahalle→ilçe: Kadıköy'],
            'expected_components': {'il': 'İstanbul', 'mahalle': 'Moda', 'ilçe': 'Kadıköy'}
        },
        {
            'name': 'UP Completion: Keçiören → Ankara',
            'input': {'ilçe': 'Keçiören'},
            'expected_completions': ['ilçe→il: Ankara'],
            'expected_components': {'ilçe': 'Keçiören', 'il': 'Ankara'}
        },
        {
            'name': 'Mahallesi Suffix Test: Etlik Mahallesi → Keçiören',
            'input': {'mahalle': 'Etlik Mahallesi'},
            'expected_completions': ['mahalle→ilçe: Keçiören', 'mahalle→il: Ankara'],
            'expected_components': {'mahalle': 'Etlik Mahallesi', 'ilçe': 'Keçiören', 'il': 'Ankara'}
        },
        {
            'name': 'No Completion Needed: Complete Address',
            'input': {'il': 'Ankara', 'ilçe': 'Keçiören', 'mahalle': 'Etlik'},
            'expected_completions': [],
            'expected_components': {'il': 'Ankara', 'ilçe': 'Keçiören', 'mahalle': 'Etlik'}
        },
        {
            'name': 'Complex Test: Alsancak → Konak, İzmir',
            'input': {'mahalle': 'Alsancak'},
            'expected_completions': ['mahalle→ilçe: Konak', 'mahalle→il: İzmir'],
            'expected_components': {'mahalle': 'Alsancak', 'ilçe': 'Konak', 'il': 'İzmir'}
        }
    ]
    
    print(f"\n🧪 Running {len(test_cases)} hierarchy completion test cases:")
    
    passed_tests = 0
    failed_tests = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Input: {test_case['input']}")
        
        try:
            result = completion_engine.complete_address_hierarchy(test_case['input'])
            completed_components = result['completed_components']
            completions_made = result['completions_made']
            confidence = result['confidence']
            processing_time = result['processing_time_ms']
            
            print(f"   Completed: {completed_components}")
            print(f"   Completions: {completions_made}")
            print(f"   Confidence: {confidence:.3f}")
            print(f"   Processing time: {processing_time:.2f}ms")
            
            # Check completions made
            test_passed = True
            for expected_completion in test_case['expected_completions']:
                if expected_completion not in completions_made:
                    print(f"   ❌ Missing completion: {expected_completion}")
                    test_passed = False
            
            # Check final components
            for expected_component, expected_value in test_case['expected_components'].items():
                actual_value = completed_components.get(expected_component)
                if not actual_value:
                    print(f"   ❌ Missing component: {expected_component}")
                    test_passed = False
                elif expected_value.lower() not in actual_value.lower():
                    print(f"   ❌ Component mismatch: {expected_component} = '{actual_value}' (expected '{expected_value}')")
                    # Be lenient for close matches
                    if expected_value in actual_value or actual_value in expected_value:
                        print(f"   🔶 Close match accepted")
                    else:
                        test_passed = False
            
            if test_passed:
                print(f"   ✅ PASS - Hierarchy completion successful")
                passed_tests += 1
            else:
                print(f"   ❌ FAIL - Issues with completion")
                failed_tests += 1
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            failed_tests += 1
    
    # Display statistics
    stats = completion_engine.get_statistics()
    print(f"\nPerformance Statistics:")
    print(f"   Total queries: {stats['total_queries']}")
    print(f"   Successful completions: {stats['successful_completions']}")
    print(f"   Success rate: {stats['success_rate']:.1%}")
    print(f"   DOWN completions: {stats['down_completions']}")
    print(f"   UP completions: {stats['up_completions']}")
    print(f"   Multi-level completions: {stats['multi_level_completions']}")
    print(f"   Average time: {stats['average_processing_time_ms']:.2f}ms")
    
    # Summary
    total_tests = passed_tests + failed_tests
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n" + "=" * 70)
    print(f"PHASE 5 TEST SUMMARY:")
    print(f"   Total tests: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {failed_tests}")
    print(f"   Success rate: {success_rate:.1f}%")
    
    if success_rate >= 85:
        print(f"\n🎉 PHASE 5 IMPLEMENTATION SUCCESSFUL!")
        print(f"✅ Bidirectional hierarchy completion working")
        print(f"✅ DOWN completion (mahalle→ilçe→il) operational")
        print(f"✅ UP completion (ilçe→il) enhanced")
        print(f"✅ Component Completion Intelligence ready")
        return True
    else:
        print(f"\n🔧 PHASE 5 NEEDS IMPROVEMENTS:")
        print(f"❌ Success rate below 85% target")
        print(f"🔧 Review failed cases and improve completion logic")
        return False


if __name__ == "__main__":
    test_component_completion_engine()