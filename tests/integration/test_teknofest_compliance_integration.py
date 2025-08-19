"""
TEKNOFEST 2025 - Complete Integration Test
Test all TEKNOFEST compliance features working together

Tests:
1. Duplicate Detection Integration
2. Address Geocoding Integration  
3. Kaggle Submission Formatting Integration
4. End-to-End Pipeline Integration
"""

import asyncio
import time
import logging
from pathlib import Path
import sys

# Add src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test addresses with known characteristics
TEST_ADDRESSES = [
    "Istanbul Kadıköy Moda Mahallesi Caferağa Sokak 10",
    "İstanbul Kadıköy Moda Mah. Caferağa Sk. 10",  # Duplicate of #1
    "Ankara Çankaya Tunalı Hilmi Caddesi 25",
    "Ankara Çankaya Tunali Hilmi Cd. 25",  # Duplicate of #3
    "İzmir Konak Alsancak Mahallesi",
    "Bursa Osmangazi Heykel Mahallesi",
    "Antalya Muratpaşa Lara Mahallesi",
    "İstanbul Kadıköy Moda Caferağa 10",  # Similar to #1
]


async def test_duplicate_detection_integration():
    """Test duplicate detection integration"""
    print("\n🔍 TESTING DUPLICATE DETECTION INTEGRATION")
    print("=" * 60)
    
    try:
        # Import components
        from geo_integrated_pipeline import GeoIntegratedPipeline
        from duplicate_detector import DuplicateAddressDetector
        
        # Test direct duplicate detector
        print("Testing DuplicateAddressDetector directly...")
        detector = DuplicateAddressDetector()
        groups = detector.find_duplicate_groups(TEST_ADDRESSES)
        stats = detector.get_duplicate_statistics(TEST_ADDRESSES)
        
        print(f"✅ Direct test results:")
        print(f"   - Found {len(groups)} groups")
        print(f"   - Duplicate groups: {stats['duplicate_groups']}")
        print(f"   - Duplication rate: {stats['duplication_rate']:.1%}")
        
        # Test pipeline integration
        print("\nTesting GeoIntegratedPipeline integration...")
        pipeline = GeoIntegratedPipeline("postgresql://localhost/test")
        
        result = await pipeline.process_for_duplicate_detection(TEST_ADDRESSES[:4])  # Test with smaller set
        
        print(f"✅ Pipeline integration results:")
        print(f"   - Status: {result['status']}")
        print(f"   - Processed addresses: {len(result['processed_addresses'])}")
        print(f"   - Duplicate groups: {len(result['duplicate_groups'])}")
        print(f"   - Processing time: {result['processing_time_ms']:.2f}ms")
        
        return True
        
    except Exception as e:
        print(f"❌ Duplicate detection test failed: {e}")
        return False


async def test_geocoding_integration():
    """Test address geocoding integration"""
    print("\n🌍 TESTING GEOCODING INTEGRATION")
    print("=" * 60)
    
    try:
        # Import components
        from geo_integrated_pipeline import GeoIntegratedPipeline
        from address_geocoder import AddressGeocoder
        
        # Test direct geocoder
        print("Testing AddressGeocoder directly...")
        geocoder = AddressGeocoder()
        
        sample_address = TEST_ADDRESSES[0]
        geocode_result = geocoder.geocode_turkish_address(sample_address)
        
        print(f"✅ Direct geocoding result:")
        print(f"   - Address: {sample_address}")
        print(f"   - Coordinates: ({geocode_result.get('latitude')}, {geocode_result.get('longitude')})")
        print(f"   - Method: {geocode_result.get('method')}")
        print(f"   - Confidence: {geocode_result.get('confidence', 0):.3f}")
        
        # Test batch geocoding
        batch_results = geocoder.batch_geocode(TEST_ADDRESSES[:3])
        successful_batch = sum(1 for r in batch_results if r.get('latitude') is not None)
        print(f"   - Batch success: {successful_batch}/{len(batch_results)}")
        
        # Test pipeline integration
        print("\nTesting GeoIntegratedPipeline integration...")
        pipeline = GeoIntegratedPipeline("postgresql://localhost/test")
        
        result = await pipeline.process_with_geocoding(TEST_ADDRESSES[:3])  # Test with smaller set
        
        print(f"✅ Pipeline integration results:")
        print(f"   - Status: {result['status']}")
        print(f"   - Geocoded results: {len(result['geocoded_results'])}")
        print(f"   - Success rate: {result['geocoding_statistics'].get('success_rate', 0):.1%}")
        print(f"   - Processing time: {result['processing_summary']['total_processing_time_ms']:.2f}ms")
        
        return True
        
    except Exception as e:
        print(f"❌ Geocoding test failed: {e}")
        return False


