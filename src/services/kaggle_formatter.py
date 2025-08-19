"""
Competition Submission Formatter
Competition Submission System

REQUIREMENT: Format processed addresses for competition leaderboard
"""

import pandas as pd
import numpy as np
import logging
import json
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import uuid
from datetime import datetime

# Import existing system components
try:
    from geo_integrated_pipeline import GeoIntegratedPipeline
    from duplicate_detector import DuplicateAddressDetector
    from address_geocoder import AddressGeocoder
    COMPONENTS_AVAILABLE = True
except ImportError:
    COMPONENTS_AVAILABLE = False
    print("Warning: Core components not available for formatter")


class KaggleSubmissionFormatter:
    """
    Competition Submission Formatter
    
    Formats processed address data into competition submission format
    for Kaggle private leaderboard evaluation
    """
    
    def __init__(self):
        """Initialize formatter with schema requirements"""
        self.logger = logging.getLogger(__name__)
        
        # Required columns for submission
        self.required_columns = self.get_teknofest_schema()
        
        # Initialize components if available
        if COMPONENTS_AVAILABLE:
            try:
                self.pipeline = GeoIntegratedPipeline("postgresql://localhost/teknofest_db")
            except:
                self.pipeline = None
                self.logger.warning("Could not initialize pipeline, using data-only mode")
        else:
            self.pipeline = None
        
        self.logger.info("KaggleSubmissionFormatter initialized")
    
    def get_teknofest_schema(self) -> Dict[str, str]:
        """
        Define competition submission schema
        
        Returns:
            Dictionary with required columns and their data types
        """
        return {
            'id': 'int64',              # Unique identifier for each record
            'il': 'object',             # Province name (standardized)
            'ilce': 'object',           # District name (standardized) 
            'mahalle': 'object',        # Neighborhood name (standardized)
            'cadde': 'object',          # Street name (optional)
            'sokak': 'object',          # Street name alternative (optional)
            'bina_no': 'object',        # Building number (optional)
            'daire_no': 'object',       # Apartment number (optional)
            'confidence': 'float64',    # Overall confidence score (0.0-1.0)
            'latitude': 'float64',      # Geographic latitude (optional)
            'longitude': 'float64',     # Geographic longitude (optional)
            'duplicate_group': 'int64', # Duplicate group identifier (optional)
        }
    
    def format_for_teknofest_submission(self, processed_addresses: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        REQUIREMENT: Format for competition leaderboard
        
        Args:
            processed_addresses: Output from GeoIntegratedPipeline or similar processing
            
        Returns:
            pandas.DataFrame with required columns:
            - id, il, ilce, mahalle, cadde, sokak, bina_no, daire_no, confidence
        """
        if not processed_addresses:
            self.logger.warning("No processed addresses provided for formatting")
            return self._create_empty_submission()
        
        self.logger.info(f"Formatting {len(processed_addresses)} addresses for submission")
        
        # Convert to standardized format
        submission_data = []
        
        for i, address_result in enumerate(processed_addresses):
            try:
                formatted_record = self._format_single_address(i, address_result)
                submission_data.append(formatted_record)
            except Exception as e:
                self.logger.error(f"Error formatting address {i}: {e}")
                # Add error record to maintain index consistency
                error_record = self._create_error_record(i, address_result, str(e))
                submission_data.append(error_record)
        
        # Create DataFrame
        df = pd.DataFrame(submission_data)
        
        # Ensure all required columns exist
        df = self._ensure_required_columns(df)
        
        # Apply data type conversions
        df = self._apply_data_types(df)
        
        # Validate submission format
        validation = self.validate_submission_format(df)
        if not validation['is_valid']:
            self.logger.warning(f"Submission validation issues: {validation['errors']}")
        
        self.logger.info(f"Created submission DataFrame: {len(df)} rows, {len(df.columns)} columns")
        return df
    
    def _format_single_address(self, index: int, address_result: Dict[str, Any]) -> Dict[str, Any]:
        """Format a single address result into submission format"""
        
        # Extract components from different possible structures
        components = self._extract_components(address_result)
        
        # Extract coordinates if available
        coordinates = self._extract_coordinates(address_result)
        
        # Calculate overall confidence
        confidence = self._calculate_overall_confidence(address_result)
        
        # Format record
        record = {
            'id': index + 1,  # 1-based indexing for submission
            'il': self._standardize_province(components.get('il', '')),
            'ilce': self._standardize_text(components.get('ilce', '')),
            'mahalle': self._standardize_text(components.get('mahalle', '')),
            'cadde': self._extract_street_name(components, 'cadde'),
            'sokak': self._extract_street_name(components, 'sokak'), 
            'bina_no': self._standardize_building_number(components.get('bina_no', '')),
            'daire_no': self._standardize_apartment_number(components.get('daire_no', '')),
            'confidence': confidence,
            'latitude': coordinates.get('latitude'),
            'longitude': coordinates.get('longitude'),
            'duplicate_group': address_result.get('duplicate_group', 0)
        }
        
        return record
    
    def _extract_components(self, address_result: Dict[str, Any]) -> Dict[str, str]:
        """Extract address components from various result structures"""
        components = {}
        
        # Try different possible locations for components
        if 'parsed_components' in address_result:
            components.update(address_result['parsed_components'])
        elif 'components' in address_result:
            components.update(address_result['components'])
        elif 'address_components' in address_result:
            components.update(address_result['address_components'])
        
        # Handle nested structures
        if 'parsing_result' in address_result:
            parsing_result = address_result['parsing_result']
            if isinstance(parsing_result, dict) and 'components' in parsing_result:
                components.update(parsing_result['components'])
        
        return components
    
    def _extract_coordinates(self, address_result: Dict[str, Any]) -> Dict[str, Optional[float]]:
        """Extract coordinates from address result"""
        coords = {'latitude': None, 'longitude': None}
        
        # Try various coordinate locations
        if 'coordinates' in address_result:
            coord_data = address_result['coordinates']
            if isinstance(coord_data, dict):
                coords['latitude'] = coord_data.get('latitude') or coord_data.get('lat')
                coords['longitude'] = coord_data.get('longitude') or coord_data.get('lon')
        
        # Try geocoding result
        if 'geocoding_result' in address_result:
            geo_result = address_result['geocoding_result']
            if isinstance(geo_result, dict):
                coords['latitude'] = geo_result.get('latitude')
                coords['longitude'] = geo_result.get('longitude')
        
        # Convert to float and validate
        try:
            if coords['latitude'] is not None:
                coords['latitude'] = float(coords['latitude'])
                if not (35.0 <= coords['latitude'] <= 42.5):  # Turkey bounds
                    coords['latitude'] = None
            
            if coords['longitude'] is not None:
                coords['longitude'] = float(coords['longitude'])
                if not (25.0 <= coords['longitude'] <= 45.0):  # Turkey bounds
                    coords['longitude'] = None
                    
        except (ValueError, TypeError):
            coords = {'latitude': None, 'longitude': None}
        
        return coords
    
    def _calculate_overall_confidence(self, address_result: Dict[str, Any]) -> float:
        """Calculate overall confidence score"""
        confidence_sources = []
        
        # Try various confidence locations
        if 'final_confidence' in address_result:
            confidence_sources.append(address_result['final_confidence'])
        if 'confidence' in address_result:
            confidence_sources.append(address_result['confidence'])
        if 'overall_confidence' in address_result:
            confidence_sources.append(address_result['overall_confidence'])
        
        # Try component-level confidences
        if 'parsing_result' in address_result:
            parsing_result = address_result['parsing_result']
            if isinstance(parsing_result, dict):
                if 'overall_confidence' in parsing_result:
                    confidence_sources.append(parsing_result['overall_confidence'])
        
        # Calculate final confidence
        if confidence_sources:
            # Use maximum confidence from available sources
            confidence = max(confidence_sources)
            return max(0.0, min(1.0, float(confidence)))  # Clamp to [0,1]
        else:
            return 0.5  # Default moderate confidence
    
    def _standardize_province(self, province: str) -> str:
        """Standardize province names according to requirements"""
        if not province or pd.isna(province):
            return ''
        
        province_str = str(province).strip()
        
        # Turkish province standardization
        province_map = {
            'istanbul': 'İstanbul',
            'ankara': 'Ankara', 
            'izmir': 'İzmir',
            'İzmir': 'İzmir',
            'bursa': 'Bursa',
            'antalya': 'Antalya',
            'adana': 'Adana',
            'konya': 'Konya',
            'şanlıurfa': 'Şanlıurfa',
            'gaziantep': 'Gaziantep',
            'kocaeli': 'Kocaeli',
            'mersin': 'Mersin',
            'diyarbakır': 'Diyarbakır',
            'kayseri': 'Kayseri',
            'eskişehir': 'Eskişehir'
        }
        
        # Try exact match first
        province_lower = province_str.lower()
        if province_lower in province_map:
            return province_map[province_lower]
        
        # Return title case as fallback
        return province_str.title()
    
    def _standardize_text(self, text: str) -> str:
        """Standardize general text fields"""
        if not text or pd.isna(text):
            return ''
        
        text_str = str(text).strip()
        if not text_str:
            return ''
        
        # Apply Turkish title case
        return text_str.title()
    
    def _extract_street_name(self, components: Dict[str, str], street_type: str) -> str:
        """Extract and standardize street names"""
        # Try direct field
        if street_type in components:
            return self._standardize_text(components[street_type])
        
        # Try combined street field
        if 'cadde_sokak' in components:
            street_name = components['cadde_sokak']
            if street_name and street_type in street_name.lower():
                return self._standardize_text(street_name)
        
        # Try general street field
        if 'sokak' in components and street_type == 'cadde':
            # If only sokak is available, don't put it in cadde field
            return ''
        elif 'cadde' in components and street_type == 'sokak':
            # If only cadde is available, don't put it in sokak field
            return ''
        
        return ''
    
    def _standardize_building_number(self, building_no: str) -> str:
        """Standardize building numbers"""
        if not building_no or pd.isna(building_no):
            return ''
        
        building_str = str(building_no).strip()
        
        # Remove common prefixes
        prefixes_to_remove = ['no:', 'no.', 'no ', 'numara:', 'numara.', '#']
        for prefix in prefixes_to_remove:
            if building_str.lower().startswith(prefix):
                building_str = building_str[len(prefix):].strip()
        
        return building_str
    
    def _standardize_apartment_number(self, apartment_no: str) -> str:
        """Standardize apartment numbers"""
        if not apartment_no or pd.isna(apartment_no):
            return ''
        
        apt_str = str(apartment_no).strip()
        
        # Remove common prefixes
        prefixes_to_remove = ['daire:', 'daire.', 'daire ', 'apt:', 'apt.', '#']
        for prefix in prefixes_to_remove:
            if apt_str.lower().startswith(prefix):
                apt_str = apt_str[len(prefix):].strip()
        
        return apt_str
    
    def _create_error_record(self, index: int, original_data: Any, error_msg: str) -> Dict[str, Any]:
        """Create error record for failed formatting"""
        return {
            'id': index + 1,
            'il': '',
            'ilce': '',
            'mahalle': '',
            'cadde': '',
            'sokak': '', 
            'bina_no': '',
            'daire_no': '',
            'confidence': 0.0,
            'latitude': None,
            'longitude': None,
            'duplicate_group': 0,
            'error': error_msg
        }
    
    def _ensure_required_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure all required columns exist in DataFrame"""
        for column, dtype in self.required_columns.items():
            if column not in df.columns:
                # Add missing column with appropriate default value
                if dtype == 'object':
                    df[column] = ''
                elif dtype == 'float64':
                    df[column] = np.nan
                elif dtype == 'int64':
                    df[column] = 0
                else:
                    df[column] = None
        
        # Reorder columns according to schema
        column_order = list(self.required_columns.keys())
        existing_columns = [col for col in column_order if col in df.columns]
        extra_columns = [col for col in df.columns if col not in column_order]
        
        df = df[existing_columns + extra_columns]
        return df
    
    def _apply_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply correct data types to DataFrame columns"""
        for column, dtype in self.required_columns.items():
            if column in df.columns:
                try:
                    if dtype == 'object':
                        df[column] = df[column].astype(str)
                        df[column] = df[column].replace('nan', '')
                    elif dtype == 'float64':
                        df[column] = pd.to_numeric(df[column], errors='coerce')
                    elif dtype == 'int64':
                        df[column] = pd.to_numeric(df[column], errors='coerce').fillna(0).astype(int)
                except Exception as e:
                    self.logger.warning(f"Could not convert column {column} to {dtype}: {e}")
        
        return df
    
    def _create_empty_submission(self) -> pd.DataFrame:
        """Create empty submission DataFrame with correct schema"""
        data = {column: [] for column in self.required_columns.keys()}
        df = pd.DataFrame(data)
        return self._apply_data_types(df)
    
    def validate_submission_format(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate submission meets all requirements
        
        Returns:
            {
                "is_valid": bool,
                "errors": List[str],
                "row_count": int,
                "missing_columns": List[str]
            }
        """
        errors = []
        missing_columns = []
        
        # Check required columns
        for column in self.required_columns.keys():
            if column not in df.columns:
                missing_columns.append(column)
                errors.append(f"Missing required column: {column}")
        
        # Check data types
        for column, expected_dtype in self.required_columns.items():
            if column in df.columns:
                actual_dtype = str(df[column].dtype)
                if expected_dtype == 'object' and not actual_dtype.startswith('object'):
                    errors.append(f"Column {column} should be text, got {actual_dtype}")
                elif expected_dtype == 'float64' and not actual_dtype.startswith('float'):
                    errors.append(f"Column {column} should be float, got {actual_dtype}")
                elif expected_dtype == 'int64' and not actual_dtype.startswith('int'):
                    errors.append(f"Column {column} should be integer, got {actual_dtype}")
        
        # Check ID column uniqueness and sequence
        if 'id' in df.columns:
            if df['id'].duplicated().any():
                errors.append("ID column contains duplicate values")
            if not df['id'].equals(pd.Series(range(1, len(df) + 1))):
                errors.append("ID column should be sequential starting from 1")
        
        # Check confidence bounds
        if 'confidence' in df.columns:
            invalid_confidence = (df['confidence'] < 0) | (df['confidence'] > 1)
            if invalid_confidence.any():
                errors.append("Confidence values should be between 0 and 1")
        
        # Check coordinate bounds for Turkey
        if 'latitude' in df.columns:
            valid_lats = df['latitude'].dropna()
            invalid_lats = (valid_lats < 35.0) | (valid_lats > 42.5)
            if invalid_lats.any():
                errors.append("Some latitude values are outside Turkey bounds (35-42.5)")
        
        if 'longitude' in df.columns:
            valid_lons = df['longitude'].dropna()
            invalid_lons = (valid_lons < 25.0) | (valid_lons > 45.0)
            if invalid_lons.any():
                errors.append("Some longitude values are outside Turkey bounds (25-45)")
        
        # Check for completely empty required fields
        core_fields = ['il', 'ilce', 'mahalle']
        for field in core_fields:
            if field in df.columns:
                empty_count = (df[field] == '').sum()
                if empty_count > len(df) * 0.5:  # More than 50% empty
                    errors.append(f"Field {field} is empty for more than 50% of records")
        
        validation_result = {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'row_count': len(df),
            'missing_columns': missing_columns,
            'column_count': len(df.columns),
            'data_types': {col: str(df[col].dtype) for col in df.columns}
        }
        
        return validation_result
    
    def create_sample_submission(self, sample_size: int = 100) -> pd.DataFrame:
        """Create sample submission file for testing"""
        self.logger.info(f"Creating sample submission with {sample_size} records")
        
        # Generate sample data
        sample_data = []
        
        # Sample Turkish locations
        sample_locations = [
            {'il': 'İstanbul', 'ilce': 'Kadıköy', 'mahalle': 'Moda'},
            {'il': 'Ankara', 'ilce': 'Çankaya', 'mahalle': 'Kızılay'},
            {'il': 'İzmir', 'ilce': 'Konak', 'mahalle': 'Alsancak'},
            {'il': 'Bursa', 'ilce': 'Osmangazi', 'mahalle': 'Heykel'},
            {'il': 'Antalya', 'ilce': 'Muratpaşa', 'mahalle': 'Lara'}
        ]
        
        for i in range(sample_size):
            location = sample_locations[i % len(sample_locations)]
            
            record = {
                'id': i + 1,
                'il': location['il'],
                'ilce': location['ilce'],
                'mahalle': location['mahalle'],
                'cadde': f"Test Caddesi {i % 10 + 1}" if i % 3 == 0 else '',
                'sokak': f"Test Sokak {i % 8 + 1}" if i % 4 == 0 else '',
                'bina_no': str(i % 100 + 1) if i % 2 == 0 else '',
                'daire_no': chr(65 + (i % 26)) if i % 5 == 0 else '',  # A, B, C, ...
                'confidence': min(1.0, 0.6 + (i % 40) / 100),  # 0.6 to 1.0
                'latitude': 39.0 + (i % 100) / 100,  # Sample Turkey latitudes
                'longitude': 35.0 + (i % 100) / 100,  # Sample Turkey longitudes
                'duplicate_group': (i // 5) + 1  # Group every 5 records
            }
            sample_data.append(record)
        
        df = pd.DataFrame(sample_data)
        df = self._apply_data_types(df)
        
        return df
    
    def save_submission(self, df: pd.DataFrame, filename: str = None) -> str:
        """Save submission DataFrame to CSV file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"teknofest_submission_{timestamp}.csv"
        
        # Ensure .csv extension
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        try:
            df.to_csv(filename, index=False, encoding='utf-8')
            self.logger.info(f"Submission saved to {filename}")
            return filename
        except Exception as e:
            self.logger.error(f"Error saving submission: {e}")
            raise
    
    def load_and_format_pipeline_results(self, results_file: str) -> pd.DataFrame:
        """Load results from pipeline processing and format for submission"""
        try:
            if results_file.endswith('.json'):
                with open(results_file, 'r', encoding='utf-8') as f:
                    results = json.load(f)
            elif results_file.endswith('.csv'):
                # Assume CSV contains processed results
                df = pd.read_csv(results_file)
                results = df.to_dict('records')
            else:
                raise ValueError("Unsupported file format. Use .json or .csv")
            
            return self.format_for_teknofest_submission(results)
            
        except Exception as e:
            self.logger.error(f"Error loading and formatting results: {e}")
            raise


# Test function for validation
def test_kaggle_formatter():
    """Test Kaggle submission formatter"""
    print("TESTING SUBMISSION FORMATTER")
    print("=" * 50)
    
    formatter = KaggleSubmissionFormatter()
    
    # Test sample data
    sample_results = [
        {
            'parsed_components': {
                'il': 'İstanbul',
                'ilce': 'Kadıköy',
                'mahalle': 'Moda',
                'sokak': 'Caferağa Sokak',
                'bina_no': '10',
                'daire_no': 'A'
            },
            'final_confidence': 0.95,
            'coordinates': {'latitude': 40.9869, 'longitude': 29.0265}
        },
        {
            'parsed_components': {
                'il': 'Ankara',
                'ilce': 'Çankaya', 
                'mahalle': 'Kızılay',
                'cadde_sokak': 'Tunalı Hilmi Caddesi',
                'bina_no': '25'
            },
            'final_confidence': 0.87
        }
    ]
    
    print(f"Formatting {len(sample_results)} sample results...")
    
    # Test formatting
    submission_df = formatter.format_for_teknofest_submission(sample_results)
    
    print(f"Created submission DataFrame:")
    print(f"  Shape: {submission_df.shape}")
    print(f"  Columns: {list(submission_df.columns)}")
    print("\nFirst few rows:")
    print(submission_df.head())
    
    # Test validation
    validation = formatter.validate_submission_format(submission_df)
    print(f"\nValidation Results:")
    print(f"  Valid: {validation['is_valid']}")
    print(f"  Errors: {len(validation['errors'])}")
    if validation['errors']:
        for error in validation['errors']:
            print(f"    - {error}")
    
    # Test sample submission creation
    print(f"\nCreating sample submission (10 records)...")
    sample_submission = formatter.create_sample_submission(10)
    print(f"Sample submission shape: {sample_submission.shape}")
    
    # Test saving
    filename = formatter.save_submission(sample_submission, "test_submission.csv")
    print(f"Sample submission saved as: {filename}")
    
    print("\n✅ Kaggle formatter test completed!")
    return submission_df, validation


if __name__ == "__main__":
    test_kaggle_formatter()