#!/usr/bin/env python3
"""
VNC Diagnostic Script
Helps identify and fix VNC issues
"""

import os
import subprocess
import sys
import json
from pathlib import Path

def check_vnc_installation():
    """Check if VNC is properly installed"""
    print("🔍 Checking VNC Installation")
    print("============================")
    
    # Check if vncserver command exists
    try:
        result = subprocess.run(['which', 'vncserver'], capture_output=True, text=True)
        if result.returncode == 0:
            vnc_path = result.stdout.strip()
            print(f"✅ VNC server found at: {vnc_path}")
            
            # Check version
            try:
                version_result = subprocess.run(['vncserver', '-version'], 
                                              capture_output=True, text=True, timeout=5)
                if version_result.returncode == 0:
                    print(f"📋 VNC version: {version_result.stdout.strip()}")
                else:
                    print("⚠️  Could not get VNC version")
            except:
                print("⚠️  Could not get VNC version")
        else:
            print("❌ VNC server not found")
            print("💡 Install VNC with: sudo apt install -y tightvncserver")
            return False
    except Exception as e:
        print(f"❌ Error checking VNC installation: {e}")
        return False
    
    return True

def check_vnc_environment():
    """Check VNC environment setup"""
    print("\n🔍 Checking VNC Environment")
    print("============================")
    
    # Check if XFCE is installed
    try:
        result = subprocess.run(['which', 'startxfce4'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ XFCE4 found")
        else:
            print("⚠️  XFCE4 not found")
            print("💡 Install XFCE4 with: sudo apt install -y xfce4 xfce4-goodies")
    except Exception as e:
        print(f"⚠️  Error checking XFCE4: {e}")
    
    # Check VNC startup script
    vnc_startup_dir = os.path.expanduser("~/.vnc")
    vnc_startup_file = os.path.join(vnc_startup_dir, "xstartup")
    
    if os.path.exists(vnc_startup_file):
        print(f"✅ VNC startup script found: {vnc_startup_file}")
        
        # Check if it's executable
        if os.access(vnc_startup_file, os.X_OK):
            print("✅ VNC startup script is executable")
        else:
            print("⚠️  VNC startup script is not executable")
            print("💡 Fix with: chmod +x ~/.vnc/xstartup")
    else:
        print(f"⚠️  VNC startup script not found: {vnc_startup_file}")
        print("💡 Creating VNC startup script...")
        
        try:
            os.makedirs(vnc_startup_dir, exist_ok=True)
            startup_content = """#!/bin/bash
xrdb $HOME/.Xresources
startxfce4 &
"""
            with open(vnc_startup_file, 'w') as f:
                f.write(startup_content)
            os.chmod(vnc_startup_file, 0o755)
            print("✅ VNC startup script created")
        except Exception as e:
            print(f"❌ Error creating VNC startup script: {e}")
    
    return True

def check_vnc_status():
    """Check if VNC is currently running"""
    print("\n🔍 Checking VNC Status")
    print("======================")
    
    try:
        result = subprocess.run(['pgrep', '-f', 'vncserver.*:1'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ VNC server is running on display :1")
            
            # Get VNC process info
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    try:
                        ps_result = subprocess.run(['ps', '-p', pid, '-o', 'pid,ppid,cmd'], 
                                                 capture_output=True, text=True)
                        if ps_result.returncode == 0:
                            print(f"📋 Process {pid}: {ps_result.stdout.strip()}")
                    except:
                        pass
        else:
            print("⚠️  VNC server is not running")
            return False
    except Exception as e:
        print(f"❌ Error checking VNC status: {e}")
        return False
    
    return True

def test_vnc_start():
    """Test starting VNC server"""
    print("\n🚀 Testing VNC Start")
    print("====================")
    
    # Check if already running
    if check_vnc_status():
        print("✅ VNC is already running")
        return True
    
    print("🔄 Starting VNC server...")
    try:
        result = subprocess.run([
            'vncserver', ':1', 
            '-geometry', '1920x1080', 
            '-depth', '24',
            '-localhost', 'no'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ VNC server started successfully")
            print(f"📋 Output: {result.stdout}")
            return True
        else:
            print("❌ Failed to start VNC server")
            print(f"📋 Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ VNC server startup timed out")
        return False
    except Exception as e:
        print(f"❌ Error starting VNC server: {e}")
        return False

def test_vnc_connection():
    """Test VNC connection"""
    print("\n🔗 Testing VNC Connection")
    print("=========================")
    
    if not check_vnc_status():
        print("⚠️  VNC is not running, cannot test connection")
        return False
    
    # Get server IP
    try:
        import socket
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        print(f"🌐 Server IP: {ip_address}")
        print(f"🔗 VNC Connection: {ip_address}:5901")
        print(f"📺 Display: :1")
        print("💡 Use a VNC viewer to connect to the above address")
        return True
    except Exception as e:
        print(f"❌ Error getting server IP: {e}")
        return False

def main():
    """Main diagnostic function"""
    print("🖥️  VNC Diagnostic Tool")
    print("=======================")
    
    # Check if running on Linux
    if os.name != 'posix':
        print("❌ This script is designed for Linux systems")
        sys.exit(1)
    
    # Run diagnostics
    vnc_installed = check_vnc_installation()
    if not vnc_installed:
        print("\n❌ VNC is not properly installed")
        print("💡 Please install VNC first:")
        print("   sudo apt update")
        print("   sudo apt install -y tightvncserver xfce4 xfce4-goodies")
        sys.exit(1)
    
    check_vnc_environment()
    
    if test_vnc_start():
        test_vnc_connection()
        print("\n🎉 VNC diagnostic completed successfully!")
        print("\n📋 Next steps:")
        print("1. Connect to VNC: your-server-ip:5901")
        print("2. Launch Chrome: ./launch_chrome_vnc.sh your_profile_name")
        print("3. Or use the web dashboard to manage profiles")
    else:
        print("\n❌ VNC diagnostic failed")
        print("💡 Please check the error messages above")

if __name__ == "__main__":
    main()
