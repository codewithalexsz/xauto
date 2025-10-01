# Twitter Automation - Complete Guide

A comprehensive Twitter automation application with web dashboard, CLI interface, and VNC support for Linux servers.

## 🎯 Overview

This application provides:
- **Web Dashboard**: Modern, responsive web interface for easy management
- **CLI Interface**: Command-line operation for server environments
- **Headless Chrome**: Runs Chrome in headless mode for server environments
- **VNC Support**: GUI mode via VNC for visual debugging and manual login
- **Profile Management**: Persistent Chrome profiles for account management
- **Automated Scraping**: Batch tweet content extraction with retry logic
- **Twitter Automation**: Like, retweet, and reply to tweets automatically
- **Systemd Service**: Optional system service integration

## 📋 Prerequisites

### System Requirements
- **OS**: Ubuntu 18.04+, CentOS 7+, RHEL 7+, or similar
- **RAM**: Minimum 2GB (4GB+ recommended)
- **Storage**: 5GB+ free space
- **Python**: 3.7 or higher
- **Chrome**: Google Chrome browser

### Network Requirements
- **Internet Access**: Required for Chrome and tweet scraping
- **Ports**: 5000 (dashboard), 5901 (VNC, optional)

## 🚀 Quick Installation

### 1. Clone/Download the Project
```bash
# Clone the repository
git clone https://github.com/codewithalexsz/xauto
cd xauto


```

### 2. Run Installation Script
```bash
# Make script executable
chmod +x install.sh

# Run installation
./install.sh
```

The installation script will:
- Install Python 3 and pip
- Install Google Chrome and ChromeDriver
- Install system dependencies (VNC, XFCE)
- Create virtual environment
- Install Python packages
- Set up directories and permissions
- Create launcher scripts
- Configure VNC support

## 🎮 Usage

### Web Dashboard

#### Start Dashboard
```bash
# Start the dashboard
./run_dashboard.sh

# Or manually
python web_dashboard.py 
```

#### Access Dashboard
- **Local**: http://localhost:5000
- **Remote**: http://YOUR_SERVER_IP:5000

#### Dashboard Features
- **Profiles Tab**: Create, view, and delete Chrome profiles
- **Scraping Tab**: Batch tweet scraping with real-time progress
- **Automation Tab**: Like, retweet, and reply to tweets
- **Tasks Tab**: Monitor and cancel running tasks
- **Files Tab**: View and download generated files
- **System Monitoring**: Real-time CPU, memory, and disk usage

## 🖥️ VNC Support

### Overview
VNC support allows you to:
- See the browser window while automation is running
- Manually log in to Twitter accounts
- Debug automation issues visually
- Monitor browser activity in real-time

### Quick Start with VNC

#### 1. Install VNC (if not already installed) ( handled by step 2)
```bash
# Ubuntu/Debian
sudo apt install -y xfce4 xfce4-goodies tightvncserver xvfb

# CentOS/RHEL
sudo yum install -y xfce4 xfce4-goodies tigervnc-server xvfb

# Fedora
sudo dnf install -y xfce4 xfce4-goodies tigervnc-server xvfb
```

#### 2. Configure VNC Server
```bash
# First-time VNC setup (you'll be prompted for a password)
vncserver :1

# Create VNC startup script
mkdir -p ~/.vnc
cat > ~/.vnc/xstartup << 'EOF'
#!/bin/bash
xrdb $HOME/.Xresources
startxfce4 &
EOF
chmod +x ~/.vnc/xstartup

# Restart VNC server
vncserver -kill :1
vncserver :1 -geometry 1920x1080 -depth 24
```

#### 3. Connect to VNC
- **From Windows**: Use TightVNC Viewer, connect to `your-server-ip:5901`
- **From Linux/macOS**: `vncviewer your-server-ip:5901`
- **From mobile -- download RVNC viewer from appstore, use ip:5901 to login

#### 4. Launch Chrome with VNC

**Method 3: Using Web Dashboard**
1. Start the dashboard: `./run_dashboard.sh`
2. Access at: `http://your-server-ip:5000`
3. Go to Settings tab → Enable "Use GUI Chrome via VNC"
4. Go to Profiles tab → Create profile → Click "Launch"



### Manual Login Process

#### Step 1: Create a Chrome Profile
```bash
# Via Web Dashboard
# Go to Profiles tab and click "Create Profile"
```

#### Step 2: Launch Chrome Browser
```bash
# Via Web Dashboard
# Click "Launch" button next to your profile
```

#### Step 3: Log into Twitter
1. Navigate to  `https://x.com`


### VNC Troubleshooting

#### Common Issues

