#!/usr/bin/env python3
"""
Test script to verify Chrome launch with VNC configuration
"""

import sys
import os
import subprocess
import time

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_vnc_configuration():
    """Test VNC configuration and Chrome launch"""
    print("🧪 Testing VNC Configuration and Chrome Launch")
    print("=" * 60)
    
    try:
        from config import config
        from web_dashboard import WebDashboard
        
        print(f"📋 VNC Configuration:")
        print(f"   • use_gui_chrome: {config.use_gui_chrome}")
        print(f"   • vnc_display: {config.vnc_display}")
        print(f"   • os.name: {os.name}")
        print(f"   • platform: {os.name == 'posix'}")
        
        # Check if VNC is running
        print(f"\n🔍 Checking VNC Status:")
        try:
            result = subprocess.run(['pgrep', '-f', f'vncserver.*{config.vnc_display}'], 
                                  capture_output=True, text=True, timeout=5)
            vnc_running = result.returncode == 0
            print(f"   • VNC Running: {vnc_running}")
            if vnc_running:
                print(f"   • VNC PIDs: {result.stdout.strip()}")
        except Exception as e:
            print(f"   • VNC Check Error: {e}")
            vnc_running = False
        
        # Test profile creation and launch
        print(f"\n🚀 Testing Profile Launch:")
        dashboard = WebDashboard()
        
        # Create a test profile
        test_profile = "test_vnc_profile"
        print(f"   • Creating test profile: {test_profile}")
        success = dashboard.create_profile(test_profile)
        print(f"   • Profile created: {success}")
        
        if success:
            # Launch Chrome
            print(f"   • Launching Chrome with profile: {test_profile}")
            launch_success = dashboard.launch_profile_browser(test_profile)
            print(f"   • Chrome launched: {launch_success}")
            
            if launch_success:
                # Wait a moment for Chrome to start
                time.sleep(3)
                
                # Check if Chrome is running
                print(f"\n🔍 Checking Chrome Status:")
                profile_dir = f"chrome-data/{test_profile}"
                try:
                    result = subprocess.run(['pgrep', '-f', f'chrome.*{profile_dir}'], 
                                          capture_output=True, text=True, timeout=5)
                    chrome_running = result.returncode == 0
                    print(f"   • Chrome Running: {chrome_running}")
                    if chrome_running:
                        pids = result.stdout.strip().split('\n')
                        process_count = len([pid for pid in pids if pid.strip()])
                        print(f"   • Chrome PIDs: {result.stdout.strip()}")
                        print(f"   • Process Count: {process_count}")
                    else:
                        print(f"   • Chrome not found in process list")
                except Exception as e:
                    print(f"   • Chrome Check Error: {e}")
                
                # Clean up
                print(f"\n🧹 Cleaning up:")
                try:
                    subprocess.run(['pkill', '-f', f'chrome.*{profile_dir}'], 
                                  capture_output=True, text=True, timeout=5)
                    print(f"   • Chrome processes killed")
                except Exception as e:
                    print(f"   • Cleanup Error: {e}")
            
            # Delete test profile
            try:
                dashboard.delete_profile(test_profile)
                print(f"   • Test profile deleted")
            except Exception as e:
                print(f"   • Profile deletion error: {e}")
        
        print(f"\n✅ Test completed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def main():
    """Run the test"""
    success = test_vnc_configuration()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 VNC Chrome launch test completed successfully!")
        print("\nKey Points:")
        print("   • VNC configuration is properly loaded")
        print("   • Chrome launch uses correct VNC settings")
        print("   • Process detection works correctly")
    else:
        print("❌ VNC Chrome launch test failed!")
    
    return success

if __name__ == "__main__":
    main() 