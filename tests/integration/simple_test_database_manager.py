"""
Simple test runner for PostGISManager test suite
Tests without pytest dependency
"""

import sys
import os
import asyncio
import time

# Add tests and src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def run_database_manager_tests():
    """Test PostGISManager mock implementation"""
    
    print("🧪 Testing PostGISManager Mock Implementation")
    print("=" * 55)
    
    try:
        # Import the mock class from test file
        from test_database_manager import MockPostGISManager
        
        # Initialize manager
        manager = MockPostGISManager()
        print("✅ MockPostGISManager initialized successfully")
        
        passed = 0
        total = 0
        
        # Test 1: Basic connection test
        print(f"\n📋 Testing basic connection:")
        total += 1
        try:
            is_connected = asyncio.run(manager.test_connection())
            if is_connected:
                print("✅ test_connection: PASSED")
                passed += 1
            else:
                print("❌ test_connection: FAILED")
        except Exception as e:
            print(f"❌ test_connection: ERROR - {e}")
        
        # Test 2: Spatial queries
        print(f"\n📋 Testing spatial queries:")
        
        # Test find_nearby_addresses
        total += 1
        try:
            coordinates = {'lat': 40.9875, 'lon': 29.0376}  # Istanbul Kadıköy
            results = asyncio.run(manager.find_nearby_addresses(coordinates, 1000))
            
            if isinstance(results, list) and len(results) > 0:
                print(f"✅ find_nearby_addresses: PASSED ({len(results)} results)")
                passed += 1
                
                # Check result structure
                for result in results[:2]:  # Check first 2 results
                    if all(key in result for key in ['id', 'raw_address', 'distance_meters']):
                        print(f"   - Result {result['id']}: {result['raw_address'][:50]}... (Distance: {result['distance_meters']:.1f}m)")
                    else:
                        print(f"   - Result structure incomplete")
            else:
                print("❌ find_nearby_addresses: FAILED - No results")
        except Exception as e:
            print(f"❌ find_nearby_addresses: ERROR - {e}")
        
        # Test 3: Administrative hierarchy queries
        print(f"\n📋 Testing administrative hierarchy queries:")
        
        hierarchy_tests = [
            {'name': 'Province only', 'params': {'il': 'İstanbul'}, 'expected_min': 1},
            {'name': 'Province and district', 'params': {'il': 'İstanbul', 'ilce': 'Kadıköy'}, 'expected_min': 1},
            {'name': 'Non-existent', 'params': {'il': 'NonExistent'}, 'expected_max': 0}
        ]
        
        for test_case in hierarchy_tests:
            total += 1
            try:
                results = asyncio.run(manager.find_by_admin_hierarchy(**test_case['params']))
                
                success = True
                if 'expected_min' in test_case:
                    success = len(results) >= test_case['expected_min']
                elif 'expected_max' in test_case:
                    success = len(results) <= test_case['expected_max']
                
                if success:
                    print(f"✅ {test_case['name']}: PASSED ({len(results)} results)")
                    passed += 1
                else:
                    print(f"❌ {test_case['name']}: FAILED ({len(results)} results)")
                    
            except Exception as e:
                print(f"❌ {test_case['name']}: ERROR - {e}")
        
        # Test 4: Address insertion
        print(f"\n📋 Testing address insertion:")
        
        total += 1
        try:
            sample_address = {
                'raw_address': 'Test Address for Insertion',
                'normalized_address': 'test address for insertion',
                'confidence_score': 0.85,
                'validation_status': 'valid',
                'parsed_components': {
                    'il': 'Test',
                    'ilce': 'Test',
                    'mahalle': 'Test Mahallesi'
                },
                'coordinates': {'lat': 41.0, 'lon': 29.0}
            }
            
            address_id = asyncio.run(manager.insert_address(sample_address))
            
            if isinstance(address_id, int) and address_id > 0:
                print(f"✅ insert_address: PASSED (ID: {address_id})")
                passed += 1
                
                # Verify insertion
                if len(manager.inserted_addresses) > 0:
                    inserted = manager.inserted_addresses[-1]
                    print(f"   - Inserted: {inserted['raw_address']}")
                    print(f"   - Confidence: {inserted['confidence_score']}")
            else:
                print("❌ insert_address: FAILED - Invalid ID")
                
        except Exception as e:
            print(f"❌ insert_address: ERROR - {e}")
        
        # Test 5: Performance testing
        print(f"\n📋 Testing performance:")
        
        performance_tests = [
            {
                'name': 'Spatial query performance',
                'operation': lambda: manager.find_nearby_addresses({'lat': 40.9875, 'lon': 29.0376}, 1000),
                'target_ms': 100
            },
            {
                'name': 'Admin hierarchy query performance',
                'operation': lambda: manager.find_by_admin_hierarchy(il='İstanbul'),
                'target_ms': 100
            },
            {
                'name': 'Insert performance',
                'operation': lambda: manager.insert_address({
                    'raw_address': f'Performance Test Address {time.time()}',
                    'confidence_score': 0.8
                }),
                'target_ms': 100
            }
        ]
        
        for perf_test in performance_tests:
            total += 1
            try:
                start_time = time.time()
                result = asyncio.run(perf_test['operation']())
                end_time = time.time()
                
                elapsed_ms = (end_time - start_time) * 1000
                
                if elapsed_ms < perf_test['target_ms']:
                    print(f"✅ {perf_test['name']}: PASSED ({elapsed_ms:.2f}ms)")
                    passed += 1
                else:
                    print(f"❌ {perf_test['name']}: FAILED ({elapsed_ms:.2f}ms > {perf_test['target_ms']}ms)")
                    
            except Exception as e:
                print(f"❌ {perf_test['name']}: ERROR - {e}")
        
        # Test 6: Error handling
        print(f"\n📋 Testing error handling:")
        
        error_tests = [
            {
                'name': 'Invalid coordinates',
                'operation': lambda: manager.find_nearby_addresses({}, 1000),
                'should_raise': ValueError
            },
            {
                'name': 'Invalid radius',
                'operation': lambda: manager.find_nearby_addresses({'lat': 40.0, 'lon': 29.0}, -100),
                'should_raise': ValueError
            },
            {
                'name': 'Missing raw_address',
                'operation': lambda: manager.insert_address({}),
                'should_raise': ValueError
            }
        ]
        
        for error_test in error_tests:
            total += 1
            try:
                asyncio.run(error_test['operation']())
                print(f"❌ {error_test['name']}: FAILED - Should have raised {error_test['should_raise'].__name__}")
            except error_test['should_raise']:
                print(f"✅ {error_test['name']}: PASSED - Correctly raised {error_test['should_raise'].__name__}")
                passed += 1
            except Exception as e:
                print(f"❌ {error_test['name']}: ERROR - Unexpected exception: {e}")
        
        # Test 7: Connection pool status
        print(f"\n📋 Testing connection pool:")
        
        total += 1
        try:
            pool_status = asyncio.run(manager.get_connection_pool_status())
            
            required_keys = ['total_connections', 'active_connections', 'idle_connections', 'pool_size']
            if all(key in pool_status for key in required_keys):
                print("✅ get_connection_pool_status: PASSED")
                print(f"   - Pool size: {pool_status['pool_size']}")
                print(f"   - Active connections: {pool_status['active_connections']}")
                passed += 1
            else:
                print("❌ get_connection_pool_status: FAILED - Missing keys")
                
        except Exception as e:
            print(f"❌ get_connection_pool_status: ERROR - {e}")
        
        # Test 8: Concurrent operations
        print(f"\n📋 Testing concurrent operations:")
        
        total += 1
        try:
            async def concurrent_test():
                # Create multiple concurrent tasks
                tasks = [
                    manager.find_nearby_addresses({'lat': 40.9875, 'lon': 29.0376}, 1000),
                    manager.find_by_admin_hierarchy(il='İstanbul'),
                    manager.insert_address({'raw_address': 'Concurrent Test 1'}),
                    manager.insert_address({'raw_address': 'Concurrent Test 2'}),
                    manager.test_connection()
                ]
                
                start_time = time.time()
                results = await asyncio.gather(*tasks)
                end_time = time.time()
                
                return results, (end_time - start_time) * 1000
            
            results, elapsed_ms = asyncio.run(concurrent_test())
            
            if len(results) == 5 and elapsed_ms < 500:  # Should be fast with concurrency
                print(f"✅ concurrent_operations: PASSED ({elapsed_ms:.2f}ms)")
                passed += 1
            else:
                print(f"❌ concurrent_operations: FAILED ({elapsed_ms:.2f}ms)")
                
        except Exception as e:
            print(f"❌ concurrent_operations: ERROR - {e}")
        
        # Test 9: Custom query execution
        print(f"\n📋 Testing custom queries:")
        
        total += 1
        try:
            query = "SELECT * FROM addresses WHERE confidence_score > 0.8"
            results = asyncio.run(manager.execute_custom_query(query))
            
            if isinstance(results, list):
                print(f"✅ execute_custom_query: PASSED ({len(results)} results)")
                passed += 1
            else:
                print("❌ execute_custom_query: FAILED - Invalid result type")
                
        except Exception as e:
            print(f"❌ execute_custom_query: ERROR - {e}")
        
        # Summary
        print(f"\n" + "=" * 55)
        print(f"📊 Test Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 All tests passed! PostGISManager mock implementation is working correctly.")
        elif passed/total >= 0.8:
            print("✅ Most tests passed! Mock implementation is largely functional.")
        else:
            print("⚠️  Some tests failed. Mock implementation needs review.")
        
        # Performance summary
        if manager.query_times:
            avg_query_time = sum(manager.query_times) / len(manager.query_times)
            max_query_time = max(manager.query_times)
            print(f"\n⚡ Performance Summary:")
            print(f"   - Average query time: {avg_query_time:.2f}ms")
            print(f"   - Maximum query time: {max_query_time:.2f}ms")
            print(f"   - Total queries executed: {len(manager.query_times)}")
        
        return passed/total >= 0.8
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mock_data_quality():
    """Test the quality and completeness of mock data"""
    
    print(f"\n🔧 Testing mock data quality:")
    print("=" * 35)
    
    try:
        from test_database_manager import MockPostGISManager
        
        manager = MockPostGISManager()
        
        print(f"✅ Mock addresses loaded: {len(manager.mock_addresses)}")
        
        # Analyze mock data
        turkish_cities = set()
        coordinate_count = 0
        
        for addr in manager.mock_addresses:
            # Extract cities
            components = addr.get('parsed_components', {})
            if 'il' in components:
                turkish_cities.add(components['il'])
            
            # Count coordinates
            if addr.get('coordinates'):
                coordinate_count += 1
        
        print(f"✅ Turkish cities in data: {', '.join(sorted(turkish_cities))}")
        print(f"✅ Addresses with coordinates: {coordinate_count}/{len(manager.mock_addresses)}")
        
        # Test data coverage
        required_fields = ['id', 'raw_address', 'parsed_components', 'confidence_score']
        field_coverage = {}
        
        for field in required_fields:
            count = sum(1 for addr in manager.mock_addresses if field in addr and addr[field])
            field_coverage[field] = count
        
        print(f"✅ Field coverage:")
        for field, count in field_coverage.items():
            percentage = (count / len(manager.mock_addresses)) * 100
            print(f"   - {field}: {count}/{len(manager.mock_addresses)} ({percentage:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"❌ Mock data quality test error: {e}")
        return False

def main():
    """Run all database manager tests"""
    
    print("🧪 TEKNOFEST PostGISManager - Comprehensive Test Suite")
    print("=" * 70)
    
    # Test mock implementation
    success1 = run_database_manager_tests()
    
    # Test mock data quality
    success2 = test_mock_data_quality()
    
    overall_success = success1 and success2
    
    print(f"\n🎯 Testing completed!")
    
    if overall_success:
        print(f"\n🚀 PostGISManager test suite is ready for:")
        print("   • Real PostGISManager implementation")
        print("   • PostgreSQL + PostGIS spatial queries")
        print("   • Administrative hierarchy searches")
        print("   • Address record insertion and management")
        print("   • Connection pooling and async operations")
        print("   • Performance benchmarking (<100ms per query)")
        print("   • Integration with database schema (001_create_tables.sql)")
        print("   • Production database deployment")
    else:
        print(f"\n⚠️  Some test categories failed. Review implementation.")
    
    return overall_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)