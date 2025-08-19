#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo script to test the interactive_test.py functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from interactive_test import InteractiveAddressTester

def demo_test():
    """Demonstrate the interactive tester functionality"""
    print("🧪 Testing Interactive Address Tester Demo")
    print("=" * 50)
    
    # Create tester instance
    tester = InteractiveAddressTester()
    
    # Test addresses
    test_addresses = [
        "istanbul kadikoy moda mh",
        "ankara cankaya kizilay",
        "izmir konak alsancak mh"
    ]
    
    for i, address in enumerate(test_addresses, 1):
        print(f"\n🔬 Demo Test {i}/{len(test_addresses)}")
        tester.process_address_step_by_step(address)
        print("\n" + "🔸" * 50)
    
    print("\n✅ Demo completed successfully!")
    print("To run interactively: python3 interactive_test.py")

if __name__ == "__main__":
    demo_test()