**1. Can't connect to VNC**
```bash
# Check if VNC is running
ps aux | grep vnc

# Restart VNC server
vncserver -kill :1
vncserver :1
```

**2. Black screen in VNC**
```bash
# Check XFCE is running
ps aux | grep xfce

# Restart XFCE if needed
startxfce4 &
```

**3. Chrome won't launch**
```bash
# Check Chrome installation
which google-chrome
google-chrome --version

# Check ChromeDriver
which chromedriver
chromedriver --version
```

** FIX VNC FONT ERROR **
```bash
sudo apt update
sudo apt install -y xfonts-base xfonts-75dpi xfonts-100dpi
vncserver -kill :1
vncserver :1 -geometry 1920x1080 -depth 24
```

**4. "Display not found" error**
```bash
# Make sure VNC server is running
vncserver -list

# Check DISPLAY environment variable
echo $DISPLAY
# Should show :1 (or your configured display)
```

#### VNC Security
```bash
# Use strong VNC password
vncpasswd

# Consider SSH tunneling for secure connection
ssh -L 5901:localhost:5901 user@your-server
```

#### VNC Management
```bash
# Start VNC server
vncserver :1

# Stop VNC server
vncserver -kill :1

# List VNC sessions
vncserver -list

# Change VNC password
vncpasswd
```


## 📁 File Structure

```
twitter-automation/
├── cli_version.py           # CLI version of the app
├── web_dashboard.py         # Web dashboard application
├── install.sh               # Complete installation script
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── run_cli.sh              # CLI launcher script
├── run_dashboard.sh        # Dashboard launcher script
├── twitter-automation.service # Systemd service file
├── vnc-server.service      # VNC service file
├── venv/                   # Python virtual environment
├── app/                    # Application data
│   └── state/             # Profile storage
│       └── profiles.json  # Saved profiles
├── chrome-data/           # Chrome profiles
├── logs/                  # Log files
├── templates/             # Web dashboard templates
├── scraped_tweets.txt     # Scraped content
├── success_log.txt        # Success logs
└── failure_log.txt        # Failure logs
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Chrome Installation Failed
```bash
# Check if Chrome is installed
google-chrome --version

# Manual installation
wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
sudo rpm -i google-chrome-stable_current_x86_64.rpm
```

#### 2. Python Dependencies Failed
```bash
# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

#### 3. Permission Issues
```bash
# Fix permissions
chmod +x cli_version.py
chmod +x run_cli.sh
chmod +x install.sh
```

#### 4. Chrome Driver Issues
```bash
# Check Chrome version
google-chrome --version

# Manual ChromeDriver installation
wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE
CHROME_VERSION=$(google-chrome --version | cut -d' ' -f3 | cut -d'.' -f1)
wget https://chromedriver.storage.googleapis.com/$CHROME_VERSION/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
```

#### 5. VNC Issues
```bash
# Check if VNC is running
ps aux | grep vnc

# Restart VNC server
vncserver -kill :1
vncserver :1

# Check XFCE is running
ps aux | grep xfce
```

### Logs and Debugging

#### Enable Debug Logging
```bash
# Run with debug output
./run_cli.sh --scrape myprofile --tweet-links links.txt 2>&1 | tee debug.log
```

#### Check Chrome Logs
```bash
# View Chrome logs
tail -f logs/chrome.log
```

#### System Logs
```bash
# View system logs
sudo journalctl -u twitter-automation -f
```

#### Dashboard Logs
```bash
# Dashboard logs
tail -f logs/dashboard.log
```

## 🔒 Security Considerations

### File Permissions
```bash
# Secure file permissions
chmod 600 app/state/profiles.json
chmod 700 chrome-data/
chmod 755 logs/
```

### Firewall Configuration
```bash
# Allow outbound connections only
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw enable

# Allow dashboard port (if needed)
sudo ufw allow 5000/tcp
```

### User Permissions
```bash
# Create dedicated user
sudo useradd -m -s /bin/bash twitterbot
sudo usermod -aG sudo twitterbot

# Switch to dedicated user
sudo su - twitterbot
```

### VNC Security
```bash
# Use strong VNC password
vncpasswd

# Consider SSH tunneling
ssh -L 5901:localhost:5901 user@your-server
```

## 📊 Monitoring

### Health Checks
```bash
# Check if service is running
sudo systemctl is-active twitter-automation

# Check disk space
df -h

# Check memory usage
free -h

# Check process status
ps aux | grep python
```

### Performance Monitoring
```bash
# Monitor resource usage
htop

# Check log file sizes
du -sh logs/
du -sh chrome-data/
```

### Dashboard Status
```bash
# Check if dashboard is running
curl http://localhost:5000/api/system/status

# Check if port is open
netstat -tulpn | grep :5000
```


