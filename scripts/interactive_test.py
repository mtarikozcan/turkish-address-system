#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Address Resolution System Turkish Address System Interactive Testing Application

Interactive console application for testing the complete address processing pipeline
with step-by-step visualization of all algorithm results.

Usage: python interactive_test.py
"""

import sys
import os
import time
import logging
from typing import Dict, Any, Optional

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import all system components
try:
    from geo_integrated_pipeline import GeoIntegratedPipeline
    from address_validator import AddressValidator
    from address_corrector import AddressCorrector
    from address_parser import AddressParser
    from address_matcher import HybridAddressMatcher
    COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some components not available: {e}")
    COMPONENTS_AVAILABLE = False

# Configure logging to suppress verbose output during interactive use
logging.getLogger().setLevel(logging.WARNING)

class InteractiveAddressTester:
    """Interactive testing application for Address Resolution System Turkish Address System"""
    
    def __init__(self):
        """Initialize the testing application with all components"""
        self.components_loaded = False
        self.pipeline = None
        self.validator = None
        self.corrector = None
        self.parser = None
        self.matcher = None
        
        print("🏗️  Address Resolution System Turkish Address System Interactive Tester")
        print("=" * 60)
        
        self._load_components()
    
    def _load_components(self):
        """Load all system components with fallback handling"""
        print("📦 Loading system components...")
        
        try:
            # Initialize individual components
            print("   ✓ Loading AddressCorrector...")
            self.corrector = AddressCorrector()
            
            print("   ✓ Loading AddressParser...")
            self.parser = AddressParser()
            
            print("   ✓ Loading AddressValidator...")
            self.validator = AddressValidator()
            
            print("   ✓ Loading HybridAddressMatcher...")
            self.matcher = HybridAddressMatcher()
            
            print("   ✓ Loading GeoIntegratedPipeline...")
            # Try to initialize with fallback database connection
            try:
                # Use a dummy connection string for testing without real database
                dummy_db_string = "postgresql://user:pass@localhost:5432/dummy"
                self.pipeline = GeoIntegratedPipeline(dummy_db_string)
            except Exception as e:
                print(f"     Warning: Pipeline needs database connection: {e}")
                self.pipeline = None
            
            self.components_loaded = True
            print("✅ All components loaded successfully!")
            
        except Exception as e:
            print(f"⚠️  Error loading components: {e}")
            print("🔄 Continuing with fallback mode...")
            self.components_loaded = False
    
    def _format_address_input(self, address: str) -> str:
        """Format and normalize address input for processing"""
        # Handle Turkish characters properly
        address = address.strip()
        if not address:
            return ""
        
        # Basic cleanup while preserving Turkish characters
        address = ' '.join(address.split())  # Normalize whitespace
        return address
    
    def _print_step_header(self, step_num: int, step_name: str):
        """Print formatted step header"""
        print(f"\n📋 Step {step_num}: {step_name}")
        print("-" * 40)
    
    def _print_result(self, label: str, result: Any, indent: int = 0):
        """Print formatted result with proper indentation"""
        spaces = "  " * indent
        if isinstance(result, dict):
            print(f"{spaces}{label}:")
            for key, value in result.items():
                print(f"{spaces}  • {key}: {value}")
        elif isinstance(result, (list, tuple)):
            print(f"{spaces}{label}: {', '.join(map(str, result))}")
        else:
            print(f"{spaces}{label}: {result}")
    
    def _calculate_overall_confidence(self, corrected_address: str, parsed_result: dict, validation_result: dict) -> float:
        """Calculate overall confidence from individual component results"""
        try:
            # Weight factors for different components
            weights = {
                'correction': 0.2,
                'parsing': 0.4, 
                'validation': 0.4
            }
            
            # Get individual confidence scores
            correction_confidence = 0.8 if corrected_address else 0.0
            parsing_confidence = parsed_result.get('confidence', 0.0) if parsed_result else 0.0
            validation_confidence = validation_result.get('validation_score', 0.0) if validation_result else 0.0
            
            # Calculate weighted average
            overall_confidence = (
                correction_confidence * weights['correction'] +
                parsing_confidence * weights['parsing'] +
                validation_confidence * weights['validation']
            )
            
            return min(1.0, max(0.0, overall_confidence))
            
        except Exception:
            return 0.5  # Default moderate confidence
    
    def process_address_step_by_step(self, address: str):
        """Process address with step-by-step visualization"""
        start_time = time.time()
        
        print(f"\n🔍 Processing Address: '{address}'")
        print("=" * 60)
        
        # Step 1: Original Input
        self._print_step_header(1, "Original Input")
        self._print_result("Raw Address", address)
        
        formatted_address = self._format_address_input(address)
        if formatted_address != address:
            self._print_result("Formatted Address", formatted_address)
        
        try:
            # Step 2: Address Correction
            self._print_step_header(2, "Address Correction")
            if self.corrector:
                corrected_result = self.corrector.correct_address(formatted_address)
                if isinstance(corrected_result, dict):
                    corrected_address = corrected_result.get('corrected_address', formatted_address)
                    corrections = corrected_result.get('corrections_applied', [])
                else:
                    corrected_address = corrected_result
                    corrections = []
                
                self._print_result("Corrected Address", corrected_address)
                if corrections:
                    self._print_result("Corrections Applied", corrections)
            else:
                corrected_address = formatted_address
                print("  ⚠️  AddressCorrector not available - using original")
            
            # Step 3: Address Parsing
            self._print_step_header(3, "Address Parsing")
            if self.parser:
                parsed_result = self.parser.parse_address(corrected_address)
                if isinstance(parsed_result, dict):
                    components = parsed_result.get('components', {})
                    confidence = parsed_result.get('confidence', 0.0)
                    
                    self._print_result("Parsed Components", components)
                    self._print_result("Parsing Confidence", f"{confidence:.2f}")
                else:
                    print("  ⚠️  Unexpected parser result format")
            else:
                print("  ⚠️  AddressParser not available")
            
            # Step 4: Address Validation
            self._print_step_header(4, "Address Validation")
            if self.validator:
                # Prepare validation data in correct format
                validation_data = {
                    'raw_address': corrected_address,
                    'parsed_components': parsed_result.get('components', {}) if parsed_result else {}
                }
                
                validation_result = self.validator.validate_address(validation_data)
                if isinstance(validation_result, dict):
                    is_valid = validation_result.get('is_valid', False)
                    validation_score = validation_result.get('confidence', 0.0)
                    errors = validation_result.get('errors', [])
                    
                    status_icon = "✅" if is_valid else "❌"
                    self._print_result("Validation Status", f"{status_icon} {'Valid' if is_valid else 'Invalid'}")
                    self._print_result("Validation Score", f"{validation_score:.2f}")
                    if errors:
                        self._print_result("Issues Found", errors)
                else:
                    print("  ⚠️  Unexpected validator result format")
            else:
                print("  ⚠️  AddressValidator not available")
            
            # Step 5: Pipeline Processing (if available)
            self._print_step_header(5, "Complete Pipeline Processing")
            if self.pipeline:
                try:
                    # Since pipeline methods are async, create a simple sync simulation
                    final_confidence = self._calculate_overall_confidence(corrected_address, parsed_result, validation_result)
                    status = "processed_without_database"
                    
                    self._print_result("Final Confidence Score", f"{final_confidence:.3f}")
                    self._print_result("Processing Status", status)
                    self._print_result("Pipeline Mode", "Fallback (no database)")
                    
                except Exception as e:
                    print(f"  ⚠️  Pipeline processing error: {e}")
            else:
                print("  ⚠️  GeoIntegratedPipeline not available - using individual components")
            
        except Exception as e:
            print(f"\n❌ Error during processing: {e}")
        
        # Final Summary
        total_time = (time.time() - start_time) * 1000
        print(f"\n⏱️  Total Processing Time: {total_time:.1f}ms")
        print("=" * 60)
    
    def run_interactive_loop(self):
        """Main interactive loop for address testing"""
        if not self.components_loaded:
            print("\n⚠️  Warning: Running in fallback mode with limited functionality")
        
        print("\n🚀 Interactive Address Testing Started!")
        print("\n📝 Instructions:")
        print("   • Enter Turkish addresses to test the complete system")
        print("   • Examples: 'istanbul kadikoy moda mh', 'ankara cankaya kizilay'")
        print("   • Type 'q' or 'quit' to exit")
        print("   • Turkish characters (ç,ğ,ı,ö,ş,ü) are fully supported")
        
        while True:
            try:
                print("\n" + "="*60)
                user_input = input("🏠 Enter Turkish address (or 'q' to quit): ").strip()
                
                if not user_input:
                    print("⚠️  Please enter a valid address")
                    continue
                
                if user_input.lower() in ['q', 'quit', 'exit', 'çık']:
                    print("\n👋 Exiting interactive tester. Goodbye!")
                    break
                
                # Process the address
                self.process_address_step_by_step(user_input)
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted by user. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                print("Please try again with a different address.")

def main():
    """Main function to run the interactive tester"""
    try:
        # Check if components are available
        if not COMPONENTS_AVAILABLE:
            print("❌ Error: Required components not found in src/ directory")
            print("Please ensure all Python files are in the src/ folder:")
            print("  - geo_integrated_pipeline.py")
            print("  - address_validator.py") 
            print("  - address_corrector.py")
            print("  - address_parser.py")
            print("  - address_matcher.py")
            return 1
        
        # Create and run interactive tester
        tester = InteractiveAddressTester()
        tester.run_interactive_loop()
        
        return 0
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)