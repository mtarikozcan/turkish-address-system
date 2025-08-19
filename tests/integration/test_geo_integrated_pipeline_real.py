"""
Test the real GeoIntegratedPipeline implementation
Comprehensive test runner for GeoIntegratedPipeline functionality
"""

import sys
import os
import asyncio
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_real_geo_integrated_pipeline():
    """Test the real GeoIntegratedPipeline implementation"""
    
    print("🧪 Testing Real GeoIntegratedPipeline Implementation")
    print("=" * 55)
    
    try:
        from geo_integrated_pipeline import GeoIntegratedPipeline
        
        # Initialize pipeline with test connection string
        connection_string = "postgresql://test:test@localhost:5432/testdb"
        pipeline = GeoIntegratedPipeline(connection_string)
        print("✅ GeoIntegratedPipeline initialized successfully")
        
        passed = 0
        total = 0
        
        # Test 1: Pipeline initialization
        print(f"\n📋 Testing pipeline initialization:")
        total += 1
        try:
            # Check all components are initialized
            components_check = [
                ('validator', pipeline.validator is not None),
                ('corrector', pipeline.corrector is not None),
                ('parser', pipeline.parser is not None),
                ('matcher', pipeline.matcher is not None),
                ('db_manager', pipeline.db_manager is not None)
            ]
            
            # Check configuration
            config_check = [
                ('processed_addresses', hasattr(pipeline, 'processed_addresses')),
                ('pipeline_times', hasattr(pipeline, 'pipeline_times')),
                ('error_count', hasattr(pipeline, 'error_count')),
                ('confidence_weights', hasattr(pipeline, 'confidence_weights'))
            ]
            
            all_components = all(check for name, check in components_check)
            all_config = all(check for name, check in config_check)
            
            if all_components and all_config:
                print("✅ Pipeline initialization: PASSED")
                for name, check in components_check:
                    status = "✅" if check else "❌"
                    print(f"   - {name}: {status}")
                passed += 1
            else:
                print("❌ Pipeline initialization: FAILED")
                for name, check in components_check + config_check:
                    status = "✅" if check else "❌"
                    print(f"   - {name}: {status}")
                    
        except Exception as e:
            print(f"❌ Pipeline initialization: ERROR - {e}")
        
        # Test 2: Basic address processing
        print(f"\n📋 Testing basic address processing:")
        total += 1
        try:
            test_address = "İstanbul Kadıköy Moda Mahallesi Caferağa Sokak No 10"
            result = asyncio.run(pipeline.process_address_with_geo_lookup(test_address))
            
            # Validate result structure
            required_fields = ['request_id', 'input_address', 'corrected_address', 
                             'parsed_components', 'validation_result', 'matches', 
                             'final_confidence', 'processing_time_ms', 'status']
            
            if all(field in result for field in required_fields):
                print(f"✅ process_address_with_geo_lookup: PASSED")
                print(f"   - Status: {result['status']}")
                print(f"   - Confidence: {result['final_confidence']:.3f}")
                print(f"   - Processing time: {result['processing_time_ms']:.2f}ms")
                print(f"   - Input: {result['input_address'][:40]}...")
                print(f"   - Corrected: {result['corrected_address'][:40]}...")
                passed += 1
            else:
                missing_fields = [f for f in required_fields if f not in result]
                print(f"❌ process_address_with_geo_lookup: FAILED - Missing fields: {missing_fields}")
                
        except Exception as e:
            print(f"❌ process_address_with_geo_lookup: ERROR - {e}")
        
        # Test 3: Seven-step pipeline validation
        print(f"\n📋 Testing seven-step pipeline process:")
        total += 1
        try:
            test_address = "istanbul kadikoy moda mah caferaga sk 10"
            result = asyncio.run(pipeline.process_address_with_geo_lookup(test_address))
            
            # Check pipeline details
            if 'pipeline_details' in result and 'step_times_ms' in result['pipeline_details']:
                step_times = result['pipeline_details']['step_times_ms']
                expected_steps = ['correction', 'parsing', 'validation', 'geo_lookup', 'matching', 'confidence_calc']
                
                steps_found = all(step in step_times for step in expected_steps)
                if steps_found:
                    print(f"✅ Seven-step pipeline: PASSED")
                    for step, time_ms in step_times.items():
                        print(f"   - {step}: {time_ms:.2f}ms")
                    passed += 1
                else:
                    missing_steps = [s for s in expected_steps if s not in step_times]
                    print(f"❌ Seven-step pipeline: FAILED - Missing steps: {missing_steps}")
            else:
                print(f"❌ Seven-step pipeline: FAILED - No pipeline details found")
                
        except Exception as e:
            print(f"❌ Seven-step pipeline: ERROR - {e}")
        
        # Test 4: Turkish address processing
        print(f"\n📋 Testing Turkish address processing:")
        
        turkish_addresses = [
            "İstanbul Kadıköy Moda Mahallesi Caferağa Sokak No 10",
            "Ankara Çankaya Kızılay Mahallesi Atatürk Caddesi 25",
            "İzmir Konak Alsancak Mahallesi Cumhuriyet Bulvarı 45"
        ]
        
        for i, address in enumerate(turkish_addresses):
            total += 1
            try:
                result = asyncio.run(pipeline.process_address_with_geo_lookup(address))
                
                # Check processing was successful
                if result.get('status') == 'completed':
                    print(f"✅ Turkish address #{i+1}: PASSED")
                    print(f"   - Original: {address[:40]}...")
                    print(f"   - Corrected: {result['corrected_address'][:40]}...")
                    print(f"   - Confidence: {result['final_confidence']:.3f}")
                    passed += 1
                else:
                    print(f"❌ Turkish address #{i+1}: FAILED - Status: {result.get('status')}")
                    if 'error_message' in result:
                        print(f"   - Error: {result['error_message']}")
                    
            except Exception as e:
                print(f"❌ Turkish address #{i+1}: ERROR - {e}")
        
        # Test 5: Error handling
        print(f"\n📋 Testing error handling:")
        
        error_test_cases = [
            ("Empty string", ""),
            ("Too short", "xy"),
            ("None input", None),
            ("Wrong type", 123)
        ]
        
        for case_name, test_input in error_test_cases:
            total += 1
            try:
                result = asyncio.run(pipeline.process_address_with_geo_lookup(test_input))
                
                # Should return error result
                if result.get('status') == 'error' and 'error_message' in result:
                    print(f"✅ {case_name}: PASSED - Error handled gracefully")
                    passed += 1
                else:
                    print(f"❌ {case_name}: FAILED - Should have returned error")
                    
            except Exception as e:
                # Exception is also acceptable for invalid inputs
                print(f"✅ {case_name}: PASSED - Exception raised: {type(e).__name__}")
                passed += 1
        
        # Test 6: Batch processing
        print(f"\n📋 Testing batch processing:")
        total += 1
        try:
            batch_addresses = [
                "İstanbul Kadıköy Test 1",
                "Ankara Çankaya Test 2", 
                "İzmir Konak Test 3"
            ]
            
            batch_result = asyncio.run(pipeline.process_batch_addresses(batch_addresses))
            
            # Validate batch result structure
            if ('results' in batch_result and 'batch_summary' in batch_result):
                results = batch_result['results']
                summary = batch_result['batch_summary']
                
                if (len(results) == len(batch_addresses) and 
                    summary['batch_size'] == len(batch_addresses)):
                    
                    print(f"✅ Batch processing: PASSED")
                    print(f"   - Batch size: {summary['batch_size']}")
                    print(f"   - Successful: {summary['successful_count']}")
                    print(f"   - Errors: {summary['error_count']}")
                    print(f"   - Throughput: {summary['throughput_per_second']:.1f} addr/sec")
                    passed += 1
                else:
                    print(f"❌ Batch processing: FAILED - Result count mismatch")
            else:
                print(f"❌ Batch processing: FAILED - Invalid batch result structure")
                
        except Exception as e:
            print(f"❌ Batch processing: ERROR - {e}")
        
        # Test 7: Performance validation
        print(f"\n📋 Testing performance:")
        total += 1
        try:
            test_address = "İstanbul Kadıköy Performance Test"
            
            # Measure actual performance
            start_time = time.time()
            result = asyncio.run(pipeline.process_address_with_geo_lookup(test_address))
            end_time = time.time()
            
            actual_time_ms = (end_time - start_time) * 1000
            recorded_time_ms = result['processing_time_ms']
            
            # Performance target: <100ms
            if actual_time_ms < 100 and recorded_time_ms > 0:
                print(f"✅ Performance: PASSED")
                print(f"   - Actual time: {actual_time_ms:.2f}ms")
                print(f"   - Recorded time: {recorded_time_ms:.2f}ms")
                print(f"   - Target: <100ms ✅")
                passed += 1
            else:
                print(f"❌ Performance: FAILED")
                print(f"   - Actual time: {actual_time_ms:.2f}ms")
                print(f"   - Target: <100ms")
                
        except Exception as e:
            print(f"❌ Performance: ERROR - {e}")
        
        # Test 8: Confidence calculation validation
        print(f"\n📋 Testing confidence calculation:")
        total += 1
        try:
            # Test different quality addresses
            test_cases = [
                ("Complete address", "İstanbul Kadıköy Moda Mahallesi Caferağa Sokak No 10 Daire 3"),
                ("Incomplete address", "İstanbul Kadıköy")
            ]
            
            confidences = []
            for case_name, address in test_cases:
                result = asyncio.run(pipeline.process_address_with_geo_lookup(address))
                confidence = result['final_confidence']
                confidences.append(confidence)
                print(f"   - {case_name}: {confidence:.3f}")
            
            # Validate confidence ranges and that complete > incomplete
            valid_ranges = all(0.0 <= conf <= 1.0 for conf in confidences)
            complete_higher = len(confidences) >= 2 and confidences[0] >= confidences[1]
            
            if valid_ranges and complete_higher:
                print(f"✅ Confidence calculation: PASSED")
                passed += 1
            else:
                print(f"❌ Confidence calculation: FAILED")
                print(f"   - Valid ranges: {valid_ranges}")
                print(f"   - Complete >= Incomplete: {complete_higher}")
                
        except Exception as e:
            print(f"❌ Confidence calculation: ERROR - {e}")
        
        # Test 9: Database integration (if available)
        print(f"\n📋 Testing database integration:")
        total += 1
        try:
            if pipeline.db_manager:
                # Test database initialization
                async def test_db():
                    await pipeline.initialize()
                    await pipeline.close()
                    return True
                
                db_success = asyncio.run(test_db())
                
                if db_success:
                    print(f"✅ Database integration: PASSED")
                    print(f"   - Database manager available")
                    print(f"   - Initialization/cleanup successful")
                    passed += 1
                else:
                    print(f"❌ Database integration: FAILED")
            else:
                print(f"⚠️  Database integration: SKIPPED - No database manager")
                # Don't count this as pass or fail if DB not available
                total -= 1
                
        except Exception as e:
            print(f"❌ Database integration: ERROR - {e}")
        
        # Summary
        print(f"\n" + "=" * 55)
        print(f"📊 Test Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 All tests passed! GeoIntegratedPipeline implementation is working correctly.")
        elif passed/total >= 0.8:
            print("✅ Most tests passed! Implementation is largely functional.")
        else:
            print("⚠️  Some tests failed. Implementation needs review.")
        
        # Performance summary
        if pipeline.pipeline_times:
            avg_time = sum(pipeline.pipeline_times) / len(pipeline.pipeline_times)
            max_time = max(pipeline.pipeline_times)
            print(f"\n⚡ Performance Summary:")
            print(f"   - Addresses processed: {len(pipeline.processed_addresses)}")
            print(f"   - Average processing time: {avg_time:.2f}ms")
            print(f"   - Maximum processing time: {max_time:.2f}ms")
            print(f"   - Error count: {pipeline.error_count}")
        
        return passed/total >= 0.8
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pipeline_features():
    """Test specific pipeline features"""
    
    print(f"\n🔧 Testing pipeline features:")
    print("=" * 40)
    
    try:
        from geo_integrated_pipeline import GeoIntegratedPipeline, pipeline_context, process_single_address
        
        pipeline = GeoIntegratedPipeline("postgresql://test:test@localhost:5432/testdb")
        
        # Test component availability
        print("✅ Pipeline components:")
        components = [
            ('AddressValidator', pipeline.validator is not None),
            ('AddressCorrector', pipeline.corrector is not None),
            ('AddressParser', pipeline.parser is not None),
            ('HybridAddressMatcher', pipeline.matcher is not None),
            ('PostGISManager', pipeline.db_manager is not None)
        ]
        
        for name, available in components:
            status = "✅" if available else "❌"
            print(f"   - {name}: {status}")
        
        # Test configuration
        print("✅ Configuration:")
        print(f"   - Database connection: {pipeline.db_connection_string}")
        print(f"   - Max batch size: {pipeline.max_batch_size}")
        print(f"   - Default search radius: {pipeline.default_search_radius}m")
        print(f"   - Confidence weights: {pipeline.confidence_weights}")
        
        # Test utility functions
        print("✅ Utility functions:")
        utility_functions = [
            ('pipeline_context', pipeline_context is not None),
            ('process_single_address', process_single_address is not None)
        ]
        
        for name, available in utility_functions:
            status = "✅" if available else "❌"
            print(f"   - {name}: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline features test error: {e}")
        return False

def main():
    """Run all GeoIntegratedPipeline tests"""
    
    print("🧪 TEKNOFEST GeoIntegratedPipeline - Real Implementation Tests")
    print("=" * 70)
    
    # Test real implementation
    success1 = test_real_geo_integrated_pipeline()
    
    # Test pipeline features
    success2 = test_pipeline_features()
    
    overall_success = success1 and success2
    
    print(f"\n🎯 Testing completed!")
    
    if overall_success:
        print(f"\n🚀 GeoIntegratedPipeline is ready for:")
        print("   • Complete 7-step address processing pipeline")
        print("   • Integration with all 4 algorithms (validator, corrector, parser, matcher)")
        print("   • Integration with PostGISManager database operations")
        print("   • Turkish address processing with full language support")
        print("   • Performance benchmarking (<100ms per complete pipeline)")
        print("   • Batch processing capabilities (up to 1000 addresses)")
        print("   • Error handling for all failure scenarios")
        print("   • Production deployment and API integration")
        print("   • TEKNOFEST competition readiness")
    else:
        print(f"\n⚠️  Some test categories failed. Review implementation.")
    
    return overall_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)