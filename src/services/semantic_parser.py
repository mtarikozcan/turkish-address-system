"""
Semantic Pattern Engine
Phase 2: Position-Independent Semantic Component Recognition

This module provides intelligent semantic pattern recognition for:
- Street number patterns (231.sk → 231 Sokak)
- Complex building numbers (no3/12 → bina_no: 3, daire: 12)
- Context-aware component classification

Key Features:
- Position-independent pattern detection
- Complex building number intelligence
- Semantic component classification
- Integration with existing address parsing
"""

import logging
import re
import time
from typing import Dict, List, Tuple, Any, Optional, Set
from pathlib import Path

class SemanticPatternEngine:
    """
    Semantic Pattern Engine
    
    Handles position-independent semantic pattern recognition for Turkish addresses:
    - Street patterns: "231.sk", "15 sk.", "atatürk sokak"
    - Building patterns: "no3/12", "25/A daire 8", "numara 15-C"
    - Component classification and disambiguation
    """
    
    def __init__(self):
        """
        Initialize Semantic Pattern Engine
        
        Loads pattern recognition rules and component indicators
        """
        self.logger = logging.getLogger(__name__)
        
        # Compile pattern recognition rules
        self.street_patterns = self._compile_street_patterns()
        self.building_patterns = self._compile_building_patterns()
        self.component_indicators = self._load_component_indicators()
        
        # Performance tracking
        self.stats = {
            'total_queries': 0,
            'successful_extractions': 0,
            'street_patterns_found': 0,
            'building_patterns_found': 0,
            'average_processing_time_ms': 0.0
        }
        
        self.logger.info(f"SemanticPatternEngine initialized with {len(self.street_patterns)} street patterns and {len(self.building_patterns)} building patterns")
    
    def classify_semantic_components(self, address_text: str) -> Dict[str, Any]:
        """
        Main method: Extract all semantic patterns from address text
        
        Args:
            address_text: Raw address string to analyze
            
        Returns:
            {
                'components': {'sokak': str, 'bina_no': str, 'daire': str, ...},
                'confidence': float,
                'processing_time_ms': float,
                'matched_patterns': List[str],
                'extraction_methods': List[str]
            }
            
        Test Cases:
            "231.sk no3 / 12" → {'sokak': '231 Sokak', 'bina_no': '3', 'daire': '12'}
            "atatürk cad 15 sk numara 25/A" → {'sokak': '15 Sokak', 'bina_no': '25/A'}
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
            # Phase 1: Extract street patterns
            street_result = self.extract_street_patterns(address_text)
            if street_result['components']:
                found_components.update(street_result['components'])
                matched_patterns.extend(street_result['patterns'])
                confidence_scores.append(street_result['confidence'])
                extraction_methods.append('street_pattern')
                self.stats['street_patterns_found'] += 1
            
            # Phase 2: Extract building patterns
            building_result = self.extract_building_patterns(address_text)
            if building_result['components']:
                # Smart merge to avoid overwriting existing components
                for component, value in building_result['components'].items():
                    if component not in found_components:
                        found_components[component] = value
                matched_patterns.extend(building_result['patterns'])
                confidence_scores.append(building_result['confidence'])
                extraction_methods.append('building_pattern')
                self.stats['building_patterns_found'] += 1
            
            # Phase 3: Additional semantic classification
            semantic_result = self.classify_additional_components(address_text, found_components)
            if semantic_result['components']:
                for component, value in semantic_result['components'].items():
                    if component not in found_components:
                        found_components[component] = value
                matched_patterns.extend(semantic_result['patterns'])
                confidence_scores.append(semantic_result['confidence'])
                extraction_methods.append('semantic_classification')
            
            # Calculate overall confidence
            overall_confidence = max(confidence_scores) if confidence_scores else 0.0
            
            # Track successful extractions
            if found_components:
                self.stats['successful_extractions'] += 1
            
        except Exception as e:
            self.logger.error(f"Error in semantic pattern extraction for '{address_text}': {e}")
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
    
    def extract_street_patterns(self, address_text: str) -> Dict[str, Any]:
        """
        Extract street number patterns from address text
        
        Handles patterns:
        - "231.sk" → {'sokak': '231 Sokak'}
        - "15 sk." → {'sokak': '15 Sokak'}
        - "atatürk sk" → {'sokak': 'Atatürk Sokak'}
        - "123 sokak" → {'sokak': '123 Sokak'}
        
        Args:
            address_text: Address text to analyze
            
        Returns:
            Dict with extracted street components
        """
        found_components = {}
        matched_patterns = []
        
        # Normalize text for pattern matching
        text_lower = address_text.lower()
        
        # Pattern 1: Number + abbreviated street (231.sk, 15 sk., etc.)
        number_abbrev_patterns = [
            r'(\d+)\.sk\b',                    # "231.sk"
            r'(\d+)\s+sk\.?\b',                # "15 sk" or "15 sk."
            r'(\d+)\s*-?\s*sk\b',              # "15-sk" or "15sk"
        ]
        
        for pattern in number_abbrev_patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                street_number = match.group(1)
                street_name = f"{street_number} Sokak"
                found_components['sokak'] = street_name
                matched_patterns.append(match.group(0))
                break  # Take first match
        
        # Pattern 2: Named street + abbreviation (atatürk sk, cumhuriyet sk.)
        if 'sokak' not in found_components:
            named_street_patterns = [
                r'([a-züçğıöş]+(?:\s+[a-züçğıöş]+)*)\s+sk\.?\b',    # "atatürk sk" or "atatürk sk."
                r'([a-züçğıöş]+(?:\s+[a-züçğıöş]+)*)\s+sokak\b',   # "atatürk sokak"
                r'([a-züçğıöş]+(?:\s+[a-züçğıöş]+)*)\s+sokağı\b',  # "atatürk sokağı"
            ]
            
            for pattern in named_street_patterns:
                matches = re.finditer(pattern, text_lower)
                for match in matches:
                    street_base = match.group(1).title()
                    street_name = f"{street_base} Sokak"
                    found_components['sokak'] = street_name
                    matched_patterns.append(match.group(0))
                    break  # Take first match
                if 'sokak' in found_components:
                    break
        
        # Calculate confidence based on pattern strength
        confidence = 0.9 if found_components else 0.0
        
        return {
            'components': found_components,
            'confidence': confidence,
            'patterns': matched_patterns
        }
    
    def extract_building_patterns(self, address_text: str) -> Dict[str, Any]:
        """
        Extract complex building number patterns from address text
        
        Handles patterns:
        - "no3 / 12" → {'bina_no': '3', 'daire': '12'}
        - "25/A daire 8" → {'bina_no': '25/A', 'daire': '8'}
        - "numara 15-C" → {'bina_no': '15', 'blok': 'C'}
        - "kat 3 daire 45" → {'kat': '3', 'daire': '45'}
        
        Args:
            address_text: Address text to analyze
            
        Returns:
            Dict with extracted building components
        """
        found_components = {}
        matched_patterns = []
        
        # Normalize text for pattern matching
        text_lower = address_text.lower()
        
        # Pattern 1: "no3 / 12" format (building number / apartment)  
        # Extract with original case preservation
        no_slash_pattern = r'no\s*(\d+(?:[/\-][a-zA-Z0-9]+)?)\s*[/\-]\s*(\d+)'
        for match in re.finditer(no_slash_pattern, address_text, re.IGNORECASE):
            # Get the original text segment with preserved case
            start, end = match.span()
            original_segment = address_text[start:end]
            
            # Re-extract from original case-preserved segment
            case_match = re.search(no_slash_pattern, original_segment, re.IGNORECASE)
            if case_match:
                building_no = case_match.group(1)
                apartment_no = case_match.group(2)
            else:
                building_no = match.group(1)
                apartment_no = match.group(2)
                
            found_components['bina_no'] = building_no
            found_components['daire'] = apartment_no
            matched_patterns.append(match.group(0))
            break  # Take first match
        
        # Pattern 2: Standard building/apartment patterns
        if not found_components:
            # "25/A", "15-B", "123/7" etc.
            building_patterns = [
                r'no\s+(\d+[/\-][a-zA-Z0-9]+)(?:\s+kat\s+(\d+))?',  # "no 25/A kat 3"
                r'(?:no\.?\s*|numara\s*)?(\d+[/\-][a-zA-Z0-9]+)(?:\s+(?:daire|kat)\s+(\d+))?',
                r'(?:no\.?\s*|numara\s*)?(\d+)(?:\s+(?:blok|block)\s+([a-zA-Z]))(?:\s+(?:daire|kat)\s+(\d+))?',
            ]
            
            for pattern in building_patterns:
                for match in re.finditer(pattern, address_text, re.IGNORECASE):
                    # Preserve original case by re-extracting from original text segment
                    start, end = match.span()
                    original_segment = address_text[start:end]
                    
                    # Re-match on original case-preserved segment
                    case_match = re.search(pattern, original_segment, re.IGNORECASE)
                    if case_match:
                        groups = case_match.groups()
                    else:
                        groups = match.groups()
                    
                    if groups[0]:  # Building number exists
                        found_components['bina_no'] = groups[0]
                        matched_patterns.append(match.group(0))
                        
                        # Check for apartment/floor number
                        if len(groups) > 1 and groups[1]:
                            matched_text = match.group(0).lower()
                            if 'blok' in matched_text:
                                found_components['blok'] = groups[1]
                            elif 'kat' in matched_text:
                                found_components['kat'] = groups[1]
                            else:
                                found_components['daire'] = groups[1]
                        
                        # Check for third group (apartment after block)
                        if len(groups) > 2 and groups[2]:
                            found_components['daire'] = groups[2]
                    break
                if found_components:
                    break
        
        # Pattern 3: Separate apartment/floor patterns
        if 'daire' not in found_components:
            # Look for standalone "daire 12", "kat 3", "apartment 5"
            apartment_patterns = [
                r'daire\s*:?\s*(\d+)',
                r'apartment\s*:?\s*(\d+)', 
                r'apt\s*:?\s*(\d+)',
                r'kat\s*:?\s*(\d+)',
                r'floor\s*:?\s*(\d+)',
            ]
            
            for pattern in apartment_patterns:
                matches = re.finditer(pattern, text_lower)
                for match in matches:
                    apartment_no = match.group(1)
                    if 'kat' in match.group(0) or 'floor' in match.group(0):
                        found_components['kat'] = apartment_no
                    else:
                        found_components['daire'] = apartment_no
                    matched_patterns.append(match.group(0))
                    break  # Take first match
        
        # Calculate confidence based on pattern complexity
        confidence = 0.95 if len(found_components) >= 2 else 0.85 if found_components else 0.0
        
        return {
            'components': found_components,
            'confidence': confidence,
            'patterns': matched_patterns
        }
    
    def classify_additional_components(self, address_text: str, existing_components: Dict) -> Dict[str, Any]:
        """
        Classify additional semantic components not covered by street/building patterns
        
        Args:
            address_text: Address text to analyze
            existing_components: Already extracted components
            
        Returns:
            Dict with additional classified components
        """
        found_components = {}
        matched_patterns = []
        
        # This method can be extended for additional pattern recognition
        # For now, focus on core street and building patterns
        
        return {
            'components': found_components,
            'confidence': 0.5 if found_components else 0.0,
            'patterns': matched_patterns
        }
    
    def _compile_street_patterns(self) -> List[Dict[str, Any]]:
        """Compile street pattern recognition rules"""
        return [
            {
                'name': 'numbered_street_abbreviated',
                'pattern': r'(\d+)\.sk\b',
                'confidence': 0.9,
                'format': '{number} Sokak'
            },
            {
                'name': 'numbered_street_spaced',
                'pattern': r'(\d+)\s+sk\.?\b',
                'confidence': 0.9,
                'format': '{number} Sokak'
            },
            {
                'name': 'named_street_abbreviated',
                'pattern': r'([a-züçğıöş]+(?:\s+[a-züçğıöş]+)*)\s+sk\.?\b',
                'confidence': 0.8,
                'format': '{name} Sokak'
            }
        ]
    
    def _compile_building_patterns(self) -> List[Dict[str, Any]]:
        """Compile building pattern recognition rules"""
        return [
            {
                'name': 'no_slash_format',
                'pattern': r'no\s*(\d+(?:[/\-][a-zA-Z0-9]+)?)\s*[/\-]\s*(\d+)',
                'confidence': 0.95,
                'components': ['bina_no', 'daire']
            },
            {
                'name': 'building_apartment',
                'pattern': r'(\d+[/\-][a-zA-Z0-9]+)(?:\s+(?:daire|kat)\s+(\d+))?',
                'confidence': 0.9,
                'components': ['bina_no', 'daire']
            }
        ]
    
    def _load_component_indicators(self) -> Dict[str, List[str]]:
        """Load component type indicators"""
        return {
            'sokak': ['sk', 'sokak', 'sokağı', 'street', 'str'],
            'cadde': ['cd', 'cad', 'cadde', 'caddesi', 'avenue', 'ave'],
            'bulvar': ['blv', 'blvr', 'bulvar', 'bulvarı', 'boulevard'],
            'bina_no': ['no', 'numara', 'number', 'bina'],
            'daire': ['daire', 'apartment', 'apt', 'suite'],
            'kat': ['kat', 'floor', 'fl'],
            'blok': ['blok', 'block', 'building']
        }
    
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
            'street_patterns_found': self.stats['street_patterns_found'],
            'building_patterns_found': self.stats['building_patterns_found'],
            'average_processing_time_ms': self.stats['average_processing_time_ms']
        }


def test_semantic_pattern_engine():
    """Test function for Semantic Pattern Engine"""
    print("🧪 Testing Semantic Pattern Engine")
    print("=" * 60)
    
    # Initialize engine
    try:
        semantic_engine = SemanticPatternEngine()
        print(f"✅ Semantic Pattern Engine initialized")
        print(f"   Street patterns: {len(semantic_engine.street_patterns)}")
        print(f"   Building patterns: {len(semantic_engine.building_patterns)}")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return
    
    # Test cases for Phase 2
    test_cases = [
        {
            'name': 'Street + Building Pattern',
            'input': "231.sk no3 / 12",
            'expected': {'sokak': '231 Sokak', 'bina_no': '3', 'daire': '12'}
        },
        {
            'name': 'Named Street Pattern',
            'input': "atatürk sk numara 25/A",
            'expected': {'sokak': 'Atatürk Sokak', 'bina_no': '25/A'}
        },
        {
            'name': 'Complex Building',
            'input': "no 15-B daire 7",
            'expected': {'bina_no': '15-B', 'daire': '7'}
        },
        {
            'name': 'Simple Street',
            'input': "45 sk.",
            'expected': {'sokak': '45 Sokak'}
        },
        {
            'name': 'Full Address Test',
            'input': "moda mah 15.sk no 25/A kat 3",
            'expected': {'sokak': '15 Sokak', 'bina_no': '25/A', 'kat': '3'}
        }
    ]
    
    print(f"\n🧪 Running {len(test_cases)} Phase 2 test cases:")
    
    passed_tests = 0
    failed_tests = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Input: '{test_case['input']}'")
        
        try:
            result = semantic_engine.classify_semantic_components(test_case['input'])
            components = result['components']
            confidence = result['confidence']
            processing_time = result['processing_time_ms']
            
            print(f"   Result: {components}")
            print(f"   Confidence: {confidence:.2f}")
            print(f"   Processing time: {processing_time:.2f}ms")
            
            # Check if expected components are found
            test_passed = True
            for expected_component, expected_value in test_case['expected'].items():
                actual_value = components.get(expected_component)
                if actual_value != expected_value:
                    print(f"   ❌ {expected_component}: expected '{expected_value}', got '{actual_value}'")
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
    stats = semantic_engine.get_statistics()
    print(f"\nPerformance Statistics:")
    print(f"   Total queries: {stats['total_queries']}")
    print(f"   Successful extractions: {stats['successful_extractions']}")
    print(f"   Success rate: {stats['success_rate']:.1%}")
    print(f"   Street patterns found: {stats['street_patterns_found']}")
    print(f"   Building patterns found: {stats['building_patterns_found']}")
    print(f"   Average time: {stats['average_processing_time_ms']:.2f}ms")
    
    # Summary
    total_tests = passed_tests + failed_tests
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n" + "=" * 60)
    print(f"PHASE 2 TEST SUMMARY:")
    print(f"   Total tests: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {failed_tests}")
    print(f"   Success rate: {success_rate:.1f}%")
    
    if failed_tests == 0:
        print(f"\n🎉 PHASE 2 IMPLEMENTATION SUCCESSFUL!")
        print(f"✅ All semantic pattern test cases passed")
        print(f"✅ Street and building patterns working")
        print(f"✅ Semantic Pattern Engine ready for integration")
        return True
    else:
        print(f"\n🔧 PHASE 2 NEEDS IMPROVEMENTS:")
        print(f"❌ {failed_tests} test cases failed")
        print(f"🔧 Review failed cases and improve pattern logic")
        return False


if __name__ == "__main__":
    test_semantic_pattern_engine()