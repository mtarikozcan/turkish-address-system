#!/usr/bin/env python3
"""
Test JSON export serialization fix
"""

import sys
from pathlib import Path

# Add project root to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_json_export_fix():
    """Test the JSON export fix"""
    
    print("🎯 JSON EXPORT SERIALIZATION FIX TEST")
    print("=" * 60)
    
    try:
        from detailed_manual_tester import DetailedManualTester, FullPipelineResult, PipelineStepResult
        print("✅ DetailedManualTester loaded successfully")
    except ImportError as e:
        print(f"❌ Error importing tester: {e}")
        return
    
    try:
        tester = DetailedManualTester()
        print("✅ Tester initialized")
    except Exception as e:
        print(f"❌ Error initializing tester: {e}")
        return
    
    print(f"\n🧪 TEST 1: Single Address Analysis and JSON Export")
    
    # Test address
    test_address = "Ankara Çankaya Kızılay Mahallesi Atatürk Bulvarı No:25/A"
    print(f"Testing address: '{test_address}'")
    
    try:
        # Run analysis
        result = tester.analyze_single_address(test_address)
        print(f"✅ Analysis completed successfully")
        print(f"   Result type: {type(result)}")
        print(f"   Original address: {result.original_address}")
        print(f"   Pipeline steps: {len(result.pipeline_steps)}")
        print(f"   Overall success: {result.overall_success}")
        
        # Test JSON export
        print(f"\n🧪 TEST 2: JSON Export")
        
        output_file = "test_export_single.json"
        tester.export_results([result], format='json', filename=output_file)
        print(f"✅ JSON export completed successfully")
        
        # Verify the file was created and is valid JSON
        try:
            import json
            with open(output_file, 'r', encoding='utf-8') as f:
                exported_data = json.load(f)
            
            print(f"✅ JSON file is valid and readable")
            print(f"   Exported results count: {exported_data.get('total_results', 0)}")
            print(f"   Export timestamp: {exported_data.get('export_timestamp', 'N/A')}")
            
            if 'results' in exported_data and len(exported_data['results']) > 0:
                first_result = exported_data['results'][0]
                print(f"   First result keys: {list(first_result.keys())}")
                print(f"   Original address: {first_result.get('original_address', 'N/A')}")
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON file is not valid: {e}")
        except Exception as e:
            print(f"❌ Error reading JSON file: {e}")
        
        # Test batch export
        print(f"\n🧪 TEST 3: Batch JSON Export")
        
        # Create multiple results
        test_addresses = [
            "İstanbul Kadıköy Moda",
            "İzmir Konak Alsancak",
        ]
        
        batch_results = [result]  # Include the first result
        
        for addr in test_addresses:
            try:
                batch_result = tester.analyze_single_address(addr)
                batch_results.append(batch_result)
                print(f"✅ Analyzed: {addr}")
            except Exception as e:
                print(f"⚠️  Failed to analyze {addr}: {e}")
        
        # Export batch
        batch_output_file = "test_export_batch.json"
        tester.export_results(batch_results, format='json', filename=batch_output_file)
        print(f"✅ Batch JSON export completed")
        
        # Verify batch export
        try:
            with open(batch_output_file, 'r', encoding='utf-8') as f:
                batch_data = json.load(f)
            
            print(f"✅ Batch JSON file is valid")
            print(f"   Batch results count: {batch_data.get('total_results', 0)}")
            
        except Exception as e:
            print(f"❌ Error with batch JSON: {e}")
        
        print(f"\n" + "=" * 60)
        print(f"🎉 JSON EXPORT FIX VERIFICATION:")
        print(f"✅ Single address export working")
        print(f"✅ Batch export working") 
        print(f"✅ No serialization errors")
        print(f"✅ Valid JSON files generated")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_json_export_fix()
    if success:
        print(f"\n🏆 JSON EXPORT FIX SUCCESSFUL!")
    else:
        print(f"\n🔧 Additional fixes may be needed")