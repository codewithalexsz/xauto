#!/usr/bin/env python3
"""
Debug script to test Chrome launch directly
"""

import sys
import os
import subprocess
import time

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_chrome_launch():
    """Debug Chrome launch process"""
    print("🔍 Debugging Chrome Launch Process")
    print("=" * 50)
    
    try:
        from config import config
        from web_dashboard import WebDashboard
        
        print(f"📋 Current Configuration:")
        print(f"   • use_gui_chrome: {config.use_gui_chrome}")
        print(f"   • vnc_display: {config.vnc_display}")
        print(f"   • os.name: {os.name}")
        
        # Check VNC status
        print(f"\n🔍 VNC Status Check:")
        try:
            # More comprehensive VNC detection
            vnc_running = False
            vnc_patterns = [
                f'vncserver.*{config.vnc_display}',
                f'Xtightvnc.*{config.vnc_display}',
                f'tightvncserver.*{config.vnc_display}',
                f'tigervncserver.*{config.vnc_display}',
                f'x11vnc.*{config.vnc_display}',
                f'vnc.*{config.vnc_display}'
            ]
            
            for pattern in vnc_patterns:
                try:
                    result = subprocess.run(['pgrep', '-f', pattern], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        vnc_running = True
                        print(f"   • VNC Running: {vnc_running} (pattern: {pattern})")
                        print(f"   • VNC PIDs: {result.stdout.strip()}")
                        break
                except Exception:
                    continue
            
            if not vnc_running:
                print(f"   • VNC Running: {vnc_running}")
                
        except Exception as e:
            print(f"   • VNC Check Error: {e}")
        
        # Check if profile exists
        profile_name = "shrekarb"
        profile_dir = f"chrome-data/{profile_name}"
        print(f"\n📁 Profile Check:")
        print(f"   • Profile: {profile_name}")
        print(f"   • Profile dir: {profile_dir}")
        print(f"   • Profile exists: {os.path.exists(profile_dir)}")
        
        if not os.path.exists(profile_dir):
            print(f"   ❌ Profile directory does not exist!")
            return False
        
        # Test Chrome launch with detailed output
        print(f"\n🚀 Testing Chrome Launch:")
        dashboard = WebDashboard()
        
        # Try to launch Chrome
        print(f"   • Attempting to launch Chrome...")
        success = dashboard.launch_profile_browser(profile_name)
        print(f"   • Launch result: {success}")
        
        if success:
            # Wait and check for processes
            print(f"\n⏳ Waiting 5 seconds for Chrome to start...")
            time.sleep(5)
            
            print(f"\n🔍 Process Check:")
            try:
                result = subprocess.run(['pgrep', '-f', f'chrome.*{profile_dir}'], 
                                      capture_output=True, text=True, timeout=5)
                chrome_running = result.returncode == 0
                print(f"   • Chrome Running: {chrome_running}")
                if chrome_running:
                    pids = result.stdout.strip().split('\n')
                    print(f"   • Chrome PIDs: {result.stdout.strip()}")
                    print(f"   • Process Count: {len([pid for pid in pids if pid.strip()])}")
                else:
                    print(f"   • Chrome not found in process list")
                    
                    # Check for any Chrome processes
                    print(f"\n🔍 Checking for any Chrome processes:")
                    result = subprocess.run(['pgrep', '-f', 'chrome'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        print(f"   • Other Chrome processes: {result.stdout.strip()}")
                    else:
                        print(f"   • No Chrome processes found")
                        
            except Exception as e:
                print(f"   • Process check error: {e}")
            
            # Clean up
            print(f"\n🧹 Cleaning up:")
            try:
                subprocess.run(['pkill', '-f', f'chrome.*{profile_dir}'], 
                              capture_output=True, text=True, timeout=5)
                print(f"   • Chrome processes killed")
            except Exception as e:
                print(f"   • Cleanup error: {e}")
        else:
            print(f"   ❌ Chrome launch failed!")
        
        return success
        
    except Exception as e:
        print(f"❌ Debug error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the debug"""
    success = debug_chrome_launch()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Chrome launch debug completed")
    else:
        print("❌ Chrome launch debug failed")
    
    return success

if __name__ == "__main__":
    main() 