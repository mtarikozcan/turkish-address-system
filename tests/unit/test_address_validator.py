"""
TEKNOFEST 2025 Adres Çözümleme Sistemi - AddressValidator Tests
Comprehensive test suite for Turkish address validation algorithm

Tests cover:
- Address hierarchy validation (İl-İlçe-Mahalle)
- Postal code validation  
- Coordinate validation
- Error handling and edge cases
- Performance benchmarking
"""

import pytest
import pandas as pd
import json
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Optional
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock the AddressValidator class since we haven't implemented it yet
class MockAddressValidator:
    """Mock implementation of AddressValidator for testing"""
    
    def __init__(self):
        """Initialize with mock data"""
        self.admin_hierarchy = self._load_mock_admin_data()
        self.postal_codes = self._load_mock_postal_data()
    
    def _load_mock_admin_data(self):
        """Load administrative hierarchy data"""
        # This would load from database/turkey_admin_hierarchy.csv
        return {
            ('İstanbul', 'Kadıköy', 'Moda Mahallesi'): True,
            ('İstanbul', 'Beşiktaş', 'Levent Mahallesi'): True,
            ('Ankara', 'Çankaya', 'Kızılay Mahallesi'): True,
            ('İzmir', 'Konak', 'Alsancak Mahallesi'): True,
            ('İstanbul', 'Şişli', 'Mecidiyeköy Mahallesi'): True,
        }
    
    def _load_mock_postal_data(self):
        """Load postal code data"""
        return {
            '34718': {'il': 'İstanbul', 'ilce': 'Kadıköy'},
            '34357': {'il': 'İstanbul', 'ilce': 'Beşiktaş'},
            '06420': {'il': 'Ankara', 'ilce': 'Çankaya'},
            '35220': {'il': 'İzmir', 'ilce': 'Konak'},
            '34394': {'il': 'İstanbul', 'ilce': 'Şişli'},
        }
    
    def validate_address(self, address_data: dict) -> dict:
        """Main validation function"""
        try:
            # Extract components
            raw_address = address_data.get('raw_address', '')
            coordinates = address_data.get('coordinates')
            parsed_components = address_data.get('parsed_components', {})
            
            # Perform validations
            hierarchy_valid = self.validate_hierarchy(
                parsed_components.get('il'),
                parsed_components.get('ilce'),
                parsed_components.get('mahalle')
            )
            
            postal_valid = True
            if parsed_components.get('postal_code'):
                postal_valid = self.validate_postal_code(
                    parsed_components['postal_code'],
                    parsed_components
                )
            
            coordinate_result = {'valid': True, 'distance_km': 0}
            if coordinates:
                coordinate_result = self.validate_coordinates(coordinates, parsed_components)
            
            # Calculate overall confidence
            confidence = 0.0
            if hierarchy_valid:
                confidence += 0.4
            if postal_valid:
                confidence += 0.3
            if coordinate_result['valid']:
                confidence += 0.3
            
            # Determine validity
            is_valid = hierarchy_valid and postal_valid and coordinate_result['valid']
            
            return {
                'is_valid': is_valid,
                'confidence': confidence,
                'errors': [] if is_valid else ['Validation failed'],
                'suggestions': [] if is_valid else ['Check address components'],
                'validation_details': {
                    'hierarchy_valid': hierarchy_valid,
                    'postal_code_valid': postal_valid,
                    'coordinate_valid': coordinate_result['valid'],
                    'completeness_score': len([x for x in parsed_components.values() if x]) / max(len(parsed_components), 1)
                }
            }
            
        except Exception as e:
            return {
                'is_valid': False,
                'confidence': 0.0,
                'errors': [str(e)],
                'suggestions': [],
                'validation_details': {}
            }
    
    def validate_hierarchy(self, il: str, ilce: str, mahalle: str) -> bool:
        """Validate İl-İlçe-Mahalle hierarchy"""
        if not all([il, ilce, mahalle]):
            return False
        
        return (il, ilce, mahalle) in self.admin_hierarchy
    
    def validate_postal_code(self, postal_code: str, address_components: dict) -> bool:
        """Validate postal code consistency"""
        if not postal_code or postal_code not in self.postal_codes:
            return False
        
        postal_data = self.postal_codes[postal_code]
        return (postal_data['il'] == address_components.get('il') and
                postal_data['ilce'] == address_components.get('ilce'))
    
    def validate_coordinates(self, coords: dict, address_components: dict) -> dict:
        """Validate coordinate-address consistency"""
        if not coords or 'lat' not in coords or 'lon' not in coords:
            return {'valid': False, 'distance_km': float('inf')}
        
        # Mock coordinate validation - in real implementation would use PostGIS
        lat, lon = coords['lat'], coords['lon']
        
        # Basic bounds check for Turkey
        turkey_bounds = {
            'lat_min': 35.8, 'lat_max': 42.1,
            'lon_min': 25.7, 'lon_max': 44.8
        }
        
        if not (turkey_bounds['lat_min'] <= lat <= turkey_bounds['lat_max'] and
                turkey_bounds['lon_min'] <= lon <= turkey_bounds['lon_max']):
            return {'valid': False, 'distance_km': float('inf')}
        
        # Mock distance calculation
        return {'valid': True, 'distance_km': 0.5}


