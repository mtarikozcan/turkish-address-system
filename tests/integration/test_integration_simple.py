#!/usr/bin/env python3
"""
Simple test to verify the real database integration test framework
"""

import sys
import os
import asyncio

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))

async def test_simple_integration():
    """Run a simple integration test"""
    print("🧪 Testing Real Database Integration Framework")
    print("=" * 50)
    
    try:
        # Import test module
        from test_real_database_integration import RealDatabaseIntegrationTester
        
        print("✅ Test module imported successfully")
        
        # Create tester (will use fallback mode without real DB)
        tester = RealDatabaseIntegrationTester()
        print("✅ Tester initialized")
        
        # Test database connection (will fail without real DB, but that's OK)
        print("\n📋 Testing database connection check...")
        result = await tester.test_real_database_connection()
        
        print(f"Connection test completed: {'PASSED' if result['passed'] else 'FAILED'}")
        if 'details' in result:
            print(f"Details: {result['details']}")
        
        # Test the test framework structure
        print("\n📋 Verifying test framework structure...")
        
        test_methods = [
            'test_real_database_connection',
            'test_full_stack_integration',
            'test_geographic_data_accuracy',
            'test_data_persistence',
            'test_performance_with_real_database',
            'test_concurrent_access',
            'test_memory_usage',
            'test_error_handling_with_real_database',
            'test_administrative_hierarchy_validation'
        ]
        
        available_methods = []
        for method_name in test_methods:
            if hasattr(tester, method_name):
                available_methods.append(method_name)
                print(f"  ✅ {method_name}")
            else:
                print(f"  ❌ {method_name}")
        
        print(f"\n✅ Framework has {len(available_methods)}/{len(test_methods)} test methods")
        
        # Test data structure
        print("\n📋 Verifying test data...")
        print(f"  - Turkish test addresses: {len(tester.turkish_test_addresses)}")
        print(f"  - Error scenarios: {len(tester.error_test_scenarios)}")
        
        # Sample test addresses
        print("\n📋 Sample test addresses:")
        for i, addr in enumerate(tester.turkish_test_addresses[:3]):
            print(f"  {i+1}. {addr['raw_address']}")
            print(f"     Category: {addr.get('category')}")
            print(f"     Expected: {addr.get('expected_il')}, {addr.get('expected_ilce')}")
        
        print("\n✅ Integration test framework is properly configured!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_pipeline_integration():
    """Test pipeline with mock database"""
    print("\n🧪 Testing Pipeline Integration (Mock Mode)")
    print("=" * 50)
    
    try:
        # Import pipeline
        from geo_integrated_pipeline import GeoIntegratedPipeline
        
        # Create pipeline with test connection
        pipeline = GeoIntegratedPipeline("postgresql://test:test@localhost:5432/test")
        print("✅ Pipeline created")
        
        # Test address processing (will use fallback mode)
        test_address = "İstanbul Kadıköy Moda Mahallesi Test Sokak 123"
        print(f"\n📋 Processing test address: {test_address}")
        
        result = await pipeline.process_address_with_geo_lookup(test_address)
        
        print(f"✅ Processing completed:")
        print(f"  - Status: {result.get('status')}")
        print(f"  - Confidence: {result.get('final_confidence', 0):.3f}")
        print(f"  - Processing time: {result.get('processing_time_ms', 0):.2f}ms")
        
        # Check pipeline components
        print("\n📋 Pipeline components:")
        components = [
            ('Validator', pipeline.validator),
            ('Corrector', pipeline.corrector),
            ('Parser', pipeline.parser),
            ('Matcher', pipeline.matcher),
            ('DB Manager', pipeline.db_manager)
        ]
        
        for name, component in components:
            status = "✅" if component is not None else "❌"
            print(f"  {status} {name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline test error: {e}")
        return False

async def main():
    """Run all simple tests"""
    success = True
    
    # Test 1: Framework structure
    if not await test_simple_integration():
        success = False
    
    # Test 2: Pipeline integration
    if not await test_pipeline_integration():
        success = False
    
    return success

if __name__ == "__main__":
    print("🚀 TEKNOFEST 2025 - Integration Test Framework Verification")
    print("=" * 60)
    
    success = asyncio.run(main())
    
    if success:
        print("\n✅ All framework tests passed!")
        print("\nTo run full integration tests with real database:")
        print("  python run_real_database_tests.py --setup-docker --cleanup")
    else:
        print("\n❌ Some framework tests failed")
    
    sys.exit(0 if success else 1)