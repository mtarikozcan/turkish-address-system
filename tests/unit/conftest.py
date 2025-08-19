"""
TEKNOFEST 2025 Adres Çözümleme Sistemi - Test Configuration
Pytest configuration and shared fixtures for all tests
"""

import pytest
import os
import sys
import json
import pandas as pd
from typing import Dict, List

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Test data directories
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'test_data')
SRC_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'src', 'data')
DATABASE_DIR = os.path.join(os.path.dirname(__file__), '..', 'database')


@pytest.fixture(scope="session")
def test_hierarchy_data():
    """Load test hierarchy data for address validation"""
    try:
        hierarchy_file = os.path.join(DATABASE_DIR, 'turkey_admin_hierarchy.csv')
        if os.path.exists(hierarchy_file):
            df = pd.read_csv(hierarchy_file)
            return df
        else:
            # Return mock data if CSV doesn't exist
            return pd.DataFrame([
                {'il_kodu': 34, 'il_adi': 'İstanbul', 'ilce_kodu': 1, 'ilce_adi': 'Kadıköy', 
                 'mahalle_kodu': 34001, 'mahalle_adi': 'Moda Mahallesi'},
                {'il_kodu': 34, 'il_adi': 'İstanbul', 'ilce_kodu': 2, 'ilce_adi': 'Beşiktaş', 
                 'mahalle_kodu': 34101, 'mahalle_adi': 'Levent Mahallesi'},
                {'il_kodu': 6, 'il_adi': 'Ankara', 'ilce_kodu': 1, 'ilce_adi': 'Çankaya', 
                 'mahalle_kodu': 6001, 'mahalle_adi': 'Kızılay Mahallesi'},
                {'il_kodu': 35, 'il_adi': 'İzmir', 'ilce_kodu': 1, 'ilce_adi': 'Konak', 
                 'mahalle_kodu': 35001, 'mahalle_adi': 'Alsancak Mahallesi'},
            ])
    except Exception as e:
        pytest.skip(f"Could not load hierarchy data: {e}")