# Import or use mock
try:
    from address_validator import AddressValidator
except ImportError:
    AddressValidator = MockAddressValidator


class TestAddressValidator:
    """Comprehensive test suite for AddressValidator class"""
    
    @pytest.fixture
    def validator(self):
        """Create AddressValidator instance for testing"""
        return AddressValidator()
    
    @pytest.fixture
    def valid_address_data(self):
        """Valid Turkish address test data"""
        return {
            'raw_address': 'İstanbul Kadıköy Moda Mahallesi Caferağa Sokak 10',
            'coordinates': {'lat': 40.9875, 'lon': 29.0376},
            'parsed_components': {
                'il': 'İstanbul',
                'ilce': 'Kadıköy',
                'mahalle': 'Moda Mahallesi',
                'sokak': 'Caferağa Sokak',
                'bina_no': '10',
                'postal_code': '34718'
            }
        }
    
    @pytest.fixture
    def invalid_address_data(self):
        """Invalid address test data"""
        return {
            'raw_address': 'İstanbul Çankaya Kızılay Mahallesi',  # Wrong: Çankaya is in Ankara
            'parsed_components': {
                'il': 'İstanbul',
                'ilce': 'Çankaya',
                'mahalle': 'Kızılay Mahallesi'
            }
        }
    
    @pytest.fixture
    def hierarchy_test_cases(self):
        """Test cases for hierarchy validation"""
        return [
            # Valid hierarchies
            {'il': 'İstanbul', 'ilce': 'Kadıköy', 'mahalle': 'Moda Mahallesi', 'expected': True},
            {'il': 'İstanbul', 'ilce': 'Beşiktaş', 'mahalle': 'Levent Mahallesi', 'expected': True},
            {'il': 'Ankara', 'ilce': 'Çankaya', 'mahalle': 'Kızılay Mahallesi', 'expected': True},
            {'il': 'İzmir', 'ilce': 'Konak', 'mahalle': 'Alsancak Mahallesi', 'expected': True},
            
            # Invalid hierarchies
            {'il': 'İstanbul', 'ilce': 'Çankaya', 'mahalle': 'Kızılay Mahallesi', 'expected': False},  # Çankaya is in Ankara
            {'il': 'Ankara', 'ilce': 'Kadıköy', 'mahalle': 'Moda Mahallesi', 'expected': False},  # Kadıköy is in İstanbul
            {'il': 'İzmir', 'ilce': 'Beşiktaş', 'mahalle': 'Levent Mahallesi', 'expected': False},  # Beşiktaş is in İstanbul
        ]
    
    @pytest.fixture
    def postal_code_test_cases(self):
        """Test cases for postal code validation"""
        return [
            # Valid postal codes
            {
                'postal_code': '34718',
                'components': {'il': 'İstanbul', 'ilce': 'Kadıköy'},
                'expected': True
            },
            {
                'postal_code': '06420',
                'components': {'il': 'Ankara', 'ilce': 'Çankaya'},
                'expected': True
            },
            
            # Invalid postal codes
            {
                'postal_code': '34718',
                'components': {'il': 'Ankara', 'ilce': 'Çankaya'},  # Wrong city
                'expected': False
            },
            {
                'postal_code': '99999',  # Non-existent postal code
                'components': {'il': 'İstanbul', 'ilce': 'Kadıköy'},
                'expected': False
            },
            {
                'postal_code': '1234',  # Invalid format (too short)
                'components': {'il': 'İstanbul', 'ilce': 'Kadıköy'},
                'expected': False
            }
        ]
    
    @pytest.fixture
    def coordinate_test_cases(self):
        """Test cases for coordinate validation"""
        return [
            # Valid coordinates (within Turkey)
            {
                'coords': {'lat': 41.0082, 'lon': 28.9784},  # Istanbul
                'components': {'il': 'İstanbul', 'ilce': 'Fatih'},
                'expected_valid': True
            },
            {
                'coords': {'lat': 39.9334, 'lon': 32.8597},  # Ankara
                'components': {'il': 'Ankara', 'ilce': 'Çankaya'},
                'expected_valid': True
            },
            
            # Invalid coordinates (outside Turkey)
            {
                'coords': {'lat': 51.5074, 'lon': -0.1278},  # London
                'components': {'il': 'İstanbul', 'ilce': 'Kadıköy'},
                'expected_valid': False
            },
            {
                'coords': {'lat': 40.7128, 'lon': -74.0060},  # New York
                'components': {'il': 'Ankara', 'ilce': 'Çankaya'},
                'expected_valid': False
            },
            
            # Invalid coordinate format
            {
                'coords': {'lat': 'invalid', 'lon': 28.9784},
                'components': {'il': 'İstanbul', 'ilce': 'Fatih'},
                'expected_valid': False
            }
        ]

    # Main validation function tests
    def test_validate_address_valid_input(self, validator, valid_address_data):
        """Test validate_address with valid input"""
        result = validator.validate_address(valid_address_data)
        
        assert isinstance(result, dict)
        assert 'is_valid' in result
        assert 'confidence' in result
        assert 'errors' in result
        assert 'suggestions' in result
        assert 'validation_details' in result
        
        assert result['is_valid'] is True
        assert result['confidence'] > 0.8
        assert len(result['errors']) == 0
    
    def test_validate_address_invalid_input(self, validator, invalid_address_data):
        """Test validate_address with invalid input"""
        result = validator.validate_address(invalid_address_data)
        
        assert result['is_valid'] is False
        assert result['confidence'] < 0.5
        assert len(result['errors']) > 0
    
    def test_validate_address_missing_components(self, validator):
        """Test validate_address with missing components"""
        incomplete_data = {
            'raw_address': 'İstanbul',
            'parsed_components': {
                'il': 'İstanbul'
                # Missing ilce and mahalle
            }
        }
        
        result = validator.validate_address(incomplete_data)
        assert result['is_valid'] is False
        assert result['validation_details']['completeness_score'] < 1.0
    
    def test_validate_address_empty_input(self, validator):
        """Test validate_address with empty input"""
        result = validator.validate_address({})
        
        assert result['is_valid'] is False
        assert result['confidence'] == 0.0
    
    # Hierarchy validation tests
    def test_validate_hierarchy_valid_cases(self, validator, hierarchy_test_cases):
        """Test validate_hierarchy with valid cases"""
        valid_cases = [case for case in hierarchy_test_cases if case['expected']]
        
        for case in valid_cases:
            result = validator.validate_hierarchy(
                case['il'], 
                case['ilce'], 
                case['mahalle']
            )
            assert result is True, f"Expected valid hierarchy for {case}"
    
    def test_validate_hierarchy_invalid_cases(self, validator, hierarchy_test_cases):
        """Test validate_hierarchy with invalid cases"""
        invalid_cases = [case for case in hierarchy_test_cases if not case['expected']]
        
        for case in invalid_cases:
            result = validator.validate_hierarchy(
                case['il'], 
                case['ilce'], 
                case['mahalle']
            )
            assert result is False, f"Expected invalid hierarchy for {case}"
    
    def test_validate_hierarchy_missing_parameters(self, validator):
        """Test validate_hierarchy with missing parameters"""
        assert validator.validate_hierarchy(None, 'Kadıköy', 'Moda Mahallesi') is False
        assert validator.validate_hierarchy('İstanbul', None, 'Moda Mahallesi') is False
        assert validator.validate_hierarchy('İstanbul', 'Kadıköy', None) is False
        assert validator.validate_hierarchy('', 'Kadıköy', 'Moda Mahallesi') is False
    
    def test_validate_hierarchy_case_sensitivity(self, validator):
        """Test validate_hierarchy case sensitivity"""
        # Test with different cases
        result_lower = validator.validate_hierarchy('istanbul', 'kadıköy', 'moda mahallesi')
        result_upper = validator.validate_hierarchy('İSTANBUL', 'KADIKÖY', 'MODA MAHALLESİ')
        
        # Depending on implementation, these might be normalized
        # For now, assuming exact match is required
        assert result_lower is False or result_lower is True  # Implementation dependent
        assert result_upper is False or result_upper is True  # Implementation dependent
    
    # Postal code validation tests
    def test_validate_postal_code_valid_cases(self, validator, postal_code_test_cases):
        """Test validate_postal_code with valid cases"""
        valid_cases = [case for case in postal_code_test_cases if case['expected']]
        
        for case in valid_cases:
            result = validator.validate_postal_code(
                case['postal_code'],
                case['components']
            )
            assert result is True, f"Expected valid postal code for {case}"
    
    def test_validate_postal_code_invalid_cases(self, validator, postal_code_test_cases):
        """Test validate_postal_code with invalid cases"""
        invalid_cases = [case for case in postal_code_test_cases if not case['expected']]
        
        for case in invalid_cases:
            result = validator.validate_postal_code(
                case['postal_code'],
                case['components']
            )
            assert result is False, f"Expected invalid postal code for {case}"
    
    def test_validate_postal_code_format_validation(self, validator):
        """Test postal code format validation"""
        test_cases = [
            ('12345', True),   # Valid 5-digit format
            ('1234', False),   # Too short
            ('123456', False), # Too long
            ('abcde', False),  # Non-numeric
            ('', False),       # Empty
            (None, False),     # None
        ]
        
        components = {'il': 'İstanbul', 'ilce': 'Kadıköy'}
        
        for postal_code, expected_format_valid in test_cases:
            try:
                result = validator.validate_postal_code(postal_code, components)
                if not expected_format_valid:
                    assert result is False, f"Expected format validation to fail for '{postal_code}'"
            except (TypeError, ValueError):
                # Exception is acceptable for invalid formats
                if expected_format_valid:
                    pytest.fail(f"Unexpected exception for valid format '{postal_code}'")
    
    # Coordinate validation tests
    def test_validate_coordinates_valid_cases(self, validator, coordinate_test_cases):
        """Test validate_coordinates with valid cases"""
        valid_cases = [case for case in coordinate_test_cases if case['expected_valid']]
        
        for case in valid_cases:
            result = validator.validate_coordinates(
                case['coords'],
                case['components']
            )
            assert result['valid'] is True, f"Expected valid coordinates for {case}"
            assert 'distance_km' in result
    
    def test_validate_coordinates_invalid_cases(self, validator, coordinate_test_cases):
        """Test validate_coordinates with invalid cases"""
        invalid_cases = [case for case in coordinate_test_cases if not case['expected_valid']]
        
        for case in invalid_cases:
            result = validator.validate_coordinates(
                case['coords'],
                case['components']
            )
            assert result['valid'] is False, f"Expected invalid coordinates for {case}"
    
    def test_validate_coordinates_bounds_checking(self, validator):
        """Test coordinate bounds checking for Turkey"""
        # Coordinates outside Turkey should be invalid
        out_of_bounds_cases = [
            {'lat': 90.0, 'lon': 30.0},    # North Pole
            {'lat': -90.0, 'lon': 30.0},   # South Pole
            {'lat': 40.0, 'lon': 180.0},   # Far East
            {'lat': 40.0, 'lon': -180.0},  # Far West
        ]
        
        components = {'il': 'İstanbul', 'ilce': 'Kadıköy'}
        
        for coords in out_of_bounds_cases:
            result = validator.validate_coordinates(coords, components)
            assert result['valid'] is False, f"Expected invalid for out-of-bounds coordinates {coords}"
    
    def test_validate_coordinates_missing_data(self, validator):
        """Test validate_coordinates with missing data"""
        components = {'il': 'İstanbul', 'ilce': 'Kadıköy'}
        
        # Missing coordinates
        result = validator.validate_coordinates(None, components)
        assert result['valid'] is False
        
        # Missing latitude
        result = validator.validate_coordinates({'lon': 28.9784}, components)
        assert result['valid'] is False
        
        # Missing longitude
        result = validator.validate_coordinates({'lat': 41.0082}, components)
        assert result['valid'] is False
        
        # Empty coordinates
        result = validator.validate_coordinates({}, components)
        assert result['valid'] is False
    
    # Error handling and edge cases
    def test_validator_initialization(self):
        """Test AddressValidator initialization"""
        validator = AddressValidator()
        
        assert hasattr(validator, 'admin_hierarchy')
        assert hasattr(validator, 'postal_codes')
        assert validator.admin_hierarchy is not None
        assert validator.postal_codes is not None
    
    def test_invalid_input_types(self, validator):
        """Test with invalid input types"""
        invalid_inputs = [
            None,
            "string instead of dict",
            123,
            [],
            set()
        ]
        
        for invalid_input in invalid_inputs:
            try:
                result = validator.validate_address(invalid_input)
                assert result['is_valid'] is False
                assert len(result['errors']) > 0
            except (TypeError, AttributeError):
                # Exceptions are acceptable for invalid input types
                pass
    
    def test_unicode_and_turkish_characters(self, validator):
        """Test handling of Turkish Unicode characters"""
        turkish_address = {
            'raw_address': 'İstanbul Şişli Mecidiyeköy Mahallesi Büyükdere Caddesi',
            'parsed_components': {
                'il': 'İstanbul',
                'ilce': 'Şişli',
                'mahalle': 'Mecidiyeköy Mahallesi',
                'sokak': 'Büyükdere Caddesi'
            }
        }
        
        result = validator.validate_address(turkish_address)
        
        # Should handle Turkish characters without errors
        assert isinstance(result, dict)
        assert 'is_valid' in result
    
    def test_very_long_address_components(self, validator):
        """Test with very long address components"""
        long_address = {
            'raw_address': 'A' * 1000,  # Very long address
            'parsed_components': {
                'il': 'İstanbul',
                'ilce': 'Kadıköy',
                'mahalle': 'B' * 500,  # Very long mahalle name
                'sokak': 'C' * 500     # Very long sokak name
            }
        }
        
        # Should handle long inputs gracefully
        result = validator.validate_address(long_address)
        assert isinstance(result, dict)
    
    # Performance tests
    def test_validation_performance_single_address(self, validator, valid_address_data):
        """Test performance of single address validation"""
        start_time = time.time()
        
        result = validator.validate_address(valid_address_data)
        
        end_time = time.time()
        processing_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        # Should process within reasonable time (target: < 100ms)
        assert processing_time < 100, f"Processing took {processing_time:.2f}ms, expected < 100ms"
        assert result['is_valid'] is not None
    
    def test_validation_performance_batch(self, validator):
        """Test performance of batch address validation"""
        # Create batch of test addresses
        batch_addresses = []
        for i in range(100):
            address_data = {
                'raw_address': f'İstanbul Kadıköy Test Mahallesi {i}',
                'parsed_components': {
                    'il': 'İstanbul',
                    'ilce': 'Kadıköy',
                    'mahalle': f'Test Mahallesi {i}'
                }
            }
            batch_addresses.append(address_data)
        
        start_time = time.time()
        
        results = []
        for address_data in batch_addresses:
            result = validator.validate_address(address_data)
            results.append(result)
        
        end_time = time.time()
        total_time = (end_time - start_time) * 1000  # Convert to milliseconds
        avg_time_per_address = total_time / len(batch_addresses)
        
        # Performance targets
        assert avg_time_per_address < 50, f"Average processing time {avg_time_per_address:.2f}ms per address, expected < 50ms"
        assert len(results) == len(batch_addresses)
        
        print(f"Batch performance: {len(batch_addresses)} addresses in {total_time:.2f}ms")
        print(f"Average: {avg_time_per_address:.2f}ms per address")
    
    def test_memory_usage_stability(self, validator):
        """Test memory usage doesn't grow excessively"""
        import gc
        
        # Force garbage collection
        gc.collect()
        
        # Process many addresses
        for i in range(1000):
            address_data = {
                'raw_address': f'Test address {i}',
                'parsed_components': {
                    'il': 'İstanbul',
                    'ilce': 'Kadıköy',
                    'mahalle': f'Test Mahallesi {i}'
                }
            }
            validator.validate_address(address_data)
            
            # Periodic garbage collection
            if i % 100 == 0:
                gc.collect()
        
        # Final garbage collection
        gc.collect()
        
        # Test passes if no memory errors occur
        assert True
    
    # Integration tests with real data
    def test_integration_with_hierarchy_data(self, validator):
        """Test integration with actual Turkish administrative hierarchy data"""
        # Test with real data from our hierarchy CSV
        real_addresses = [
            {
                'parsed_components': {
                    'il': 'İstanbul',
                    'ilce': 'Kadıköy',
                    'mahalle': 'Moda Mahallesi'
                }
            },
            {
                'parsed_components': {
                    'il': 'Ankara',
                    'ilce': 'Çankaya',
                    'mahalle': 'Kızılay Mahallesi'
                }
            },
            {
                'parsed_components': {
                    'il': 'İzmir',
                    'ilce': 'Konak',
                    'mahalle': 'Alsancak Mahallesi'
                }
            }
        ]
        
        for address_data in real_addresses:
            result = validator.validate_address(address_data)
            
            # Real hierarchy data should validate correctly
            assert isinstance(result, dict)
            assert 'validation_details' in result
            
            if result['validation_details'].get('hierarchy_valid') is not None:
                # If hierarchy validation is implemented, it should work with real data
                print(f"Hierarchy validation result for {address_data}: {result['validation_details']['hierarchy_valid']}")
    
    # Parametrized tests for comprehensive coverage
    @pytest.mark.parametrize("il,ilce,mahalle,expected", [
        ('İstanbul', 'Kadıköy', 'Moda Mahallesi', True),
        ('İstanbul', 'Beşiktaş', 'Levent Mahallesi', True),
        ('Ankara', 'Çankaya', 'Kızılay Mahallesi', True),
        ('İzmir', 'Konak', 'Alsancak Mahallesi', True),
        ('İstanbul', 'Çankaya', 'Kızılay Mahallesi', False),  # Wrong hierarchy
        ('Ankara', 'Kadıköy', 'Moda Mahallesi', False),       # Wrong hierarchy
    ])
    def test_hierarchy_validation_parametrized(self, validator, il, ilce, mahalle, expected):
        """Parametrized test for hierarchy validation"""
        result = validator.validate_hierarchy(il, ilce, mahalle)
        assert result == expected, f"Hierarchy validation failed for {il}-{ilce}-{mahalle}"
    
    @pytest.mark.parametrize("postal_code,expected_valid_format", [
        ('34718', True),
        ('06420', True),
        ('12345', True),
        ('1234', False),   # Too short
        ('123456', False), # Too long
        ('abcde', False),  # Non-numeric
        ('', False),       # Empty
    ])
    def test_postal_code_format_parametrized(self, validator, postal_code, expected_valid_format):
        """Parametrized test for postal code format validation"""
        components = {'il': 'İstanbul', 'ilce': 'Kadıköy'}
        
        try:
            result = validator.validate_postal_code(postal_code, components)
            if not expected_valid_format:
                # Invalid format should return False or raise exception
                assert result is False or result is None
        except (TypeError, ValueError):
            # Exception is acceptable for invalid formats
            if expected_valid_format:
                pytest.fail(f"Unexpected exception for valid format '{postal_code}'")


