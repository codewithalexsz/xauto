#!/bin/bash

# Twitter Automation Complete Installation Script
# This script sets up the complete Twitter automation environment

set -e

echo "🚀 Twitter Automation Complete Installation Script"
echo "=================================================="
echo "This script will install all components needed for the Twitter automation system"
echo ""



# Detect Linux distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
else
    echo "❌ Could not detect Linux distribution"
    exit 1
fi

echo "📋 Detected OS: $OS $VER"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install packages based on distribution
install_packages() {
    local packages=("$@")
    
    if command_exists apt-get; then
        echo "📦 Installing packages using apt-get..."
        sudo apt-get update
        sudo apt-get install -y "${packages[@]}"
    elif command_exists yum; then
        echo "📦 Installing packages using yum..."
        sudo yum update -y
        sudo yum install -y "${packages[@]}"
    elif command_exists dnf; then
        echo "📦 Installing packages using dnf..."
        sudo dnf update -y
        sudo dnf install -y "${packages[@]}"
    else
        echo "❌ No supported package manager found"
        exit 1
    fi
}

# Function to install Chrome
install_chrome() {
    echo "🌐 Installing Google Chrome..."
    
    if command_exists google-chrome; then
        echo "✅ Chrome already installed"
        return
    fi
    
    if command_exists apt-get; then
        # Ubuntu/Debian
        wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
        echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
        sudo apt-get update
        sudo apt-get install -y google-chrome-stable
    elif command_exists yum; then
        # CentOS/RHEL
        sudo yum install -y wget
        wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo rpm --import -
        sudo yum install -y https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
    elif command_exists dnf; then
        # Fedora
        sudo dnf install -y wget
        wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo rpm --import -
        sudo dnf install -y https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
    fi
    
    echo "✅ Chrome installed successfully"
}

# Function to install ChromeDriver

