#!/usr/bin/env python3
"""
Test script to verify VNC checking consistency
"""

import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_vnc_consistency():
    """Test that all VNC checking methods return consistent results"""
    print("=== Testing VNC Checking Consistency ===")
    
    try:
        from vnc_checker import check_vnc_running, check_vnc_running_simple, get_vnc_status
        from config import config
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return
    
    display = config.vnc_display
    print(f"Testing VNC status on display: {display}")
    
    # Test 1: Simple method
    print("\n1. Testing simple VNC check...")
    simple_running, simple_error = check_vnc_running_simple(display)
    print(f"   Simple check: Running={simple_running}, Error={simple_error}")
    
    # Test 2: Comprehensive method
    print("\n2. Testing comprehensive VNC check...")
    comp_running, comp_error = check_vnc_running(display)
    print(f"   Comprehensive check: Running={comp_running}, Error={comp_error}")
    
    # Test 3: Status method
    print("\n3. Testing VNC status method...")
    status = get_vnc_status(display)
    print(f"   Status check: Running={status['running']}, Errors={status['errors']}")
    
    # Check consistency
    print("\n4. Checking consistency...")
    methods = [
        ("Simple", simple_running),
        ("Comprehensive", comp_running),
        ("Status", status['running'])
    ]
    
    all_same = all(method[1] == methods[0][1] for method in methods)
    
    if all_same:
        print("✅ All VNC checking methods return consistent results!")
        print(f"   VNC server is {'running' if simple_running else 'not running'}")
    else:
        print("❌ VNC checking methods are inconsistent!")
        for name, running in methods:
            print(f"   {name}: {'running' if running else 'not running'}")
    
    # Show detailed status if VNC is running
    if status['running'] and status['processes']:
        print("\n5. VNC Process Details:")
        for process in status['processes']:
            print(f"   {process}")
    
    print("\n=== Test completed ===")

if __name__ == "__main__":
    test_vnc_consistency() 