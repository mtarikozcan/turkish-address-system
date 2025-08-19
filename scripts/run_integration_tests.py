#!/usr/bin/env python3
"""
Address Resolution System Turkish Address Resolution System
Real Database Integration Test Runner

This script provides a simple way to run the comprehensive integration tests
with a real PostgreSQL+PostGIS database setup.

Usage:
  python run_integration_tests.py [--docker] [--connection-string=...]
  
Options:
  --docker                 Start Docker Compose database automatically
  --connection-string=...  Custom database connection string
  --test-category=...      Run specific test category only
  --verbose               Enable verbose logging
  --cleanup               Clean up test data after completion

Examples:
  # Run with Docker Compose (automatic setup)
  python run_integration_tests.py --docker
  
  # Run with custom database
  python run_integration_tests.py --connection-string="postgresql://user:pass@host:5432/db"
  
  # Run specific test category
  python run_integration_tests.py --docker --test-category=performance
  
  # Verbose mode with cleanup
  python run_integration_tests.py --docker --verbose --cleanup

Author: Address Resolution System Address Resolution Team
Version: 1.0.0
"""

import sys
import os
import asyncio
import argparse
import subprocess
import time
import json
from pathlib import Path

# Add tests directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))

# Import the integration tester
try:
    from test_real_database_integration import RealDatabaseIntegrationTester
except ImportError as e:
    print(f"❌ Failed to import integration tester: {e}")
    print("Make sure tests/test_real_database_integration.py exists")
    sys.exit(1)


