#!/usr/bin/env python3
"""
SIMPLIFIED PERFORMANCE ANALYSIS
Tests system performance without external dependencies
"""

import sys
import os
import time
from typing import List, Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from address_parser import AddressParser
    from address_corrector import AddressCorrector
    from address_validator import AddressValidator
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

class SimplePerformanceAnalyzer:
    """
    Lightweight performance analysis without external dependencies
    """
    
    def __init__(self):
        print("⚡ INITIALIZING SIMPLE PERFORMANCE ANALYZER")
        self.parser = AddressParser()
        self.corrector = AddressCorrector()
        self.validator = AddressValidator()
        
        # Test addresses representing different complexity levels
        self.test_addresses = [
            "istanbul",  # Simple
            "ankara çankaya",  # Medium
            "istanbul kadıköy moda mahallesi",  # Complex
            "şişli mecidiyeköy büyükdere cd no:127/A",  # Very complex
            "beyoğlu istiklal caddesi taksim meydanı",  # Famous location
            "bursa osmangazi heykel mahallesi atatürk caddesi 15",  # Provincial
            "izmir konak alsancak mah. kıbrıs şehitleri cd. 25/B",  # With abbreviations
            "antalya muratpaşa lara mahallesi kenan evren bulvarı",  # Long name
        ]
    
    def test_component_performance(self) -> Dict[str, Any]:
        """Test individual component performance"""
        print("\n" + "="*50)
        print("🧩 COMPONENT PERFORMANCE ANALYSIS")
        print("="*50)
        
        iterations = 20
        component_results = {}
        
        # Test each component
        for component_name, component in [
            ('AddressCorrector', self.corrector),
            ('AddressParser', self.parser),
            ('AddressValidator', self.validator)
        ]:
            print(f"\n🔍 Testing {component_name}...")
            
            component_times = []
            successful_processes = 0
            
            for address in self.test_addresses:
                address_times = []
                
                for _ in range(iterations):
                    start_time = time.perf_counter()
                    
                    try:
                        if component_name == 'AddressCorrector':
                            result = component.correct_address(address)
                        elif component_name == 'AddressParser':
                            result = component.parse_address(address)
                        elif component_name == 'AddressValidator':
                            result = component.validate_address({'raw_address': address})
                        
                        successful_processes += 1
                        
                    except Exception as e:
                        print(f"   ⚠️ Error processing '{address}': {e}")
                        continue
                    
                    end_time = time.perf_counter()
                    address_times.append((end_time - start_time) * 1000)  # Convert to ms
                
                if address_times:
                    avg_time = sum(address_times) / len(address_times)
                    component_times.extend(address_times)
                    print(f"   {address[:30]:<30}: {avg_time:.2f}ms avg")
            
            if component_times:
                result = {
                    'average_ms': sum(component_times) / len(component_times),
                    'min_ms': min(component_times),
                    'max_ms': max(component_times),
                    'successful_processes': successful_processes,
                    'total_tests': len(self.test_addresses) * iterations
                }
                component_results[component_name] = result
                
                print(f"   📊 {component_name} Summary:")
                print(f"      Average: {result['average_ms']:.2f}ms")
                print(f"      Range: {result['min_ms']:.2f}-{result['max_ms']:.2f}ms")
                print(f"      Success: {result['successful_processes']}/{result['total_tests']}")
        
        return component_results
    
    def test_pipeline_performance(self) -> Dict[str, Any]:
        """Test full pipeline performance"""
        print("\n" + "="*50)
        print("🔄 FULL PIPELINE PERFORMANCE")
        print("="*50)
        
        pipeline_times = []
        successful_pipelines = 0
        pipeline_results = []
        
        for address in self.test_addresses:
            print(f"\n🧪 Testing: {address}")
            
            address_times = []
            iterations = 15
            
            for iteration in range(iterations):
                start_time = time.perf_counter()
                
                try:
                    # Full pipeline
                    corrected = self.corrector.correct_address(address)
                    parsed = self.parser.parse_address(corrected['corrected_address'])
                    validated = self.validator.validate_address({'raw_address': address})
                    
                    end_time = time.perf_counter()
                    pipeline_time = (end_time - start_time) * 1000  # ms
                    address_times.append(pipeline_time)
                    successful_pipelines += 1
                    
                except Exception as e:
                    print(f"   ❌ Pipeline error (iteration {iteration}): {e}")
                    continue
            
            if address_times:
                avg_time = sum(address_times) / len(address_times)
                min_time = min(address_times)
                max_time = max(address_times)
                
                result = {
                    'address': address,
                    'average_ms': avg_time,
                    'min_ms': min_time,
                    'max_ms': max_time,
                    'successful_iterations': len(address_times),
                    'total_iterations': iterations
                }
                
                pipeline_results.append(result)
                pipeline_times.extend(address_times)
                
                print(f"   ⏱️ Average: {avg_time:.2f}ms ({min_time:.2f}-{max_time:.2f}ms)")
                
                # TEKNOFEST compliance check
                teknofest_ok = avg_time < 100
                print(f"   🎯 TEKNOFEST: {'✅ PASS' if teknofest_ok else '❌ FAIL'} (<100ms)")
        
        # Overall pipeline analysis
        overall_analysis = {
            'total_tests': len(self.test_addresses) * 15,
            'successful_pipelines': successful_pipelines,
            'success_rate': successful_pipelines / (len(self.test_addresses) * 15) if self.test_addresses else 0,
            'average_pipeline_ms': sum(pipeline_times) / len(pipeline_times) if pipeline_times else 0,
            'min_pipeline_ms': min(pipeline_times) if pipeline_times else 0,
            'max_pipeline_ms': max(pipeline_times) if pipeline_times else 0,
            'teknofest_compliant': (sum(pipeline_times) / len(pipeline_times) if pipeline_times else 100) < 100,
            'pipeline_results': pipeline_results
        }
        
        print(f"\n📊 OVERALL PIPELINE PERFORMANCE:")
        print(f"   Average: {overall_analysis['average_pipeline_ms']:.2f}ms")
        print(f"   Success rate: {overall_analysis['success_rate']:.1%}")
        print(f"   TEKNOFEST compliant: {'✅ YES' if overall_analysis['teknofest_compliant'] else '❌ NO'}")
        
        return overall_analysis
    
    def test_batch_processing(self, batch_size: int = 100) -> Dict[str, Any]:
        """Test batch processing capabilities"""
        print(f"\n" + "="*50)
        print(f"📦 BATCH PROCESSING TEST ({batch_size} addresses)")
        print("="*50)
        
        # Generate test batch
        batch_addresses = []
        for i in range(batch_size):
            base_addr = self.test_addresses[i % len(self.test_addresses)]
            # Add variation
            if i % 3 == 0:
                batch_addresses.append(f"{base_addr} {10 + (i % 90)}")
            elif i % 3 == 1:
                batch_addresses.append(base_addr.replace("mahallesi", "mah.") if "mahallesi" in base_addr else base_addr)
            else:
                batch_addresses.append(base_addr)
        
        print(f"📋 Generated {len(batch_addresses)} test addresses")
        
        # Process batch
        start_time = time.perf_counter()
        processed = 0
        errors = 0
        total_pipeline_time = 0
        
        for i, address in enumerate(batch_addresses):
            if i % 20 == 0:
                print(f"   Progress: {i}/{len(batch_addresses)} ({i/len(batch_addresses):.1%})")
            
            pipeline_start = time.perf_counter()
            try:
                corrected = self.corrector.correct_address(address)
                parsed = self.parser.parse_address(corrected['corrected_address'])
                validated = self.validator.validate_address({'raw_address': address})
                processed += 1
                
                pipeline_end = time.perf_counter()
                total_pipeline_time += (pipeline_end - pipeline_start)
                
            except Exception as e:
                errors += 1
                if errors <= 5:  # Log first 5 errors only
                    print(f"   ⚠️ Error #{errors}: {e}")
        
        end_time = time.perf_counter()
        
        total_time = end_time - start_time
        throughput = processed / total_time if total_time > 0 else 0
        avg_time_per_address = (total_pipeline_time * 1000) / processed if processed > 0 else 0
        
        batch_analysis = {
            'batch_size': batch_size,
            'processed': processed,
            'errors': errors,
            'error_rate': errors / batch_size if batch_size > 0 else 0,
            'total_time_sec': total_time,
            'avg_time_per_address_ms': avg_time_per_address,
            'throughput_per_sec': throughput,
            'success_rate': processed / batch_size if batch_size > 0 else 0
        }
        
        print(f"\n📊 BATCH PROCESSING RESULTS:")
        print(f"   Processed: {processed}/{batch_size} ({batch_analysis['success_rate']:.1%})")
        print(f"   Total time: {total_time:.2f} seconds")
        print(f"   Throughput: {throughput:.1f} addresses/second")
        print(f"   Avg per address: {avg_time_per_address:.2f}ms")
        print(f"   Error rate: {batch_analysis['error_rate']:.1%}")
        
        return batch_analysis
    
    def generate_performance_summary(self) -> str:
        """Generate comprehensive performance summary"""
        print("\n" + "⚡"*20)
        print("GENERATING PERFORMANCE SUMMARY")
        print("⚡"*20)
        
        # Run all tests
        component_perf = self.test_component_performance()
        pipeline_perf = self.test_pipeline_performance()
        batch_perf = self.test_batch_processing(100)
        
        # Generate summary report
        report = f"""
# SIMPLE PERFORMANCE ANALYSIS REPORT
**System:** TEKNOFEST Turkish Address Processing System
**Test Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}

## 🎯 EXECUTIVE SUMMARY

### Key Performance Metrics
- **Pipeline Average:** {pipeline_perf['average_pipeline_ms']:.2f}ms per address
- **TEKNOFEST Compliance:** {'✅ PASS' if pipeline_perf['teknofest_compliant'] else '❌ FAIL'} (<100ms requirement)
- **Batch Throughput:** {batch_perf['throughput_per_sec']:.1f} addresses/second
- **System Reliability:** {pipeline_perf['success_rate']:.1%} success rate

### Competitive Assessment
"""
        
        # Determine competitive status
        speed_ok = pipeline_perf['teknofest_compliant']
        reliability_ok = pipeline_perf['success_rate'] > 0.95
        throughput_ok = batch_perf['throughput_per_sec'] > 20
        
        competitive_score = sum([speed_ok, reliability_ok, throughput_ok])
        
        if competitive_score == 3:
            competitive_status = "✅ HIGHLY COMPETITIVE: Meets all performance requirements"
        elif competitive_score == 2:
            competitive_status = "⚠️ COMPETITIVE: Minor optimizations recommended"
        else:
            competitive_status = "❌ NOT COMPETITIVE: Significant performance issues"
        
        report += f"{competitive_status}\n"
        
        report += f"""
## 📊 COMPONENT PERFORMANCE BREAKDOWN

"""
        
        for component_name, results in component_perf.items():
            report += f"""### {component_name}
- Average processing time: {results['average_ms']:.2f}ms
- Performance range: {results['min_ms']:.2f} - {results['max_ms']:.2f}ms
- Reliability: {results['successful_processes']}/{results['total_tests']} ({results['successful_processes']/results['total_tests']:.1%})

"""
        
        report += f"""## 🔄 FULL PIPELINE ANALYSIS

### Processing Times by Address Complexity
"""
        
        for result in pipeline_perf['pipeline_results']:
            complexity = len(result['address'].split())
            report += f"- {result['address'][:40]:<40} ({complexity} words): {result['average_ms']:.2f}ms\n"
        
        report += f"""
### Pipeline Performance Summary
- **Average time:** {pipeline_perf['average_pipeline_ms']:.2f}ms
- **Fastest processing:** {pipeline_perf['min_pipeline_ms']:.2f}ms
- **Slowest processing:** {pipeline_perf['max_pipeline_ms']:.2f}ms
- **Success rate:** {pipeline_perf['success_rate']:.1%}

## 📦 BATCH PROCESSING CAPABILITIES

### Batch Test Results ({batch_perf['batch_size']} addresses)
- **Total processing time:** {batch_perf['total_time_sec']:.2f} seconds
- **Throughput:** {batch_perf['throughput_per_sec']:.1f} addresses/second
- **Average per address:** {batch_perf['avg_time_per_address_ms']:.2f}ms
- **Success rate:** {batch_perf['success_rate']:.1%}
- **Error rate:** {batch_perf['error_rate']:.1%}

## 🏆 TEKNOFEST COMPETITION READINESS

### Requirements Check
- **Speed requirement (<100ms):** {'✅ PASS' if pipeline_perf['teknofest_compliant'] else '❌ FAIL'} ({pipeline_perf['average_pipeline_ms']:.2f}ms average)
- **Reliability requirement (>95%):** {'✅ PASS' if pipeline_perf['success_rate'] > 0.95 else '❌ FAIL'} ({pipeline_perf['success_rate']:.1%})
- **Batch processing:** {'✅ CAPABLE' if batch_perf['throughput_per_sec'] > 10 else '❌ TOO SLOW'} ({batch_perf['throughput_per_sec']:.1f} addr/sec)

### Performance Ranking Estimate
"""
        
        if pipeline_perf['average_pipeline_ms'] < 50:
            rank_estimate = "TOP TIER: <50ms average (excellent)"
        elif pipeline_perf['average_pipeline_ms'] < 80:
            rank_estimate = "HIGH TIER: <80ms average (very good)"
        elif pipeline_perf['average_pipeline_ms'] < 100:
            rank_estimate = "MID TIER: <100ms average (acceptable)"
        else:
            rank_estimate = "LOW TIER: >100ms average (needs optimization)"
        
        report += f"**Estimated ranking:** {rank_estimate}\n"
        
        report += f"""
## 📋 OPTIMIZATION RECOMMENDATIONS

### Priority Actions
"""
        
        # Find slowest component
        slowest_component = max(component_perf.keys(), 
                              key=lambda k: component_perf[k]['average_ms'])
        
        report += f"1. **Optimize {slowest_component}** (slowest component: {component_perf[slowest_component]['average_ms']:.2f}ms avg)\n"
        
        if not pipeline_perf['teknofest_compliant']:
            report += "2. **Critical: Reduce pipeline time below 100ms for TEKNOFEST compliance**\n"
        
        if pipeline_perf['success_rate'] < 0.95:
            report += f"3. **Improve reliability** (current: {pipeline_perf['success_rate']:.1%}, target: >95%)\n"
        
        if batch_perf['throughput_per_sec'] < 50:
            report += f"4. **Optimize batch processing** (current: {batch_perf['throughput_per_sec']:.1f} addr/sec)\n"
        
        report += f"""
### Performance Targets for Competition
- **Target pipeline time:** <80ms (currently {pipeline_perf['average_pipeline_ms']:.2f}ms)
- **Target throughput:** >100 addr/sec (currently {batch_perf['throughput_per_sec']:.1f} addr/sec)
- **Target reliability:** >98% (currently {pipeline_perf['success_rate']:.1%})

---
*Generated by Simple_Performance_Analysis*
"""
        
        return report


if __name__ == "__main__":
    analyzer = SimplePerformanceAnalyzer()
    
    print("🚀 STARTING SIMPLE PERFORMANCE ANALYSIS")
    print("="*50)
    
    # Generate report
    report = analyzer.generate_performance_summary()
    
    # Save report
    with open('Simple_Performance_Report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("\n" + "✅"*15)
    print("PERFORMANCE ANALYSIS COMPLETE")
    print("✅"*15)
    
    print(f"\n📄 Report saved to: Simple_Performance_Report.md")