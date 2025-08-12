# WSL Setup Guide for Linux Commands in Windows Terminal

## What is WSL?
Windows Subsystem for Linux (WSL) allows you to run a Linux environment directly on Windows without the overhead of a traditional virtual machine.

## Quick Setup

### 1. Enable WSL Feature
Open PowerShell as Administrator and run:
```powershell
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
```

### 2. Restart Your Computer
After enabling the features, restart your computer.

### 3. Install WSL 2
```powershell
wsl --set-default-version 2
```

### 4. Install a Linux Distribution
```powershell
# List available distributions
wsl --list --online

# Install Ubuntu (recommended for beginners)
wsl --install -d Ubuntu

# Or install other popular distributions:
# wsl --install -d Debian
# wsl --install -d openSUSE-42
# wsl --install -d SLES-12
```

### 5. Set Up Your Linux User
When you first launch your Linux distribution, you'll be prompted to:
- Create a username
- Set a password

## Using Linux Commands

### Access WSL
- **Windows Terminal**: Open Windows Terminal and click the dropdown → select your Linux distribution
- **Command Prompt**: Type `wsl` or `wsl -d Ubuntu`
- **PowerShell**: Type `wsl` or `wsl -d Ubuntu`

### Example Commands
```bash
# File operations
ls -la
cp file1 file2
mv oldname newname
rm filename

# Package management (Ubuntu/Debian)
sudo apt update
sudo apt install package_name

# Package management (CentOS/RHEL)
sudo yum install package_name

# Process management
ps aux
kill process_id
top

# Network tools
curl https://example.com
wget https://example.com/file.zip
ping google.com

# Text processing
grep "pattern" file.txt
sed 's/old/new/g' file.txt
awk '{print $1}' file.txt
```

## Integration with Windows

### Access Windows Files from WSL
```bash
# Windows C: drive is mounted at /mnt/c
cd /mnt/c/Users/YourUsername/Desktop

# Windows D: drive is mounted at /mnt/d
ls /mnt/d/
```

### Access WSL Files from Windows
```
# In Windows Explorer, navigate to:
\\wsl$\Ubuntu\home\yourusername
```

### Run Windows Commands from WSL
```bash
# Run Windows executables
notepad.exe
explorer.exe .

# Run PowerShell commands
powershell.exe "Get-Process"
```

## Alternative Options

### Option 2: Git Bash
If you only need basic Linux commands:
1. Install Git for Windows (includes Git Bash)
2. Use Git Bash terminal for basic Linux commands

### Option 3: Cygwin
For more comprehensive Unix tools:
1. Download Cygwin from https://www.cygwin.com/
2. Install during setup
3. Use Cygwin terminal

### Option 4: Windows Terminal + PowerShell with Unix Aliases
Create PowerShell profile with Unix command aliases:
```powershell
# Create profile if it doesn't exist
if (!(Test-Path -Path $PROFILE)) {
    New-Item -ItemType File -Path $PROFILE -Force
}

# Add Unix-like aliases
Add-Content $PROFILE @"
# Unix-like aliases
Set-Alias -Name ls -Value Get-ChildItem
Set-Alias -Name ll -Value Get-ChildItem
Set-Alias -Name grep -Value Select-String
Set-Alias -Name cat -Value Get-Content
Set-Alias -Name pwd -Value Get-Location
Set-Alias -Name clear -Value Clear-Host
"@
```

## Troubleshooting

### WSL Installation Issues
```powershell
# Check WSL status
wsl --status

# Update WSL
wsl --update

# Reset WSL
wsl --shutdown
```

### Performance Issues
- Ensure WSL 2 is being used: `wsl --set-version Ubuntu 2`
- Check Windows virtualization is enabled in BIOS
- Update Windows to latest version

### File Permission Issues
```bash
# Fix file permissions in WSL
chmod +x script.sh
chown username:group filename
```

## Recommended Setup for Development

1. **Install Windows Terminal** (from Microsoft Store)
2. **Install WSL with Ubuntu**
3. **Install VS Code with WSL extension**
4. **Set up your development environment in WSL**

This gives you the best of both worlds: Windows GUI applications and Linux command-line tools.

## Next Steps

After setting up WSL, you can:
- Install development tools (Node.js, Python, etc.)
- Set up your project environment
- Use Linux package managers
- Run Linux-specific applications
- Access your existing Windows files from Linux

WSL is the most comprehensive solution for running Linux commands in Windows! 