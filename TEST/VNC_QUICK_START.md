# VNC Quick Start for Headless Machine

## 🎯 What You Need to Do

### Step 1: Install VNC (if not done)
```bash
# Install VNC and XFCE
sudo apt update
sudo apt install -y xfce4 xfce4-goodies tightvncserver xvfb
```

### Step 2: Start VNC Server
```bash
# First time setup (set password when prompted)
vncserver :1

# Create startup script
mkdir -p ~/.vnc
cat > ~/.vnc/xstartup << 'EOF'
#!/bin/bash
xrdb $HOME/.Xresources
startxfce4 &
EOF
chmod +x ~/.vnc/xstartup

# Restart with better settings
vncserver -kill :1
vncserver :1 -geometry 1920x1080 -depth 24
```

### Step 3: Connect to VNC
- **Windows**: Download TightVNC Viewer → Connect to `your-server-ip:5901`
- **Linux/macOS**: `vncviewer your-server-ip:5901`

### Step 4: Launch Chrome

#### Option A: Use the VNC Launcher Script
```bash
# Make executable and run
chmod +x launch_chrome_vnc.sh
./launch_chrome_vnc.sh my_twitter_account
```

#### Option B: Use CLI
```bash
# Set display and launch
export DISPLAY=:1
./run_cli.sh --create-profile my_twitter_account
./run_cli.sh --launch-browser my_twitter_account
```

#### Option C: Use Web Dashboard
```bash
# Start dashboard
./run_dashboard.sh

# Then in browser: http://your-server-ip:5000
# Go to Settings → Enable VNC → Profiles → Create → Launch
```

### Step 5: Log into Twitter
1. Chrome will open in your VNC session
2. Navigate to `https://twitter.com`
3. Log in with your credentials
4. Complete 2FA if needed
5. Verify you're logged in

### Step 6: Test Everything
```bash
# Test scraping
echo "https://twitter.com/user/status/123456789" > test_links.txt
./run_cli.sh --scrape my_twitter_account --tweet-links test_links.txt
```

## 🔧 Quick Commands

### VNC Management
```bash
# Start VNC
vncserver :1

# Stop VNC
vncserver -kill :1

# Check VNC status
vncserver -list
```

### Chrome with VNC
```bash
# Set display
export DISPLAY=:1

# Launch Chrome
./launch_chrome_vnc.sh myprofile

# Test VNC
python test_vnc_simple.py
```

## 🆘 Troubleshooting

### VNC Not Working?
```bash
# Check if VNC is running
ps aux | grep vnc

# Restart VNC
vncserver -kill :1 && vncserver :1
```

### Chrome Not Visible?
```bash
# Check display
echo $DISPLAY

# Set display
export DISPLAY=:1
```

### Permission Issues?
```bash
# Fix VNC permissions
chmod +x ~/.vnc/xstartup

# Fix script permissions
chmod +x launch_chrome_vnc.sh
```

## 🎯 Success Checklist

- [ ] VNC server running (`vncserver -list` shows `:1`)
- [ ] Can connect via VNC viewer
- [ ] XFCE desktop visible in VNC
- [ ] Chrome launches in VNC session
- [ ] Can navigate to Twitter
- [ ] Can log into Twitter account
- [ ] Profile works for scraping

## 📞 Need Help?

1. Check the main README.md (VNC Support section)
2. Run `python test_vnc_simple.py` for diagnostics
3. Check VNC logs: `tail -f ~/.vnc/*.log`
4. Verify Chrome: `google-chrome --version`

---

**You're ready to use Chrome with VNC on your headless machine! 🖥️🚀**
