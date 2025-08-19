#!/usr/bin/env python3
"""
DEEP ANALYSIS: OSM Data Usage Analyzer
Critical verification of actual vs claimed data utilization in Turkish Address System
"""

import sys
import os
import json
import pandas as pd
from typing import Dict, List, Set, Tuple, Any
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from address_parser import AddressParser
    from address_corrector import AddressCorrector
    from address_validator import AddressValidator
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

class OSMDataUsageAnalyzer:
    """
    Deep analysis tool to verify ACTUAL OSM data utilization
    vs claimed improvements
    """
    
    def __init__(self):
        print("🔍 INITIALIZING OSM DATA USAGE ANALYZER")
        self.parser = AddressParser()
        self.corrector = AddressCorrector()
        self.validator = AddressValidator()
        
        # Load the actual OSM dataset
        self.osm_data = self._load_osm_dataset()
        self.total_osm_records = len(self.osm_data) if self.osm_data is not None else 0
        
        # Known hardcoded mappings (from previous analysis)
        self.known_hardcoded = {
            "istiklal caddesi": {"ilce": "beyoğlu", "mahalle": "beyoğlu"},
            "bağdat caddesi": {"ilce": "kadıköy"},
            "tunalı hilmi": {"il": "ankara", "ilce": "çankaya"},
            "konur sokak": {"mahalle": "kızılay"},
            "atatürk bulvarı": {"il": "ankara"}
        }
        
        print(f"📊 Loaded {self.total_osm_records} OSM records for analysis")
    
    def _load_osm_dataset(self) -> pd.DataFrame:
        """Load the actual OSM dataset to compare against"""
        try:
            csv_path = Path(__file__).parent / "database" / "enhanced_turkish_neighborhoods.csv"
            if csv_path.exists():
                df = pd.read_csv(csv_path)
                print(f"✅ Loaded OSM dataset: {len(df)} records")
                return df
            else:
                print(f"❌ OSM dataset not found at {csv_path}")
                return None
        except Exception as e:
            print(f"❌ Error loading OSM dataset: {e}")
            return None
    
    def analyze_actual_mappings(self) -> Dict[str, Any]:
        """
        CRITICAL: Verify how many street→neighborhood mappings are actually used
        vs claimed dynamic inference from 55K dataset
        """
        print("\n" + "="*60)
        print("🔍 ANALYZING ACTUAL STREET→NEIGHBORHOOD MAPPINGS")
        print("="*60)
        
        # Test addresses that should use dynamic OSM data
        test_addresses = [
            # Addresses NOT in hardcoded list
            "ankara çankaya güvenpark",
            "istanbul beylikdüzü migros",
            "izmir konak göztepe",
            "bursa nilüfer özlüce", 
            "antalya kepez santral",
            "ankara etimesgut eryaman",
            "istanbul maltepe bağlarbaşı",
            "izmir bornova evka",
            "adana seyhan reşatbey",
            "eskişehir tepebaşı aşağısöğütönü"
        ]
        
        dynamic_inferences = 0
        hardcoded_matches = 0
        failed_inferences = 0
        inference_details = []
        
        for address in test_addresses:
            print(f"\nTesting: {address}")
            
            result = self.parser.parse_address(address)
            components = result.get('components', {})
            
            # Check if this was likely hardcoded
            is_hardcoded = self._is_likely_hardcoded(address.lower(), components)
            
            # Check if meaningful inference occurred
            has_inference = bool(components.get('il') or components.get('ilce') or components.get('mahalle'))
            
            detail = {
                'address': address,
                'components': components,
                'is_hardcoded': is_hardcoded,
                'has_inference': has_inference,
                'confidence': result.get('overall_confidence', 0)
            }
            inference_details.append(detail)
            
            if is_hardcoded:
                hardcoded_matches += 1
                print(f"  📌 Hardcoded match detected")
            elif has_inference:
                dynamic_inferences += 1
                print(f"  🧠 Dynamic inference: {components}")
            else:
                failed_inferences += 1
                print(f"  ❌ No inference: {components}")
        
        # Check parser's internal data usage
        osm_utilization = self._analyze_parser_osm_usage()
        
        analysis = {
            'total_tests': len(test_addresses),
            'dynamic_inferences': dynamic_inferences,
            'hardcoded_matches': hardcoded_matches,
            'failed_inferences': failed_inferences,
            'inference_details': inference_details,
            'osm_utilization': osm_utilization,
            'actual_dynamic_ratio': dynamic_inferences / len(test_addresses) if test_addresses else 0
        }
        
        print(f"\n📊 MAPPING ANALYSIS RESULTS:")
        print(f"   Dynamic inferences: {dynamic_inferences}/{len(test_addresses)} ({analysis['actual_dynamic_ratio']:.1%})")
        print(f"   Hardcoded matches: {hardcoded_matches}/{len(test_addresses)}")
        print(f"   Failed inferences: {failed_inferences}/{len(test_addresses)}")
        
        return analysis
    
    def _is_likely_hardcoded(self, address: str, components: Dict) -> bool:
        """Check if inference was likely from hardcoded mapping"""
        for hardcoded_key in self.known_hardcoded.keys():
            if hardcoded_key in address:
                return True
        return False
    
    def _analyze_parser_osm_usage(self) -> Dict[str, Any]:
        """Analyze how the parser actually uses OSM data internally"""
        print(f"\n🔍 ANALYZING PARSER'S OSM DATA UTILIZATION")
        
        # Inspect parser's internal data structures
        parser_analysis = {
            'has_osm_data': hasattr(self.parser, 'turkish_locations'),
            'osm_records_loaded': 0,
            'neighborhood_index_size': 0,
            'street_mappings_available': 0,
            'reverse_lookup_enabled': False
        }
        
        if hasattr(self.parser, 'turkish_locations') and self.parser.turkish_locations:
            parser_analysis['osm_records_loaded'] = len(self.parser.turkish_locations)
            
            # Check if neighborhoods are indexed
            if isinstance(self.parser.turkish_locations, dict):
                parser_analysis['neighborhood_index_size'] = len(self.parser.turkish_locations)
                
                # Sample some entries to understand structure
                sample_keys = list(self.parser.turkish_locations.keys())[:5]
                print(f"   Sample OSM entries: {sample_keys}")
                
                # Check if street names are available
                for key in sample_keys[:3]:
                    entry = self.parser.turkish_locations[key]
                    if isinstance(entry, dict):
                        if 'street' in str(entry) or 'cadde' in str(entry) or 'sokak' in str(entry):
                            parser_analysis['street_mappings_available'] += 1
        
        # Check validator's data usage
        if hasattr(self.validator, 'admin_hierarchy'):
            parser_analysis['validator_records'] = len(self.validator.admin_hierarchy)
        
        print(f"   OSM records in parser: {parser_analysis['osm_records_loaded']}")
        print(f"   Neighborhood index size: {parser_analysis['neighborhood_index_size']}")
        print(f"   Street mappings found: {parser_analysis['street_mappings_available']}")
        
        return parser_analysis
    
    def count_dynamic_vs_hardcoded_inferences(self) -> Dict[str, int]:
        """
        Test inference capabilities with streets NOT in hardcoded list
        to verify true dynamic capabilities
        """
        print("\n" + "="*60)
        print("🧠 TESTING DYNAMIC VS HARDCODED INFERENCE CAPABILITIES")
        print("="*60)
        
        # Streets/areas that should NOT be in hardcoded mappings
        non_hardcoded_tests = [
            ("kordon izmir", "İzmir"),  # Famous İzmir waterfront
            ("galata istanbul", "Beyoğlu"),  # Galata area should infer Beyoğlu
            ("ulus ankara", "Çankaya"),  # Central Ankara area
            ("kemer antalya", "Antalya"),  # Kemer district
            ("alanya antalya", "Antalya"),  # Alanya area
            ("palandöken erzurum", "Erzurum"),  # Ski resort area
            ("trabzon ortahisar", "Trabzon"),  # Trabzon center
            ("rize merkez", "Rize"),  # Rize center
            ("artvin merkez", "Artvin"),  # Artvin center
            ("van edremit", "Van")  # Van district
        ]
        
        dynamic_successes = 0
        hardcoded_fallbacks = 0
        total_failures = 0
        results = []
        
        for test_address, expected_il in non_hardcoded_tests:
            print(f"\nTesting: {test_address} (expecting {expected_il})")
            
            result = self.parser.parse_address(test_address)
            components = result.get('components', {})
            
            # Check result
            inferred_il = components.get('il', '').lower()
            expected_il_lower = expected_il.lower()
            
            is_hardcoded = self._is_likely_hardcoded(test_address, components)
            is_correct = expected_il_lower in inferred_il or inferred_il in expected_il_lower
            
            result_entry = {
                'input': test_address,
                'expected': expected_il,
                'inferred_il': components.get('il', 'NONE'),
                'inferred_ilce': components.get('ilce', 'NONE'),
                'inferred_mahalle': components.get('mahalle', 'NONE'),
                'is_correct': is_correct,
                'is_hardcoded': is_hardcoded,
                'confidence': result.get('overall_confidence', 0)
            }
            results.append(result_entry)
            
            if is_correct and not is_hardcoded:
                dynamic_successes += 1
                print(f"  ✅ Dynamic success: {components.get('il')} (confidence: {result.get('overall_confidence', 0):.2f})")
            elif is_hardcoded:
                hardcoded_fallbacks += 1
                print(f"  📌 Hardcoded fallback: {components}")
            else:
                total_failures += 1
                print(f"  ❌ Failed: {components} (expected {expected_il})")
        
        analysis = {
            'dynamic_successes': dynamic_successes,
            'hardcoded_fallbacks': hardcoded_fallbacks,
            'total_failures': total_failures,
            'total_tests': len(non_hardcoded_tests),
            'dynamic_success_rate': dynamic_successes / len(non_hardcoded_tests),
            'results': results
        }
        
        print(f"\n📊 DYNAMIC INFERENCE ANALYSIS:")
        print(f"   True dynamic successes: {dynamic_successes}/{len(non_hardcoded_tests)} ({analysis['dynamic_success_rate']:.1%})")
        print(f"   Hardcoded fallbacks: {hardcoded_fallbacks}/{len(non_hardcoded_tests)}")
        print(f"   Total failures: {total_failures}/{len(non_hardcoded_tests)}")
        
        return analysis
    
    def measure_osm_data_extraction_efficiency(self) -> Dict[str, Any]:
        """
        Measure how much of the 55,955 OSM records are actually leveraged
        vs just loaded into memory
        """
        print("\n" + "="*60)
        print("📈 MEASURING OSM DATA EXTRACTION EFFICIENCY")
        print("="*60)
        
        if self.osm_data is None:
            print("❌ Cannot measure efficiency - OSM data not loaded")
            return {'error': 'OSM data not available'}
        
        # Analyze OSM dataset structure
        osm_analysis = {
            'total_records': len(self.osm_data),
            'unique_provinces': self.osm_data['il'].nunique() if 'il' in self.osm_data.columns else 0,
            'unique_districts': self.osm_data['ilce'].nunique() if 'ilce' in self.osm_data.columns else 0,
            'unique_neighborhoods': self.osm_data['mahalle'].nunique() if 'mahalle' in self.osm_data.columns else 0,
            'has_coordinates': ('latitude' in self.osm_data.columns and 'longitude' in self.osm_data.columns),
            'coordinate_coverage': 0
        }
        
        print(f"📊 OSM Dataset Structure:")
        print(f"   Total records: {osm_analysis['total_records']}")
        print(f"   Unique provinces: {osm_analysis['unique_provinces']}")
        print(f"   Unique districts: {osm_analysis['unique_districts']}")
        print(f"   Unique neighborhoods: {osm_analysis['unique_neighborhoods']}")
        
        if osm_analysis['has_coordinates']:
            coord_complete = self.osm_data.dropna(subset=['latitude', 'longitude'])
            osm_analysis['coordinate_coverage'] = len(coord_complete) / len(self.osm_data)
            print(f"   Coordinate coverage: {osm_analysis['coordinate_coverage']:.1%}")
        
        # Test if system can leverage this data for inference
        sample_neighborhoods = self.osm_data['mahalle'].unique()[:20]  # Test 20 random neighborhoods
        successful_inferences = 0
        
        print(f"\n🧪 Testing inference capability with {len(sample_neighborhoods)} OSM neighborhoods...")
        
        for neighborhood in sample_neighborhoods:
            if pd.isna(neighborhood) or not neighborhood:
                continue
                
            # Create test address with this neighborhood
            test_addr = f"ankara {neighborhood} mahallesi"
            result = self.parser.parse_address(test_addr)
            components = result.get('components', {})
            
            # Check if neighborhood was correctly identified
            if components.get('mahalle', '').lower() in neighborhood.lower():
                successful_inferences += 1
        
        inference_rate = successful_inferences / len(sample_neighborhoods) if sample_neighborhoods else 0
        osm_analysis['sample_inference_rate'] = inference_rate
        
        print(f"   Sample inference success: {successful_inferences}/{len(sample_neighborhoods)} ({inference_rate:.1%})")
        
        # Calculate utilization score
        utilization_factors = [
            osm_analysis['coordinate_coverage'],  # Are coordinates being used?
            inference_rate,  # Can we infer from neighborhood names?
            1.0 if hasattr(self.parser, 'turkish_locations') else 0.0,  # Is data loaded?
        ]
        
        overall_utilization = sum(utilization_factors) / len(utilization_factors)
        osm_analysis['overall_utilization_score'] = overall_utilization
        
        print(f"\n🎯 OVERALL OSM UTILIZATION SCORE: {overall_utilization:.1%}")
        
        if overall_utilization < 0.3:
            print("❌ CRITICAL: Very low OSM data utilization - mostly metadata usage")
        elif overall_utilization < 0.6:
            print("⚠️ WARNING: Moderate OSM utilization - room for improvement") 
        else:
            print("✅ GOOD: High OSM data utilization")
        
        return osm_analysis
    
    def generate_usage_report(self) -> str:
        """Generate comprehensive OSM data usage report"""
        print("\n" + "🔍"*30)
        print("GENERATING COMPREHENSIVE OSM DATA USAGE REPORT")
        print("🔍"*30)
        
        # Run all analyses
        mapping_analysis = self.analyze_actual_mappings()
        inference_analysis = self.count_dynamic_vs_hardcoded_inferences()
        efficiency_analysis = self.measure_osm_data_extraction_efficiency()
        
        report = f"""
# OSM DATA USAGE ANALYSIS REPORT
**Generated:** {pd.Timestamp.now()}
**System:** Address Resolution System Turkish Address Processing System

## 📊 EXECUTIVE SUMMARY

### Data Loading Status
- **OSM Records Available:** {self.total_osm_records:,}
- **System Claims:** Using dynamic inference from 55K dataset
- **Reality Check:** {mapping_analysis['dynamic_inferences']}/{mapping_analysis['total_tests']} dynamic inferences successful

### Key Findings
- **Dynamic Inference Rate:** {inference_analysis['dynamic_success_rate']:.1%} (True dynamic capabilities)
- **Hardcoded Fallback Rate:** {inference_analysis['hardcoded_fallbacks']}/{inference_analysis['total_tests']} tests
- **OSM Utilization Score:** {efficiency_analysis.get('overall_utilization_score', 0):.1%}

## 🔍 DETAILED ANALYSIS

### 1. Street→Neighborhood Mapping Analysis
**Test Results:**
- Dynamic inferences: {mapping_analysis['dynamic_inferences']}/{mapping_analysis['total_tests']}
- Hardcoded matches: {mapping_analysis['hardcoded_matches']}/{mapping_analysis['total_tests']}
- Failed inferences: {mapping_analysis['failed_inferences']}/{mapping_analysis['total_tests']}

**Parser OSM Usage:**
- Records loaded: {mapping_analysis['osm_utilization'].get('osm_records_loaded', 'Unknown')}
- Neighborhood index size: {mapping_analysis['osm_utilization'].get('neighborhood_index_size', 'Unknown')}
- Street mappings available: {mapping_analysis['osm_utilization'].get('street_mappings_available', 'Unknown')}

### 2. Dynamic Intelligence Verification
**Non-Hardcoded Test Results:**
- True dynamic successes: {inference_analysis['dynamic_successes']}/{inference_analysis['total_tests']} ({inference_analysis['dynamic_success_rate']:.1%})
- Hardcoded fallbacks: {inference_analysis['hardcoded_fallbacks']}/{inference_analysis['total_tests']}
- Total failures: {inference_analysis['total_failures']}/{inference_analysis['total_tests']}

### 3. OSM Data Efficiency Metrics
"""
        
        if 'error' not in efficiency_analysis:
            report += f"""
- **Dataset Structure:**
  - Total records: {efficiency_analysis['total_records']:,}
  - Unique provinces: {efficiency_analysis['unique_provinces']}
  - Unique districts: {efficiency_analysis['unique_districts']}
  - Unique neighborhoods: {efficiency_analysis['unique_neighborhoods']:,}
  - Coordinate coverage: {efficiency_analysis['coordinate_coverage']:.1%}

- **Inference Capability:**
  - Sample inference rate: {efficiency_analysis['sample_inference_rate']:.1%}
  - Overall utilization: {efficiency_analysis['overall_utilization_score']:.1%}
"""
        
        # Add recommendations
        if inference_analysis['dynamic_success_rate'] < 0.3:
            recommendation = "❌ CRITICAL: System primarily relies on hardcoded mappings"
        elif inference_analysis['dynamic_success_rate'] < 0.6:
            recommendation = "⚠️ MODERATE: Partial dynamic capability, needs improvement"
        else:
            recommendation = "✅ GOOD: Strong dynamic inference from OSM data"
        
        report += f"""

## 📋 CONCLUSIONS & RECOMMENDATIONS

**Overall Assessment:** {recommendation}

**Priority Actions:**
1. {'✅' if inference_analysis['dynamic_success_rate'] > 0.6 else '❌'} Dynamic inference from OSM data
2. {'✅' if efficiency_analysis.get('overall_utilization_score', 0) > 0.6 else '❌'} Efficient OSM data utilization
3. {'✅' if mapping_analysis['dynamic_inferences'] > mapping_analysis['hardcoded_matches'] else '❌'} Move beyond hardcoded mappings

**Competitive Advantage:**
The 55K OSM dataset is {'being effectively leveraged' if efficiency_analysis.get('overall_utilization_score', 0) > 0.5 else 'UNDERUTILIZED'} for Address Resolution System competition advantage.

---
*Report generated by OSM_Data_Usage_Analyzer*
"""
        
        return report


if __name__ == "__main__":
    analyzer = OSMDataUsageAnalyzer()
    
    print("🚀 STARTING COMPREHENSIVE OSM DATA USAGE ANALYSIS")
    print("="*80)
    
    # Generate and save report
    report = analyzer.generate_usage_report()
    
    # Save report to file
    with open('OSM_Data_Usage_Report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("\n" + "✅"*30)
    print("ANALYSIS COMPLETE - REPORT SAVED TO OSM_Data_Usage_Report.md")
    print("✅"*30)
    
    # Print key findings
    print(f"\n🎯 KEY FINDINGS:")
    print(f"   - OSM Data Available: {analyzer.total_osm_records:,} records")
    print(f"   - Analysis complete - check OSM_Data_Usage_Report.md for details")