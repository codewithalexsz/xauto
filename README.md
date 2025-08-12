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
git clone <repository-url>
cd twitter-automation

# Or download and extract
wget <download-url>
tar -xzf twitter-automation.tar.gz
cd twitter-automation
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
python web_dashboard.py --host 0.0.0.0 --port 5000
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

### CLI Interface

#### Basic Commands
```bash
# List profiles
./run_cli.sh --list-profiles

# Create profile
./run_cli.sh --create-profile myprofile

# Delete profile
./run_cli.sh --delete-profile myprofile

# Scrape tweets
./run_cli.sh --scrape myprofile --tweet-links links.txt --output results.txt --max-retries 5
```

#### Command Options
| Option | Description | Example |
|--------|-------------|---------|
| `--list-profiles` | List all saved profiles | `--list-profiles` |
| `--create-profile` | Create new profile | `--create-profile myprofile` |
| `--delete-profile` | Delete existing profile | `--delete-profile myprofile` |
| `--scrape` | Profile name for scraping | `--scrape myprofile` |
| `--tweet-links` | File with tweet URLs | `--tweet-links links.txt` |
| `--output` | Output file (default: scraped_tweets.txt) | `--output results.txt` |
| `--max-retries` | Max retries per tweet (default: 3) | `--max-retries 5` |

## 🖥️ VNC Support

### Overview
VNC support allows you to:
- See the browser window while automation is running
- Manually log in to Twitter accounts
- Debug automation issues visually
- Monitor browser activity in real-time

### Quick Start with VNC

#### 1. Install VNC (if not already installed)
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

#### 4. Launch Chrome with VNC

**Method 1: Using the VNC Launcher Script**
```bash
# Make script executable
chmod +x launch_chrome_vnc.sh

# Launch Chrome with a profile
./launch_chrome_vnc.sh my_twitter_account
```

**Method 2: Using CLI**
```bash
# Set display environment variable
export DISPLAY=:1

# Create a profile (if needed)
./run_cli.sh --create-profile my_twitter_account

# Launch Chrome with the profile
./run_cli.sh --launch-browser my_twitter_account
```

**Method 3: Using Web Dashboard**
1. Start the dashboard: `./run_dashboard.sh`
2. Access at: `http://your-server-ip:5000`
3. Go to Settings tab → Enable "Use GUI Chrome via VNC"
4. Go to Profiles tab → Create profile → Click "Launch"

**Method 4: Test VNC Support**
```bash
# Run the VNC test script
python test_vnc_simple.py
```

### Manual Login Process

#### Step 1: Create a Chrome Profile
```bash
# Via CLI
./run_cli.sh --create-profile my_twitter_account

# Via Web Dashboard
# Go to Profiles tab and click "Create Profile"
```

#### Step 2: Launch Chrome Browser
```bash
# Via CLI
export DISPLAY=:1
./run_cli.sh --launch-browser my_twitter_account

# Via Web Dashboard
# Click "Launch" button next to your profile
```

#### Step 3: Log into Twitter
1. Navigate to `https://twitter.com` or `https://x.com`
2. Enter your email/username and password
3. Complete any 2FA if enabled
4. Verify login by checking your profile picture/name

#### Step 4: Test the Profile
```bash
# Test scraping with one link
echo "https://twitter.com/user/status/123456789" > test_links.txt
./run_cli.sh --scrape my_twitter_account --tweet-links test_links.txt
```

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

## 🔐 Login Guide

### Manual Login Process

#### 1. Create a Chrome Profile
```bash
# Via CLI
./run_cli.sh --create-profile my_twitter_account

# Via Web Dashboard
# Go to Profiles tab and click "Create Profile"
```

#### 2. Launch Chrome Browser
```bash
# Via CLI
./run_cli.sh --launch-browser my_twitter_account

# Via Web Dashboard
# Click "Launch" button next to your profile
```

#### 3. Log into Twitter
1. Navigate to `https://twitter.com` or `https://x.com`
2. Enter your email/username and password
3. Complete any 2FA if enabled
4. Verify login by checking your profile picture/name

#### 4. Test the Profile
```bash
# Test scraping with one link
echo "https://twitter.com/user/status/123456789" > test_links.txt
./run_cli.sh --scrape my_twitter_account --tweet-links test_links.txt
```

## 🔄 Automation

### Cron Jobs

#### Daily Scraping
```bash
# Edit crontab
crontab -e

# Add this line for daily scraping at 2 AM
0 2 * * * cd /path/to/twitter-automation && ./run_cli.sh --scrape production --tweet-links daily_links.txt --output daily_results.txt
```

#### Hourly Scraping
```bash
# Add this line for hourly scraping
0 * * * * cd /path/to/twitter-automation && ./run_cli.sh --scrape production --tweet-links hourly_links.txt --output hourly_results.txt
```

### Systemd Service

#### Install as Service
```bash
# Copy service file
sudo cp twitter-automation.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable twitter-automation
sudo systemctl start twitter-automation

# Check status
sudo systemctl status twitter-automation
```

#### Service Management
```bash
# Start service
sudo systemctl start twitter-automation

# Stop service
sudo systemctl stop twitter-automation

# Restart service
sudo systemctl restart twitter-automation

# View logs
sudo journalctl -u twitter-automation -f
```

## 🐳 Docker Deployment

### Option 1: Docker Build
```bash
# Build and run with Docker
docker build -t twitter-automation .
docker run -it --rm twitter-automation --help
```

### Option 2: Docker Compose
```bash
# Use docker-compose
docker-compose up -d
docker-compose exec twitter-automation ./run_cli.sh --list-profiles
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

## 🆘 Support

### Getting Help
1. Check the troubleshooting section above
2. Review logs in the `logs/` directory
3. Check system logs: `sudo journalctl -u twitter-automation`
4. Verify Chrome installation: `google-chrome --version`
5. Check VNC status: `vncserver -list`

### Common Commands Reference
```bash
# Quick status check
./run_cli.sh --list-profiles

# Test scraping with one link
echo "https://twitter.com/user/status/123456789" > test_links.txt
./run_cli.sh --scrape myprofile --tweet-links test_links.txt

# View recent results
tail -20 scraped_tweets.txt

# Start dashboard
./run_dashboard.sh

# Check dashboard status
curl http://localhost:5000/api/system/status
```

## 🔧 Advanced Configuration

### Environment Variables
```bash
# Set Chrome profile directory
export CHROME_PROFILE_DIR=~/.config/chrome_profiles

# Set ChromeDriver path
export CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

# Set VNC display
export DISPLAY=:1
```

### Custom Chrome Options
The application supports custom Chrome options for advanced users. These can be configured in the web dashboard or CLI interface.

### Automation Settings
- **Min Wait**: Minimum seconds between actions (1-60)
- **Max Wait**: Maximum seconds between actions (1-120)
- **Max Retries**: Retry attempts for failed actions (1-10)
- **Randomized Order**: Process tweets in random order for natural behavior

## 📝 Changelog

### Recent Fixes
- ✅ JavaScript detection issues resolved
- ✅ Comprehensive retry logic added
- ✅ Improved error handling
- ✅ VNC support for GUI mode
- ✅ Web dashboard with real-time updates
- ✅ System monitoring integration
- ✅ Enhanced security features

---

**Happy Automating! 🚀🐧**
