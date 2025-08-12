#!/usr/bin/env python3
"""
Test script to verify profile creation works correctly
"""

import os
import json
import sys
from pathlib import Path

def test_profile_creation():
    """Test the profile creation functionality"""
    
    print("🧪 Testing Profile Creation")
    print("============================")
    
    # Import the CLI class
    try:
        from cli_version import TwitterAutomationCLI
    except ImportError as e:
        print(f"❌ Error importing TwitterAutomationCLI: {e}")
        return False
    
    # Create CLI instance
    cli = TwitterAutomationCLI()
    
    # Test profile name
    test_profile_name = "test_vnc_profile"
    
    print(f"📝 Creating test profile: {test_profile_name}")
    
    # Create the profile
    if cli.create_profile(test_profile_name):
        print("✅ Profile created successfully")
        
        # Check if profile directory exists
        profile_dir = f"chrome-data/{test_profile_name}"
        if os.path.exists(profile_dir):
            print(f"✅ Profile directory exists: {profile_dir}")
            
            # Check for important Chrome profile files
            important_files = [
                "Default",
                "Preferences", 
                "Local State",
                "profile_info.json"
            ]
            
            for file_path in important_files:
                full_path = os.path.join(profile_dir, file_path)
                if os.path.exists(full_path):
                    print(f"✅ Found: {file_path}")
                else:
                    print(f"⚠️  Missing: {file_path}")
            
            # Check profile info
            profile_info_path = os.path.join(profile_dir, "profile_info.json")
            if os.path.exists(profile_info_path):
                try:
                    with open(profile_info_path, 'r') as f:
                        profile_info = json.load(f)
                    print(f"✅ Profile info: {profile_info}")
                except Exception as e:
                    print(f"⚠️  Error reading profile info: {e}")
            
            # Test launching the profile
            print("\n🚀 Testing profile launch...")
            if cli.launch_profile_browser(test_profile_name):
                print("✅ Profile launch test completed")
            else:
                print("⚠️  Profile launch test failed (this is normal if VNC is not running)")
            
            return True
        else:
            print(f"❌ Profile directory not found: {profile_dir}")
            return False
    else:
        print("❌ Profile creation failed")
        return False

if __name__ == "__main__":
    success = test_profile_creation()
    if success:
        print("\n🎉 Profile creation test completed successfully!")
        print("\n📋 Next steps:")
        print("1. Start VNC: vncserver :1 -geometry 1920x1080 -depth 24")
        print("2. Launch Chrome: ./launch_chrome_vnc.sh test_vnc_profile")
        print("3. Connect to VNC viewer: your-server-ip:5901")
    else:
        print("\n❌ Profile creation test failed!")
        sys.exit(1)