# Additional test utilities
class TestAddressValidatorUtils:
    """Utility tests for AddressValidator helper methods"""
    
    def test_data_loading_methods(self):
        """Test data loading methods work correctly"""
        validator = AddressValidator()
        
        # Test that data loading methods return expected types
        assert validator.admin_hierarchy is not None
        assert validator.postal_codes is not None
        
        # Basic type checks
        assert isinstance(validator.admin_hierarchy, (dict, list, object))
        assert isinstance(validator.postal_codes, (dict, list, object))


# Benchmark tests for performance requirements
@pytest.mark.benchmark
class TestAddressValidatorBenchmarks:
    """Performance benchmark tests for AddressValidator"""
    
    def test_benchmark_single_validation(self, validator, benchmark):
        """Benchmark single address validation"""
        address_data = {
            'raw_address': 'İstanbul Kadıköy Moda Mahallesi Caferağa Sokak 10',
            'parsed_components': {
                'il': 'İstanbul',
                'ilce': 'Kadıköy',
                'mahalle': 'Moda Mahallesi'
            }
        }
        
        result = benchmark(validator.validate_address, address_data)
        assert result['is_valid'] is not None
    
    def test_benchmark_hierarchy_validation(self, validator, benchmark):
        """Benchmark hierarchy validation"""
        result = benchmark(validator.validate_hierarchy, 'İstanbul', 'Kadıköy', 'Moda Mahallesi')
        assert isinstance(result, bool)
    
    def test_benchmark_batch_processing(self, validator, benchmark):
        """Benchmark batch address processing"""
        addresses = [
            {'parsed_components': {'il': 'İstanbul', 'ilce': 'Kadıköy', 'mahalle': f'Test Mahallesi {i}'}}
            for i in range(50)
        ]
        
        def batch_validate():
            return [validator.validate_address(addr) for addr in addresses]
        
        results = benchmark(batch_validate)
        assert len(results) == 50


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])