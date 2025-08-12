#!/usr/bin/env python3
"""
Test script for VNC support
"""

import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cli_version import TweetScraper, ProfileManager
from config import config
from vnc_checker import check_vnc_running, verify_vnc_environment

def test_vnc_support():
    """Test VNC support and GUI Chrome"""
    print("=== Testing VNC Support ===")
    
    # Check if we're on Linux
    if os.name != 'posix':
        print("❌ VNC support is only available on Linux")
        print("Current platform:", os.name)
        return
    
    # Check VNC environment
    print("\n1. Checking VNC Environment...")
    env_ready, env_error = verify_vnc_environment(config.vnc_display)
    if env_ready:
        print("✅ VNC environment is properly configured")
    else:
        print(f"❌ VNC environment issue: {env_error}")
        print("\nPlease follow the setup instructions in README.md (VNC Support section)")
        return
    
    # Check if VNC is running
    print("\n2. Checking VNC Server...")
    vnc_running, error = check_vnc_running(config.vnc_display)
    if vnc_running:
        print("✅ VNC server is running")
    else:
        print(f"❌ VNC server issue: {error}")
        print("\nPlease start the VNC server:")
        print("  vncserver :1")
        return
    
    # Test profile manager
    print("\n3. Testing Profile Manager...")
    profile_manager = ProfileManager()
    profiles = profile_manager.get_all_profiles()
    print(f"Found {len(profiles)} profiles: {profiles}")
    
    # Create a test profile if none exists
    if not profiles:
        print("Creating test profile...")
        profile_manager.add_profile("test_profile", "chrome-data/test_profile")
        profiles = ["test_profile"]
    
    profile_name = profiles[0] if profiles else "test_profile"
    print(f"Using profile: {profile_name}")
    
    # Initialize scraper with GUI mode
    print("\n4. Testing Chrome in GUI Mode...")
    scraper = TweetScraper(profile_name)
    print("Setting up Chrome driver with GUI support...")
    
    if scraper.setup_driver(use_gui=True, display=config.vnc_display):
        print("✅ Chrome driver initialized successfully in GUI mode")
        
        # Test opening a URL
        test_url = "https://twitter.com"
        print(f"\n5. Testing browser visibility (opening {test_url})...")
        try:
            scraper.driver.get(test_url)
            print("✅ Browser window should be visible in VNC session")
            print("Please check your VNC viewer to see the Chrome window")
            
            # Wait for user confirmation
            input("\nPress Enter after verifying the browser is visible...")
            
        except Exception as e:
            print(f"❌ Error opening URL: {e}")
        
        scraper.cleanup()
        print("\n6. Browser closed")
    else:
        print("❌ Failed to initialize Chrome driver in GUI mode")
    
    print("\n=== Test completed ===")
    print("\nNext steps:")
    print("1. If all tests passed, the VNC support is working correctly")
    print("2. You can now use GUI Chrome via VNC in the main application")
    print("3. Configure VNC settings in the web dashboard")
    print("4. Follow README.md (VNC Support section) for usage instructions")

if __name__ == "__main__":
    test_vnc_support()
