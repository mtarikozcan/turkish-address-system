#!/usr/bin/env python3
"""
DEEP ANALYSIS: Intelligence Engine Analysis
Tests dynamic inference capabilities beyond hardcoded mappings
"""

import sys
import os
import pandas as pd
from typing import Dict, List, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from address_parser import AddressParser
    from address_corrector import AddressCorrector
    from address_validator import AddressValidator
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

class IntelligenceEngineAnalyzer:
    """
    Deep analysis of intelligence engine capabilities
    Tests if system uses dynamic inference or just enhanced hardcoding
    """
    
    def __init__(self):
        print("🧠 INITIALIZING INTELLIGENCE ENGINE ANALYZER")
        self.parser = AddressParser()
        self.corrector = AddressCorrector()
        self.validator = AddressValidator()
        
        # Load OSM data for comparison
        self.osm_data = self._load_osm_data()
    
    def _load_osm_data(self) -> pd.DataFrame:
        """Load OSM data with correct column names"""
        try:
            csv_path = "database/enhanced_turkish_neighborhoods.csv"
            df = pd.read_csv(csv_path)
            print(f"✅ OSM Data: {len(df)} records loaded")
            print(f"   Columns: {list(df.columns)}")
            
            # Standardize column names
            df = df.rename(columns={
                'il_adi': 'il',
                'ilce_adi': 'ilce', 
                'mahalle_adi': 'mahalle'
            })
            
            return df
        except Exception as e:
            print(f"❌ Error loading OSM data: {e}")
            return pd.DataFrame()
    
    def test_true_dynamic_intelligence(self) -> Dict[str, Any]:
        """
        Test intelligence with completely unknown addresses
        that should NOT be in any hardcoded mapping
        """
        print("\n" + "="*70)
        print("🧠 TESTING TRUE DYNAMIC INTELLIGENCE ENGINE")
        print("="*70)
        
        # Test cases from different regions with varying complexity
        unknown_addresses = [
            # Small towns/districts that shouldn't be hardcoded
            {"input": "sinop boyabat merkez", "expected_il": "Sinop", "type": "small_town"},
            {"input": "kastamonu tosya", "expected_il": "Kastamonu", "type": "district"},
            {"input": "çorum iskilip", "expected_il": "Çorum", "type": "district"},
            {"input": "amasya merzifon", "expected_il": "Amasya", "type": "district"},
            {"input": "tokat turhal", "expected_il": "Tokat", "type": "district"},
            {"input": "yozgat sorgun", "expected_il": "Yozgat", "type": "district"},
            {"input": "nevşehir avanos", "expected_il": "Nevşehir", "type": "tourist_area"},
            {"input": "kırşehir mucur", "expected_il": "Kırşehir", "type": "small_district"},
            {"input": "niğde bor", "expected_il": "Niğde", "type": "district"},
            {"input": "aksaray ortaköy", "expected_il": "Aksaray", "type": "district"},
            
            # More obscure but real Turkish locations
            {"input": "bartın ulus", "expected_il": "Bartın", "type": "small_province"},
            {"input": "ardahan göle", "expected_il": "Ardahan", "type": "border_town"},
            {"input": "kilis elbeyli", "expected_il": "Kilis", "type": "border_district"},
            {"input": "yalova çiftlikköy", "expected_il": "Yalova", "type": "district"},
            {"input": "düzce kaynaşlı", "expected_il": "Düzce", "type": "district"},
        ]
        
        results = []
        dynamic_successes = 0
        total_tests = len(unknown_addresses)
        
        for test_case in unknown_addresses:
            input_addr = test_case["input"]
            expected_il = test_case["expected_il"]
            area_type = test_case["type"]
            
            print(f"\n🔍 Testing: {input_addr} ({area_type})")
            print(f"   Expected province: {expected_il}")
            
            # Parse the address
            result = self.parser.parse_address(input_addr)
            components = result.get('components', {})
            confidence = result.get('overall_confidence', 0)
            
            # Analyze result
            inferred_il = components.get('il', '').strip()
            inferred_ilce = components.get('ilce', '').strip()
            inferred_mahalle = components.get('mahalle', '').strip()
            
            # Check correctness
            is_correct = expected_il.lower() in inferred_il.lower() if inferred_il else False
            has_meaningful_inference = bool(inferred_il or inferred_ilce or inferred_mahalle)
            
            result_data = {
                'input': input_addr,
                'type': area_type,
                'expected_il': expected_il,
                'inferred_il': inferred_il,
                'inferred_ilce': inferred_ilce,
                'inferred_mahalle': inferred_mahalle,
                'is_correct': is_correct,
                'has_inference': has_meaningful_inference,
                'confidence': confidence,
                'quality_score': self._calculate_quality_score(inferred_il, inferred_ilce, inferred_mahalle, is_correct)
            }
            
            results.append(result_data)
            
            if is_correct:
                dynamic_successes += 1
                print(f"   ✅ SUCCESS: {inferred_il} (confidence: {confidence:.2f})")
                if inferred_ilce:
                    print(f"      ↳ District: {inferred_ilce}")
                if inferred_mahalle:
                    print(f"      ↳ Neighborhood: {inferred_mahalle}")
            elif has_meaningful_inference:
                print(f"   ⚠️ PARTIAL: Got {inferred_il or 'unknown'} (expected {expected_il})")
                if inferred_ilce or inferred_mahalle:
                    print(f"      ↳ But inferred: {inferred_ilce}, {inferred_mahalle}")
            else:
                print(f"   ❌ FAILED: No meaningful inference")
        
        analysis = {
            'total_tests': total_tests,
            'dynamic_successes': dynamic_successes,
            'success_rate': dynamic_successes / total_tests if total_tests > 0 else 0,
            'results': results,
            'average_quality': sum(r['quality_score'] for r in results) / len(results) if results else 0
        }
        
        print(f"\n📊 INTELLIGENCE ENGINE RESULTS:")
        print(f"   Dynamic successes: {dynamic_successes}/{total_tests} ({analysis['success_rate']:.1%})")
        print(f"   Average quality score: {analysis['average_quality']:.2f}/5.0")
        
        return analysis
    
    def _calculate_quality_score(self, il: str, ilce: str, mahalle: str, is_correct: bool) -> float:
        """Calculate quality score for inference (0-5 scale)"""
        score = 0.0
        
        if is_correct:
            score += 3.0  # Correct province
        elif il:
            score += 1.0  # At least some province inferred
        
        if ilce:
            score += 1.0  # District inferred
        if mahalle:
            score += 1.0  # Neighborhood inferred
        
        return score
    
    def analyze_osm_data_usage_patterns(self) -> Dict[str, Any]:
        """
        Analyze how the system actually uses OSM data
        vs just having it loaded in memory
        """
        print("\n" + "="*70)
        print("📊 ANALYZING OSM DATA USAGE PATTERNS")
        print("="*70)
        
        if self.osm_data.empty:
            return {'error': 'OSM data not available'}
        
        # Check if parser has loaded OSM data properly
        parser_data_analysis = {
            'osm_records_available': len(self.osm_data),
            'unique_provinces': self.osm_data['il'].nunique() if 'il' in self.osm_data.columns else 0,
            'unique_districts': self.osm_data['ilce'].nunique() if 'ilce' in self.osm_data.columns else 0,
            'unique_neighborhoods': self.osm_data['mahalle'].nunique() if 'mahalle' in self.osm_data.columns else 0,
        }
        
        print(f"📈 OSM Dataset Structure:")
        print(f"   Available records: {parser_data_analysis['osm_records_available']:,}")
        print(f"   Unique provinces: {parser_data_analysis['unique_provinces']}")
        print(f"   Unique districts: {parser_data_analysis['unique_districts']}")
        print(f"   Unique neighborhoods: {parser_data_analysis['unique_neighborhoods']:,}")
        
        # Test if system can handle neighborhood lookups
        sample_neighborhoods = []
        if 'mahalle' in self.osm_data.columns:
            sample_neighborhoods = self.osm_data['mahalle'].dropna().unique()[:15]
        
        neighborhood_lookup_success = 0
        if len(sample_neighborhoods) > 0:
            print(f"\n🧪 Testing neighborhood lookup with {len(sample_neighborhoods)} samples...")
            
            for neighborhood in sample_neighborhoods:
                if not neighborhood or pd.isna(neighborhood):
                    continue
                    
                # Get the province for this neighborhood from OSM data
                province_row = self.osm_data[self.osm_data['mahalle'] == neighborhood].iloc[0]
                expected_province = province_row['il']
                
                # Test if parser can infer this
                test_address = f"{neighborhood} mahallesi"
                result = self.parser.parse_address(test_address)
                components = result.get('components', {})
                
                inferred_province = components.get('il', '')
                if expected_province.lower() in inferred_province.lower():
                    neighborhood_lookup_success += 1
        
        lookup_rate = neighborhood_lookup_success / len(sample_neighborhoods) if sample_neighborhoods else 0
        parser_data_analysis['neighborhood_lookup_rate'] = lookup_rate
        
        print(f"   Neighborhood lookup success: {neighborhood_lookup_success}/{len(sample_neighborhoods)} ({lookup_rate:.1%})")
        
        return parser_data_analysis
    
    def test_context_inference_depth(self) -> Dict[str, Any]:
        """
        Test depth of context inference - can it handle complex relationships?
        """
        print("\n" + "="*70)
        print("🔗 TESTING CONTEXT INFERENCE DEPTH")
        print("="*70)
        
        complex_cases = [
            {
                "input": "galata kulesi istanbul",
                "expected": {"ilce": "beyoğlu", "famous_landmark": True},
                "test_type": "landmark_inference"
            },
            {
                "input": "dolmabahçe sarayı",
                "expected": {"il": "istanbul", "ilce": "beşiktaş", "famous_landmark": True},
                "test_type": "palace_inference"
            },
            {
                "input": "anıtkabir ankara",
                "expected": {"ilce": "çankaya", "famous_landmark": True},
                "test_type": "monument_inference"
            },
            {
                "input": "kapalıçarşı fatih",
                "expected": {"il": "istanbul", "ilce": "fatih", "famous_landmark": True},
                "test_type": "historic_market"
            },
            {
                "input": "aspendos antalya",
                "expected": {"ilce": "serik", "famous_landmark": True},
                "test_type": "ancient_site"
            }
        ]
        
        context_depth_results = []
        successful_complex_inferences = 0
        
        for case in complex_cases:
            input_addr = case["input"]
            expected = case["expected"]
            test_type = case["test_type"]
            
            print(f"\n🔍 Complex test: {input_addr} ({test_type})")
            
            result = self.parser.parse_address(input_addr)
            components = result.get('components', {})
            
            # Check if inference is contextually correct
            context_correct = True
            details = []
            
            for key, expected_value in expected.items():
                if key == "famous_landmark":
                    continue  # Skip metadata
                    
                actual_value = components.get(key, '').lower()
                expected_lower = str(expected_value).lower()
                
                if expected_lower in actual_value or actual_value in expected_lower:
                    details.append(f"✅ {key}: {actual_value} matches {expected_value}")
                else:
                    context_correct = False
                    details.append(f"❌ {key}: {actual_value} != {expected_value}")
            
            if context_correct:
                successful_complex_inferences += 1
                print(f"   ✅ CONTEXT SUCCESS")
            else:
                print(f"   ❌ CONTEXT FAILED")
            
            for detail in details:
                print(f"      {detail}")
            
            context_depth_results.append({
                'input': input_addr,
                'test_type': test_type,
                'expected': expected,
                'actual': components,
                'context_correct': context_correct
            })
        
        context_analysis = {
            'total_complex_tests': len(complex_cases),
            'successful_complex_inferences': successful_complex_inferences,
            'complex_success_rate': successful_complex_inferences / len(complex_cases),
            'results': context_depth_results
        }
        
        print(f"\n📊 CONTEXT DEPTH ANALYSIS:")
        print(f"   Complex inference success: {successful_complex_inferences}/{len(complex_cases)} ({context_analysis['complex_success_rate']:.1%})")
        
        return context_analysis
    
    def generate_intelligence_report(self) -> str:
        """Generate comprehensive intelligence engine analysis report"""
        print("\n" + "🧠"*25)
        print("GENERATING INTELLIGENCE ENGINE REPORT")
        print("🧠"*25)
        
        # Run all analyses
        dynamic_analysis = self.test_true_dynamic_intelligence()
        usage_analysis = self.analyze_osm_data_usage_patterns()
        context_analysis = self.test_context_inference_depth()
        
        report = f"""
# INTELLIGENCE ENGINE ANALYSIS REPORT
**Generated:** {pd.Timestamp.now()}
**System:** TEKNOFEST Turkish Address Processing System

## 🎯 EXECUTIVE SUMMARY

### Intelligence Capabilities Assessment
- **Dynamic Inference Success:** {dynamic_analysis['success_rate']:.1%} ({dynamic_analysis['dynamic_successes']}/{dynamic_analysis['total_tests']})
- **Average Quality Score:** {dynamic_analysis['average_quality']:.2f}/5.0
- **Complex Context Success:** {context_analysis['complex_success_rate']:.1%} ({context_analysis['successful_complex_inferences']}/{context_analysis['total_complex_tests']})
- **OSM Data Utilization:** {"HIGH" if usage_analysis.get('neighborhood_lookup_rate', 0) > 0.6 else "LOW" if usage_analysis.get('neighborhood_lookup_rate', 0) < 0.3 else "MODERATE"}

### Competitive Assessment
"""
        
        if dynamic_analysis['success_rate'] > 0.7:
            assessment = "✅ STRONG: System demonstrates true dynamic intelligence beyond hardcoded mappings"
        elif dynamic_analysis['success_rate'] > 0.4:
            assessment = "⚠️ MODERATE: Partial dynamic capabilities with room for improvement"
        else:
            assessment = "❌ WEAK: Primarily hardcoded with limited dynamic inference"
        
        report += f"{assessment}\n"
        
        report += f"""
## 🔍 DETAILED FINDINGS

### 1. Dynamic Intelligence Test Results
**Unknown Location Processing:**
- Test cases: {dynamic_analysis['total_tests']} diverse Turkish locations
- Success rate: {dynamic_analysis['success_rate']:.1%}
- Quality score: {dynamic_analysis['average_quality']:.2f}/5.0

**Performance by Location Type:**
"""
        
        # Analyze by location type
        type_performance = {}
        for result in dynamic_analysis['results']:
            loc_type = result['type']
            if loc_type not in type_performance:
                type_performance[loc_type] = {'correct': 0, 'total': 0}
            type_performance[loc_type]['total'] += 1
            if result['is_correct']:
                type_performance[loc_type]['correct'] += 1
        
        for loc_type, perf in type_performance.items():
            rate = perf['correct'] / perf['total'] if perf['total'] > 0 else 0
            report += f"- {loc_type.replace('_', ' ').title()}: {perf['correct']}/{perf['total']} ({rate:.1%})\n"
        
        report += f"""
### 2. OSM Data Utilization Analysis
**Dataset Statistics:**"""
        
        if 'error' not in usage_analysis:
            report += f"""
- Available records: {usage_analysis['osm_records_available']:,}
- Unique provinces: {usage_analysis['unique_provinces']}
- Unique districts: {usage_analysis['unique_districts']}
- Unique neighborhoods: {usage_analysis['unique_neighborhoods']:,}
- Neighborhood lookup success: {usage_analysis.get('neighborhood_lookup_rate', 0):.1%}
"""
        
        report += f"""
### 3. Context Inference Depth
**Complex Scenario Processing:**
- Famous landmarks: {context_analysis['successful_complex_inferences']}/{context_analysis['total_complex_tests']} ({context_analysis['complex_success_rate']:.1%})
- Context awareness: {"GOOD" if context_analysis['complex_success_rate'] > 0.6 else "LIMITED"}
"""
        
        # Add competitive edge analysis
        edge_factors = []
        if dynamic_analysis['success_rate'] > 0.6:
            edge_factors.append("✅ Dynamic inference capabilities")
        if usage_analysis.get('neighborhood_lookup_rate', 0) > 0.5:
            edge_factors.append("✅ Effective OSM data utilization")
        if context_analysis['complex_success_rate'] > 0.5:
            edge_factors.append("✅ Context-aware processing")
        
        if len(edge_factors) == 0:
            edge_factors.append("❌ Limited competitive advantages found")
        
        report += f"""
## 🏆 COMPETITIVE EDGE ANALYSIS

**Advantages for TEKNOFEST:**
"""
        for factor in edge_factors:
            report += f"{factor}\n"
        
        report += f"""
**Overall Intelligence Rating:** {len(edge_factors)}/3 factors present

## 📋 RECOMMENDATIONS

**Immediate Actions:**
1. {'✅' if dynamic_analysis['success_rate'] > 0.6 else '❌'} Dynamic inference is {'working well' if dynamic_analysis['success_rate'] > 0.6 else 'needs improvement'}
2. {'✅' if usage_analysis.get('neighborhood_lookup_rate', 0) > 0.5 else '❌'} OSM data utilization is {'effective' if usage_analysis.get('neighborhood_lookup_rate', 0) > 0.5 else 'underutilized'}
3. {'✅' if context_analysis['complex_success_rate'] > 0.5 else '❌'} Context awareness is {'strong' if context_analysis['complex_success_rate'] > 0.5 else 'limited'}

**Next Steps:**
- Focus on {'maintaining current performance' if dynamic_analysis['success_rate'] > 0.6 else 'improving dynamic inference algorithms'}
- {'Leverage existing OSM integration' if usage_analysis.get('neighborhood_lookup_rate', 0) > 0.5 else 'Enhance OSM data extraction and indexing'}
- {'Build on context strengths' if context_analysis['complex_success_rate'] > 0.5 else 'Develop context inference capabilities'}

---
*Generated by Intelligence_Engine_Analysis*
"""
        
        return report


if __name__ == "__main__":
    analyzer = IntelligenceEngineAnalyzer()
    
    print("🚀 STARTING COMPREHENSIVE INTELLIGENCE ENGINE ANALYSIS")
    print("="*80)
    
    # Generate and save report
    report = analyzer.generate_intelligence_report()
    
    # Save report
    with open('Intelligence_Engine_Analysis_Report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("\n" + "✅"*25)
    print("INTELLIGENCE ANALYSIS COMPLETE")
    print("✅"*25)
    
    print(f"\n📄 Report saved to: Intelligence_Engine_Analysis_Report.md")