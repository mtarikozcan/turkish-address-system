#!/usr/bin/env python3
"""
TEKNOFEST 2025 - Detailed Manual Tester Demo
Demonstration of the detailed manual testing interface capabilities

This script shows examples of using the detailed manual tester
without requiring interactive input.
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Import the detailed tester
from detailed_manual_tester import DetailedManualTester


def demo_single_address_analysis():
    """Demo: Single address analysis"""
    print("🎯 DEMO 1: SINGLE ADDRESS ANALYSIS")
    print("=" * 50)
    
    tester = DetailedManualTester()
    
    # Test with a complex Turkish address
    test_address = "İSTANBUL kadıköy MODA mahallesi caferağa sk 10"
    
    print(f"Testing address: {test_address}")
    result = tester.analyze_single_address(test_address)
    
    return result


def demo_two_address_comparison():
    """Demo: Two address comparison"""
    print("\n🎯 DEMO 2: TWO ADDRESS COMPARISON")
    print("=" * 50)
    
    tester = DetailedManualTester()
    
    # Test abbreviation nightmare case
    addr1 = "Ank. Çank. Kızılay Mh. Atatürk Blv. No:25/A Daire:3"
    addr2 = "Ankara Çankaya Kızılay Mahallesi Atatürk Bulvarı Numara:25/A Daire:3"
    
    print(f"Testing similarity between:")
    print(f"  Address 1: {addr1}")
    print(f"  Address 2: {addr2}")
    
    result = tester.compare_two_addresses(addr1, addr2)
    
    return result


def demo_batch_analysis():
    """Demo: Batch analysis"""
    print("\n🎯 DEMO 3: BATCH ANALYSIS")
    print("=" * 50)
    
    tester = DetailedManualTester()
    
    # Test Turkish character hell batch
    test_addresses = [
        "İSTANBUL kadıköy MODA mahallesi caferağa sk 10",
        "istanbul KADİKÖY moda MAHALLESİ caferaga sokak 10",
        "Izmit Körfez Ihsaniye Mahallesi Deniz Caddesi",
        "İzmit Körfez İhsaniye Mahallesi Deniz Caddesi"
    ]
    
    print(f"Testing batch of {len(test_addresses)} addresses for duplicates:")
    for i, addr in enumerate(test_addresses, 1):
        print(f"  {i}. {addr}")
    
    result = tester.batch_analysis(test_addresses)
    
    return result


def demo_predefined_test_cases():
    """Demo: Predefined test cases"""
    print("\n🎯 DEMO 4: PREDEFINED TEST CASES")
    print("=" * 50)
    
    tester = DetailedManualTester()
    
    print("Available predefined test case groups:")
    for group_name, addresses in tester.predefined_test_cases.items():
        print(f"  • {group_name}: {len(addresses)} addresses")
    
    # Test the abbreviation nightmare group
    abbreviation_addresses = tester.predefined_test_cases["Abbreviation Nightmare"]
    
    print(f"\nTesting 'Abbreviation Nightmare' group:")
    result = tester.batch_analysis(abbreviation_addresses)
    
    return result


def demo_export_functionality():
    """Demo: Export functionality"""
    print("\n🎯 DEMO 5: EXPORT FUNCTIONALITY")
    print("=" * 50)
    
    tester = DetailedManualTester()
    
    # Perform a few tests to generate results
    test_results = []
    
    # Single address test
    result1 = tester.analyze_single_address("Istanbul Kadıköy Moda Mahallesi")
    test_results.append(result1)
    
    # Comparison test
    result2 = tester.compare_two_addresses(
        "Ankara Çankaya",
        "Ank. Çank."
    )
    test_results.append(result2)
    
    # Export to JSON
    tester.export_results(test_results, "demo_results.json", "json")
    
    # Export to CSV (for single address results only)
    single_results = [r for r in test_results if hasattr(r, 'original_address')]
    if single_results:
        tester.export_results(single_results, "demo_results.csv", "csv")
    
    return test_results


def main():
    """Run all demos"""
    print("🚀 TEKNOFEST 2025 - DETAILED MANUAL TESTER DEMO")
    print("=" * 80)
    print("This demo shows all capabilities of the detailed manual testing interface")
    print()
    
    try:
        # Demo 1: Single address analysis
        demo_single_address_analysis()
        
        # Demo 2: Two address comparison
        demo_two_address_comparison()
        
        # Demo 3: Batch analysis
        demo_batch_analysis()
        
        # Demo 4: Predefined test cases
        demo_predefined_test_cases()
        
        # Demo 5: Export functionality
        demo_export_functionality()
        
        print("\n" + "=" * 80)
        print("🎉 ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print()
        print("Key Features Demonstrated:")
        print("✅ Single Address Pipeline Analysis - Complete step-by-step breakdown")
        print("✅ Two Address Similarity Comparison - Detailed similarity calculation")
        print("✅ Batch Duplicate Detection - Multiple address analysis")
        print("✅ Predefined Test Cases - Jury test scenarios")
        print("✅ Export Functionality - JSON and CSV export")
        print("✅ Color-coded Output - Visual pass/fail indicators")
        print("✅ Performance Timing - Processing time measurement")
        print("✅ Error Analysis - Warning and error detection")
        print()
        print("🎯 Ready for TEKNOFEST 2025 jury evaluation!")
        print()
        print("To use interactively, run: python3 detailed_manual_tester.py")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()