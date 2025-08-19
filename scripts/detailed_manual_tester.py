#!/usr/bin/env python3
"""
TEKNOFEST 2025 - Detailed Manual Address Testing Interface
Interactive testing interface for comprehensive address pipeline analysis

This tool provides detailed step-by-step analysis of address processing
for manual jury evaluation and system debugging.

Author: TEKNOFEST 2025 Address Resolution Team
Version: 1.0.0
"""

import sys
import time
import json
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Import all system components
try:
    from address_validator import AddressValidator
    from address_corrector import AddressCorrector
    from address_parser import AddressParser
    from address_matcher import HybridAddressMatcher
    from address_geocoder import AddressGeocoder
    from duplicate_detector import DuplicateAddressDetector
    from geo_integrated_pipeline import GeoIntegratedPipeline
    COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some components not available: {e}")
    COMPONENTS_AVAILABLE = False


# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


@dataclass
class PipelineStepResult:
    """Result structure for individual pipeline steps"""
    step_name: str
    input_data: Any
    output_data: Any
    processing_time_ms: float
    success: bool
    confidence: float
    warnings: List[str]
    errors: List[str]
    metadata: Dict[str, Any]


@dataclass
class FullPipelineResult:
    """Complete pipeline analysis result"""
    original_address: str
    pipeline_steps: List[PipelineStepResult]
    total_processing_time_ms: float
    final_confidence: float
    overall_success: bool
    summary: Dict[str, Any]
    timestamp: str


def convert_to_json_serializable(obj: Any) -> Any:
    """
    Convert complex objects to JSON-serializable format
    
    CRITICAL FIX: Handles FullPipelineResult and other custom objects
    """
    if isinstance(obj, (FullPipelineResult, PipelineStepResult)):
        # Convert dataclass to dictionary
        result = asdict(obj)
        # Recursively convert nested objects
        return convert_to_json_serializable(result)
    
    elif isinstance(obj, dict):
        # Convert dictionary values recursively
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
    
    elif isinstance(obj, (list, tuple)):
        # Convert list/tuple items recursively
        return [convert_to_json_serializable(item) for item in obj]
    
    elif isinstance(obj, datetime):
        # Convert datetime to ISO string
        return obj.isoformat()
    
    elif hasattr(obj, '__dict__'):
        # Convert objects with __dict__ (like custom classes)
        try:
            return convert_to_json_serializable(obj.__dict__)
        except:
            # If __dict__ conversion fails, convert to string
            return str(obj)
    
    elif isinstance(obj, (int, float, str, bool, type(None))):
        # Already JSON serializable
        return obj
    
    else:
        # Convert everything else to string representation
        try:
            return str(obj)
        except:
            return f"<non-serializable: {type(obj).__name__}>"


