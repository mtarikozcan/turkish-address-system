#!/usr/bin/env python3
"""
TEKNOFEST 2025 Turkish Address Resolution System
Real Database Integration Test Runner

This script provides a simple way to run the comprehensive real database
integration tests with optional Docker setup.

Usage:
    python run_real_database_tests.py [--setup-docker] [--cleanup]
    
Options:
    --setup-docker: Start Docker containers before testing
    --cleanup: Stop and remove Docker containers after testing
    --connection: Custom database connection string
"""

import sys
import os
import asyncio
import subprocess
import time
import argparse
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseTestRunner:
    """Manages Docker containers and runs integration tests"""
    
    def __init__(self, connection_string=None):
        self.connection_string = connection_string
        self.docker_compose_file = "docker-compose.test.yml"
        
    def check_docker_installed(self) -> bool:
        """Check if Docker and Docker Compose are installed"""
        try:
            subprocess.run(["docker", "--version"], 
                         capture_output=True, check=True)
            subprocess.run(["docker-compose", "--version"], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def start_docker_containers(self) -> bool:
        """Start Docker containers for testing"""
        logger.info("Starting Docker containers...")
        
        try:
            # Stop any existing containers
            subprocess.run(
                ["docker-compose", "-f", self.docker_compose_file, "down"],
                capture_output=True
            )
            
            # Start new containers
            result = subprocess.run(
                ["docker-compose", "-f", self.docker_compose_file, "up", "-d"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Failed to start containers: {result.stderr}")
                return False
            
            logger.info("Docker containers started, waiting for database to be ready...")
            
            # Wait for database to be ready
            max_attempts = 30
            for attempt in range(max_attempts):
                try:
                    result = subprocess.run(
                        ["docker", "exec", "teknofest-test-db", 
                         "pg_isready", "-U", "test_user", "-d", "address_resolution_test"],
                        capture_output=True
                    )
                    
                    if result.returncode == 0:
                        logger.info("✅ Database is ready!")
                        time.sleep(2)  # Extra time for PostGIS initialization
                        return True
                    
                except subprocess.CalledProcessError:
                    pass
                
                time.sleep(1)
                if attempt % 5 == 0:
                    logger.info(f"Waiting for database... ({attempt}/{max_attempts})")
            
            logger.error("Database failed to become ready")
            return False
            
        except Exception as e:
            logger.error(f"Error starting Docker containers: {e}")
            return False
    
    def stop_docker_containers(self):
        """Stop and remove Docker containers"""
        logger.info("Stopping Docker containers...")
        
        try:
            subprocess.run(
                ["docker-compose", "-f", self.docker_compose_file, "down", "-v"],
                capture_output=True
            )
            logger.info("✅ Docker containers stopped and removed")
            
        except Exception as e:
            logger.error(f"Error stopping Docker containers: {e}")
    
    def get_container_logs(self):
        """Get logs from the database container"""
        try:
            result = subprocess.run(
                ["docker", "logs", "teknofest-test-db", "--tail", "50"],
                capture_output=True,
                text=True
            )
            return result.stdout
        except:
            return "Could not retrieve container logs"
    
    async def run_integration_tests(self) -> bool:
        """Run the real database integration tests"""
        logger.info("Running real database integration tests...")
        
        try:
            # Import test module
            from test_real_database_integration import RealDatabaseIntegrationTester
            
            # Create tester with connection string
            tester = RealDatabaseIntegrationTester(self.connection_string)
            
            # Run all tests
            results = await tester.run_all_integration_tests()
            
            # Print detailed results
            self._print_test_results(results)
            
            return results['overall_success']
            
        except ImportError as e:
            logger.error(f"Failed to import test module: {e}")
            return False
        except Exception as e:
            logger.error(f"Test execution error: {e}")
            
            # Print container logs for debugging
            if self.check_docker_installed():
                logger.info("Database container logs:")
                print(self.get_container_logs())
            
            return False
    
    def _print_test_results(self, results):
        """Print detailed test results"""
        print("\n" + "=" * 70)
        print("📊 DETAILED TEST RESULTS")
        print("=" * 70)
        
        for test_result in results['test_results']:
            test_name = test_result.get('test_name', 'Unknown')
            passed = test_result.get('passed', False)
            status = "✅ PASSED" if passed else "❌ FAILED"
            
            print(f"\n{test_name}: {status}")
            
            # Print details for failed tests
            if not passed:
                details = test_result.get('details', {})
                if 'exception' in details:
                    print(f"  Exception: {details['exception']}")
                if 'error' in details:
                    print(f"  Error: {details['error']}")
            
            # Print performance metrics if available
            if 'performance_metrics' in test_result:
                metrics = test_result['performance_metrics']
                print("  Performance Metrics:")
                for key, value in metrics.items():
                    if isinstance(value, float):
                        print(f"    - {key}: {value:.2f}")
                    else:
                        print(f"    - {key}: {value}")
        
        print("\n" + "=" * 70)
        
        # Print summary
        summary = results.get('summary', {})
        print("\n📈 TEST SUMMARY")
        print("=" * 40)
        print(f"Overall Success: {'✅ YES' if results['overall_success'] else '❌ NO'}")
        print(f"Success Rate: {results['success_rate']:.1%}")
        print(f"Tests Passed: {results['passed_tests']}/{results['total_tests']}")
        
        if summary:
            print("\nValidation Status:")
            for key, value in summary.items():
                status = "✅" if value else "❌"
                print(f"  - {key.replace('_', ' ').title()}: {status}")
        
        print("=" * 40)


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Run TEKNOFEST 2025 Real Database Integration Tests"
    )
    parser.add_argument(
        "--setup-docker",
        action="store_true",
        help="Start Docker containers before testing"
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Stop and remove Docker containers after testing"
    )
    parser.add_argument(
        "--connection",
        type=str,
        help="Custom database connection string"
    )
    
    args = parser.parse_args()
    
    # Create test runner
    runner = DatabaseTestRunner(args.connection)
    
    success = False
    
    try:
        # Setup Docker if requested
        if args.setup_docker:
            if not runner.check_docker_installed():
                logger.error("Docker is not installed or not running")
                return 1
            
            if not runner.start_docker_containers():
                logger.error("Failed to start Docker containers")
                return 1
        
        # Run tests
        success = await runner.run_integration_tests()
        
    finally:
        # Cleanup if requested
        if args.cleanup and runner.check_docker_installed():
            runner.stop_docker_containers()
    
    # Return appropriate exit code
    return 0 if success else 1


if __name__ == "__main__":
    print("🧪 TEKNOFEST 2025 - Real Database Integration Test Runner")
    print("=" * 70)
    
    exit_code = asyncio.run(main())
    
    if exit_code == 0:
        print("\n✅ All integration tests completed successfully!")
    else:
        print("\n❌ Some integration tests failed. Please check the logs above.")
    
    sys.exit(exit_code)