@pytest.fixture(scope="session")
def test_abbreviations_data():
    """Load test abbreviations data"""
    try:
        abbrev_file = os.path.join(SRC_DATA_DIR, 'abbreviations.json')
        if os.path.exists(abbrev_file):
            with open(abbrev_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Return mock abbreviations data
            return {
                "abbreviations": {
                    "mh.": "mahallesi",
                    "sk.": "sokak",
                    "cd.": "caddesi",
                    "no.": "numara"
                },
                "metadata": {
                    "total_abbreviations": 4
                }
            }
    except Exception as e:
        pytest.skip(f"Could not load abbreviations data: {e}")


@pytest.fixture(scope="session")
def test_spelling_corrections_data():
    """Load test spelling corrections data"""
    try:
        corrections_file = os.path.join(SRC_DATA_DIR, 'spelling_corrections.json')
        if os.path.exists(corrections_file):
            with open(corrections_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Return mock corrections data
            return {
                "spelling_corrections": {
                    "istbl": "istanbul",
                    "kadikoy": "kadıköy",
                    "besiktas": "beşiktaş"
                },
                "metadata": {
                    "total_corrections": 3
                }
            }
    except Exception as e:
        pytest.skip(f"Could not load spelling corrections data: {e}")


@pytest.fixture
def sample_valid_addresses():
    """Sample valid Turkish addresses for testing"""
    return [
        {
            'raw_address': 'İstanbul Kadıköy Moda Mahallesi Caferağa Sokak 10',
            'parsed_components': {
                'il': 'İstanbul',
                'ilce': 'Kadıköy',
                'mahalle': 'Moda Mahallesi',
                'sokak': 'Caferağa Sokak',
                'bina_no': '10'
            },
            'coordinates': {'lat': 40.9875, 'lon': 29.0376}
        },
        {
            'raw_address': 'Ankara Çankaya Kızılay Mahallesi Atatürk Bulvarı 25',
            'parsed_components': {
                'il': 'Ankara',
                'ilce': 'Çankaya',
                'mahalle': 'Kızılay Mahallesi',
                'sokak': 'Atatürk Bulvarı',
                'bina_no': '25'
            },
            'coordinates': {'lat': 39.9208, 'lon': 32.8541}
        },
        {
            'raw_address': 'İzmir Konak Alsancak Mahallesi Kıbrıs Şehitleri Caddesi 15',
            'parsed_components': {
                'il': 'İzmir',
                'ilce': 'Konak',
                'mahalle': 'Alsancak Mahallesi',
                'sokak': 'Kıbrıs Şehitleri Caddesi',
                'bina_no': '15'
            },
            'coordinates': {'lat': 38.4192, 'lon': 27.1287}
        }
    ]


@pytest.fixture
def sample_invalid_addresses():
    """Sample invalid Turkish addresses for testing"""
    return [
        {
            'raw_address': 'İstanbul Çankaya Kızılay Mahallesi',  # Wrong: Çankaya is in Ankara
            'parsed_components': {
                'il': 'İstanbul',
                'ilce': 'Çankaya',
                'mahalle': 'Kızılay Mahallesi'
            }
        },
        {
            'raw_address': 'Ankara Kadıköy Moda Mahallesi',  # Wrong: Kadıköy is in İstanbul
            'parsed_components': {
                'il': 'Ankara',
                'ilce': 'Kadıköy',
                'mahalle': 'Moda Mahallesi'
            }
        },
        {
            'raw_address': 'İzmir Beşiktaş Levent Mahallesi',  # Wrong: Beşiktaş is in İstanbul
            'parsed_components': {
                'il': 'İzmir',
                'ilce': 'Beşiktaş',
                'mahalle': 'Levent Mahallesi'
            }
        }
    ]


@pytest.fixture
def turkey_coordinate_bounds():
    """Geographic bounds for Turkey"""
    return {
        'lat_min': 35.8,
        'lat_max': 42.1,
        'lon_min': 25.7,
        'lon_max': 44.8
    }


@pytest.fixture
def performance_test_config():
    """Configuration for performance tests"""
    return {
        'max_processing_time_ms': 100,  # Maximum processing time per address
        'batch_size': 100,              # Size for batch processing tests
        'benchmark_iterations': 10,     # Number of iterations for benchmarks
        'memory_test_iterations': 1000  # Number of iterations for memory tests
    }


# Test markers configuration
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "benchmark: mark test as a performance benchmark"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )


# Custom test collection
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Add marker based on test name patterns
        if "benchmark" in item.name or "performance" in item.name:
            item.add_marker(pytest.mark.benchmark)
        
        if "integration" in item.name:
            item.add_marker(pytest.mark.integration)
        
        if "batch" in item.name or "memory" in item.name:
            item.add_marker(pytest.mark.slow)
        
        if not any(marker.name in ["benchmark", "integration", "slow"] 
                  for marker in item.iter_markers()):
            item.add_marker(pytest.mark.unit)


# Utility functions for tests
class TestHelpers:
    """Helper functions for tests"""
    
    @staticmethod
    def create_test_address(il='İstanbul', ilce='Kadıköy', mahalle='Test Mahallesi', **kwargs):
        """Create a test address with default values"""
        address = {
            'raw_address': f'{il} {ilce} {mahalle}',
            'parsed_components': {
                'il': il,
                'ilce': ilce,
                'mahalle': mahalle
            }
        }
        address.update(kwargs)
        return address
    
    @staticmethod
    def assert_valid_validation_result(result):
        """Assert that a validation result has the expected structure"""
        assert isinstance(result, dict)
        assert 'is_valid' in result
        assert 'confidence' in result
        assert 'errors' in result
        assert 'suggestions' in result
        assert 'validation_details' in result
        
        assert isinstance(result['is_valid'], bool)
        assert isinstance(result['confidence'], (int, float))
        assert isinstance(result['errors'], list)
        assert isinstance(result['suggestions'], list)
        assert isinstance(result['validation_details'], dict)
        
        assert 0.0 <= result['confidence'] <= 1.0


@pytest.fixture
def test_helpers():
    """Provide test helper functions"""
    return TestHelpers()