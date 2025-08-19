"""
Turkish Address Resolution System
GeoIntegratedPipeline - Complete 7-Step Address Processing Pipeline

This module implements the main address processing pipeline that integrates
all 4 core algorithms with database operations to provide complete address
resolution with Turkish language specialization.

Author: Address Resolution Team
Version: 1.0.0
"""

import asyncio
import time
import uuid
import logging
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

# Import all required components
try:
    from address_validator import AddressValidator
except ImportError:
    AddressValidator = None

try:
    from address_corrector import AddressCorrector  
except ImportError:
    AddressCorrector = None

try:
    from address_parser import AddressParser
except ImportError:
    AddressParser = None

try:
    from address_matcher import HybridAddressMatcher
except ImportError:
    HybridAddressMatcher = None

try:
    from database_manager import PostGISManager
except ImportError:
    PostGISManager = None

# Import compliance components
try:
    from duplicate_detector import DuplicateAddressDetector
except ImportError:
    DuplicateAddressDetector = None

try:
    from address_geocoder import AddressGeocoder
except ImportError:
    AddressGeocoder = None

try:
    from kaggle_formatter import KaggleSubmissionFormatter
except ImportError:
    KaggleSubmissionFormatter = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeoIntegratedPipeline:
    """
    Complete 7-step address processing pipeline with geographic lookup.
    
    Integrates all 4 core algorithms (validator, corrector, parser, matcher)
    with PostGIS database operations for comprehensive Turkish address resolution.
    
    Processing Steps:
    1. Address Correction and Normalization
    2. Address Parsing
    3. Address Validation
    4. Geographic Candidate Lookup
    5. Similarity Matching
    6. Confidence Calculation
    7. Result Assembly
    """
    
    def __init__(self, db_connection_string: str):
        """
        Initialize the GeoIntegratedPipeline with all required components.
        
        Args:
            db_connection_string: PostgreSQL connection string for PostGIS database
        """
        self.db_connection_string = db_connection_string
        
        # Initialize all algorithm components
        self.validator = AddressValidator() if AddressValidator else None
        self.corrector = AddressCorrector() if AddressCorrector else None
        self.parser = AddressParser() if AddressParser else None
        self.matcher = HybridAddressMatcher() if HybridAddressMatcher else None
        self.db_manager = PostGISManager(db_connection_string) if PostGISManager else None
        
        # Initialize compliance components
        self.duplicate_detector = DuplicateAddressDetector() if DuplicateAddressDetector else None
        self.geocoder = AddressGeocoder() if AddressGeocoder else None
        self.kaggle_formatter = KaggleSubmissionFormatter() if KaggleSubmissionFormatter else None
        
        # Performance tracking
        self.processed_addresses = []
        self.pipeline_times = []
        self.error_count = 0
        
        # Configuration
        self.max_batch_size = 1000
        self.default_search_radius = 500  # meters
        self.default_candidate_limit = 20
        
        # Confidence calculation weights
        self.confidence_weights = {
            'validation': 0.35,     # 35% - Address validity
            'parsing': 0.25,        # 25% - Parsing quality
            'correction': 0.15,     # 15% - Correction confidence
            'matching': 0.25        # 25% - Best match similarity
        }
        
        logger.info("GeoIntegratedPipeline initialized")
        
    async def initialize(self):
        """Initialize database connection pool."""
        if self.db_manager:
            await self.db_manager.initialize_pool()
            logger.info("Database connection pool initialized")
    
    async def close(self):
        """Close database connection pool."""
        if self.db_manager:
            await self.db_manager.close_pool()
            logger.info("Database connection pool closed")
    
    async def process_address_with_geo_lookup(self, raw_address: str, 
                                            request_id: str = None) -> Dict:
        """
        Process a single address through the complete 7-step pipeline.
        
        Args:
            raw_address: Raw input address string
            request_id: Optional request ID for tracking
            
        Returns:
            Complete processing result with all pipeline steps
        """
        start_time = time.time()
        
        if request_id is None:
            request_id = str(uuid.uuid4())
        
        # Input validation
        if not raw_address or not isinstance(raw_address, str):
            return self._create_error_result(
                request_id, raw_address, "Invalid input: address must be a non-empty string"
            )
        
        if len(raw_address.strip()) < 3:
            return self._create_error_result(
                request_id, raw_address, "Invalid input: address too short (minimum 3 characters)"
            )
        
        try:
            # Initialize step timing
            step_times = {}
            
            # Step 1: Address Correction and Normalization
            step_start = time.time()
            correction_result = await self._step1_address_correction(raw_address)
            step_times['correction'] = (time.time() - step_start) * 1000
            
            if correction_result.get('error'):
                return self._create_error_result(
                    request_id, raw_address, f"Correction failed: {correction_result['error']}"
                )
            
            # Step 2: Address Parsing
            step_start = time.time()
            parsing_result = await self._step2_address_parsing(
                correction_result['corrected']
            )
            step_times['parsing'] = (time.time() - step_start) * 1000
            
            if parsing_result.get('error'):
                return self._create_error_result(
                    request_id, raw_address, f"Parsing failed: {parsing_result['error']}"
                )
            
            # Step 3: Address Validation
            step_start = time.time()
            validation_input = {
                'corrected_address': correction_result['corrected'],
                'parsed_components': parsing_result['components']
            }
            validation_result = await self._step3_address_validation(validation_input)
            step_times['validation'] = (time.time() - step_start) * 1000
            
            # Step 4: Geographic Candidate Lookup
            step_start = time.time()
            geo_candidates = await self._step4_geographic_lookup(parsing_result['components'])
            step_times['geo_lookup'] = (time.time() - step_start) * 1000
            
            # Step 5: Similarity Matching
            step_start = time.time()
            matches = await self._step5_similarity_matching(
                correction_result['corrected'],
                parsing_result['components'],
                geo_candidates
            )
            step_times['matching'] = (time.time() - step_start) * 1000
            
            # Step 6: Confidence Calculation
            step_start = time.time()
            final_confidence = self._step6_confidence_calculation(
                validation_result, parsing_result, correction_result, matches
            )
            step_times['confidence_calc'] = (time.time() - step_start) * 1000
            
            # Step 7: Result Assembly
            total_time = (time.time() - start_time) * 1000
            
            result = {
                'request_id': request_id,
                'input_address': raw_address,
                'corrected_address': correction_result['corrected'],
                'parsed_components': parsing_result['components'],
                'validation_result': validation_result,
                'matches': matches,
                'final_confidence': final_confidence,
                'processing_time_ms': total_time,
                'status': 'completed',
                'corrections_applied': correction_result.get('corrections'),
                'pipeline_details': {
                    'step_times_ms': step_times,
                    'total_candidates_found': len(geo_candidates),
                    'total_matches_calculated': len(matches)
                }
            }
            
            # Track performance
            self.processed_addresses.append(request_id)
            self.pipeline_times.append(total_time)
            
            logger.info(f"Address processed successfully in {total_time:.2f}ms")
            return result
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Pipeline error: {e}")
            return self._create_error_result(request_id, raw_address, str(e))
    
    async def process_batch_addresses(self, addresses: List[str]) -> Dict:
        """
        Process multiple addresses in batch.
        
        Args:
            addresses: List of raw address strings
            
        Returns:
            Batch processing results with summary statistics
        """
        if not addresses:
            raise ValueError("Empty address list provided")
        
        if len(addresses) > self.max_batch_size:
            raise ValueError(f"Batch size {len(addresses)} exceeds maximum {self.max_batch_size}")
        
        batch_start_time = time.time()
        results = []
        
        logger.info(f"Starting batch processing of {len(addresses)} addresses")
        
        # Process addresses concurrently (but with limited concurrency)
        semaphore = asyncio.Semaphore(10)  # Limit concurrent operations
        
        async def process_single(address):
            async with semaphore:
                return await self.process_address_with_geo_lookup(address)
        
        # Execute all addresses
        results = await asyncio.gather(
            *[process_single(addr) for addr in addresses],
            return_exceptions=False
        )
        
        # Calculate batch statistics
        batch_end_time = time.time()
        batch_duration = batch_end_time - batch_start_time
        
        successful_count = sum(1 for r in results if r.get('status') == 'completed')
        error_count = len(results) - successful_count
        throughput = len(addresses) / max(batch_duration, 0.001)  # Avoid division by zero
        
        avg_confidence = 0.0
        if successful_count > 0:
            total_confidence = sum(r.get('final_confidence', 0) for r in results 
                                 if r.get('status') == 'completed')
            avg_confidence = total_confidence / successful_count
        
        batch_summary = {
            'batch_size': len(addresses),
            'successful_count': successful_count,
            'error_count': error_count,
            'total_processing_time_seconds': batch_duration,
            'throughput_per_second': throughput,
            'average_confidence': avg_confidence
        }
        
        logger.info(f"Batch completed: {successful_count}/{len(addresses)} successful, "
                   f"{throughput:.1f} addr/sec")
        
        return {
            'results': results,
            'batch_summary': batch_summary
        }
    
    async def find_duplicates_in_batch(self, addresses: List[str]) -> List[List[int]]:
        """
        Find potential duplicate addresses in a batch.
        
        Args:
            addresses: List of address strings
            
        Returns:
            List of duplicate groups, each containing indices of similar addresses
        """
        if not addresses:
            return []
        
        logger.info(f"Finding duplicates in batch of {len(addresses)} addresses")
        
        # Process all addresses to get normalized forms
        processed_addresses = []
        for i, address in enumerate(addresses):
            result = await self.process_address_with_geo_lookup(address)
            processed_addresses.append({
                'index': i,
                'original': address,
                'corrected': result.get('corrected_address', address),
                'components': result.get('parsed_components', {}),
                'coordinates': result.get('parsed_components', {}).get('coordinates')
            })
        
        # Find duplicates using similarity matching
        duplicate_groups = []
        processed_indices = set()
        
        for i, addr1 in enumerate(processed_addresses):
            if i in processed_indices:
                continue
                
            current_group = [i]
            
            for j, addr2 in enumerate(processed_addresses[i+1:], i+1):
                if j in processed_indices:
                    continue
                
                # Calculate similarity between addresses
                similarity = await self._calculate_address_similarity(addr1, addr2)
                
                # Consider as duplicate if similarity > 0.8
                if similarity > 0.8:
                    current_group.append(j)
                    processed_indices.add(j)
            
            if len(current_group) > 1:
                duplicate_groups.append(current_group)
                processed_indices.update(current_group)
        
        logger.info(f"Found {len(duplicate_groups)} duplicate groups")
        return duplicate_groups
    
    # COMPLIANCE INTEGRATION METHODS
    
    async def process_for_duplicate_detection(self, addresses: List[str]) -> Dict[str, Any]:
        """
        REQUIREMENT: Process addresses and find duplicate groups
        
        Args:
            addresses: List of address strings to process and detect duplicates
            
        Returns:
            {
                "processed_addresses": List[Dict],  # Processed address results
                "duplicate_groups": List[List[int]], # Groups of duplicate indices
                "statistics": Dict                   # Duplicate detection stats
            }
        """
        if not addresses:
            return {
                "processed_addresses": [],
                "duplicate_groups": [],
                "statistics": {"total_addresses": 0, "duplicate_groups": 0}
            }
        
        start_time = time.time()
        logger.info(f"Processing {len(addresses)} addresses for duplicate detection")
        
        try:
            # Step 1: Process all addresses through the pipeline
            processed_results = []
            for address in addresses:
                result = await self.process_address_with_geo_lookup(address)
                processed_results.append(result)
            
            # Step 2: Use DuplicateDetector if available
            if self.duplicate_detector:
                duplicate_groups = self.duplicate_detector.find_duplicate_groups(addresses)
                statistics = self.duplicate_detector.get_duplicate_statistics(addresses)
            else:
                # Fallback: Use existing pipeline duplicate detection
                duplicate_groups = await self.find_duplicates_in_batch(addresses)
                statistics = {
                    "total_addresses": len(addresses),
                    "duplicate_groups": len([g for g in duplicate_groups if len(g) > 1]),
                    "total_duplicates": sum(len(g) - 1 for g in duplicate_groups if len(g) > 1),
                    "unique_addresses": len(duplicate_groups)
                }
            
            processing_time = (time.time() - start_time) * 1000
            
            logger.info(f"Duplicate detection completed in {processing_time:.2f}ms")
            logger.info(f"Found {statistics.get('duplicate_groups', 0)} duplicate groups")
            
            return {
                "processed_addresses": processed_results,
                "duplicate_groups": duplicate_groups,
                "statistics": statistics,
                "processing_time_ms": processing_time,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Error in duplicate detection processing: {e}")
            return {
                "processed_addresses": [],
                "duplicate_groups": [],
                "statistics": {"error": str(e)},
                "processing_time_ms": 0,
                "status": "error"
            }
    
    async def process_with_geocoding(self, addresses: List[str]) -> Dict[str, Any]:
        """
        REQUIREMENT: Process addresses with enhanced geocoding
        
        Args:
            addresses: List of address strings to process and geocode
            
        Returns:
            {
                "geocoded_results": List[Dict],  # Results with coordinates
                "geocoding_statistics": Dict,    # Success rates and accuracy
                "processing_summary": Dict       # Performance metrics
            }
        """
        if not addresses:
            return {
                "geocoded_results": [],
                "geocoding_statistics": {"total_addresses": 0, "success_rate": 0},
                "processing_summary": {}
            }
        
        start_time = time.time()
        logger.info(f"Processing {len(addresses)} addresses with enhanced geocoding")
        
        try:
            geocoded_results = []
            
            for address in addresses:
                # Step 1: Process through main pipeline
                pipeline_result = await self.process_address_with_geo_lookup(address)
                
                # Step 2: Enhanced geocoding if geocoder available
                if self.geocoder:
                    geocoding_result = self.geocoder.geocode_turkish_address(address)
                    
                    # Merge results
                    enhanced_result = {
                        **pipeline_result,
                        "geocoding_result": geocoding_result,
                        "enhanced_coordinates": {
                            "latitude": geocoding_result.get("latitude"),
                            "longitude": geocoding_result.get("longitude"),
                            "geocoding_confidence": geocoding_result.get("confidence", 0.0),
                            "geocoding_method": geocoding_result.get("method", "unknown")
                        }
                    }
                else:
                    # Use pipeline's existing coordinate extraction
                    enhanced_result = pipeline_result
                
                geocoded_results.append(enhanced_result)
            
            # Calculate statistics
            if self.geocoder:
                geocoding_stats = self.geocoder.get_geocoding_statistics(addresses)
            else:
                # Fallback statistics
                successful_coords = sum(1 for r in geocoded_results 
                                      if r.get("enhanced_coordinates", {}).get("latitude") is not None)
                geocoding_stats = {
                    "total_addresses": len(addresses),
                    "successful_geocoding": successful_coords,
                    "success_rate": successful_coords / len(addresses) if addresses else 0
                }
            
            processing_time = (time.time() - start_time) * 1000
            
            processing_summary = {
                "total_processing_time_ms": processing_time,
                "average_time_per_address_ms": processing_time / len(addresses) if addresses else 0,
                "throughput_per_second": len(addresses) / (processing_time / 1000) if processing_time > 0 else 0
            }
            
            logger.info(f"Enhanced geocoding completed in {processing_time:.2f}ms")
            logger.info(f"Geocoding success rate: {geocoding_stats.get('success_rate', 0):.1%}")
            
            return {
                "geocoded_results": geocoded_results,
                "geocoding_statistics": geocoding_stats,
                "processing_summary": processing_summary,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Error in enhanced geocoding processing: {e}")
            return {
                "geocoded_results": [],
                "geocoding_statistics": {"error": str(e)},
                "processing_summary": {"error": str(e)},
                "status": "error"
            }
    
    async def format_for_kaggle_submission(self, addresses: List[str]) -> Dict[str, Any]:
        """
        REQUIREMENT: Process addresses and format for competition
        
        Args:
            addresses: List of address strings to process and format
            
        Returns:
            {
                "submission_dataframe": pandas.DataFrame,  # submission format
                "validation_result": Dict,                 # Format validation
                "processing_summary": Dict                 # Processing metrics
            }
        """
        if not addresses:
            return {
                "submission_dataframe": None,
                "validation_result": {"is_valid": False, "errors": ["Empty address list"]},
                "processing_summary": {}
            }
        
        start_time = time.time()
        logger.info(f"Processing {len(addresses)} addresses for Kaggle submission")
        
        try:
            # Step 1: Process all addresses through enhanced pipeline
            geocoding_result = await self.process_with_geocoding(addresses)
            
            if geocoding_result.get("status") != "completed":
                raise Exception("Enhanced geocoding processing failed")
            
            processed_addresses = geocoding_result["geocoded_results"]
            
            # Step 2: Format for Kaggle submission
            if self.kaggle_formatter:
                submission_df = self.kaggle_formatter.format_for_teknofest_submission(processed_addresses)
                validation_result = self.kaggle_formatter.validate_submission_format(submission_df)
            else:
                # Fallback: Create basic submission format
                import pandas as pd
                
                basic_data = []
                for i, result in enumerate(processed_addresses):
                    components = result.get("parsed_components", {})
                    coords = result.get("enhanced_coordinates", {})
                    
                    basic_data.append({
                        "id": i + 1,
                        "il": components.get("il", ""),
                        "ilce": components.get("ilce", ""),
                        "mahalle": components.get("mahalle", ""),
                        "cadde": components.get("cadde", ""),
                        "sokak": components.get("sokak", ""),
                        "bina_no": components.get("bina_no", ""),
                        "daire_no": components.get("daire_no", ""),
                        "confidence": result.get("final_confidence", 0.0),
                        "latitude": coords.get("latitude"),
                        "longitude": coords.get("longitude"),
                        "duplicate_group": 0
                    })
                
                submission_df = pd.DataFrame(basic_data)
                validation_result = {"is_valid": True, "errors": [], "fallback_mode": True}
            
            processing_time = (time.time() - start_time) * 1000
            
            processing_summary = {
                "total_processing_time_ms": processing_time,
                "total_addresses_processed": len(addresses),
                "submission_rows": len(submission_df) if submission_df is not None else 0,
                "validation_status": "valid" if validation_result.get("is_valid") else "invalid",
                "throughput_per_second": len(addresses) / (processing_time / 1000) if processing_time > 0 else 0
            }
            
            logger.info(f"Kaggle submission formatting completed in {processing_time:.2f}ms")
            logger.info(f"Created submission with {len(submission_df)} rows")
            
            if not validation_result.get("is_valid"):
                logger.warning(f"Submission validation issues: {validation_result.get('errors', [])}")
            
            return {
                "submission_dataframe": submission_df,
                "validation_result": validation_result,
                "processing_summary": processing_summary,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Error in Kaggle submission formatting: {e}")
            return {
                "submission_dataframe": None,
                "validation_result": {"is_valid": False, "errors": [str(e)]},
                "processing_summary": {"error": str(e)},
                "status": "error"
            }
    
    # Private methods for pipeline steps
    
    async def _step1_address_correction(self, raw_address: str) -> Dict:
        """Step 1: Address correction and normalization."""
        if not self.corrector:
            # Fallback mode - basic normalization
            corrected = raw_address.strip()
            return {
                'corrected': corrected,
                'corrections': [],
                'confidence': 1.0
            }
        
        try:
            result = self.corrector.correct_address(raw_address)
            # Ensure consistent key naming
            if 'corrected_address' in result and 'corrected' not in result:
                result['corrected'] = result['corrected_address']
            return result
        except Exception as e:
            return {'error': str(e)}
    
    async def _step2_address_parsing(self, corrected_address: str) -> Dict:
        """Step 2: Address parsing into components."""
        if not self.parser:
            # Fallback mode - basic parsing
            return {
                'components': {'raw': corrected_address},
                'confidence': 0.5
            }
        
        try:
            result = self.parser.parse_address(corrected_address)
            return result
        except Exception as e:
            return {'error': str(e)}
    
    async def _step3_address_validation(self, validation_input: Dict) -> Dict:
        """Step 3: Address validation."""
        if not self.validator:
            # Fallback mode - assume valid
            return {
                'is_valid': True,
                'confidence_score': 0.8,
                'validation_details': {'fallback_mode': True}
            }
        
        try:
            result = self.validator.validate_address(validation_input)
            return result
        except Exception as e:
            logger.warning(f"Validation failed: {e}")
            return {
                'is_valid': False,
                'confidence_score': 0.0,
                'validation_details': {'error': str(e)}
            }
    
    async def _step4_geographic_lookup(self, components: Dict) -> List[Dict]:
        """Step 4: Geographic candidate lookup from database."""
        candidates = []
        
        if not self.db_manager:
            return candidates
        
        try:
            # Try coordinate-based lookup first
            coordinates = components.get('coordinates')
            if coordinates and isinstance(coordinates, dict):
                if 'lat' in coordinates and 'lon' in coordinates:
                    spatial_results = await self.db_manager.find_nearby_addresses(
                        coordinates, 
                        radius_meters=self.default_search_radius,
                        limit=self.default_candidate_limit
                    )
                    candidates.extend(spatial_results)
            
            # Try administrative hierarchy lookup
            hierarchy_results = await self.db_manager.find_by_admin_hierarchy(
                il=components.get('il'),
                ilce=components.get('ilce'),
                mahalle=components.get('mahalle'),
                limit=self.default_candidate_limit
            )
            
            # Merge results, avoiding duplicates
            existing_ids = {c.get('id') for c in candidates if c.get('id')}
            for result in hierarchy_results:
                if result.get('id') not in existing_ids:
                    candidates.append(result)
            
        except Exception as e:
            logger.warning(f"Geographic lookup failed: {e}")
        
        return candidates[:self.default_candidate_limit]
    
    async def _step5_similarity_matching(self, corrected_address: str, 
                                       components: Dict, 
                                       candidates: List[Dict]) -> List[Dict]:
        """Step 5: Calculate similarity scores for candidates."""
        matches = []
        
        if not candidates or not self.matcher:
            return matches
        
        try:
            for candidate in candidates:
                # Prepare candidate data for similarity calculation
                candidate_components = candidate.get('parsed_components', {})
                
                similarity_result = self.matcher.calculate_hybrid_similarity(
                    corrected_address,
                    candidate.get('corrected_address', candidate.get('raw_address', ''))
                )
                
                # Add candidate info to match result
                match_info = {
                    'candidate_id': candidate.get('id'),
                    'candidate_address': candidate.get('raw_address'),
                    'candidate_corrected': candidate.get('corrected_address'),
                    'candidate_components': candidate_components,
                    'distance_meters': candidate.get('distance_meters'),
                    **similarity_result
                }
                
                matches.append(match_info)
            
            # Sort by overall similarity (descending)
            matches.sort(key=lambda x: x.get('overall_similarity', 0), reverse=True)
            
        except Exception as e:
            logger.warning(f"Similarity matching failed: {e}")
        
        return matches
    
    def _step6_confidence_calculation(self, validation_result: Dict, 
                                    parsing_result: Dict,
                                    correction_result: Dict, 
                                    matches: List[Dict]) -> float:
        """Step 6: Calculate final weighted confidence score."""
        
        # Extract individual confidence scores
        validation_confidence = validation_result.get('confidence_score', 0.0)
        parsing_confidence = parsing_result.get('confidence', 0.0)
        correction_confidence = correction_result.get('confidence', 1.0)
        
        # Best match similarity (0 if no matches)
        matching_confidence = 0.0
        if matches:
            best_match = matches[0]
            matching_confidence = best_match.get('overall_similarity', 0.0)
        
        # Calculate weighted final confidence
        final_confidence = (
            validation_confidence * self.confidence_weights['validation'] +
            parsing_confidence * self.confidence_weights['parsing'] +
            correction_confidence * self.confidence_weights['correction'] +
            matching_confidence * self.confidence_weights['matching']
        )
        
        # Ensure confidence is within [0, 1] range
        return min(max(final_confidence, 0.0), 1.0)
    
    def _create_error_result(self, request_id: str, input_address: str, error_message: str) -> Dict:
        """Create standardized error result."""
        return {
            'request_id': request_id,
            'input_address': input_address,
            'corrected_address': '',
            'parsed_components': {},
            'validation_result': {'is_valid': False, 'confidence_score': 0.0},
            'matches': [],
            'final_confidence': 0.0,
            'processing_time_ms': 0.0,
            'status': 'error',
            'error_message': error_message,
            'corrections_applied': None,
            'pipeline_details': {
                'step_times_ms': {},
                'total_candidates_found': 0,
                'total_matches_calculated': 0
            }
        }
    
    async def _calculate_address_similarity(self, addr1: Dict, addr2: Dict) -> float:
        """Calculate similarity between two processed addresses."""
        if not self.matcher:
            # Fallback - simple string similarity
            corrected1 = addr1.get('corrected', '').lower()
            corrected2 = addr2.get('corrected', '').lower()
            
            if corrected1 == corrected2:
                return 1.0
            elif corrected1 in corrected2 or corrected2 in corrected1:
                return 0.8
            else:
                return 0.0
        
        try:
            result = self.matcher.calculate_hybrid_similarity(
                addr1.get('corrected', ''),
                addr2.get('corrected', '')
            )
            return result.get('overall_similarity', 0.0)
        except Exception:
            return 0.0


# Async context manager for pipeline lifecycle
@asynccontextmanager
async def pipeline_context(db_connection_string: str):
    """Context manager for GeoIntegratedPipeline lifecycle management."""
    pipeline = GeoIntegratedPipeline(db_connection_string)
    try:
        await pipeline.initialize()
        yield pipeline
    finally:
        await pipeline.close()


# Utility functions
async def process_single_address(db_connection_string: str, address: str) -> Dict:
    """Convenience function to process a single address."""
    async with pipeline_context(db_connection_string) as pipeline:
        return await pipeline.process_address_with_geo_lookup(address)


async def process_address_batch(db_connection_string: str, addresses: List[str]) -> Dict:
    """Convenience function to process a batch of addresses."""
    async with pipeline_context(db_connection_string) as pipeline:
        return await pipeline.process_batch_addresses(addresses)


# Performance monitoring
class PipelinePerformanceMonitor:
    """Monitor and report pipeline performance metrics."""
    
    def __init__(self, pipeline: GeoIntegratedPipeline):
        self.pipeline = pipeline
    
    def get_performance_stats(self) -> Dict:
        """Get current performance statistics."""
        if not self.pipeline.pipeline_times:
            return {
                'total_processed': 0,
                'average_time_ms': 0.0,
                'max_time_ms': 0.0,
                'min_time_ms': 0.0,
                'error_rate': 0.0
            }
        
        times = self.pipeline.pipeline_times
        total_processed = len(self.pipeline.processed_addresses)
        
        return {
            'total_processed': total_processed,
            'average_time_ms': sum(times) / len(times),
            'max_time_ms': max(times),
            'min_time_ms': min(times),
            'error_rate': self.pipeline.error_count / max(total_processed, 1),
            'addresses_per_second': len(times) / (sum(times) / 1000) if times else 0
        }
    
    def reset_stats(self):
        """Reset performance statistics."""
        self.pipeline.processed_addresses.clear()
        self.pipeline.pipeline_times.clear()
        self.pipeline.error_count = 0


if __name__ == "__main__":
    # Example usage and testing
    async def main():
        print("GeoIntegratedPipeline - Demo")
        
        # Test with sample address
        test_address = "istanbul kadikoy moda mah caferaga sk 10"
        db_connection = "postgresql://test:test@localhost:5432/addresses"
        
        try:
            result = await process_single_address(db_connection, test_address)
            print(f"✅ Processing result:")
            print(f"   - Status: {result['status']}")
            print(f"   - Confidence: {result['final_confidence']:.3f}")
            print(f"   - Processing time: {result['processing_time_ms']:.2f}ms")
            print(f"   - Corrected: {result['corrected_address']}")
            
        except Exception as e:
            print(f"❌ Processing failed: {e}")
    
    # Run demo
    asyncio.run(main())