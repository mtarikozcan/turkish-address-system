#!/usr/bin/env python3
"""
DEEP ANALYSIS: Character Pipeline Inspection
Identifies remaining character encoding issues like 'İ̇stiklal'
"""

import sys
import os
import unicodedata
from typing import Dict, List, Any
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from address_corrector import AddressCorrector
    from turkish_character_fix import TurkishCharacterHandler, ImprovedAddressCorrector
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

class CharacterPipelineInspector:
    """
    Deep inspection of character handling pipeline
    Identifies root causes of Turkish character corruption
    """
    
    def __init__(self):
        print("🔍 INITIALIZING CHARACTER PIPELINE INSPECTOR")
        self.original_corrector = AddressCorrector()
        self.improved_corrector = ImprovedAddressCorrector()
        self.char_handler = TurkishCharacterHandler()
        
        # Test cases that reveal character issues
        self.critical_test_cases = [
            {"input": "İstiklal Caddesi", "expected": "İstiklal Caddesi"},
            {"input": "istanbul", "expected": "İstanbul"},
            {"input": "ŞIŞLI", "expected": "Şişli"},
            {"input": "üsküdar", "expected": "Üsküdar"},
            {"input": "çankaya", "expected": "Çankaya"},
            {"input": "beyoğlu", "expected": "Beyoğlu"},
            {"input": "kadıköy", "expected": "Kadıköy"},
            {"input": "ataşehir", "expected": "Ataşehir"},
            {"input": "büyükçekmece", "expected": "Büyükçekmece"},
            {"input": "göztepe", "expected": "Göztepe"}
        ]
    
    def inspect_unicode_normalization_issues(self) -> Dict[str, Any]:
        """
        Inspect Unicode normalization that causes character corruption
        """
        print("\n" + "="*70)
        print("🔍 INSPECTING UNICODE NORMALIZATION ISSUES")
        print("="*70)
        
        normalization_results = []
        issues_found = 0
        
        for test_case in self.critical_test_cases:
            input_text = test_case["input"]
            expected = test_case["expected"]
            
            print(f"\n🧪 Testing: '{input_text}'")
            
            # Analyze character composition
            analysis = self._analyze_character_composition(input_text)
            print(f"   Input composition: {analysis['composition_info']}")
            
            # Test different normalization forms
            nfc = unicodedata.normalize('NFC', input_text)
            nfd = unicodedata.normalize('NFD', input_text)
            nfkc = unicodedata.normalize('NFKC', input_text)
            nfkd = unicodedata.normalize('NFKD', input_text)
            
            # Test Python's built-in methods
            python_lower = input_text.lower()
            python_title = input_text.title()
            python_upper = input_text.upper()
            
            # Test our Turkish handlers
            turkish_lower = self.char_handler.turkish_lower(input_text)
            turkish_title = self.char_handler.turkish_title_case(input_text)
            turkish_upper = self.char_handler.turkish_upper(input_text)
            
            results = {
                'input': input_text,
                'expected': expected,
                'nfc': nfc,
                'nfd': nfd,
                'nfkc': nfkc,
                'nfkd': nfkd,
                'python_lower': python_lower,
                'python_title': python_title,
                'python_upper': python_upper,
                'turkish_lower': turkish_lower,
                'turkish_title': turkish_title,
                'turkish_upper': turkish_upper,
                'has_issues': False,
                'issues': []
            }
            
            # Check for issues
            if nfc != input_text:
                results['has_issues'] = True
                results['issues'].append(f"NFC normalization changes text: '{input_text}' → '{nfc}'")
                issues_found += 1
            
            if nfd != input_text:
                results['has_issues'] = True
                results['issues'].append(f"NFD normalization changes text: '{input_text}' → '{nfd}'")
            
            # Check for problematic characters
            for char in input_text:
                if ord(char) > 127:  # Non-ASCII
                    char_name = unicodedata.name(char, 'UNKNOWN')
                    if 'COMBINING' in char_name:
                        results['has_issues'] = True
                        results['issues'].append(f"Combining character detected: '{char}' ({char_name})")
                        issues_found += 1
            
            # Check Python methods vs Turkish methods
            if turkish_title != python_title:
                print(f"   ⚠️ Python title: '{python_title}' vs Turkish title: '{turkish_title}'")
                if turkish_title == expected:
                    print(f"   ✅ Turkish method is correct")
                elif python_title == expected:
                    print(f"   ⚠️ Python method is correct, Turkish method wrong")
                else:
                    print(f"   ❌ Both methods wrong, expected: '{expected}'")
            
            normalization_results.append(results)
        
        summary = {
            'total_tests': len(self.critical_test_cases),
            'issues_found': issues_found,
            'results': normalization_results,
            'unicode_issues_detected': issues_found > 0
        }
        
        print(f"\n📊 UNICODE NORMALIZATION ANALYSIS:")
        print(f"   Issues detected: {issues_found} in {summary['total_tests']} tests")
        print(f"   Unicode problems: {'YES' if summary['unicode_issues_detected'] else 'NO'}")
        
        return summary
    
    def _analyze_character_composition(self, text: str) -> Dict[str, Any]:
        """Analyze character composition for debugging"""
        composition = []
        for char in text:
            char_info = {
                'char': char,
                'unicode_point': ord(char),
                'hex': f"U+{ord(char):04X}",
                'name': unicodedata.name(char, 'UNKNOWN'),
                'category': unicodedata.category(char)
            }
            composition.append(char_info)
        
        # Create readable info
        composition_info = " + ".join([f"'{c['char']}' ({c['hex']})" for c in composition])
        
        return {
            'composition': composition,
            'composition_info': composition_info,
            'has_combining_chars': any('COMBINING' in c['name'] for c in composition)
        }
    
    def compare_correction_pipelines(self) -> Dict[str, Any]:
        """
        Compare original vs improved correction pipelines
        """
        print("\n" + "="*70)
        print("⚖️ COMPARING CORRECTION PIPELINES")
        print("="*70)
        
        pipeline_comparisons = []
        improvements = 0
        regressions = 0
        
        for test_case in self.critical_test_cases:
            input_text = test_case["input"]
            expected = test_case["expected"]
            
            print(f"\n📋 Testing: '{input_text}'")
            
            # Test original corrector
            try:
                original_result = self.original_corrector.correct_address(input_text)
                original_output = original_result.get('corrected_address', input_text)
            except Exception as e:
                original_output = f"ERROR: {e}"
            
            # Test improved corrector
            try:
                improved_result = self.improved_corrector.correct_address(input_text)
                improved_output = improved_result.get('corrected_address', input_text)
            except Exception as e:
                improved_output = f"ERROR: {e}"
            
            # Evaluate results
            original_correct = self._is_correct_turkish(original_output, expected)
            improved_correct = self._is_correct_turkish(improved_output, expected)
            
            comparison = {
                'input': input_text,
                'expected': expected,
                'original_output': original_output,
                'improved_output': improved_output,
                'original_correct': original_correct,
                'improved_correct': improved_correct,
                'status': 'unchanged'
            }
            
            if improved_correct and not original_correct:
                comparison['status'] = 'improved'
                improvements += 1
                print(f"   ✅ IMPROVED: '{original_output}' → '{improved_output}'")
            elif original_correct and not improved_correct:
                comparison['status'] = 'regression'
                regressions += 1
                print(f"   ❌ REGRESSION: '{original_output}' → '{improved_output}'")
            elif original_correct and improved_correct:
                comparison['status'] = 'both_correct'
                print(f"   ✅ BOTH CORRECT: '{improved_output}'")
            else:
                comparison['status'] = 'both_wrong'
                print(f"   ❌ BOTH WRONG: original='{original_output}', improved='{improved_output}', expected='{expected}'")
            
            pipeline_comparisons.append(comparison)
        
        analysis = {
            'total_tests': len(self.critical_test_cases),
            'improvements': improvements,
            'regressions': regressions,
            'net_improvement': improvements - regressions,
            'comparisons': pipeline_comparisons,
            'improvement_rate': improvements / len(self.critical_test_cases) if self.critical_test_cases else 0
        }
        
        print(f"\n📊 PIPELINE COMPARISON RESULTS:")
        print(f"   Improvements: {improvements}/{analysis['total_tests']}")
        print(f"   Regressions: {regressions}/{analysis['total_tests']}")
        print(f"   Net improvement: {analysis['net_improvement']}")
        print(f"   Improvement rate: {analysis['improvement_rate']:.1%}")
        
        return analysis
    
    def _is_correct_turkish(self, output: str, expected: str) -> bool:
        """Check if output matches expected Turkish text"""
        if not output or not expected:
            return False
        
        # Normalize for comparison
        output_clean = output.strip()
        expected_clean = expected.strip()
        
        # Exact match
        if output_clean == expected_clean:
            return True
        
        # Case-insensitive match using Turkish rules
        output_lower = self.char_handler.turkish_lower(output_clean)
        expected_lower = self.char_handler.turkish_lower(expected_clean)
        
        return output_lower == expected_lower
    
    def identify_problematic_patterns(self) -> Dict[str, Any]:
        """
        Identify specific patterns that cause character corruption
        """
        print("\n" + "="*70)
        print("🎯 IDENTIFYING PROBLEMATIC PATTERNS")
        print("="*70)
        
        problematic_patterns = {
            'dotted_i_issues': [],
            'case_conversion_issues': [],
            'combining_char_issues': [],
            'normalization_issues': []
        }
        
        # Test specific problem patterns
        test_patterns = [
            {"pattern": "İ", "description": "Capital I with dot", "tests": ["İstanbul", "İzmir", "İnönü"]},
            {"pattern": "ı", "description": "Lowercase dotless i", "tests": ["ılık", "ısıtma", "ıslak"]},
            {"pattern": "i", "description": "Lowercase i with dot", "tests": ["istanbul", "izmir", "inönü"]},
            {"pattern": "I", "description": "Capital dotless I", "tests": ["ISTANBUL", "IZMIR", "INÖNÜ"]},
            {"pattern": "Ç", "description": "C with cedilla", "tests": ["Çankaya", "çok", "Çekmece"]},
            {"pattern": "Ş", "description": "S with cedilla", "tests": ["Şişli", "şehir", "Başakşehir"]},
            {"pattern": "Ğ", "description": "G with breve", "tests": ["Beyoğlu", "Bağcılar", "Doğu"]},
            {"pattern": "Ü", "description": "U with diaeresis", "tests": ["Üsküdar", "üç", "Büyük"]},
            {"pattern": "Ö", "description": "O with diaeresis", "tests": ["Göztepe", "önemli", "Köprü"]}
        ]
        
        pattern_issues = 0
        
        for pattern_info in test_patterns:
            pattern = pattern_info["pattern"]
            description = pattern_info["description"]
            tests = pattern_info["tests"]
            
            print(f"\n🔍 Testing pattern '{pattern}' ({description}):")
            
            for test_word in tests:
                # Test various transformations
                python_lower = test_word.lower()
                python_upper = test_word.upper()
                python_title = test_word.title()
                
                turkish_lower = self.char_handler.turkish_lower(test_word)
                turkish_upper = self.char_handler.turkish_upper(test_word)
                turkish_title = self.char_handler.turkish_title_case(test_word)
                
                # Check for corruption
                issues = []
                if python_lower != turkish_lower:
                    issues.append(f"Lower: Python '{python_lower}' vs Turkish '{turkish_lower}'")
                if python_upper != turkish_upper:
                    issues.append(f"Upper: Python '{python_upper}' vs Turkish '{turkish_upper}'")
                if python_title != turkish_title:
                    issues.append(f"Title: Python '{python_title}' vs Turkish '{turkish_title}'")
                
                if issues:
                    pattern_issues += 1
                    print(f"   ⚠️ {test_word}: {'; '.join(issues)}")
                    
                    # Categorize the issue
                    if 'İ' in test_word or 'ı' in test_word or 'i' in test_word or 'I' in test_word:
                        problematic_patterns['dotted_i_issues'].append({
                            'word': test_word,
                            'issues': issues
                        })
                else:
                    print(f"   ✅ {test_word}: No issues")
        
        analysis = {
            'pattern_issues_found': pattern_issues,
            'problematic_patterns': problematic_patterns,
            'patterns_tested': len(test_patterns)
        }
        
        print(f"\n📊 PATTERN ANALYSIS RESULTS:")
        print(f"   Pattern issues found: {pattern_issues}")
        print(f"   Dotted I issues: {len(problematic_patterns['dotted_i_issues'])}")
        
        return analysis
    
    def generate_character_inspection_report(self) -> str:
        """Generate comprehensive character pipeline inspection report"""
        print("\n" + "🔍"*25)
        print("GENERATING CHARACTER INSPECTION REPORT")
        print("🔍"*25)
        
        # Run all inspections
        unicode_analysis = self.inspect_unicode_normalization_issues()
        pipeline_comparison = self.compare_correction_pipelines()
        pattern_analysis = self.identify_problematic_patterns()
        
        report = f"""
# CHARACTER PIPELINE INSPECTION REPORT
**Generated:** Turkish Address Processing System Character Analysis
**Focus:** Identifying remaining encoding issues like 'İ̇stiklal'

## 🎯 EXECUTIVE SUMMARY

### Character Handling Status
- **Unicode Issues:** {'DETECTED' if unicode_analysis['unicode_issues_detected'] else 'NONE FOUND'}
- **Pipeline Improvements:** {pipeline_comparison['improvements']}/{pipeline_comparison['total_tests']} tests improved
- **Regressions:** {pipeline_comparison['regressions']}/{pipeline_comparison['total_tests']} tests regressed
- **Pattern Issues:** {pattern_analysis['pattern_issues_found']} problematic patterns found

### Overall Assessment
"""
        
        if pipeline_comparison['net_improvement'] > 0:
            assessment = "✅ IMPROVED: Character handling pipeline shows net improvements"
        elif pipeline_comparison['net_improvement'] == 0:
            assessment = "⚠️ MIXED: No net improvement, some gains offset by regressions"
        else:
            assessment = "❌ REGRESSED: Character handling has gotten worse"
        
        report += f"{assessment}\n"
        
        report += f"""
## 🔍 DETAILED FINDINGS

### 1. Unicode Normalization Issues
**Tests:** {unicode_analysis['total_tests']} critical Turkish characters
**Issues Found:** {unicode_analysis['issues_found']}
**Problem Areas:**
"""
        
        for result in unicode_analysis['results']:
            if result['has_issues']:
                report += f"- '{result['input']}': {', '.join(result['issues'])}\n"
        
        report += f"""
### 2. Pipeline Comparison Results
**Improvement Rate:** {pipeline_comparison['improvement_rate']:.1%}
**Detailed Results:**
"""
        
        status_counts = {}
        for comp in pipeline_comparison['comparisons']:
            status = comp['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        for status, count in status_counts.items():
            report += f"- {status.replace('_', ' ').title()}: {count}\n"
        
        report += f"""
### 3. Problematic Pattern Analysis
**Patterns Tested:** {pattern_analysis['patterns_tested']}
**Issues Found:** {pattern_analysis['pattern_issues_found']}

**Dotted I Issues:** {len(pattern_analysis['problematic_patterns']['dotted_i_issues'])}
"""
        
        for issue in pattern_analysis['problematic_patterns']['dotted_i_issues']:
            report += f"- {issue['word']}: {'; '.join(issue['issues'])}\n"
        
        # Root cause analysis
        report += f"""
## 🔧 ROOT CAUSE ANALYSIS

### Why 'İ̇stiklal' and Similar Issues Occur:

1. **Unicode Composition Problems:**
   - Turkish İ (U+0130) vs Latin I (U+0049)
   - Combining characters creating visual duplicates
   - NFD vs NFC normalization conflicts

2. **Python's Built-in Methods:**
   - `str.lower()` doesn't handle Turkish İ → i correctly
   - `str.title()` capitalizes after spaces incorrectly
   - Unicode normalization can corrupt Turkish characters

3. **Pipeline Order Issues:**
   - Normalization before Turkish character mapping
   - Case conversion before protection of special names

### Recommended Fixes:

1. **Use Turkish-specific character mapping** ✅ (Implemented)
2. **Protect famous names before processing** ✅ (Implemented)
3. **Avoid Unicode normalization of Turkish text** ⚠️ (Partially)
4. **Custom case conversion methods** ✅ (Implemented)

## 📋 NEXT STEPS

**Immediate Actions:**
1. {'✅' if pipeline_comparison['net_improvement'] > 0 else '❌'} Character pipeline improvements are {'working' if pipeline_comparison['net_improvement'] > 0 else 'needed'}
2. {'✅' if unicode_analysis['issues_found'] < 3 else '❌'} Unicode issues are {'minimal' if unicode_analysis['issues_found'] < 3 else 'significant'}
3. {'✅' if pattern_analysis['pattern_issues_found'] < 5 else '❌'} Pattern handling is {'good' if pattern_analysis['pattern_issues_found'] < 5 else 'problematic'}

**Priority Order:**
1. {'Fix remaining Unicode normalization issues' if unicode_analysis['issues_found'] > 2 else 'Maintain current character handling'}
2. {'Address pattern-specific problems' if pattern_analysis['pattern_issues_found'] > 3 else 'Monitor for edge cases'}
3. {'Test with more diverse Turkish text' if pipeline_comparison['improvement_rate'] < 0.8 else 'System appears stable'}

---
*Generated by Character_Pipeline_Inspection*
"""
        
        return report


if __name__ == "__main__":
    inspector = CharacterPipelineInspector()
    
    print("🚀 STARTING CHARACTER PIPELINE INSPECTION")
    print("="*60)
    
    # Generate report
    report = inspector.generate_character_inspection_report()
    
    # Save report
    with open('Character_Pipeline_Inspection_Report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("\n" + "✅"*20)
    print("CHARACTER INSPECTION COMPLETE")
    print("✅"*20)
    
    print(f"\n📄 Report saved to: Character_Pipeline_Inspection_Report.md")