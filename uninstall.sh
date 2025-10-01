cleanup_env() {
    echo "🧹 Cleaning up Chromium, ChromeDriver, and VNC..."

    # Remove Chromium + Chromedriver
    sudo apt-get purge -y chromium-chromedriver chromium-browser chromium
    sudo apt-get autoremove -y
    sudo apt-get clean
    sudo snap remove chromium || true

    # Remove Chromium configs
    rm -rf ~/.config/chromium
    rm -rf ~/.cache/chromium

    # Stop running VNC processes
    vncserver -kill :1 || true
    pkill -f Xtigervnc || true
    pkill -f Xvnc || true

    # Remove VNC packages
    sudo apt purge -y tigervnc-standalone-server tigervnc-common tightvncserver vnc4server
    sudo apt autoremove -y
    sudo apt clean

    # Remove VNC configs and lock files
    rm -rf ~/.vnc
    sudo rm -f /tmp/.X*-lock
    sudo rm -f /tmp/.X11-unix/X*

    echo "✅ Cleanup complete. System is ready for fresh reinstall."
}