class IntegrationTestRunner:
    """Main test runner for real database integration tests"""
    
    def __init__(self):
        self.docker_started = False
        self.verbose = False
        
    def parse_arguments(self):
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(
            description='Address Resolution System Real Database Integration Test Runner',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s --docker                                    # Use Docker Compose
  %(prog)s --connection-string="postgresql://..."     # Custom database
  %(prog)s --docker --test-category=performance       # Specific tests
  %(prog)s --docker --verbose --cleanup               # Verbose with cleanup
            """
        )
        
        parser.add_argument(
            '--docker',
            action='store_true',
            help='Start Docker Compose database automatically'
        )
        
        parser.add_argument(
            '--connection-string',
            type=str,
            default=None,
            help='Custom PostgreSQL connection string'
        )
        
        parser.add_argument(
            '--test-category',
            type=str,
            choices=['connection', 'integration', 'performance', 'concurrency', 'all'],
            default='all',
            help='Specific test category to run'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose logging'
        )
        
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Clean up test data after completion'
        )
        
        parser.add_argument(
            '--timeout',
            type=int,
            default=300,
            help='Test timeout in seconds (default: 300)'
        )
        
        return parser.parse_args()
    
    def setup_logging(self, verbose: bool):
        """Setup logging configuration"""
        import logging
        
        level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        self.verbose = verbose
        
    def start_docker_database(self):
        """Start Docker Compose database"""
        print("🐳 Starting Docker Compose database...")
        
        # Check if Docker Compose file exists
        compose_file = Path("docker-compose.test.yml")
        if not compose_file.exists():
            print(f"❌ Docker Compose file not found: {compose_file}")
            return False
        
        try:
            # Start database service
            result = subprocess.run([
                'docker-compose', '-f', 'docker-compose.test.yml',
                'up', '-d', 'test-database'
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                print(f"❌ Failed to start Docker database:")
                print(result.stderr)
                return False
            
            print("✅ Docker database started")
            
            # Wait for database to be ready
            print("⏳ Waiting for database to be ready...")
            max_wait = 60  # 60 seconds
            wait_interval = 2
            
            for attempt in range(max_wait // wait_interval):
                try:
                    # Test connection
                    test_result = subprocess.run([
                        'docker', 'exec', 'teknofest-test-db',
                        'pg_isready', '-U', 'test_user', '-d', 'address_resolution_test'
                    ], capture_output=True, text=True, timeout=10)
                    
                    if test_result.returncode == 0:
                        print("✅ Database is ready")
                        self.docker_started = True
                        return True
                        
                except subprocess.TimeoutExpired:
                    pass
                
                time.sleep(wait_interval)
                print(f"   Still waiting... ({attempt + 1}/{max_wait // wait_interval})")
            
            print("❌ Database failed to become ready within timeout")
            return False
            
        except Exception as e:
            print(f"❌ Error starting Docker database: {e}")
            return False
    
    def stop_docker_database(self):
        """Stop Docker Compose database"""
        if not self.docker_started:
            return
            
        print("🐳 Stopping Docker Compose database...")
        
        try:
            subprocess.run([
                'docker-compose', '-f', 'docker-compose.test.yml',
                'down'
            ], capture_output=True, text=True, timeout=30)
            
            print("✅ Docker database stopped")
            
        except Exception as e:
            print(f"⚠️ Warning: Error stopping Docker database: {e}")
    
    def get_connection_string(self, args):
        """Get database connection string"""
        if args.connection_string:
            return args.connection_string
        elif args.docker or self.docker_started:
            return "postgresql://test_user:test_password@localhost:5432/address_resolution_test"
        else:
            print("❌ No database connection specified")
            print("Use --docker for Docker Compose or --connection-string for custom database")
            return None
    
    async def run_specific_test_category(self, tester, category: str):
        """Run specific test category"""
        if category == 'connection':
            return await tester.test_real_database_connection()
        elif category == 'integration':
            return await tester.test_full_stack_integration()
        elif category == 'performance':
            return await tester.test_performance_with_real_database()
        elif category == 'concurrency':
            return await tester.test_concurrent_access()
        else:
            # Run all tests
            return await tester.run_all_integration_tests()
    
    def print_results_summary(self, results):
        """Print detailed test results summary"""
        print("\n" + "=" * 80)
        print("📊 DETAILED TEST RESULTS SUMMARY")
        print("=" * 80)
        
        if isinstance(results, dict) and 'test_results' in results:
            # Full test suite results
            overall_results = results
            test_results = results['test_results']
            
            print(f"🎯 Overall Success: {'✅ PASSED' if overall_results['overall_success'] else '❌ FAILED'}")
            print(f"📈 Success Rate: {overall_results['success_rate']:.1%} ({overall_results['passed_tests']}/{overall_results['total_tests']})")
            print(f"⏱️  Total Tests: {overall_results['total_tests']}")
            print(f"✅ Passed Tests: {overall_results['passed_tests']}")
            print(f"❌ Failed Tests: {overall_results['failed_tests']}")
            
            print(f"\n🔍 Test Category Breakdown:")
            
            for test_result in test_results:
                test_name = test_result.get('test_name', 'Unknown')
                passed = test_result.get('passed', False)
                status = "✅ PASSED" if passed else "❌ FAILED"
                
                print(f"   • {test_name:<35} {status}")
                
                # Show performance metrics if available
                if 'performance_metrics' in test_result:
                    perf = test_result['performance_metrics']
                    if 'single_address_avg_ms' in perf:
                        print(f"     └─ Avg processing time: {perf['single_address_avg_ms']:.2f}ms")
                    if 'batch_throughput_per_sec' in perf:
                        print(f"     └─ Batch throughput: {perf['batch_throughput_per_sec']:.1f} addr/sec")
                
                # Show error details if failed
                if not passed and 'details' in test_result:
                    error = test_result['details'].get('exception') or test_result['details'].get('error')
                    if error:
                        error_short = str(error)[:60] + "..." if len(str(error)) > 60 else str(error)
                        print(f"     └─ Error: {error_short}")
            
            # Summary metrics
            summary = overall_results.get('summary', {})
            print(f"\n🏆 System Validation Summary:")
            print(f"   • Database Integration: {'✅' if summary.get('real_database_integration') else '❌'}")
            print(f"   • Performance Validated: {'✅' if summary.get('performance_validated') else '❌'}")
            print(f"   • Concurrency Validated: {'✅' if summary.get('concurrency_validated') else '❌'}")
            print(f"   • Data Persistence: {'✅' if summary.get('data_persistence_validated') else '❌'}")
            print(f"   • Geographic Accuracy: {'✅' if summary.get('geographic_accuracy_validated') else '❌'}")
            
        else:
            # Single test result
            test_name = results.get('test_name', 'Single Test')
            passed = results.get('passed', False)
            status = "✅ PASSED" if passed else "❌ FAILED"
            
            print(f"🎯 Test: {test_name} - {status}")
            
            if 'performance_metrics' in results:
                print(f"\n📊 Performance Metrics:")
                for metric, value in results['performance_metrics'].items():
                    if isinstance(value, float):
                        print(f"   • {metric}: {value:.2f}")
                    else:
                        print(f"   • {metric}: {value}")
        
        print("=" * 80)
    
    def save_results_to_file(self, results, filename="integration_test_results.json"):
        """Save test results to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            print(f"📄 Results saved to: {filename}")
        except Exception as e:
            print(f"⚠️ Warning: Could not save results to file: {e}")
    
    async def run_tests(self, args):
        """Main test execution function"""
        print("🧪 Address Resolution System - Real Database Integration Test Runner")
        print("=" * 70)
        
        # Setup logging
        self.setup_logging(args.verbose)
        
        # Start Docker database if requested
        if args.docker:
            if not self.start_docker_database():
                return 1
        
        # Get connection string
        connection_string = self.get_connection_string(args)
        if not connection_string:
            return 1
        
        print(f"🔗 Database: {connection_string}")
        print(f"📋 Test Category: {args.test_category}")
        print(f"⏱️  Timeout: {args.timeout}s")
        print()
        
        try:
            # Initialize tester
            tester = RealDatabaseIntegrationTester(connection_string)
            
            # Run tests with timeout
            print("🚀 Starting integration tests...")
            start_time = time.time()
            
            if args.test_category == 'all':
                results = await asyncio.wait_for(
                    tester.run_all_integration_tests(),
                    timeout=args.timeout
                )
            else:
                results = await asyncio.wait_for(
                    self.run_specific_test_category(tester, args.test_category),
                    timeout=args.timeout
                )
            
            execution_time = time.time() - start_time
            
            # Print results
            self.print_results_summary(results)
            print(f"\n⏱️ Total execution time: {execution_time:.1f}s")
            
            # Save results to file
            self.save_results_to_file(results)
            
            # Cleanup if requested
            if args.cleanup:
                print("\n🧹 Cleaning up test data...")
                await tester.cleanup_test_environment()
            
            # Determine exit code
            if isinstance(results, dict):
                success = results.get('overall_success', results.get('passed', False))
            else:
                success = False
            
            if success:
                print("\n🎉 All integration tests completed successfully!")
                return 0
            else:
                print("\n⚠️ Some integration tests failed. Check results above.")
                return 1
                
        except asyncio.TimeoutError:
            print(f"\n⏰ Tests timed out after {args.timeout}s")
            return 1
            
        except KeyboardInterrupt:
            print("\n⚠️ Tests interrupted by user")
            return 1
            
        except Exception as e:
            print(f"\n❌ Test execution error: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            return 1
        
        finally:
            # Always stop Docker if we started it
            if args.docker:
                self.stop_docker_database()

    def run(self):
        """Main entry point"""
        args = self.parse_arguments()
        
        try:
            return asyncio.run(self.run_tests(args))
        except KeyboardInterrupt:
            print("\n⚠️ Interrupted by user")
            return 1
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            return 1


def main():
    """Entry point for script execution"""
    runner = IntegrationTestRunner()
    exit_code = runner.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()