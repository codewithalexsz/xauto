#!/bin/bash
# Twitter Automation Web Dashboard Launcher with VNC Support

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run install.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if required files exist
if [ ! -f "web_dashboard.py" ]; then
    echo "❌ web_dashboard.py not found"
    exit 1
fi

if [ ! -f "cli_version.py" ]; then
    echo "❌ cli_version.py not found"
    exit 1
fi

# Function to start VNC server
start_vnc_server() {
    echo "🖥️  Starting VNC server..."
    
    # Check if VNC is already running (check for various VNC server types)
    if pgrep -f "vncserver.*:1" > /dev/null || pgrep -f "Xtightvnc.*:1" > /dev/null || pgrep -f "tightvncserver.*:1" > /dev/null; then
        echo "✅ VNC server is already running on display :1"
    else
        echo "🚀 Starting VNC server on display :1..."
        
        # Check if VNC startup script exists
        if [ ! -f ~/.vnc/xstartup ]; then
            echo "📝 Creating VNC startup script..."
            mkdir -p ~/.vnc
            cat > ~/.vnc/xstartup << 'VNC_EOF'
#!/bin/bash
xrdb $HOME/.Xresources
startxfce4 &
VNC_EOF
            chmod +x ~/.vnc/xstartup
        fi
        
        # Start VNC server
        vncserver :1 -geometry 1920x1080 -depth 24 > /dev/null 2>&1
        
        if [ $? -eq 0 ]; then
            echo "✅ VNC server started successfully on display :1"
        else
            echo "⚠️  Failed to start VNC server. You may need to set a password first:"
            echo "   vncpasswd"
            echo "   Then run: vncserver :1"
        fi
    fi
}

# Function to stop VNC server
stop_vnc_server() {
    echo ""
    echo "🛑 Stopping VNC server..."
    vncserver -kill :1 > /dev/null 2>&1
    echo "✅ VNC server stopped"
}

# Start VNC server
start_vnc_server

# Get IP address
IP_ADDRESS=$(hostname -I | awk '{print $1}')

echo ""
echo "🚀 Starting Twitter Automation Web Dashboard"
echo "=============================================="
echo "📊 Dashboard will be available at:"
echo "   Local:  http://localhost:5000"
echo "   Remote: http://$IP_ADDRESS:5000"
echo ""
echo "🖥️  VNC Connection Info:"
echo "   Server: $IP_ADDRESS:5901"
echo "   Display: :1"
echo "   Password: (the one you set with vncpasswd)"
echo ""
echo "🔧 Press Ctrl+C to stop the dashboard and VNC server"
echo ""

# Set up trap to stop VNC server when script exits
trap 'stop_vnc_server; exit 0' INT TERM

# Start the dashboard
python3 web_dashboard.py --host 0.0.0.0 --port 5000
