#!/usr/bin/env python3
"""
Simple VNC test script
"""

import os
import subprocess
import sys

def check_vnc_status():
    """Check if VNC is running"""
    print("🔍 Checking VNC status...")
    
    # Check if VNC server is running
    try:
        result = subprocess.run(['pgrep', '-f', 'vncserver.*:1'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ VNC server is running on display :1")
            return True
        else:
            print("❌ VNC server not running on display :1")
            return False
    except Exception as e:
        print(f"❌ Error checking VNC: {e}")
        return False

def check_display():
    """Check if DISPLAY is set"""
    print("📺 Checking DISPLAY environment...")
    
    display = os.environ.get('DISPLAY')
    if display:
        print(f"✅ DISPLAY is set to: {display}")
        return True
    else:
        print("❌ DISPLAY not set")
        return False

def check_chrome():
    """Check if Chrome is installed"""
    print("🌐 Checking Chrome installation...")
    
    try:
        result = subprocess.run(['google-chrome', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Chrome found: {version}")
            return True
        else:
            print("❌ Chrome not found")
            return False
    except Exception as e:
        print(f"❌ Error checking Chrome: {e}")
        return False

def test_chrome_launch():
    """Test launching Chrome with VNC"""
    print("🚀 Testing Chrome launch...")
    
    # Set display
    os.environ['DISPLAY'] = ':1'
    
    try:
        # Launch Chrome in background
        cmd = [
            'google-chrome',
            '--user-data-dir=/tmp/test_chrome_vnc',
            '--no-first-run',
            '--no-default-browser-check',
            '--disable-default-apps',
            '--disable-popup-blocking',
            '--disable-notifications',
            '--start-maximized',
            '--disable-web-security',
            '--allow-running-insecure-content',
            '--disable-features=TranslateUI',
            '--disable-ipc-flooding-protection',
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'https://twitter.com'
        ]
        
        process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"✅ Chrome launched with PID: {process.pid}")
        
        # Wait a bit for Chrome to start
        import time
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Chrome is running successfully")
            print("🎯 Check your VNC viewer to see the Chrome window")
            
            # Ask user to confirm
            input("\nPress Enter after verifying Chrome is visible in VNC...")
            
            # Stop Chrome
            process.terminate()
            process.wait()
            print("✅ Chrome stopped")
            return True
        else:
            print("❌ Chrome failed to start")
            return False
            
    except Exception as e:
        print(f"❌ Error launching Chrome: {e}")
        return False

def main():
    """Main test function"""
    print("🖥️  Simple VNC Test")
    print("==================")
    
    # Check if we're on Linux
    if os.name != 'posix':
        print("❌ This test is designed for Linux systems")
        return
    
    # Run checks
    vnc_ok = check_vnc_status()
    display_ok = check_display()
    chrome_ok = check_chrome()
    
    print("\n📊 Test Results:")
    print(f"  VNC Server: {'✅' if vnc_ok else '❌'}")
    print(f"  DISPLAY: {'✅' if display_ok else '❌'}")
    print(f"  Chrome: {'✅' if chrome_ok else '❌'}")
    
    if not vnc_ok:
        print("\n🔧 To start VNC server:")
        print("  vncserver :1")
        return
    
    if not display_ok:
        print("\n🔧 To set DISPLAY:")
        print("  export DISPLAY=:1")
        return
    
    if not chrome_ok:
        print("\n🔧 To install Chrome:")
        print("  sudo apt update && sudo apt install -y google-chrome-stable")
        return
    
    # All checks passed, test Chrome launch
    print("\n🎯 All checks passed! Testing Chrome launch...")
    test_chrome_launch()
    
    print("\n✅ VNC test completed!")

if __name__ == "__main__":
    main()
