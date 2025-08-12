#!/bin/bash

# Chrome VNC Launcher Script
# This script helps you launch Chrome with VNC support on a headless Linux machine

set -e

echo "🖥️  Chrome VNC Launcher"
echo "========================"

# Check if we're on Linux
if [ "$(uname)" != "Linux" ]; then
    echo "❌ This script is designed for Linux systems"
    exit 1
fi

# Check if VNC is running
echo "🔍 Checking VNC status..."
if ! pgrep -f "vncserver.*:1" > /dev/null; then
    echo "⚠️  VNC server not running on display :1"
    echo "Starting VNC server..."
    vncserver :1 -geometry 1920x1080 -depth 24
    sleep 2
else
    echo "✅ VNC server is running on display :1"
fi

# Set display environment variable
export DISPLAY=:1
echo "📺 Set DISPLAY to :1"

# Check if Chrome is installed
if ! command -v google-chrome &> /dev/null; then
    echo "❌ Google Chrome not found"
    echo "Please install Chrome first:"
    echo "  sudo apt update && sudo apt install -y google-chrome-stable"
    exit 1
fi

echo "✅ Chrome found: $(google-chrome --version)"

# Check if we have a profile name
if [ -z "$1" ]; then
    echo "📝 Usage: $0 <profile_name>"
    echo ""
    echo "Available profiles:"
    if [ -d "chrome-data" ]; then
        ls -1 chrome-data/ 2>/dev/null || echo "No profiles found"
    else
        echo "No profiles directory found"
    fi
    echo ""
    echo "To create a new profile:"
    echo "  ./run_cli.sh --create-profile <profile_name>"
    exit 1
fi

PROFILE_NAME="$1"
PROFILE_DIR="chrome-data/$PROFILE_NAME"

# Check if profile exists
if [ ! -d "$PROFILE_DIR" ]; then
    echo "❌ Profile '$PROFILE_NAME' not found"
    echo "Creating profile..."
    mkdir -p "$PROFILE_DIR"
    echo "✅ Profile directory created: $PROFILE_DIR"
fi

echo "🚀 Launching Chrome with profile: $PROFILE_NAME"
echo "📁 Profile directory: $PROFILE_DIR"

# Launch Chrome with the profile
google-chrome \
    --user-data-dir="$(pwd)/$PROFILE_DIR" \
    --no-first-run \
    --no-default-browser-check \
    --disable-default-apps \
    --disable-popup-blocking \
    --disable-notifications \
    --start-maximized \
    --allow-running-insecure-content \
    --disable-features=TranslateUI \
    --disable-ipc-flooding-protection \
    --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
    "https://x.com" &

CHROME_PID=$!
echo "✅ Chrome launched with PID: $CHROME_PID"
echo ""
echo "🎯 Next steps:"
echo "1. Check your VNC viewer to see the Chrome window"
echo "2. Navigate to Twitter and log in"
echo "3. Close Chrome when done (Ctrl+C in this terminal)"
echo ""
echo "🔧 VNC Connection Info:"
echo "  - Server: $(hostname -I | awk '{print $1}'):5901"
echo "  - Display: :1"
echo "  - Password: (the one you set with vncpasswd)"
echo ""
echo "Press Ctrl+C to stop Chrome..."

# Wait for user to stop
trap "echo ''; echo '🛑 Stopping Chrome...'; kill $CHROME_PID 2>/dev/null; echo '✅ Chrome stopped'; exit 0" INT

# Keep script running
wait $CHROME_PID
