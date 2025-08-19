#!/usr/bin/env python3
"""
TEKNOFEST 2025 - Comprehensive Manual Jury Testing Framework
Interactive test framework for comprehensive address system validation

This framework tests the system with challenging real-world scenarios
that juries might use to evaluate TEKNOFEST competition submissions.

Author: TEKNOFEST 2025 Address Resolution Team
Version: 1.0.0
"""

import sys
import time
import json
import traceback
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime
from dataclasses import dataclass

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Import all system components
from duplicate_detector import DuplicateAddressDetector
from address_geocoder import AddressGeocoder
from geo_integrated_pipeline import GeoIntegratedPipeline


@dataclass
class TestBatchResult:
    """Result structure for a test batch"""
    batch_name: str
    addresses: List[str]
    duplicate_groups: List[List[int]]
    geocoding_results: List[Dict]
    processing_times: List[float]
    errors: List[str]
    success_rate: float
    duplicate_detection_rate: float
    geocoding_success_rate: float
    avg_processing_time: float
    passed_tests: int
    total_tests: int
    overall_score: float


class ManualJuryTestFramework:
    """
    Comprehensive manual testing framework for TEKNOFEST 2025 jury evaluation.
    
    Tests 5 challenging batches:
    1. Turkish Character Hell - Character normalization stress test
    2. Abbreviation Nightmare - Abbreviation handling validation
    3. Real World Chaos - Messy real-world address formats
    4. Geocoding Accuracy - Coordinate assignment precision
    5. Edge Cases & System Breakers - Robustness testing
    """
    
    def __init__(self):
        """Initialize the testing framework with all components"""
        print("🚀 INITIALIZING TEKNOFEST 2025 MANUAL JURY TEST FRAMEWORK")
        print("=" * 80)
        
        # Initialize system components
        try:
            self.duplicate_detector = DuplicateAddressDetector(similarity_threshold=0.75)
            self.geocoder = AddressGeocoder()
            self.pipeline = GeoIntegratedPipeline("postgresql://test:test@localhost/test")
            print("✅ All system components initialized successfully")
        except Exception as e:
            print(f"⚠️  Component initialization warning: {e}")
            print("   Continuing with available components...")
        
        # Define the 5 test batches
        self.test_batches = self._define_test_batches()
        
        # Test criteria and scoring weights
        self.scoring_weights = {
            'duplicate_detection': 0.30,  # 30% - Critical for TEKNOFEST
            'geocoding_accuracy': 0.25,   # 25% - Geographic precision
            'processing_speed': 0.20,     # 20% - Performance requirement
            'error_handling': 0.15,       # 15% - System robustness
            'turkish_support': 0.10       # 10% - Language specialization
        }
        
        # Pass/fail criteria
        self.pass_criteria = {
            'min_duplicate_detection_rate': 0.15,  # TEKNOFEST minimum 15%
            'max_processing_time_ms': 100,         # <100ms requirement
            'min_geocoding_success_rate': 0.70,    # 70% geocoding success
            'max_error_rate': 0.10,                # <10% error rate
            'min_overall_score': 0.70              # 70% overall score to pass
        }
        
        # Results storage
        self.batch_results = []
        self.overall_results = {}
        
        print(f"✅ Framework initialized with {len(self.test_batches)} test batches")
        print(f"✅ Pass criteria: {self.pass_criteria['min_overall_score']:.0%} overall score required")
    
    def _define_test_batches(self) -> Dict[str, List[str]]:
        """Define the 5 challenging test batches for jury evaluation"""
        
        return {
            "TEST_BATCH_1_TURKISH_CHARACTER_HELL": [
                "İSTANBUL kadıköy MODA mahallesi caferağa sk 10",
                "istanbul KADİKÖY moda MAHALLESİ caferaga sokak 10",
                "Izmit Körfez Ihsaniye Mahallesi Deniz Caddesi",
                "İzmit Körfez İhsaniye Mahallesi Deniz Caddesi",
                "Mugla Bodrum Gumbet Mahallesi Sahil Yolu",
                "Muğla Bodrum Gümbet Mahallesi Sahil Yolu"
            ],
            
            "TEST_BATCH_2_ABBREVIATION_NIGHTMARE": [
                "Ank. Çank. Kızılay Mh. Atatürk Blv. No:25/A Daire:3",
                "Ankara Çankaya Kızılay Mahallesi Atatürk Bulvarı Numara:25/A Daire:3",
                "İst. Beşiktaş Levent Mah. Büyükdere Cd. No:15",
                "İstanbul Beşiktaş Levent Mahallesi Büyükdere Caddesi 15",
                "İzm. Krnk. Basmane Mhl. İstasyon Cad. Apt:5",
                "İzmir Konak Basmane Mahallesi İstasyon Caddesi Apartman:5"
            ],
            
            "TEST_BATCH_3_REAL_WORLD_CHAOS": [
                "istanbul  kadikoy   moda mah.caferaga sk.no:10/a",
                "İstanbul Kadıköy Moda Mahallesi Caferağa Sokak 10/A",
                "Ankara Çankaya Büklüm Sokak Mahallesi Atatürk Cad",
                "Ankara Çankaya Kavaklıdere Mahallesi Atatürk Caddesi",
                "İzmir Konak Alsancak Mah. Cumhuriyet Cad. No:45 Kat:3 Daire:5",
                "İzmir Konak Alsancak Mahallesi Cumhuriyet Caddesi 45/3/5",
                "Bursa Osmangazi Heykel Mahallesi Atatürk Caddesi Üzeri Market Yanı",
                "Bursa Osmangazi Heykel Mah. Atatürk Cad."
            ],
            
            "TEST_BATCH_4_GEOCODING_ACCURACY": [
                "İstanbul Beyoğlu Taksim Mahallesi",
                "Ankara Çankaya Kızılay Mahallesi", 
                "İzmir Konak Alsancak Mahallesi",
                "Bursa Osmangazi Heykel Mahallesi",
                "Antalya Muratpaşa Lara Mahallesi",
                "Gaziantep Şahinbey Merkez Mahallesi",
                "Adana Seyhan Kurtuluş Mahallesi"
            ],
            
            "TEST_BATCH_5_EDGE_CASES_SYSTEM_BREAKERS": [
                "asdfghjkl zxcvbnm qwertyuiop",  # Garbage input
                "Kadıköy",  # Too short/incomplete
                "İstanbul Kadıköy Moda Mahallesi Caferağa Sokak 10 Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua ut enim ad minim veniam quis nostrud exercitation",  # Too long
                "İstanbul Kadıköy Moda",  # Partial address
                "İstanbul Kadıköy"  # Minimal address
            ]
        }
    
    def run_comprehensive_jury_tests(self) -> Dict[str, Any]:
        """
        Run all 5 test batches and generate comprehensive jury evaluation report.
        
        Returns:
            Complete test results with pass/fail determination
        """
        print("\n🔥 STARTING COMPREHENSIVE JURY TESTING")
        print("=" * 80)
        print("Testing system against 5 challenging batches designed to stress-test")
        print("all aspects of the TEKNOFEST 2025 address resolution requirements...")
        
        overall_start_time = time.time()
        
        # Run each test batch
        for batch_name, addresses in self.test_batches.items():
            print(f"\n🎯 RUNNING {batch_name}")
            print("-" * 60)
            
            batch_result = self._run_single_test_batch(batch_name, addresses)
            self.batch_results.append(batch_result)
            
            # Display batch results immediately
            self._display_batch_results(batch_result)
        
        # Calculate overall results
        overall_time = time.time() - overall_start_time
        self.overall_results = self._calculate_overall_results(overall_time)
        
        # Generate comprehensive report
        self._generate_jury_report()
        
        return {
            'batch_results': self.batch_results,
            'overall_results': self.overall_results,
            'test_timestamp': datetime.now().isoformat(),
            'pass_status': self.overall_results['overall_pass']
        }
    
    def _run_single_test_batch(self, batch_name: str, addresses: List[str]) -> TestBatchResult:
        """Run tests on a single batch and return detailed results"""
        
        print(f"📋 Processing {len(addresses)} addresses...")
        for i, addr in enumerate(addresses, 1):
            print(f"   {i}. {addr}")
        
        # Initialize result tracking
        processing_times = []
        errors = []
        duplicate_groups = []
        geocoding_results = []
        
        # Test 1: Duplicate Detection
        print(f"\n🔍 TEST 1: Duplicate Detection")
        try:
            start_time = time.time()
            duplicate_groups = self.duplicate_detector.find_duplicate_groups(addresses)
            duplicate_time = (time.time() - start_time) * 1000
            processing_times.append(duplicate_time)
            
            duplicate_count = len([g for g in duplicate_groups if len(g) > 1])
            duplicate_rate = (sum(len(g) - 1 for g in duplicate_groups if len(g) > 1)) / len(addresses)
            
            print(f"   ✅ Found {duplicate_count} duplicate groups")
            print(f"   ✅ Duplicate detection rate: {duplicate_rate:.1%}")
            print(f"   ✅ Processing time: {duplicate_time:.2f}ms")
            
        except Exception as e:
            error_msg = f"Duplicate detection failed: {str(e)}"
            errors.append(error_msg)
            print(f"   ❌ {error_msg}")
            duplicate_rate = 0.0
        
        # Test 2: Geocoding Accuracy
        print(f"\n🌍 TEST 2: Geocoding Accuracy")
        geocoding_successes = 0
        
        for i, address in enumerate(addresses):
            try:
                start_time = time.time()
                geocoding_result = self.geocoder.geocode_turkish_address(address)
                geocoding_time = (time.time() - start_time) * 1000
                processing_times.append(geocoding_time)
                
                geocoding_results.append(geocoding_result)
                
                if geocoding_result.get('latitude') and geocoding_result.get('longitude'):
                    if geocoding_result.get('method') != 'turkey_center':  # Not fallback
                        geocoding_successes += 1
                        print(f"   ✅ Address {i+1}: ({geocoding_result['latitude']:.4f}, {geocoding_result['longitude']:.4f}) - {geocoding_result.get('method', 'unknown')}")
                    else:
                        print(f"   ⚠️  Address {i+1}: Fallback coordinates used")
                else:
                    print(f"   ❌ Address {i+1}: No coordinates found")
                    
            except Exception as e:
                error_msg = f"Geocoding failed for address {i+1}: {str(e)}"
                errors.append(error_msg)
                print(f"   ❌ {error_msg}")
                geocoding_results.append({'error': str(e)})
        
        geocoding_success_rate = geocoding_successes / len(addresses) if addresses else 0
        print(f"   📊 Geocoding success rate: {geocoding_success_rate:.1%}")
        
        # Test 3: Processing Speed Analysis
        print(f"\n⚡ TEST 3: Processing Speed Analysis")
        if processing_times:
            avg_time = sum(processing_times) / len(processing_times)
            max_time = max(processing_times)
            min_time = min(processing_times)
            
            print(f"   📊 Average processing time: {avg_time:.2f}ms")
            print(f"   📊 Max processing time: {max_time:.2f}ms")
            print(f"   📊 Min processing time: {min_time:.2f}ms")
            
            speed_pass = avg_time < self.pass_criteria['max_processing_time_ms']
            print(f"   {'✅' if speed_pass else '❌'} Speed requirement (<100ms): {'PASS' if speed_pass else 'FAIL'}")
        else:
            avg_time = 0
            print(f"   ❌ No processing times recorded")
        
        # Test 4: Error Rate Analysis
        print(f"\n🛡️  TEST 4: Error Rate Analysis")
        error_rate = len(errors) / (len(addresses) * 2) if addresses else 0  # 2 tests per address
        print(f"   📊 Error count: {len(errors)}")
        print(f"   📊 Error rate: {error_rate:.1%}")
        
        error_pass = error_rate < self.pass_criteria['max_error_rate']
        print(f"   {'✅' if error_pass else '❌'} Error rate requirement (<10%): {'PASS' if error_pass else 'FAIL'}")
        
        # Calculate batch score
        passed_tests = 0
        total_tests = 4
        
        if duplicate_rate >= self.pass_criteria['min_duplicate_detection_rate']:
            passed_tests += 1
        if geocoding_success_rate >= self.pass_criteria['min_geocoding_success_rate']:
            passed_tests += 1
        if avg_time < self.pass_criteria['max_processing_time_ms']:
            passed_tests += 1
        if error_rate < self.pass_criteria['max_error_rate']:
            passed_tests += 1
        
        overall_score = passed_tests / total_tests
        success_rate = (len(addresses) * 2 - len(errors)) / (len(addresses) * 2) if addresses else 0
        
        return TestBatchResult(
            batch_name=batch_name,
            addresses=addresses,
            duplicate_groups=duplicate_groups,
            geocoding_results=geocoding_results,
            processing_times=processing_times,
            errors=errors,
            success_rate=success_rate,
            duplicate_detection_rate=duplicate_rate,
            geocoding_success_rate=geocoding_success_rate,
            avg_processing_time=avg_time,
            passed_tests=passed_tests,
            total_tests=total_tests,
            overall_score=overall_score
        )
    
    def _display_batch_results(self, result: TestBatchResult):
        """Display formatted batch results"""
        print(f"\n📊 BATCH RESULTS: {result.batch_name}")
        print("-" * 40)
        print(f"Addresses tested: {len(result.addresses)}")
        print(f"Success rate: {result.success_rate:.1%}")
        print(f"Duplicate detection rate: {result.duplicate_detection_rate:.1%}")
        print(f"Geocoding success rate: {result.geocoding_success_rate:.1%}")
        print(f"Average processing time: {result.avg_processing_time:.2f}ms")
        print(f"Errors encountered: {len(result.errors)}")
        print(f"Tests passed: {result.passed_tests}/{result.total_tests}")
        print(f"Batch score: {result.overall_score:.1%}")
        
        batch_pass = result.overall_score >= 0.70
        print(f"Batch status: {'✅ PASS' if batch_pass else '❌ FAIL'}")
    
    def _calculate_overall_results(self, total_time: float) -> Dict[str, Any]:
        """Calculate comprehensive overall results"""
        
        if not self.batch_results:
            return {'error': 'No batch results available'}
        
        # Aggregate metrics
        total_addresses = sum(len(r.addresses) for r in self.batch_results)
        total_errors = sum(len(r.errors) for r in self.batch_results)
        
        avg_duplicate_rate = sum(r.duplicate_detection_rate for r in self.batch_results) / len(self.batch_results)
        avg_geocoding_rate = sum(r.geocoding_success_rate for r in self.batch_results) / len(self.batch_results)
        
        all_times = []
        for result in self.batch_results:
            all_times.extend(result.processing_times)
        
        overall_avg_time = sum(all_times) / len(all_times) if all_times else 0
        overall_error_rate = total_errors / (total_addresses * 2) if total_addresses else 0
        overall_success_rate = 1 - overall_error_rate
        
        # Calculate weighted overall score
        scores = {
            'duplicate_detection': min(avg_duplicate_rate / self.pass_criteria['min_duplicate_detection_rate'], 1.0),
            'geocoding_accuracy': avg_geocoding_rate,
            'processing_speed': min(100 / max(overall_avg_time, 1), 1.0),
            'error_handling': 1 - overall_error_rate,
            'turkish_support': sum(r.overall_score for r in self.batch_results) / len(self.batch_results)
        }
        
        weighted_overall_score = sum(
            scores[metric] * weight 
            for metric, weight in self.scoring_weights.items()
        )
        
        # Determine pass/fail
        overall_pass = weighted_overall_score >= self.pass_criteria['min_overall_score']
        
        # Individual criteria checks
        criteria_results = {
            'duplicate_detection_pass': avg_duplicate_rate >= self.pass_criteria['min_duplicate_detection_rate'],
            'processing_speed_pass': overall_avg_time < self.pass_criteria['max_processing_time_ms'],
            'geocoding_accuracy_pass': avg_geocoding_rate >= self.pass_criteria['min_geocoding_success_rate'],
            'error_rate_pass': overall_error_rate < self.pass_criteria['max_error_rate'],
            'overall_score_pass': weighted_overall_score >= self.pass_criteria['min_overall_score']
        }
        
        return {
            'total_test_time_seconds': total_time,
            'total_addresses_tested': total_addresses,
            'total_batches': len(self.batch_results),
            'overall_success_rate': overall_success_rate,
            'avg_duplicate_detection_rate': avg_duplicate_rate,
            'avg_geocoding_success_rate': avg_geocoding_rate,
            'overall_avg_processing_time_ms': overall_avg_time,
            'overall_error_rate': overall_error_rate,
            'weighted_overall_score': weighted_overall_score,
            'component_scores': scores,
            'criteria_results': criteria_results,
            'overall_pass': overall_pass,
            'batches_passed': sum(1 for r in self.batch_results if r.overall_score >= 0.70),
            'recommendation': 'READY FOR TEKNOFEST COMPETITION' if overall_pass else 'NEEDS IMPROVEMENT BEFORE COMPETITION'
        }
    
    def _generate_jury_report(self):
        """Generate comprehensive jury evaluation report"""
        print("\n" + "=" * 80)
        print("🏆 TEKNOFEST 2025 JURY EVALUATION REPORT")
        print("=" * 80)
        
        print(f"\n📋 EXECUTIVE SUMMARY")
        print("-" * 40)
        print(f"Total test duration: {self.overall_results['total_test_time_seconds']:.1f} seconds")
        print(f"Total addresses tested: {self.overall_results['total_addresses_tested']}")
        print(f"Total batches tested: {self.overall_results['total_batches']}")
        print(f"Batches passed: {self.overall_results['batches_passed']}/{len(self.batch_results)}")
        
        print(f"\n📊 KEY PERFORMANCE METRICS")
        print("-" * 40)
        print(f"Overall success rate: {self.overall_results['overall_success_rate']:.1%}")
        print(f"Duplicate detection rate: {self.overall_results['avg_duplicate_detection_rate']:.1%}")
        print(f"Geocoding success rate: {self.overall_results['avg_geocoding_success_rate']:.1%}")
        print(f"Average processing time: {self.overall_results['overall_avg_processing_time_ms']:.2f}ms")
        print(f"Overall error rate: {self.overall_results['overall_error_rate']:.1%}")
        
        print(f"\n🎯 TEKNOFEST COMPLIANCE CHECK")
        print("-" * 40)
        criteria = self.overall_results['criteria_results']
        print(f"{'✅' if criteria['duplicate_detection_pass'] else '❌'} Duplicate detection rate ≥ 15%: {self.overall_results['avg_duplicate_detection_rate']:.1%}")
        print(f"{'✅' if criteria['processing_speed_pass'] else '❌'} Processing time < 100ms: {self.overall_results['overall_avg_processing_time_ms']:.2f}ms")
        print(f"{'✅' if criteria['geocoding_accuracy_pass'] else '❌'} Geocoding success ≥ 70%: {self.overall_results['avg_geocoding_success_rate']:.1%}")
        print(f"{'✅' if criteria['error_rate_pass'] else '❌'} Error rate < 10%: {self.overall_results['overall_error_rate']:.1%}")
        
        print(f"\n🏅 COMPONENT SCORES")
        print("-" * 40)
        for component, score in self.overall_results['component_scores'].items():
            weight = self.scoring_weights[component]
            print(f"{component.replace('_', ' ').title()}: {score:.1%} (weight: {weight:.0%})")
        
        print(f"\n🎖️  FINAL EVALUATION")
        print("-" * 40)
        overall_score = self.overall_results['weighted_overall_score']
        overall_pass = self.overall_results['overall_pass']
        
        print(f"Weighted Overall Score: {overall_score:.1%}")
        print(f"Pass Threshold: {self.pass_criteria['min_overall_score']:.0%}")
        print(f"\nFINAL VERDICT: {'🏆 PASS - ' + self.overall_results['recommendation'] if overall_pass else '❌ FAIL - ' + self.overall_results['recommendation']}")
        
        if overall_pass:
            print(f"\n🎉 CONGRATULATIONS!")
            print("Your system meets TEKNOFEST 2025 competition requirements.")
            print("The system demonstrates robust Turkish address handling,")
            print("effective duplicate detection, and reliable geocoding.")
        else:
            print(f"\n⚠️  AREAS FOR IMPROVEMENT:")
            if not criteria['duplicate_detection_pass']:
                print("- Improve duplicate detection rate to ≥15%")
            if not criteria['processing_speed_pass']:
                print("- Optimize processing speed to <100ms")
            if not criteria['geocoding_accuracy_pass']:
                print("- Enhance geocoding success rate to ≥70%")
            if not criteria['error_rate_pass']:
                print("- Reduce error rate to <10%")
        
        # Individual batch summaries
        print(f"\n📝 INDIVIDUAL BATCH SUMMARIES")
        print("-" * 40)
        for result in self.batch_results:
            status = "PASS" if result.overall_score >= 0.70 else "FAIL"
            print(f"{result.batch_name}: {result.overall_score:.0%} - {status}")
            if result.errors:
                print(f"   Errors: {len(result.errors)}")
        
        print("\n" + "=" * 80)
    
    def save_detailed_results(self, filename: str = None):
        """Save detailed test results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"jury_test_results_{timestamp}.json"
        
        detailed_results = {
            'test_framework_info': {
                'framework_name': 'TEKNOFEST 2025 Manual Jury Testing Framework',
                'version': '1.0.0',
                'test_timestamp': datetime.now().isoformat(),
                'pass_criteria': self.pass_criteria,
                'scoring_weights': self.scoring_weights
            },
            'batch_results': [
                {
                    'batch_name': r.batch_name,
                    'addresses': r.addresses,
                    'duplicate_groups': r.duplicate_groups,
                    'processing_times': r.processing_times,
                    'errors': r.errors,
                    'success_rate': r.success_rate,
                    'duplicate_detection_rate': r.duplicate_detection_rate,
                    'geocoding_success_rate': r.geocoding_success_rate,
                    'avg_processing_time': r.avg_processing_time,
                    'passed_tests': r.passed_tests,
                    'total_tests': r.total_tests,
                    'overall_score': r.overall_score
                }
                for r in self.batch_results
            ],
            'overall_results': self.overall_results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(detailed_results, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Detailed results saved to: {filename}")
        return filename
    
    def interactive_manual_testing_mode(self):
        """Interactive mode for manual jury testing with step-by-step validation"""
        print("\n🎮 INTERACTIVE MANUAL TESTING MODE")
        print("=" * 80)
        print("This mode allows you to manually validate each test step.")
        print("You can observe results and provide pass/fail judgments.")
        
        while True:
            print(f"\n📋 AVAILABLE TEST BATCHES:")
            for i, (batch_name, addresses) in enumerate(self.test_batches.items(), 1):
                print(f"  {i}. {batch_name} ({len(addresses)} addresses)")
            print(f"  6. Run all batches automatically")
            print(f"  0. Exit")
            
            try:
                choice = input(f"\nSelect test batch (0-6): ").strip()
                
                if choice == '0':
                    break
                elif choice == '6':
                    self.run_comprehensive_jury_tests()
                    self.save_detailed_results()
                    break
                elif choice in ['1', '2', '3', '4', '5']:
                    batch_index = int(choice) - 1
                    batch_name, addresses = list(self.test_batches.items())[batch_index]
                    
                    print(f"\n🎯 MANUALLY TESTING: {batch_name}")
                    result = self._run_single_test_batch(batch_name, addresses)
                    self._display_batch_results(result)
                    
                    # Manual validation
                    print(f"\n👨‍💼 MANUAL JURY VALIDATION")
                    print("Based on the test results above, do you accept this batch as PASS?")
                    manual_decision = input("Enter 'pass' or 'fail': ").strip().lower()
                    
                    if manual_decision == 'pass':
                        print("✅ Batch manually approved by jury")
                    else:
                        print("❌ Batch manually rejected by jury")
                else:
                    print("❌ Invalid choice. Please select 0-6.")
                    
            except (ValueError, KeyboardInterrupt):
                print("❌ Invalid input or interrupted. Exiting...")
                break


def main():
    """Main function to run the comprehensive jury testing framework"""
    print("🚀 TEKNOFEST 2025 - MANUAL JURY TESTING FRAMEWORK")
    print("=" * 80)
    print("This framework tests your address resolution system against")
    print("challenging real-world scenarios that juries use for evaluation.")
    print("")
    print("Available modes:")
    print("1. Automatic comprehensive testing (recommended)")
    print("2. Interactive manual testing")
    print("3. Individual batch testing")
    
    try:
        framework = ManualJuryTestFramework()
        
        while True:
            print(f"\n📋 SELECT TESTING MODE:")
            print("  1. Run automatic comprehensive testing")
            print("  2. Interactive manual testing mode")
            print("  3. Individual batch testing")
            print("  0. Exit")
            
            choice = input(f"\nSelect mode (0-3): ").strip()
            
            if choice == '0':
                print("👋 Exiting TEKNOFEST jury testing framework")
                break
            elif choice == '1':
                print("🚀 Starting automatic comprehensive testing...")
                results = framework.run_comprehensive_jury_tests()
                filename = framework.save_detailed_results()
                
                print(f"\n📄 Results saved to: {filename}")
                print("✅ Comprehensive testing completed!")
                break
            elif choice == '2':
                framework.interactive_manual_testing_mode()
            elif choice == '3':
                # Individual batch testing (simplified version)
                print("📋 Individual batch testing not implemented yet")
                print("Please use mode 1 or 2 for now.")
            else:
                print("❌ Invalid choice. Please select 0-3.")
                
    except Exception as e:
        print(f"❌ Framework error: {e}")
        print("Traceback:")
        traceback.print_exc()


if __name__ == "__main__":
    main()