install_chromedriver() {
    echo "🔧 Installing ChromeDriver..."

    if command -v chromedriver &> /dev/null; then
        echo "✅ ChromeDriver already installed"
        return
    fi

    # Get Chrome full version (e.g., 140.0.7339.207)
    CHROME_VERSION=$(google-chrome --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    echo "📋 Chrome version: $CHROME_VERSION"

    # Set platform
    PLATFORM="linux64"

    # Build download URL
    CHROMEDRIVER_URL="https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/${PLATFORM}/chromedriver-${PLATFORM}.zip"
    echo "📥 Downloading from: $CHROMEDRIVER_URL"

    # Download and install
    sudo wget -q -O /tmp/chromedriver.zip "$CHROMEDRIVER_URL"
    sudo unzip -o /tmp/chromedriver.zip -d /tmp/
    sudo mv /tmp/chromedriver-${PLATFORM}/chromedriver /usr/local/bin/
    sudo chmod +x /usr/local/bin/chromedriver

    echo "✅ ChromeDriver installed successfully"
}


# Function to install VNC server
install_vnc() {
    echo "🖥️ Installing VNC Server..."
    
    if command_exists vncserver; then
        echo "✅ VNC server already installed"
        return
    fi
    
    if command_exists apt-get; then
        # Ubuntu/Debian
        sudo apt-get install -y tightvncserver xfce4 xfce4-goodies
    elif command_exists yum; then
        # CentOS/RHEL
        sudo yum install -y tigervnc-server tigervnc-server-module xfce4
    elif command_exists dnf; then
        # Fedora
        sudo dnf install -y tigervnc-server tigervnc-server-module xfce4
    fi
    
    echo "✅ VNC server installed successfully"
}

# Function to setup VNC environment
setup_vnc() {
    echo "⚙️ Setting up VNC environment..."
    
    # Create VNC directory
    mkdir -p ~/.vnc
    
    # Create xstartup file
    cat > ~/.vnc/xstartup << 'EOF'
#!/bin/bash
xrdb $HOME/.Xresources
startxfce4 &
EOF
    
    chmod +x ~/.vnc/xstartup
    
    echo "✅ VNC environment configured"
}

# Function to install Python dependencies
install_python_deps() {
    echo "🐍 Installing Python dependencies..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        echo "📦 Installing requirements from requirements.txt..."
        pip install -r requirements.txt --break-system-packages
    else
        echo "📦 Installing core dependencies..."
        pip install selenium webdriver-manager flask flask-socketio requests beautifulsoup4 lxml psutil
    fi
    
    echo "✅ Python dependencies installed"
}

# Function to create necessary directories
create_directories() {
    echo "📁 Creating necessary directories..."
    
    mkdir -p app/state
    mkdir -p app/config
    mkdir -p chrome-data
    mkdir -p logs
    mkdir -p templates
    
    echo "✅ Directories created"
}

# Function to set permissions
set_permissions() {
    echo "🔐 Setting permissions..."
    
    chmod +x web_dashboard.py
    chmod +x cli_version.py
    chmod +x run_dashboard.sh
    chmod +x run_cli.sh
    chmod +x launch_chrome_vnc.sh
    
    echo "✅ Permissions set"
}

# Function to create launcher scripts
create_launchers() {
    echo "🚀 Creating launcher scripts..."
    
    # Dashboard launcher
    cat > run_dashboard.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python3 web_dashboard.py --host 0.0.0.0 --port 5000
EOF
    
    # CLI launcher
    cat > run_cli.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python3 cli_version.py "$@"
EOF
    
    # Chrome VNC launcher
    cat > launch_chrome_vnc.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python3 web_dashboard.py --host 0.0.0.0 --port 5000
EOF
    
    chmod +x run_dashboard.sh run_cli.sh launch_chrome_vnc.sh
    
    echo "✅ Launcher scripts created"
}

# Function to create systemd services
create_services() {
    echo "🔧 Creating systemd services..."
    
    # VNC service
    sudo tee /etc/systemd/system/vnc-server.service > /dev/null << EOF
[Unit]
Description=VNC Server
After=network.target

[Service]
Type=forking
User=$USER
WorkingDirectory=/home/$USER
ExecStart=/usr/bin/vncserver :1 -geometry 1920x1080 -depth 24
ExecStop=/usr/bin/vncserver -kill :1
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF
    
    # Twitter automation service
    sudo tee /etc/systemd/system/twitter-automation.service > /dev/null << EOF
[Unit]
Description=Twitter Automation Dashboard
After=network.target vnc-server.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/run_dashboard.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd
    sudo systemctl daemon-reload
    
    echo "✅ Systemd services created"
    echo "   To enable services:"
    echo "   sudo systemctl enable vnc-server.service"
    echo "   sudo systemctl enable twitter-automation.service"
}

# Function to display final instructions
show_final_instructions() {
    echo ""
    echo "🎉 Installation completed successfully!"
    echo "======================================"
    echo ""
    echo "📋 Next steps:"
    echo "1. Start VNC server:"
    echo "   vncserver :1 -geometry 1920x1080 -depth 24 "
    echo ""
    echo "2. Start the dashboard:"
    echo "   ./run_dashboard.sh"
    echo ""
    echo "3. Access the dashboard:"
    echo "   http://localhost:5000"
    echo ""
    echo "4. Connect to VNC (optional):"
    echo "   Use a VNC viewer to connect to MCHINE_IP:5901"
    echo ""
    echo "📁 Important directories:"
    echo "   • Chrome profiles: ./chrome-data/"
    echo "   • Application state: ./app/state/"
    echo "   • Logs: ./logs/"
    echo ""
    echo "🔧 Useful commands:"
    echo "   • Start dashboard: ./run_dashboard.sh"
    echo "   • CLI interface: ./run_cli.sh --help"
    echo "   • Stop VNC: vncserver -kill :1"
    echo ""
    echo "📚 Documentation:"
    echo "   • README.md - Complete usage guide"
    echo "   • VNC_SETUP_GUIDE.md - VNC configuration"
    echo ""
}

# Main installation process
main() {
    echo "🚀 Starting installation process..."
    echo ""
    
    # Update package list
    echo "📦 Updating package list..."
    if command_exists apt-get; then
        sudo apt-get update
    elif command_exists yum; then
        sudo yum update -y
    elif command_exists dnf; then
        sudo dnf update -y
    fi
    echo ""
    
    # Install system dependencies
    echo "🔧 Installing system dependencies..."
    SYSTEM_PACKAGES=(
        "python3"
        "python3-pip"
        "python3-venv"
        "wget"
        "curl"
        "unzip"
        "build-essential"
        "libssl-dev"
        "libffi-dev"
        "python3-dev"
        "gnupg"
        "git"
    )
    install_packages "${SYSTEM_PACKAGES[@]}"
    echo ""
    
    # Install Chrome
    install_chrome
    echo ""
    
    # Install ChromeDriver
    install_chromedriver
    echo ""
    
    # Install VNC server
    install_vnc
    echo ""
    
    # Setup VNC environment
    setup_vnc
    echo ""
    
    # Create directories
    create_directories
    echo ""
    
    # Install Python dependencies
    install_python_deps
    echo ""
    
    # Set permissions
    set_permissions
    echo ""
    
    # Create launcher scripts
    create_launchers
    echo ""
    
    # Create systemd services
    create_services
    echo ""
    
    # Show final instructions
    show_final_instructions
}

# Run main function
main "$@"
