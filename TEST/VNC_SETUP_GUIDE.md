# VNC Setup Guide for Headless Linux Machine

This guide will walk you through setting up VNC to launch and use Chrome on your headless Linux machine.

## 🎯 Overview

VNC (Virtual Network Computing) allows you to:
- See the browser window while automation is running
- Manually log in to Twitter accounts
- Debug automation issues visually
- Monitor browser activity in real-time

## 📋 Prerequisites

1. **Linux Server** (headless)
2. **SSH access** to your server
3. **VNC client** on your local machine (TightVNC Viewer, RealVNC Viewer, etc.)

## 🚀 Step-by-Step Setup

### Step 1: Install VNC and XFCE

```bash
# Update package list
sudo apt update

# Install XFCE desktop environment
sudo apt install -y xfce4 xfce4-goodies

# Install TightVNC server
sudo apt install -y tightvncserver

# Install Xvfb (virtual framebuffer)
sudo apt install -y xvfb
```

### Step 2: Configure VNC Server

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

# Make the startup script executable
chmod +x ~/.vnc/xstartup

# Kill the existing VNC session
vncserver -kill :1

# Start VNC server with specific resolution
vncserver :1 -geometry 1920x1080 -depth 24
```

### Step 3: Connect to VNC

#### From Windows:
1. Download and install TightVNC Viewer
2. Open TightVNC Viewer
3. Enter your server IP and port: `your-server-ip:5901`
4. Enter the VNC password you set

#### From Linux/macOS:
```bash
# Install VNC viewer
sudo apt install -y tigervnc-viewer  # Ubuntu/Debian
# or
brew install tigervnc-viewer  # macOS

# Connect to VNC
vncviewer your-server-ip:5901
```

### Step 4: Test VNC Connection

Once connected, you should see the XFCE desktop environment. You can:
- Open a terminal
- Navigate to your application directory
- Test Chrome installation

## 🎮 Using Chrome with VNC

### Method 1: Launch Chrome via CLI

```bash
# Set the display environment variable
export DISPLAY=:1

# Navigate to your application directory
cd /path/to/your/twitter-automation

# Create a profile (if needed)
./run_cli.sh --create-profile my_twitter_account

# Launch Chrome with the profile
./run_cli.sh --launch-browser my_twitter_account
```

### Method 2: Launch Chrome via Web Dashboard

1. **Start the web dashboard:**
   ```bash
   ./run_dashboard.sh
   ```

2. **Access the dashboard:**
   - Open your browser and go to: `http://your-server-ip:5000`

3. **Configure VNC settings:**
   - Go to the "Settings" tab
   - Enable "Use GUI Chrome via VNC"
   - Set VNC display to `:1`
   - Click "Save Changes"

4. **Create and launch a profile:**
   - Go to the "Profiles" tab
   - Create a new profile
   - Click "Launch" next to your profile

### Method 3: Test VNC Support

```bash
# Run the VNC test script
python test_vnc.py
```

This will:
- Check if VNC environment is properly configured
- Verify VNC server is running
- Test Chrome in GUI mode
- Open Twitter in the browser

## 🔐 Manual Login Process

### Step 1: Create a Chrome Profile

```bash
# Via CLI
./run_cli.sh --create-profile my_twitter_account

# Via Web Dashboard
# Go to Profiles tab and click "Create Profile"
```

### Step 2: Launch Chrome Browser

```bash
# Via CLI
export DISPLAY=:1
./run_cli.sh --launch-browser my_twitter_account

# Via Web Dashboard
# Click "Launch" button next to your profile
```

### Step 3: Log into Twitter

1. **Navigate to Twitter:**
   - Go to `https://twitter.com` or `https://x.com`
   - You should see the login page

2. **Login Process:**
   - Enter your email/username and password
   - Complete any 2FA if enabled
   - You may need to verify your account or solve captchas
   - Once logged in, you should see your Twitter feed

3. **Verify Login:**
   - Check that you're logged in by looking at your profile picture/name
   - Try to post a test tweet or like a tweet to ensure full access

### Step 4: Test the Profile

```bash
# Test scraping with one link
echo "https://twitter.com/user/status/123456789" > test_links.txt
./run_cli.sh --scrape my_twitter_account --tweet-links test_links.txt
```

## 🔧 Troubleshooting

### VNC Issues

#### 1. Can't connect to VNC
```bash
# Check if VNC is running
ps aux | grep vnc

# Restart VNC server
vncserver -kill :1
vncserver :1
```

#### 2. Black screen in VNC
```bash
# Check XFCE is running
ps aux | grep xfce

# Restart XFCE if needed
startxfce4 &
```

#### 3. Chrome won't launch
```bash
# Check Chrome installation
which google-chrome
google-chrome --version

# Check ChromeDriver
which chromedriver
chromedriver --version
```

### Common Problems

#### 1. "Display not found" error
```bash
# Make sure VNC server is running
vncserver -list

# Check DISPLAY environment variable
echo $DISPLAY
# Should show :1 (or your configured display)
```

#### 2. Chrome crashes
```bash
# Check Chrome profile directory permissions
ls -la ~/.config/chrome_profiles/

# Ensure enough memory is available
free -h
```

#### 3. ChromeDriver version mismatch
```bash
# Get Chrome version
google-chrome --version

# Get matching ChromeDriver
CHROME_VERSION=$(google-chrome --version | cut -d ' ' -f 3 | cut -d '.' -f 1)
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION"
sudo unzip /tmp/chromedriver.zip -d /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
```

## 🔒 Security Considerations

### VNC Security
```bash
# Use strong VNC password
vncpasswd

# Consider SSH tunneling for secure connection
ssh -L 5901:localhost:5901 user@your-server
```

### Firewall Configuration
```bash
# Only allow VNC connections from trusted IPs
sudo ufw allow from YOUR_IP to any port 5901
```

## 📊 Monitoring

### Check VNC Status
```bash
# List running VNC servers
vncserver -list

# Check VNC logs
tail -f ~/.vnc/*.log
```

### System Resources
```bash
# Monitor resource usage
htop

# Check memory usage
free -h

# Check disk space
df -h
```

## 🎯 Quick Commands Reference

### VNC Management
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

### Chrome with VNC
```bash
# Set display and launch Chrome
export DISPLAY=:1
./run_cli.sh --launch-browser myprofile

# Test VNC support
python test_vnc.py

# Check VNC status
curl http://localhost:5000/api/config/vnc/status
```

## 🆘 Getting Help

### Common Issues and Solutions

1. **VNC connection refused:**
   - Check if VNC server is running: `vncserver -list`
   - Restart VNC server: `vncserver -kill :1 && vncserver :1`

2. **Chrome not visible in VNC:**
   - Ensure DISPLAY is set: `export DISPLAY=:1`
   - Check if XFCE is running: `ps aux | grep xfce`

3. **Permission denied errors:**
   - Check file permissions: `ls -la ~/.vnc/`
   - Fix permissions: `chmod +x ~/.vnc/xstartup`

4. **Chrome crashes on startup:**
   - Check Chrome installation: `google-chrome --version`
   - Verify ChromeDriver: `chromedriver --version`

### Support Resources

1. Check the main README.md (VNC Support section)
2. Review logs in the `logs/` directory
3. Check VNC logs: `tail -f ~/.vnc/*.log`
4. Verify Chrome installation: `google-chrome --version`
5. Test VNC status: `python test_vnc.py`

---

**Happy VNC-ing! 🖥️🚀**