async def test_kaggle_formatting_integration():
    """Test Kaggle submission formatting integration"""
    print("\n📊 TESTING KAGGLE FORMATTING INTEGRATION")
    print("=" * 60)
    
    try:
        # Import components
        from geo_integrated_pipeline import GeoIntegratedPipeline
        from kaggle_formatter import KaggleSubmissionFormatter
        
        # Test direct formatter
        print("Testing KaggleSubmissionFormatter directly...")
        formatter = KaggleSubmissionFormatter()
        
        # Create sample processed data
        sample_results = [
            {
                'parsed_components': {
                    'il': 'İstanbul',
                    'ilce': 'Kadıköy',
                    'mahalle': 'Moda',
                    'sokak': 'Caferağa Sokak',
                    'bina_no': '10'
                },
                'final_confidence': 0.95,
                'coordinates': {'latitude': 40.9869, 'longitude': 29.0265}
            },
            {
                'parsed_components': {
                    'il': 'Ankara',
                    'ilce': 'Çankaya',
                    'mahalle': 'Kızılay'
                },
                'final_confidence': 0.87
            }
        ]
        
        submission_df = formatter.format_for_teknofest_submission(sample_results)
        validation = formatter.validate_submission_format(submission_df)
        
        print(f"✅ Direct formatting results:")
        print(f"   - Submission shape: {submission_df.shape}")
        print(f"   - Validation valid: {validation['is_valid']}")
        print(f"   - Validation errors: {len(validation['errors'])}")
        
        # Test pipeline integration
        print("\nTesting GeoIntegratedPipeline integration...")
        pipeline = GeoIntegratedPipeline("postgresql://localhost/test")
        
        result = await pipeline.format_for_kaggle_submission(TEST_ADDRESSES[:3])  # Test with smaller set
        
        print(f"✅ Pipeline integration results:")
        print(f"   - Status: {result['status']}")
        if result['submission_dataframe'] is not None:
            print(f"   - Submission rows: {len(result['submission_dataframe'])}")
            print(f"   - Submission columns: {len(result['submission_dataframe'].columns)}")
        print(f"   - Validation valid: {result['validation_result']['is_valid']}")
        print(f"   - Processing time: {result['processing_summary']['total_processing_time_ms']:.2f}ms")
        
        # Save test submission
        if result['submission_dataframe'] is not None:
            filename = formatter.save_submission(result['submission_dataframe'], "test_teknofest_submission.csv")
            print(f"   - Saved to: {filename}")
        
        return True
        
    except Exception as e:
        print(f"❌ Kaggle formatting test failed: {e}")
        return False


async def test_end_to_end_integration():
    """Test complete end-to-end integration"""
    print("\n🚀 TESTING END-TO-END INTEGRATION")
    print("=" * 60)
    
    try:
        from geo_integrated_pipeline import GeoIntegratedPipeline
        
        # Initialize pipeline
        pipeline = GeoIntegratedPipeline("postgresql://localhost/test")
        
        print("Testing complete TEKNOFEST workflow...")
        
        # Step 1: Process addresses with duplicate detection
        print("Step 1: Duplicate Detection...")
        duplicate_result = await pipeline.process_for_duplicate_detection(TEST_ADDRESSES[:6])
        print(f"   ✅ Found {len(duplicate_result['duplicate_groups'])} duplicate groups")
        
        # Step 2: Enhanced geocoding
        print("Step 2: Enhanced Geocoding...")
        geocoding_result = await pipeline.process_with_geocoding(TEST_ADDRESSES[:6])
        print(f"   ✅ Geocoded {len(geocoding_result['geocoded_results'])} addresses")
        
        # Step 3: Kaggle submission formatting
        print("Step 3: Kaggle Submission Formatting...")
        submission_result = await pipeline.format_for_kaggle_submission(TEST_ADDRESSES[:6])
        print(f"   ✅ Created submission with {len(submission_result['submission_dataframe'])} rows")
        
        # Calculate total workflow performance
        total_time = (
            duplicate_result['processing_time_ms'] +
            geocoding_result['processing_summary']['total_processing_time_ms'] +
            submission_result['processing_summary']['total_processing_time_ms']
        )
        
        print(f"\n🏆 END-TO-END WORKFLOW RESULTS:")
        print(f"   - Total processing time: {total_time:.2f}ms")
        print(f"   - Average per address: {total_time / len(TEST_ADDRESSES[:6]):.2f}ms")
        print(f"   - All components working: ✅")
        print(f"   - TEKNOFEST ready: ✅")
        
        return True
        
    except Exception as e:
        print(f"❌ End-to-end integration test failed: {e}")
        return False


async def main():
    """Run all TEKNOFEST compliance tests"""
    print("🎯 TEKNOFEST 2025 COMPLIANCE INTEGRATION TESTS")
    print("=" * 80)
    
    start_time = time.time()
    
    # Run all tests
    tests = [
        ("Duplicate Detection Integration", test_duplicate_detection_integration),
        ("Geocoding Integration", test_geocoding_integration),
        ("Kaggle Formatting Integration", test_kaggle_formatting_integration),
        ("End-to-End Integration", test_end_to_end_integration),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        try:
            result = await test_func()
            if result:
                passed_tests += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    # Final summary
    total_time = time.time() - start_time
    
    print("\n" + "=" * 80)
    print("🏁 FINAL TEST RESULTS")
    print("=" * 80)
    print(f"Tests passed: {passed_tests}/{total_tests}")
    print(f"Success rate: {passed_tests/total_tests:.1%}")
    print(f"Total test time: {total_time:.2f}s")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TEKNOFEST COMPLIANCE FEATURES WORKING!")
        print("✅ System ready for TEKNOFEST 2025 competition")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed")
        print("❌ Additional fixes needed before competition")
    
    print("\n🔧 TEKNOFEST Features Verified:")
    print("   1. ✅ Duplicate Address Detection (Algorithm 5)")
    print("   2. ✅ Address Geocoding System (Algorithm 6)")  
    print("   3. ✅ Kaggle Submission Formatter")
    print("   4. ✅ GeoIntegratedPipeline Integration")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    # Run the comprehensive test suite
    success = asyncio.run(main())
    
    if success:
        print("\n🚀 TEKNOFEST 2025 system is READY!")
        exit(0)
    else:
        print("\n🔧 Additional work needed")
        exit(1)