class DetailedManualTester:
    """
    Detailed Manual Address Testing Interface
    
    Provides comprehensive step-by-step analysis of address processing
    with interactive modes for single address analysis, duplicate comparison,
    batch processing, and result export.
    """
    
    def __init__(self):
        """Initialize the detailed manual testing interface"""
        print(f"{Colors.HEADER}🔬 TEKNOFEST 2025 - DETAILED MANUAL ADDRESS TESTER{Colors.ENDC}")
        print("=" * 80)
        print("Interactive interface for comprehensive address pipeline analysis")
        print()
        
        # Initialize all components
        self._initialize_components()
        
        # Test results storage
        self.test_results = []
        self.current_session = {
            'start_time': datetime.now(),
            'test_count': 0,
            'results': []
        }
        
        # Predefined test cases for easy testing
        self.predefined_test_cases = {
            "Turkish Character Hell": [
                "İSTANBUL kadıköy MODA mahallesi caferağa sk 10",
                "istanbul KADİKÖY moda MAHALLESİ caferaga sokak 10",
                "Izmit Körfez Ihsaniye Mahallesi Deniz Caddesi",
                "İzmit Körfez İhsaniye Mahallesi Deniz Caddesi"
            ],
            "Abbreviation Nightmare": [
                "Ank. Çank. Kızılay Mh. Atatürk Blv. No:25/A Daire:3",
                "Ankara Çankaya Kızılay Mahallesi Atatürk Bulvarı Numara:25/A Daire:3",
                "İst. Beşiktaş Levent Mah. Büyükdere Cd. No:15",
                "İstanbul Beşiktaş Levent Mahallesi Büyükdere Caddesi 15"
            ],
            "Real World Chaos": [
                "istanbul  kadikoy   moda mah.caferaga sk.no:10/a",
                "İstanbul Kadıköy Moda Mahallesi Caferağa Sokak 10/A",
                "Ankara Çankaya Büklüm Sokak Mahallesi Atatürk Cad",
                "Ankara Çankaya Kavaklıdere Mahallesi Atatürk Caddesi"
            ]
        }
        
        print(f"{Colors.OKGREEN}✅ Detailed manual tester initialized successfully{Colors.ENDC}")
        print(f"{Colors.OKGREEN}✅ {len(self.predefined_test_cases)} predefined test case groups loaded{Colors.ENDC}")
    
    def _initialize_components(self):
        """Initialize all system components with error handling"""
        try:
            if COMPONENTS_AVAILABLE:
                self.validator = AddressValidator()
                self.corrector = AddressCorrector()
                self.parser = AddressParser()
                self.matcher = HybridAddressMatcher()
                self.geocoder = AddressGeocoder()
                self.duplicate_detector = DuplicateAddressDetector()
                self.pipeline = GeoIntegratedPipeline("postgresql://test:test@localhost/test")
                print(f"{Colors.OKGREEN}✅ All system components initialized{Colors.ENDC}")
            else:
                raise ImportError("Components not available")
                
        except Exception as e:
            print(f"{Colors.WARNING}⚠️  Component initialization warning: {e}{Colors.ENDC}")
            print(f"{Colors.WARNING}   Some features may be limited{Colors.ENDC}")
    
    def analyze_single_address(self, address: str) -> FullPipelineResult:
        """
        Perform comprehensive step-by-step analysis of a single address
        
        Args:
            address: Input address string
            
        Returns:
            Complete pipeline analysis result
        """
        print(f"\n{Colors.HEADER}🔍 SINGLE ADDRESS PIPELINE ANALYSIS{Colors.ENDC}")
        print("=" * 60)
        print(f"{Colors.BOLD}Original Address:{Colors.ENDC} {address}")
        print()
        
        pipeline_start_time = time.time()
        pipeline_steps = []
        
        # Step 1: Address Correction
        step_result = self._analyze_correction_step(address)
        pipeline_steps.append(step_result)
        self._display_step_result(step_result, 1)
        
        corrected_address = step_result.output_data.get('corrected_address', address)
        
        # Step 2: Address Parsing
        step_result = self._analyze_parsing_step(corrected_address)
        pipeline_steps.append(step_result)
        self._display_step_result(step_result, 2)
        
        parsed_components = step_result.output_data.get('components', {})
        
        # Step 3: Address Validation
        step_result = self._analyze_validation_step({
            'corrected_address': corrected_address,
            'parsed_components': parsed_components
        })
        pipeline_steps.append(step_result)
        self._display_step_result(step_result, 3)
        
        # Step 4: Address Geocoding
        step_result = self._analyze_geocoding_step(address)
        pipeline_steps.append(step_result)
        self._display_step_result(step_result, 4)
        
        # Calculate overall results
        total_time = (time.time() - pipeline_start_time) * 1000
        final_confidence = sum(step.confidence for step in pipeline_steps) / len(pipeline_steps)
        overall_success = all(step.success for step in pipeline_steps)
        
        # Create summary
        summary = {
            'original_length': len(address),
            'corrections_applied': len(pipeline_steps[0].output_data.get('corrections_applied', [])),
            'components_extracted': len(parsed_components),
            'validation_passed': pipeline_steps[2].success,
            'geocoding_successful': pipeline_steps[3].success,
            'geocoding_method': pipeline_steps[3].output_data.get('geocoding_method', 'unknown'),
            'final_coordinates': pipeline_steps[3].output_data.get('coordinates')
        }
        
        result = FullPipelineResult(
            original_address=address,
            pipeline_steps=pipeline_steps,
            total_processing_time_ms=total_time,
            final_confidence=final_confidence,
            overall_success=overall_success,
            summary=summary,
            timestamp=datetime.now().isoformat()
        )
        
        # Display final summary
        self._display_pipeline_summary(result)
        
        return result
    
    def _analyze_correction_step(self, address: str) -> PipelineStepResult:
        """Analyze address correction step"""
        step_start_time = time.time()
        warnings = []
        errors = []
        
        try:
            if hasattr(self, 'corrector'):
                correction_result = self.corrector.correct_address(address)
                
                output_data = {
                    'corrected_address': correction_result.get('corrected_address', address),
                    'corrections_applied': correction_result.get('corrections_applied', []),
                    'correction_confidence': correction_result.get('confidence', 1.0),
                    'correction_method': correction_result.get('method', 'standard')
                }
                
                success = True
                confidence = correction_result.get('confidence', 1.0)
                
                # Check for significant changes
                if len(correction_result.get('corrections_applied', [])) > 5:
                    warnings.append("Many corrections applied - verify accuracy")
                
            else:
                # Fallback mode
                output_data = {
                    'corrected_address': address.strip(),
                    'corrections_applied': [],
                    'correction_confidence': 1.0,
                    'correction_method': 'fallback'
                }
                success = True
                confidence = 1.0
                warnings.append("Using fallback correction mode")
                
        except Exception as e:
            errors.append(f"Correction failed: {str(e)}")
            output_data = {'corrected_address': address, 'error': str(e)}
            success = False
            confidence = 0.0
        
        processing_time = (time.time() - step_start_time) * 1000
        
        return PipelineStepResult(
            step_name="Address Correction",
            input_data={'original_address': address},
            output_data=output_data,
            processing_time_ms=processing_time,
            success=success,
            confidence=confidence,
            warnings=warnings,
            errors=errors,
            metadata={'method': output_data.get('correction_method', 'unknown')}
        )
    
    def _analyze_parsing_step(self, address: str) -> PipelineStepResult:
        """Analyze address parsing step"""
        step_start_time = time.time()
        warnings = []
        errors = []
        
        try:
            if hasattr(self, 'parser'):
                parsing_result = self.parser.parse_address(address)
                
                components = parsing_result.get('components', {})
                output_data = {
                    'components': components,
                    'parsing_confidence': parsing_result.get('confidence', 0.0),
                    'parsing_method': parsing_result.get('method', 'standard'),
                    'component_count': len(components)
                }
                
                success = len(components) > 0
                confidence = parsing_result.get('confidence', 0.0)
                
                # Component validation
                required_components = ['il', 'ilce', 'mahalle']
                missing_components = [comp for comp in required_components if not components.get(comp)]
                
                if missing_components:
                    warnings.append(f"Missing components: {', '.join(missing_components)}")
                
                if len(components) < 3:
                    warnings.append("Few components extracted - address may be incomplete")
                
            else:
                # Fallback mode
                output_data = {
                    'components': {'raw': address},
                    'parsing_confidence': 0.5,
                    'parsing_method': 'fallback',
                    'component_count': 1
                }
                success = True
                confidence = 0.5
                warnings.append("Using fallback parsing mode")
                
        except Exception as e:
            errors.append(f"Parsing failed: {str(e)}")
            output_data = {'components': {}, 'error': str(e)}
            success = False
            confidence = 0.0
        
        processing_time = (time.time() - step_start_time) * 1000
        
        return PipelineStepResult(
            step_name="Address Parsing",
            input_data={'corrected_address': address},
            output_data=output_data,
            processing_time_ms=processing_time,
            success=success,
            confidence=confidence,
            warnings=warnings,
            errors=errors,
            metadata={'method': output_data.get('parsing_method', 'unknown')}
        )
    
    def _analyze_validation_step(self, validation_input: Dict) -> PipelineStepResult:
        """Analyze address validation step"""
        step_start_time = time.time()
        warnings = []
        errors = []
        
        try:
            if hasattr(self, 'validator'):
                validation_result = self.validator.validate_address(validation_input)
                
                output_data = {
                    'is_valid': validation_result.get('is_valid', False),
                    'validation_confidence': validation_result.get('confidence_score', 0.0),
                    'validation_details': validation_result.get('validation_details', {}),
                    'validation_issues': validation_result.get('issues', [])
                }
                
                success = validation_result.get('is_valid', False)
                confidence = validation_result.get('confidence_score', 0.0)
                
                # Check validation issues
                issues = validation_result.get('issues', [])
                if issues:
                    warnings.extend([f"Validation issue: {issue}" for issue in issues])
                
                if confidence < 0.7:
                    warnings.append("Low validation confidence - verify address accuracy")
                
            else:
                # Fallback mode
                output_data = {
                    'is_valid': True,
                    'validation_confidence': 0.8,
                    'validation_details': {'fallback_mode': True},
                    'validation_issues': []
                }
                success = True
                confidence = 0.8
                warnings.append("Using fallback validation mode")
                
        except Exception as e:
            errors.append(f"Validation failed: {str(e)}")
            output_data = {'is_valid': False, 'error': str(e)}
            success = False
            confidence = 0.0
        
        processing_time = (time.time() - step_start_time) * 1000
        
        return PipelineStepResult(
            step_name="Address Validation",
            input_data=validation_input,
            output_data=output_data,
            processing_time_ms=processing_time,
            success=success,
            confidence=confidence,
            warnings=warnings,
            errors=errors,
            metadata={'method': 'standard'}
        )
    
    def _analyze_geocoding_step(self, address: str) -> PipelineStepResult:
        """Analyze address geocoding step"""
        step_start_time = time.time()
        warnings = []
        errors = []
        
        try:
            if hasattr(self, 'geocoder'):
                geocoding_result = self.geocoder.geocode_turkish_address(address)
                
                lat = geocoding_result.get('latitude')
                lon = geocoding_result.get('longitude')
                method = geocoding_result.get('method', 'unknown')
                geo_confidence = geocoding_result.get('confidence', 0.0)
                
                output_data = {
                    'coordinates': {'latitude': lat, 'longitude': lon} if lat and lon else None,
                    'geocoding_method': method,
                    'geocoding_confidence': geo_confidence,
                    'geocoding_details': geocoding_result
                }
                
                success = lat is not None and lon is not None
                confidence = geo_confidence
                
                # Geocoding quality checks
                if method == 'turkey_center':
                    warnings.append("Using Turkey center fallback - low precision")
                elif method == 'province_centroid':
                    warnings.append("Using province centroid - medium precision")
                elif geo_confidence < 0.7:
                    warnings.append("Low geocoding confidence")
                
                if not success:
                    warnings.append("Geocoding failed - no coordinates found")
                
            else:
                # Fallback mode
                output_data = {
                    'coordinates': None,
                    'geocoding_method': 'fallback',
                    'geocoding_confidence': 0.0,
                    'geocoding_details': {}
                }
                success = False
                confidence = 0.0
                warnings.append("Using fallback geocoding mode")
                
        except Exception as e:
            errors.append(f"Geocoding failed: {str(e)}")
            output_data = {'coordinates': None, 'error': str(e)}
            success = False
            confidence = 0.0
        
        processing_time = (time.time() - step_start_time) * 1000
        
        return PipelineStepResult(
            step_name="Address Geocoding",
            input_data={'address': address},
            output_data=output_data,
            processing_time_ms=processing_time,
            success=success,
            confidence=confidence,
            warnings=warnings,
            errors=errors,
            metadata={'method': method}
        )
    
    def _display_step_result(self, step: PipelineStepResult, step_number: int):
        """Display formatted step result"""
        print(f"{Colors.OKBLUE}📍 STEP {step_number}: {step.step_name}{Colors.ENDC}")
        print("-" * 40)
        
        # Success/Failure status
        status_color = Colors.OKGREEN if step.success else Colors.FAIL
        status_text = "SUCCESS" if step.success else "FAILED"
        print(f"Status: {status_color}{status_text}{Colors.ENDC}")
        print(f"Processing Time: {step.processing_time_ms:.2f}ms")
        print(f"Confidence: {step.confidence:.3f}")
        
        # Step-specific output
        if step.step_name == "Address Correction":
            corrected = step.output_data.get('corrected_address', '')
            corrections = step.output_data.get('corrections_applied', [])
            print(f"Corrected: {Colors.OKCYAN}{corrected}{Colors.ENDC}")
            if corrections:
                print(f"Corrections: {len(corrections)} applied")
                for correction in corrections[:3]:  # Show first 3
                    print(f"  • {correction}")
                if len(corrections) > 3:
                    print(f"  • ... and {len(corrections) - 3} more")
        
        elif step.step_name == "Address Parsing":
            components = step.output_data.get('components', {})
            print(f"Components Extracted: {len(components)}")
            for key, value in components.items():
                if value:
                    print(f"  • {key}: {Colors.OKCYAN}{value}{Colors.ENDC}")
        
        elif step.step_name == "Address Validation":
            is_valid = step.output_data.get('is_valid', False)
            valid_color = Colors.OKGREEN if is_valid else Colors.FAIL
            print(f"Valid: {valid_color}{is_valid}{Colors.ENDC}")
            issues = step.output_data.get('validation_issues', [])
            if issues:
                print(f"Issues: {len(issues)}")
                for issue in issues[:2]:
                    print(f"  • {Colors.WARNING}{issue}{Colors.ENDC}")
        
        elif step.step_name == "Address Geocoding":
            coords = step.output_data.get('coordinates')
            method = step.output_data.get('geocoding_method', 'unknown')
            if coords:
                lat, lon = coords['latitude'], coords['longitude']
                print(f"Coordinates: {Colors.OKGREEN}({lat:.4f}, {lon:.4f}){Colors.ENDC}")
                print(f"Method: {method}")
            else:
                print(f"{Colors.FAIL}No coordinates found{Colors.ENDC}")
        
        # Warnings and errors
        if step.warnings:
            print(f"{Colors.WARNING}Warnings:{Colors.ENDC}")
            for warning in step.warnings:
                print(f"  ⚠️  {warning}")
        
        if step.errors:
            print(f"{Colors.FAIL}Errors:{Colors.ENDC}")
            for error in step.errors:
                print(f"  ❌ {error}")
        
        print()
    
    def _display_pipeline_summary(self, result: FullPipelineResult):
        """Display comprehensive pipeline summary"""
        print(f"{Colors.HEADER}📊 PIPELINE ANALYSIS SUMMARY{Colors.ENDC}")
        print("=" * 60)
        
        # Overall status
        status_color = Colors.OKGREEN if result.overall_success else Colors.FAIL
        status_text = "SUCCESS" if result.overall_success else "FAILED"
        print(f"Overall Status: {status_color}{status_text}{Colors.ENDC}")
        print(f"Final Confidence: {result.final_confidence:.3f}")
        print(f"Total Processing Time: {result.total_processing_time_ms:.2f}ms")
        print()
        
        # Step summary
        print(f"{Colors.BOLD}Step Summary:{Colors.ENDC}")
        for i, step in enumerate(result.pipeline_steps, 1):
            status_icon = "✅" if step.success else "❌"
            print(f"  {status_icon} Step {i}: {step.step_name} ({step.processing_time_ms:.2f}ms, conf: {step.confidence:.3f})")
        print()
        
        # Key results
        summary = result.summary
        print(f"{Colors.BOLD}Key Results:{Colors.ENDC}")
        print(f"  Original Length: {summary['original_length']} characters")
        print(f"  Corrections Applied: {summary['corrections_applied']}")
        print(f"  Components Extracted: {summary['components_extracted']}")
        print(f"  Validation Passed: {'✅' if summary['validation_passed'] else '❌'}")
        print(f"  Geocoding Successful: {'✅' if summary['geocoding_successful'] else '❌'}")
        
        if summary.get('final_coordinates'):
            coords = summary['final_coordinates']
            print(f"  Final Coordinates: ({coords['latitude']:.4f}, {coords['longitude']:.4f})")
        
        print(f"  Geocoding Method: {summary['geocoding_method']}")
        print()
    
    def compare_two_addresses(self, addr1: str, addr2: str) -> Dict[str, Any]:
        """
        Detailed similarity comparison between two addresses
        
        Args:
            addr1: First address
            addr2: Second address
            
        Returns:
            Detailed comparison result
        """
        print(f"\n{Colors.HEADER}🔄 TWO ADDRESS SIMILARITY ANALYSIS{Colors.ENDC}")
        print("=" * 60)
        print(f"{Colors.BOLD}Address 1:{Colors.ENDC} {addr1}")
        print(f"{Colors.BOLD}Address 2:{Colors.ENDC} {addr2}")
        print()
        
        comparison_start_time = time.time()
        
        # Step 1: Process both addresses individually
        print(f"{Colors.OKBLUE}📋 INDIVIDUAL PROCESSING{Colors.ENDC}")
        print("-" * 30)
        
        result1 = self.analyze_single_address(addr1)
        result2 = self.analyze_single_address(addr2)
        
        # Step 2: Detailed similarity analysis
        print(f"\n{Colors.OKBLUE}🔍 SIMILARITY ANALYSIS{Colors.ENDC}")
        print("-" * 30)
        
        similarity_result = self._calculate_detailed_similarity(addr1, addr2, result1, result2)
        
        # Step 3: Duplicate detection
        print(f"\n{Colors.OKBLUE}🎯 DUPLICATE DETECTION{Colors.ENDC}")
        print("-" * 30)
        
        duplicate_result = self._analyze_duplicate_detection([addr1, addr2])
        
        total_time = (time.time() - comparison_start_time) * 1000
        
        # Comprehensive comparison result
        comparison_result = {
            'addresses': [addr1, addr2],
            'individual_results': [result1, result2],
            'similarity_analysis': similarity_result,
            'duplicate_detection': duplicate_result,
            'total_processing_time_ms': total_time,
            'timestamp': datetime.now().isoformat()
        }
        
        # Display final comparison summary
        self._display_comparison_summary(comparison_result)
        
        return comparison_result
    
    def _calculate_detailed_similarity(self, addr1: str, addr2: str, 
                                     result1: FullPipelineResult, 
                                     result2: FullPipelineResult) -> Dict[str, Any]:
        """Calculate detailed similarity breakdown"""
        
        similarity_details = {}
        
        try:
            if hasattr(self, 'matcher'):
                # Use HybridAddressMatcher for detailed similarity
                similarity_result = self.matcher.calculate_hybrid_similarity(addr1, addr2)
                
                similarity_details = {
                    'overall_similarity': similarity_result.get('overall_similarity', 0.0),
                    'breakdown': similarity_result.get('breakdown', {}),
                    'method': 'hybrid_matcher',
                    'details': similarity_result
                }
                
                print(f"Overall Similarity: {Colors.OKGREEN}{similarity_details['overall_similarity']:.3f}{Colors.ENDC}")
                
                # Display breakdown
                breakdown = similarity_details['breakdown']
                if breakdown:
                    print(f"Similarity Breakdown:")
                    for component, score in breakdown.items():
                        if isinstance(score, (int, float)):
                            print(f"  • {component}: {score:.3f}")
                
            else:
                # Fallback similarity calculation
                similarity_details = {
                    'overall_similarity': 0.0,
                    'breakdown': {},
                    'method': 'fallback',
                    'details': {}
                }
                print(f"{Colors.WARNING}Using fallback similarity calculation{Colors.ENDC}")
            
            # Component-level comparison
            comp1 = result1.pipeline_steps[1].output_data.get('components', {})
            comp2 = result2.pipeline_steps[1].output_data.get('components', {})
            
            component_matches = {}
            all_components = set(comp1.keys()).union(set(comp2.keys()))
            
            for component in all_components:
                val1 = comp1.get(component, '').lower().strip()
                val2 = comp2.get(component, '').lower().strip()
                
                if val1 and val2:
                    match = val1 == val2
                    component_matches[component] = {
                        'value1': comp1.get(component, ''),
                        'value2': comp2.get(component, ''),
                        'exact_match': match,
                        'similarity': 1.0 if match else 0.0
                    }
            
            similarity_details['component_comparison'] = component_matches
            
            # Display component comparison
            if component_matches:
                print(f"\nComponent Comparison:")
                for comp, details in component_matches.items():
                    match_icon = "✅" if details['exact_match'] else "❌"
                    print(f"  {match_icon} {comp}: '{details['value1']}' ↔ '{details['value2']}'")
                    
        except Exception as e:
            similarity_details = {
                'overall_similarity': 0.0,
                'error': str(e),
                'method': 'error'
            }
            print(f"{Colors.FAIL}Similarity calculation failed: {e}{Colors.ENDC}")
        
        return similarity_details
    
    def _analyze_duplicate_detection(self, addresses: List[str]) -> Dict[str, Any]:
        """Analyze duplicate detection for address list"""
        
        try:
            if hasattr(self, 'duplicate_detector'):
                # Find duplicate groups
                duplicate_groups = self.duplicate_detector.find_duplicate_groups(addresses)
                
                # Get detailed statistics
                stats = self.duplicate_detector.get_duplicate_statistics(addresses)
                
                duplicate_result = {
                    'duplicate_groups': duplicate_groups,
                    'statistics': stats,
                    'method': 'duplicate_detector'
                }
                
                # Display results
                print(f"Duplicate Groups Found: {len([g for g in duplicate_groups if len(g) > 1])}")
                print(f"Duplication Rate: {stats.get('duplication_rate', 0.0):.1%}")
                
                for i, group in enumerate(duplicate_groups):
                    if len(group) > 1:
                        print(f"  Group {i+1}: {group}")
                        for idx in group:
                            if idx < len(addresses):
                                print(f"    - {addresses[idx]}")
                
            else:
                duplicate_result = {
                    'duplicate_groups': [[i] for i in range(len(addresses))],
                    'statistics': {'error': 'Duplicate detector not available'},
                    'method': 'fallback'
                }
                print(f"{Colors.WARNING}Duplicate detector not available{Colors.ENDC}")
                
        except Exception as e:
            duplicate_result = {
                'duplicate_groups': [],
                'error': str(e),
                'method': 'error'
            }
            print(f"{Colors.FAIL}Duplicate detection failed: {e}{Colors.ENDC}")
        
        return duplicate_result
    
    def _display_comparison_summary(self, comparison_result: Dict[str, Any]):
        """Display comprehensive comparison summary"""
        print(f"\n{Colors.HEADER}📊 COMPARISON SUMMARY{Colors.ENDC}")
        print("=" * 60)
        
        similarity = comparison_result['similarity_analysis'].get('overall_similarity', 0.0)
        duplicate_groups = comparison_result['duplicate_detection'].get('duplicate_groups', [])
        
        # Overall similarity
        if similarity > 0.85:
            sim_color = Colors.OKGREEN
            sim_status = "HIGH SIMILARITY"
        elif similarity > 0.7:
            sim_color = Colors.WARNING
            sim_status = "MEDIUM SIMILARITY"
        else:
            sim_color = Colors.FAIL
            sim_status = "LOW SIMILARITY"
        
        print(f"Overall Similarity: {sim_color}{similarity:.3f} ({sim_status}){Colors.ENDC}")
        
        # Duplicate detection result
        is_duplicate = len([g for g in duplicate_groups if len(g) > 1]) > 0
        dup_color = Colors.OKGREEN if is_duplicate else Colors.FAIL
        dup_status = "DETECTED AS DUPLICATES" if is_duplicate else "NOT DUPLICATES"
        print(f"Duplicate Detection: {dup_color}{dup_status}{Colors.ENDC}")
        
        # Processing time
        total_time = comparison_result['total_processing_time_ms']
        print(f"Total Analysis Time: {total_time:.2f}ms")
        
        # Recommendation
        print(f"\n{Colors.BOLD}Recommendation:{Colors.ENDC}")
        if is_duplicate or similarity > 0.8:
            print(f"  {Colors.OKGREEN}✅ These addresses likely refer to the same location{Colors.ENDC}")
        elif similarity > 0.6:
            print(f"  {Colors.WARNING}⚠️  These addresses might be related - manual review recommended{Colors.ENDC}")
        else:
            print(f"  {Colors.FAIL}❌ These addresses appear to be different locations{Colors.ENDC}")
        
        print()
    
    def batch_analysis(self, addresses: List[str]) -> Dict[str, Any]:
        """
        Batch analysis of multiple addresses for duplicate detection
        
        Args:
            addresses: List of addresses to analyze
            
        Returns:
            Comprehensive batch analysis result
        """
        print(f"\n{Colors.HEADER}📊 BATCH ADDRESS ANALYSIS{Colors.ENDC}")
        print("=" * 60)
        print(f"Analyzing {len(addresses)} addresses for duplicates...")
        print()
        
        batch_start_time = time.time()
        
        # Display input addresses
        print(f"{Colors.BOLD}Input Addresses:{Colors.ENDC}")
        for i, addr in enumerate(addresses, 1):
            print(f"  {i}. {addr}")
        print()
        
        # Duplicate detection analysis
        duplicate_result = self._analyze_duplicate_detection(addresses)
        
        # Individual address analysis (optional, for detailed view)
        individual_results = []
        if len(addresses) <= 5:  # Only for small batches
            print(f"{Colors.OKBLUE}📋 INDIVIDUAL ADDRESS ANALYSIS{Colors.ENDC}")
            print("-" * 40)
            for addr in addresses:
                result = self.analyze_single_address(addr)
                individual_results.append(result)
        
        total_time = (time.time() - batch_start_time) * 1000
        
        batch_result = {
            'addresses': addresses,
            'duplicate_analysis': duplicate_result,
            'individual_results': individual_results,
            'total_processing_time_ms': total_time,
            'timestamp': datetime.now().isoformat()
        }
        
        # Display batch summary
        self._display_batch_summary(batch_result)
        
        return batch_result
    
    def _display_batch_summary(self, batch_result: Dict[str, Any]):
        """Display batch analysis summary"""
        print(f"\n{Colors.HEADER}📊 BATCH ANALYSIS SUMMARY{Colors.ENDC}")
        print("=" * 60)
        
        addresses = batch_result['addresses']
        duplicate_analysis = batch_result['duplicate_analysis']
        
        print(f"Total Addresses: {len(addresses)}")
        print(f"Processing Time: {batch_result['total_processing_time_ms']:.2f}ms")
        print(f"Average Time per Address: {batch_result['total_processing_time_ms']/len(addresses):.2f}ms")
        
        # Duplicate detection results
        duplicate_groups = duplicate_analysis.get('duplicate_groups', [])
        stats = duplicate_analysis.get('statistics', {})
        
        print(f"\n{Colors.BOLD}Duplicate Detection Results:{Colors.ENDC}")
        print(f"  Duplicate Groups: {len([g for g in duplicate_groups if len(g) > 1])}")
        print(f"  Unique Addresses: {stats.get('unique_addresses', len(addresses))}")
        print(f"  Duplication Rate: {stats.get('duplication_rate', 0.0):.1%}")
        
        # Show duplicate groups
        duplicate_found = False
        for i, group in enumerate(duplicate_groups):
            if len(group) > 1:
                duplicate_found = True
                print(f"\n  {Colors.OKGREEN}Duplicate Group {i+1}:{Colors.ENDC}")
                for idx in group:
                    if idx < len(addresses):
                        print(f"    • {addresses[idx]}")
        
        if not duplicate_found:
            print(f"  {Colors.FAIL}No duplicates detected{Colors.ENDC}")
        
        print()
    
    def export_results(self, results: List[Dict[str, Any]], filename: str = None, format: str = 'json'):
        """
        Export test results to file
        
        Args:
            results: List of test results to export
            filename: Output filename (auto-generated if None)
            format: Export format ('json' or 'csv')
        """
        if not results:
            print(f"{Colors.WARNING}No results to export{Colors.ENDC}")
            return
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"detailed_test_results_{timestamp}.{format}"
        
        try:
            if format.lower() == 'json':
                # CRITICAL FIX: Convert complex objects to JSON-serializable format
                serializable_data = {
                    'export_timestamp': datetime.now().isoformat(),
                    'total_results': len(results),
                    'results': convert_to_json_serializable(results)
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(serializable_data, f, indent=2, ensure_ascii=False)
                    
            elif format.lower() == 'csv':
                # Flatten results for CSV export
                flattened_results = []
                for result in results:
                    if isinstance(result, FullPipelineResult):
                        flattened_results.append({
                            'original_address': result.original_address,
                            'total_time_ms': result.total_processing_time_ms,
                            'final_confidence': result.final_confidence,
                            'overall_success': result.overall_success,
                            'corrections_applied': result.summary.get('corrections_applied', 0),
                            'components_extracted': result.summary.get('components_extracted', 0),
                            'validation_passed': result.summary.get('validation_passed', False),
                            'geocoding_successful': result.summary.get('geocoding_successful', False),
                            'geocoding_method': result.summary.get('geocoding_method', ''),
                            'timestamp': result.timestamp
                        })
                
                if flattened_results:
                    with open(filename, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=flattened_results[0].keys())
                        writer.writeheader()
                        writer.writerows(flattened_results)
            
            print(f"{Colors.OKGREEN}✅ Results exported to: {filename}{Colors.ENDC}")
            
        except Exception as e:
            print(f"{Colors.FAIL}❌ Export failed: {e}{Colors.ENDC}")
    
    def interactive_mode(self):
        """Main interactive mode for the detailed manual tester"""
        
        while True:
            print(f"\n{Colors.HEADER}🎮 DETAILED MANUAL TESTER - INTERACTIVE MODE{Colors.ENDC}")
            print("=" * 80)
            print("Select testing mode:")
            print("  1. Single Address Analysis - Complete pipeline breakdown")
            print("  2. Two Address Comparison - Detailed similarity analysis")
            print("  3. Batch Analysis - Multiple address duplicate detection")
            print("  4. Predefined Test Cases - Use jury test addresses")
            print("  5. Export Results - Save results to file")
            print("  6. Session Summary - View current session statistics")
            print("  0. Exit")
            
            try:
                choice = input(f"\n{Colors.BOLD}Select mode (0-6): {Colors.ENDC}").strip()
                
                if choice == '0':
                    print(f"{Colors.OKCYAN}👋 Exiting detailed manual tester{Colors.ENDC}")
                    break
                    
                elif choice == '1':
                    self._mode_single_address()
                    
                elif choice == '2':
                    self._mode_two_address_comparison()
                    
                elif choice == '3':
                    self._mode_batch_analysis()
                    
                elif choice == '4':
                    self._mode_predefined_test_cases()
                    
                elif choice == '5':
                    self._mode_export_results()
                    
                elif choice == '6':
                    self._display_session_summary()
                    
                else:
                    print(f"{Colors.FAIL}❌ Invalid choice. Please select 0-6.{Colors.ENDC}")
                    
            except (KeyboardInterrupt, EOFError):
                print(f"\n{Colors.OKCYAN}👋 Exiting detailed manual tester{Colors.ENDC}")
                break
            except Exception as e:
                print(f"{Colors.FAIL}❌ An error occurred: {e}{Colors.ENDC}")
    
    def _mode_single_address(self):
        """Mode 1: Single address analysis"""
        print(f"\n{Colors.OKBLUE}📍 SINGLE ADDRESS ANALYSIS MODE{Colors.ENDC}")
        print("Enter an address for complete pipeline analysis:")
        
        try:
            address = input(f"{Colors.BOLD}Address: {Colors.ENDC}").strip()
            
            if not address:
                print(f"{Colors.WARNING}Empty address entered{Colors.ENDC}")
                return
            
            result = self.analyze_single_address(address)
            self.current_session['results'].append(result)
            self.current_session['test_count'] += 1
            
            # Ask if user wants to save this result
            save_choice = input(f"\n{Colors.BOLD}Save this result? (y/n): {Colors.ENDC}").strip().lower()
            if save_choice in ['y', 'yes']:
                self.test_results.append(result)
                
        except (KeyboardInterrupt, EOFError):
            print(f"{Colors.WARNING}Operation cancelled{Colors.ENDC}")
    
    def _mode_two_address_comparison(self):
        """Mode 2: Two address comparison"""
        print(f"\n{Colors.OKBLUE}🔄 TWO ADDRESS COMPARISON MODE{Colors.ENDC}")
        print("Enter two addresses for detailed similarity analysis:")
        
        try:
            addr1 = input(f"{Colors.BOLD}Address 1: {Colors.ENDC}").strip()
            addr2 = input(f"{Colors.BOLD}Address 2: {Colors.ENDC}").strip()
            
            if not addr1 or not addr2:
                print(f"{Colors.WARNING}Both addresses required{Colors.ENDC}")
                return
            
            result = self.compare_two_addresses(addr1, addr2)
            self.current_session['results'].append(result)
            self.current_session['test_count'] += 1
            
            # Ask if user wants to save this result
            save_choice = input(f"\n{Colors.BOLD}Save this result? (y/n): {Colors.ENDC}").strip().lower()
            if save_choice in ['y', 'yes']:
                self.test_results.append(result)
                
        except (KeyboardInterrupt, EOFError):
            print(f"{Colors.WARNING}Operation cancelled{Colors.ENDC}")
    
    def _mode_batch_analysis(self):
        """Mode 3: Batch analysis"""
        print(f"\n{Colors.OKBLUE}📊 BATCH ANALYSIS MODE{Colors.ENDC}")
        print("Enter multiple addresses (one per line, empty line to finish):")
        
        addresses = []
        try:
            while True:
                addr = input(f"{Colors.BOLD}Address {len(addresses)+1}: {Colors.ENDC}").strip()
                if not addr:
                    break
                addresses.append(addr)
            
            if len(addresses) < 2:
                print(f"{Colors.WARNING}At least 2 addresses required for batch analysis{Colors.ENDC}")
                return
            
            result = self.batch_analysis(addresses)
            self.current_session['results'].append(result)
            self.current_session['test_count'] += 1
            
            # Ask if user wants to save this result
            save_choice = input(f"\n{Colors.BOLD}Save this result? (y/n): {Colors.ENDC}").strip().lower()
            if save_choice in ['y', 'yes']:
                self.test_results.append(result)
                
        except (KeyboardInterrupt, EOFError):
            print(f"{Colors.WARNING}Operation cancelled{Colors.ENDC}")
    
    def _mode_predefined_test_cases(self):
        """Mode 4: Predefined test cases"""
        print(f"\n{Colors.OKBLUE}📋 PREDEFINED TEST CASES MODE{Colors.ENDC}")
        print("Select a test case group:")
        
        groups = list(self.predefined_test_cases.keys())
        for i, group in enumerate(groups, 1):
            count = len(self.predefined_test_cases[group])
            print(f"  {i}. {group} ({count} addresses)")
        
        try:
            choice = input(f"\n{Colors.BOLD}Select group (1-{len(groups)}): {Colors.ENDC}").strip()
            
            if choice.isdigit() and 1 <= int(choice) <= len(groups):
                group_name = groups[int(choice) - 1]
                addresses = self.predefined_test_cases[group_name]
                
                print(f"\n{Colors.OKCYAN}Testing {group_name} ({len(addresses)} addresses){Colors.ENDC}")
                
                result = self.batch_analysis(addresses)
                self.current_session['results'].append(result)
                self.current_session['test_count'] += 1
                self.test_results.append(result)  # Auto-save predefined test results
                
            else:
                print(f"{Colors.FAIL}Invalid selection{Colors.ENDC}")
                
        except (KeyboardInterrupt, EOFError):
            print(f"{Colors.WARNING}Operation cancelled{Colors.ENDC}")
    
    def _mode_export_results(self):
        """Mode 5: Export results"""
        if not self.test_results:
            print(f"{Colors.WARNING}No saved results to export{Colors.ENDC}")
            return
        
        print(f"\n{Colors.OKBLUE}💾 EXPORT RESULTS MODE{Colors.ENDC}")
        print(f"Available results: {len(self.test_results)}")
        print("Export formats:")
        print("  1. JSON (detailed)")
        print("  2. CSV (summary)")
        
        try:
            format_choice = input(f"{Colors.BOLD}Select format (1-2): {Colors.ENDC}").strip()
            
            if format_choice == '1':
                self.export_results(self.test_results, format='json')
            elif format_choice == '2':
                self.export_results(self.test_results, format='csv')
            else:
                print(f"{Colors.FAIL}Invalid format selection{Colors.ENDC}")
                
        except (KeyboardInterrupt, EOFError):
            print(f"{Colors.WARNING}Operation cancelled{Colors.ENDC}")
    
    def _display_session_summary(self):
        """Display current session summary"""
        print(f"\n{Colors.HEADER}📊 SESSION SUMMARY{Colors.ENDC}")
        print("=" * 40)
        
        duration = datetime.now() - self.current_session['start_time']
        
        print(f"Session Duration: {duration}")
        print(f"Tests Performed: {self.current_session['test_count']}")
        print(f"Results Saved: {len(self.test_results)}")
        print(f"Start Time: {self.current_session['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print()


def main():
    """Main function to run the detailed manual tester"""
    try:
        tester = DetailedManualTester()
        tester.interactive_mode()
    except Exception as e:
        print(f"{Colors.FAIL}❌ Failed to initialize tester: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()