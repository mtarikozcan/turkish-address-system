#!/usr/bin/env python3
"""
PERFORMANCE & SCALE ANALYSIS
Tests batch processing capabilities and system scalability
"""

import sys
import os
import time
import psutil
import gc
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from address_parser import AddressParser
    from address_corrector import AddressCorrector
    from address_validator import AddressValidator
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

class PerformanceScaleAnalyzer:
    """
    Comprehensive performance and scalability analysis
    """
    
    def __init__(self):
        print("⚡ INITIALIZING PERFORMANCE & SCALE ANALYZER")
        self.parser = AddressParser()
        self.corrector = AddressCorrector()
        self.validator = AddressValidator()
        
        # Test datasets of different sizes
        self.small_dataset = self._generate_address_dataset(100)
        self.medium_dataset = self._generate_address_dataset(500)
        self.large_dataset = self._generate_address_dataset(1000)
        
        print(f"📊 Generated test datasets: 100, 500, 1000 addresses")
    
    def _generate_address_dataset(self, size: int) -> List[str]:
        """Generate realistic Turkish address dataset for testing"""
        base_addresses = [
            "istanbul kadıköy moda mahallesi",
            "ankara çankaya kızılay mahallesi tunalı hilmi caddesi",
            "izmir konak alsancak mahallesi atatürk caddesi",
            "bursa osmangazi heykel mahallesi",
            "antalya muratpaşa lara mahallesi",
            "adana seyhan reşatbey mahallesi",
            "eskişehir tepebaşı aşağısöğütönü mahallesi",
            "mersin yenişehir mahmudiye mahallesi",
            "kayseri kocasinan hunat mahallesi",
            "şanlıurfa haliliye yıldırım beyazıt mahallesi"
        ]
        
        dataset = []
        for i in range(size):
            base_addr = base_addresses[i % len(base_addresses)]
            # Add variations with building numbers, errors, etc.
            variations = [
                base_addr,
                f"{base_addr} {10 + (i % 90)}",
                f"{base_addr} no:{5 + (i % 95)}",
                f"{base_addr} {15 + (i % 85)}/A",
                base_addr.replace("mahallesi", "mah."),
                base_addr.replace("caddesi", "cd.") if "caddesi" in base_addr else base_addr
            ]
            dataset.append(variations[i % len(variations)])
        
        return dataset
    
    def test_single_address_performance(self) -> Dict[str, Any]:
        """Test performance of single address processing"""
        print("\n" + "="*60)
        print("🏃 SINGLE ADDRESS PERFORMANCE TEST")
        print("="*60)
        
        test_address = "istanbul beyoğlu istiklal caddesi no:127/A"
        iterations = 100
        
        # Memory before
        process = psutil.Process()
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Corrector performance
        corrector_times = []
        for _ in range(iterations):
            start = time.perf_counter()
            self.corrector.correct_address(test_address)
            end = time.perf_counter()
            corrector_times.append((end - start) * 1000)  # ms
        
        # Parser performance  
        parser_times = []
        for _ in range(iterations):
            start = time.perf_counter()
            self.parser.parse_address(test_address)
            end = time.perf_counter()
            parser_times.append((end - start) * 1000)  # ms
        
        # Validator performance
        validator_times = []
        for _ in range(iterations):
            start = time.perf_counter()
            self.validator.validate_address({'raw_address': test_address})
            end = time.perf_counter()
            validator_times.append((end - start) * 1000)  # ms
        
        # Memory after
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        
        results = {
            'test_address': test_address,
            'iterations': iterations,
            'corrector_avg_ms': sum(corrector_times) / len(corrector_times),
            'corrector_min_ms': min(corrector_times),
            'corrector_max_ms': max(corrector_times),
            'parser_avg_ms': sum(parser_times) / len(parser_times),
            'parser_min_ms': min(parser_times),
            'parser_max_ms': max(parser_times),
            'validator_avg_ms': sum(validator_times) / len(validator_times),
            'validator_min_ms': min(validator_times),
            'validator_max_ms': max(validator_times),
            'total_avg_ms': (sum(corrector_times) + sum(parser_times) + sum(validator_times)) / (3 * iterations),
            'memory_usage_mb': memory_after - memory_before
        }
        
        print(f"⏱️ Performance Results ({iterations} iterations):")
        print(f"   Corrector: {results['corrector_avg_ms']:.2f}ms avg ({results['corrector_min_ms']:.2f}-{results['corrector_max_ms']:.2f}ms)")
        print(f"   Parser: {results['parser_avg_ms']:.2f}ms avg ({results['parser_min_ms']:.2f}-{results['parser_max_ms']:.2f}ms)")
        print(f"   Validator: {results['validator_avg_ms']:.2f}ms avg ({results['validator_min_ms']:.2f}-{results['validator_max_ms']:.2f}ms)")
        print(f"   Total Pipeline: {results['total_avg_ms']:.2f}ms avg")
        print(f"   Memory Usage: {results['memory_usage_mb']:.2f} MB")
        
        # TEKNOFEST compliance check
        teknofest_compliant = results['total_avg_ms'] < 100
        print(f"🎯 TEKNOFEST Compliance (<100ms): {'✅ PASS' if teknofest_compliant else '❌ FAIL'}")
        
        return results
    
    def test_batch_processing_scalability(self) -> Dict[str, Any]:
        """Test batch processing with different dataset sizes"""
        print("\n" + "="*60)
        print("📊 BATCH PROCESSING SCALABILITY TEST")
        print("="*60)
        
        datasets = [
            ('small', self.small_dataset),
            ('medium', self.medium_dataset),
            ('large', self.large_dataset)
        ]
        
        batch_results = []
        
        for dataset_name, dataset in datasets:
            print(f"\n🔍 Testing {dataset_name} dataset ({len(dataset)} addresses)...")
            
            process = psutil.Process()
            memory_before = process.memory_info().rss / 1024 / 1024
            
            start_time = time.perf_counter()
            processed_count = 0
            errors = 0
            
            for address in dataset:
                try:
                    # Full pipeline processing
                    corrected = self.corrector.correct_address(address)
                    parsed = self.parser.parse_address(corrected['corrected_address'])
                    validated = self.validator.validate_address({'raw_address': address})
                    processed_count += 1
                except Exception as e:
                    errors += 1
                    if errors == 1:  # Log first error
                        print(f"   ⚠️ First error: {e}")
            
            end_time = time.perf_counter()
            memory_after = process.memory_info().rss / 1024 / 1024
            
            total_time = end_time - start_time
            throughput = len(dataset) / total_time if total_time > 0 else 0
            avg_time_ms = (total_time * 1000) / len(dataset) if dataset else 0
            
            result = {
                'dataset_name': dataset_name,
                'dataset_size': len(dataset),
                'processed_count': processed_count,
                'errors': errors,
                'total_time_sec': total_time,
                'avg_time_ms': avg_time_ms,
                'throughput_per_sec': throughput,
                'memory_used_mb': memory_after - memory_before,
                'error_rate': errors / len(dataset) if dataset else 0
            }
            
            batch_results.append(result)
            
            print(f"   ⏱️ Total time: {total_time:.2f}s")
            print(f"   📈 Throughput: {throughput:.1f} addresses/sec")
            print(f"   ⚡ Avg per address: {avg_time_ms:.2f}ms")
            print(f"   💾 Memory used: {memory_after - memory_before:.2f} MB")
            print(f"   ❌ Error rate: {result['error_rate']:.1%}")
        
        # Analyze scalability
        scalability_analysis = self._analyze_scalability_trends(batch_results)
        
        return {
            'batch_results': batch_results,
            'scalability_analysis': scalability_analysis
        }
    
    def _analyze_scalability_trends(self, results: List[Dict]) -> Dict[str, Any]:
        """Analyze scalability trends from batch results"""
        if len(results) < 2:
            return {'trend': 'insufficient_data'}
        
        # Compare small to large dataset performance
        small_result = next(r for r in results if r['dataset_name'] == 'small')
        large_result = next(r for r in results if r['dataset_name'] == 'large')
        
        throughput_ratio = large_result['throughput_per_sec'] / small_result['throughput_per_sec'] if small_result['throughput_per_sec'] > 0 else 0
        memory_ratio = large_result['memory_used_mb'] / small_result['memory_used_mb'] if small_result['memory_used_mb'] > 0 else 0
        
        # Determine scalability trend
        if throughput_ratio >= 0.8:  # Less than 20% degradation
            scalability = 'excellent'
        elif throughput_ratio >= 0.6:  # 20-40% degradation
            scalability = 'good'
        elif throughput_ratio >= 0.4:  # 40-60% degradation
            scalability = 'moderate'
        else:
            scalability = 'poor'
        
        return {
            'scalability_rating': scalability,
            'throughput_ratio': throughput_ratio,
            'memory_ratio': memory_ratio,
            'small_throughput': small_result['throughput_per_sec'],
            'large_throughput': large_result['throughput_per_sec']
        }
    
    def test_concurrent_processing(self) -> Dict[str, Any]:
        """Test concurrent processing capabilities"""
        print("\n" + "="*60)
        print("🧵 CONCURRENT PROCESSING TEST")
        print("="*60)
        
        test_addresses = self.medium_dataset[:200]  # Use subset for threading test
        thread_counts = [1, 2, 4, 8]
        concurrent_results = []
        
        def process_address_batch(addresses_batch: List[str]) -> Dict[str, Any]:
            """Process a batch of addresses in a thread"""
            thread_id = threading.current_thread().ident
            results = {'thread_id': thread_id, 'processed': 0, 'errors': 0}
            
            for address in addresses_batch:
                try:
                    corrected = self.corrector.correct_address(address)
                    parsed = self.parser.parse_address(corrected['corrected_address'])
                    validated = self.validator.validate_address({'raw_address': address})
                    results['processed'] += 1
                except Exception:
                    results['errors'] += 1
            
            return results
        
        for thread_count in thread_counts:
            print(f"\n🧵 Testing with {thread_count} threads...")
            
            # Split addresses into batches
            batch_size = len(test_addresses) // thread_count
            batches = [test_addresses[i:i+batch_size] for i in range(0, len(test_addresses), batch_size)]
            
            start_time = time.perf_counter()
            
            with ThreadPoolExecutor(max_workers=thread_count) as executor:
                futures = [executor.submit(process_address_batch, batch) for batch in batches]
                thread_results = [future.result() for future in as_completed(futures)]
            
            end_time = time.perf_counter()
            
            total_time = end_time - start_time
            total_processed = sum(r['processed'] for r in thread_results)
            total_errors = sum(r['errors'] for r in thread_results)
            throughput = total_processed / total_time if total_time > 0 else 0
            
            result = {
                'thread_count': thread_count,
                'total_addresses': len(test_addresses),
                'total_processed': total_processed,
                'total_errors': total_errors,
                'total_time_sec': total_time,
                'throughput_per_sec': throughput,
                'speedup': 0  # Will calculate after collecting all results
            }
            
            concurrent_results.append(result)
            
            print(f"   ⏱️ Time: {total_time:.2f}s")
            print(f"   📈 Throughput: {throughput:.1f} addresses/sec")
            print(f"   ✅ Processed: {total_processed}/{len(test_addresses)}")
            print(f"   ❌ Errors: {total_errors}")
        
        # Calculate speedup relative to single thread
        single_thread_throughput = concurrent_results[0]['throughput_per_sec']
        for result in concurrent_results:
            result['speedup'] = result['throughput_per_sec'] / single_thread_throughput if single_thread_throughput > 0 else 0
        
        return {
            'concurrent_results': concurrent_results,
            'optimal_thread_count': max(concurrent_results, key=lambda x: x['throughput_per_sec'])['thread_count']
        }
    
    def analyze_memory_usage_patterns(self) -> Dict[str, Any]:
        """Analyze memory usage patterns during processing"""
        print("\n" + "="*60)
        print("💾 MEMORY USAGE PATTERN ANALYSIS")
        print("="*60)
        
        process = psutil.Process()
        memory_snapshots = []
        
        # Baseline memory
        gc.collect()  # Force garbage collection
        baseline_memory = process.memory_info().rss / 1024 / 1024
        memory_snapshots.append(('baseline', baseline_memory))
        
        # Process increasing dataset sizes and monitor memory
        test_sizes = [50, 100, 250, 500, 750, 1000]
        
        for size in test_sizes:
            print(f"   📊 Processing {size} addresses...")
            
            dataset = self._generate_address_dataset(size)
            
            memory_before = process.memory_info().rss / 1024 / 1024
            
            # Process the dataset
            for address in dataset:
                try:
                    corrected = self.corrector.correct_address(address)
                    parsed = self.parser.parse_address(corrected['corrected_address'])
                except Exception:
                    pass  # Continue processing
            
            memory_after = process.memory_info().rss / 1024 / 1024
            memory_snapshots.append((f'{size}_addresses', memory_after))
            
            print(f"      Memory: {memory_before:.1f} → {memory_after:.1f} MB (+{memory_after - memory_before:.1f} MB)")
        
        # Analyze memory growth patterns
        memory_growth = []
        for i in range(1, len(memory_snapshots)):
            prev_memory = memory_snapshots[i-1][1]
            curr_memory = memory_snapshots[i][1]
            growth = curr_memory - prev_memory
            memory_growth.append(growth)
        
        avg_growth = sum(memory_growth) / len(memory_growth) if memory_growth else 0
        max_growth = max(memory_growth) if memory_growth else 0
        total_growth = memory_snapshots[-1][1] - memory_snapshots[0][1]
        
        analysis = {
            'baseline_memory_mb': baseline_memory,
            'final_memory_mb': memory_snapshots[-1][1],
            'total_growth_mb': total_growth,
            'average_growth_per_batch_mb': avg_growth,
            'max_growth_mb': max_growth,
            'memory_snapshots': memory_snapshots,
            'memory_efficiency': 'good' if total_growth < 100 else 'moderate' if total_growth < 200 else 'poor'
        }
        
        print(f"\n💾 Memory Analysis Results:")
        print(f"   Baseline: {baseline_memory:.1f} MB")
        print(f"   Final: {memory_snapshots[-1][1]:.1f} MB")
        print(f"   Total growth: {total_growth:.1f} MB")
        print(f"   Efficiency: {analysis['memory_efficiency']}")
        
        return analysis
    
    def generate_performance_report(self) -> str:
        """Generate comprehensive performance and scalability report"""
        print("\n" + "⚡"*25)
        print("GENERATING PERFORMANCE REPORT")
        print("⚡"*25)
        
        # Run all performance tests
        single_perf = self.test_single_address_performance()
        batch_perf = self.test_batch_processing_scalability()
        concurrent_perf = self.test_concurrent_processing()
        memory_analysis = self.analyze_memory_usage_patterns()
        
        report = f"""
# PERFORMANCE & SCALE ANALYSIS REPORT
**Generated:** Turkish Address Processing System Performance Analysis
**Focus:** Batch processing readiness and TEKNOFEST compliance

## 🎯 EXECUTIVE SUMMARY

### Performance Metrics
- **Single Address Processing:** {single_perf['total_avg_ms']:.2f}ms average
- **TEKNOFEST Compliance:** {'✅ PASS' if single_perf['total_avg_ms'] < 100 else '❌ FAIL'} (<100ms requirement)
- **Peak Throughput:** {max(r['throughput_per_sec'] for r in batch_perf['batch_results']):.1f} addresses/second
- **Scalability Rating:** {batch_perf['scalability_analysis']['scalability_rating'].title()}
- **Memory Efficiency:** {memory_analysis['memory_efficiency'].title()}

### Competitive Readiness
"""
        
        # Determine competitive readiness
        teknofest_ready = single_perf['total_avg_ms'] < 100
        scale_ready = batch_perf['scalability_analysis']['scalability_rating'] in ['excellent', 'good']
        memory_ready = memory_analysis['memory_efficiency'] in ['good', 'moderate']
        
        readiness_score = sum([teknofest_ready, scale_ready, memory_ready])
        
        if readiness_score == 3:
            readiness = "✅ FULLY READY: System meets all performance requirements"
        elif readiness_score == 2:
            readiness = "⚠️ MOSTLY READY: Minor optimizations needed"
        else:
            readiness = "❌ NOT READY: Significant performance issues"
        
        report += f"{readiness}\n"
        
        report += f"""
## 📊 DETAILED PERFORMANCE ANALYSIS

### 1. Single Address Performance
**Component Breakdown:**
- Address Corrector: {single_perf['corrector_avg_ms']:.2f}ms average
- Address Parser: {single_perf['parser_avg_ms']:.2f}ms average  
- Address Validator: {single_perf['validator_avg_ms']:.2f}ms average
- **Total Pipeline: {single_perf['total_avg_ms']:.2f}ms average**

**Performance Range:**
- Fastest: {min(single_perf['corrector_min_ms'], single_perf['parser_min_ms'], single_perf['validator_min_ms']):.2f}ms
- Slowest: {max(single_perf['corrector_max_ms'], single_perf['parser_max_ms'], single_perf['validator_max_ms']):.2f}ms

### 2. Batch Processing Scalability
"""
        
        for result in batch_perf['batch_results']:
            report += f"""
**{result['dataset_name'].title()} Dataset ({result['dataset_size']} addresses):**
- Processing time: {result['total_time_sec']:.2f} seconds
- Throughput: {result['throughput_per_sec']:.1f} addresses/second
- Average per address: {result['avg_time_ms']:.2f}ms
- Error rate: {result['error_rate']:.1%}
- Memory used: {result['memory_used_mb']:.1f} MB
"""
        
        scalability = batch_perf['scalability_analysis']
        report += f"""
**Scalability Analysis:**
- Performance degradation: {(1-scalability['throughput_ratio']):.1%} from small to large dataset
- Throughput ratio: {scalability['throughput_ratio']:.2f}
- Memory scaling: {scalability['memory_ratio']:.2f}x
- Rating: {scalability['scalability_rating'].title()}

### 3. Concurrent Processing Results
**Threading Performance:**
"""
        
        for result in concurrent_perf['concurrent_results']:
            report += f"- {result['thread_count']} threads: {result['throughput_per_sec']:.1f} addr/sec ({result['speedup']:.1f}x speedup)\n"
        
        report += f"""
- **Optimal thread count:** {concurrent_perf['optimal_thread_count']} threads

### 4. Memory Usage Analysis
- **Baseline memory:** {memory_analysis['baseline_memory_mb']:.1f} MB
- **Final memory:** {memory_analysis['final_memory_mb']:.1f} MB  
- **Total growth:** {memory_analysis['total_growth_mb']:.1f} MB
- **Memory efficiency:** {memory_analysis['memory_efficiency'].title()}

## 🏆 TEKNOFEST COMPETITION READINESS

### Performance Requirements Check
- **Speed requirement (<100ms):** {'✅ PASS' if single_perf['total_avg_ms'] < 100 else '❌ FAIL'}
- **Batch processing capability:** {'✅ READY' if scale_ready else '❌ NEEDS WORK'}
- **Memory efficiency:** {'✅ GOOD' if memory_ready else '❌ OPTIMIZE'}
- **Error handling:** {'✅ STABLE' if all(r['error_rate'] < 0.05 for r in batch_perf['batch_results']) else '⚠️ MONITOR'}

### Competitive Advantages
"""
        
        advantages = []
        if single_perf['total_avg_ms'] < 50:
            advantages.append("⚡ Ultra-fast processing (<50ms)")
        elif single_perf['total_avg_ms'] < 100:
            advantages.append("⚡ Fast processing (<100ms)")
        
        peak_throughput = max(r['throughput_per_sec'] for r in batch_perf['batch_results'])
        if peak_throughput > 100:
            advantages.append(f"📈 High throughput ({peak_throughput:.0f} addr/sec)")
        
        if memory_analysis['memory_efficiency'] == 'good':
            advantages.append("💾 Memory efficient")
        
        if concurrent_perf['optimal_thread_count'] > 1:
            advantages.append(f"🧵 Concurrent processing ({concurrent_perf['optimal_thread_count']} threads optimal)")
        
        for advantage in advantages:
            report += f"{advantage}\n"
        
        if not advantages:
            report += "⚠️ No clear performance advantages identified\n"
        
        report += f"""
## 📋 OPTIMIZATION RECOMMENDATIONS

**Immediate Actions:**
1. {'✅' if single_perf['total_avg_ms'] < 100 else '❌'} Single address performance is {'acceptable' if single_perf['total_avg_ms'] < 100 else 'too slow - optimize critical path'}
2. {'✅' if scale_ready else '❌'} Batch processing is {'scalable' if scale_ready else 'having scalability issues'}
3. {'✅' if memory_ready else '❌'} Memory usage is {'efficient' if memory_ready else 'growing too fast'}

**Performance Tuning Priorities:**
"""
        
        if single_perf['corrector_avg_ms'] > single_perf['parser_avg_ms']:
            report += "1. Optimize AddressCorrector (slowest component)\n"
        else:
            report += "1. Optimize AddressParser (slowest component)\n"
        
        if not scale_ready:
            report += "2. Improve batch processing scalability\n"
        
        if not memory_ready:
            report += "3. Implement memory optimization strategies\n"
        
        report += f"""
**System Limits Identified:**
- Single-threaded optimal processing: {single_perf['total_avg_ms']:.0f}ms per address
- Peak throughput capacity: {peak_throughput:.0f} addresses/second
- Memory growth rate: {memory_analysis['average_growth_per_batch_mb']:.1f} MB per batch
- Recommended concurrent threads: {concurrent_perf['optimal_thread_count']}

---
*Generated by Performance_Scale_Test*
"""
        
        return report


if __name__ == "__main__":
    analyzer = PerformanceScaleAnalyzer()
    
    print("🚀 STARTING COMPREHENSIVE PERFORMANCE & SCALE ANALYSIS")
    print("="*70)
    
    # Generate report
    report = analyzer.generate_performance_report()
    
    # Save report
    with open('Performance_Scale_Analysis_Report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("\n" + "✅"*20)
    print("PERFORMANCE ANALYSIS COMPLETE")
    print("✅"*20)
    
    print(f"\n📄 Report saved to: Performance_Scale_Analysis_Report.md")