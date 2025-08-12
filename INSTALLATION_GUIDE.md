# Twitter Automation - Complete Installation Guide

This guide covers installation of the Twitter automation system on different platforms.

## 🚀 Quick Installation

### Linux (Ubuntu/Debian/CentOS/RHEL/Fedora)

```bash
# Make script executable
chmod +x install.sh

# Run installation
./install.sh
```

### Windows

```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy Bypass -Scope Process -Force
.\install.ps1
```

### macOS

```bash
# Install Homebrew first (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python3 wget curl git

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt

# Install Chrome (if not already installed)
brew install --cask google-chrome
```

## 📋 System Requirements

### Minimum Requirements
- **OS**: Ubuntu 18.04+, CentOS 7+, RHEL 7+, Windows 10+, macOS 10.14+
- **RAM**: 2GB (4GB+ recommended)
- **Storage**: 5GB+ free space
- **Python**: 3.7 or higher
- **Chrome**: Google Chrome browser

### Recommended Requirements
- **OS**: Ubuntu 20.04+, Windows 11+, macOS 11+
- **RAM**: 8GB+
- **Storage**: 10GB+ free space
- **CPU**: Multi-core processor
- **Network**: Stable internet connection

## 🔧 Manual Installation

### Step 1: Install System Dependencies

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv wget curl unzip \
    build-essential libssl-dev libffi-dev python3-dev gnupg git
```

#### CentOS/RHEL
```bash
sudo yum update -y
sudo yum groupinstall -y "Development Tools"
sudo yum install -y python3 python3-pip wget curl unzip \
    openssl-devel libffi-devel python3-devel gnupg git
```

#### Fedora
```bash
sudo dnf update -y
sudo dnf groupinstall -y "Development Tools"
sudo dnf install -y python3 python3-pip wget curl unzip \
    openssl-devel libffi-devel python3-devel gnupg git
```

### Step 2: Install Google Chrome

#### Ubuntu/Debian
```bash
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install -y google-chrome-stable
```

#### CentOS/RHEL
```bash
sudo yum install -y wget
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo rpm --import -
sudo yum install -y https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
```

#### Fedora
```bash
sudo dnf install -y wget
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo rpm --import -
sudo dnf install -y https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
```

### Step 3: Install ChromeDriver

```bash
# Get Chrome version
CHROME_VERSION=$(google-chrome --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)

# Get ChromeDriver version
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")

# Download and install
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
unzip /tmp/chromedriver.zip -d /tmp/
sudo mv /tmp/chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
```

### Step 4: Install VNC Server (Linux only)

#### Ubuntu/Debian
```bash
sudo apt install -y tightvncserver xfce4 xfce4-goodies
```

#### CentOS/RHEL
```bash
sudo yum install -y tigervnc-server tigervnc-server-module xfce4
```

#### Fedora
```bash
sudo dnf install -y tigervnc-server tigervnc-server-module xfce4
```

### Step 5: Setup VNC Environment

```bash
# Create VNC directory
mkdir -p ~/.vnc

# Create xstartup file
cat > ~/.vnc/xstartup << 'EOF'
#!/bin/bash
xrdb $HOME/.Xresources
startxfce4 &
EOF

chmod +x ~/.vnc/xstartup
```

### Step 6: Setup Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

### Step 7: Create Directories

```bash
mkdir -p app/state app/config chrome-data logs templates
```

### Step 8: Set Permissions

```bash
chmod +x web_dashboard.py cli_version.py run_dashboard.sh run_cli.sh
```

## 🚀 Post-Installation Setup

### 1. Start VNC Server (Linux)

```bash
# Start VNC server
vncserver :1 -geometry 1920x1080 -depth 24 -localhost no

# Set VNC password (first time only)
vncpasswd
```

### 2. Start the Dashboard

```bash
# Activate virtual environment
source venv/bin/activate

# Start dashboard
python3 web_dashboard.py --host 0.0.0.0 --port 5000
```

### 3. Access the Dashboard

Open your web browser and navigate to:
- **Local**: http://localhost:5000
- **Remote**: http://YOUR_SERVER_IP:5000

### 4. Connect to VNC (Optional)

Use a VNC viewer to connect to:
- **Address**: localhost:5901
- **Password**: The password you set with `vncpasswd`

## 🔧 Configuration

### Environment Variables

You can set these environment variables to customize the installation:

```bash
export TWITTER_AUTOMATION_PORT=5000
export TWITTER_AUTOMATION_HOST=0.0.0.0
export CHROME_PROFILE_DIR=./chrome-data
export VNC_DISPLAY=:1
```

### Configuration Files

The system creates configuration files in:
- **State**: `app/state/profiles.json`
- **Config**: `app/config/settings.json`
- **Logs**: `logs/`

## 🛠️ Troubleshooting

### Common Issues

#### 1. Chrome/ChromeDriver Version Mismatch
```bash
# Check Chrome version
google-chrome --version

# Check ChromeDriver version
chromedriver --version

# If versions don't match, reinstall ChromeDriver
```

#### 2. VNC Connection Issues
```bash
# Check if VNC is running
ps aux | grep vnc

# Kill existing VNC processes
vncserver -kill :1

# Start VNC server
vncserver :1 -geometry 1920x1080 -depth 24 -localhost no
```

#### 3. Python Import Errors
```bash
# Activate virtual environment
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

#### 4. Permission Issues
```bash
# Fix permissions
chmod +x *.py *.sh
chmod 755 app/ chrome-data/ logs/
```

### Getting Help

1. **Check logs**: Look in the `logs/` directory for error messages
2. **Verify installation**: Run `python3 -c "import selenium; print('Selenium OK')"`
3. **Test Chrome**: Run `google-chrome --version`
4. **Test ChromeDriver**: Run `chromedriver --version`

## 📚 Additional Resources

- **README.md**: Complete usage guide
- **VNC_SETUP_GUIDE.md**: Detailed VNC configuration
- **WSL_SETUP_GUIDE.md**: Windows Subsystem for Linux setup
- **Dockerfile**: Container deployment option

## 🔄 Updates

To update the system:

```bash
# Pull latest changes
git pull origin main

# Update Python dependencies
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Restart services
sudo systemctl restart twitter-automation.service
```

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the logs in the `logs/` directory
3. Verify your system meets the requirements
4. Try the manual installation steps

For additional help, refer to the documentation files in the project directory. 