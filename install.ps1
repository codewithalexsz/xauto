# Twitter Automation Windows Installation Script
# Run this script in PowerShell as Administrator

param(
    [switch]$SkipChrome,
    [switch]$SkipVNC
)

Write-Host "🚀 Twitter Automation Windows Installation Script" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""

# Check if running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "❌ Please run this script as Administrator" -ForegroundColor Red
    Write-Host "   Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

# Function to check if command exists
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Function to install Chocolatey if not present
function Install-Chocolatey {
    if (Test-Command choco) {
        Write-Host "✅ Chocolatey already installed" -ForegroundColor Green
        return
    }
    
    Write-Host "📦 Installing Chocolatey..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    
    # Refresh environment variables
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

# Function to install Python
function Install-Python {
    if (Test-Command python) {
        Write-Host "✅ Python already installed" -ForegroundColor Green
        return
    }
    
    Write-Host "🐍 Installing Python..." -ForegroundColor Yellow
    choco install python -y
    
    # Refresh environment variables
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

# Function to install Chrome
function Install-Chrome {
    if ($SkipChrome) {
        Write-Host "⏭️ Skipping Chrome installation" -ForegroundColor Yellow
        return
    }
    
    if (Test-Command chrome) {
        Write-Host "✅ Chrome already installed" -ForegroundColor Green
        return
    }
    
    Write-Host "🌐 Installing Google Chrome..." -ForegroundColor Yellow
    choco install googlechrome -y
}

# Function to install ChromeDriver
function Install-ChromeDriver {
    if (Test-Command chromedriver) {
        Write-Host "✅ ChromeDriver already installed" -ForegroundColor Green
        return
    }
    
    Write-Host "🔧 Installing ChromeDriver..." -ForegroundColor Yellow
    
    # Get Chrome version
    $chromeVersion = (Get-ItemProperty "HKLM:\SOFTWARE\Google\Chrome\BLBeacon").version
    Write-Host "📋 Chrome version: $chromeVersion" -ForegroundColor Cyan
    
    # Download ChromeDriver
    $majorVersion = $chromeVersion.Split('.')[0]
    $chromedriverVersion = Invoke-RestMethod -Uri "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$majorVersion"
    Write-Host "📋 ChromeDriver version: $chromedriverVersion" -ForegroundColor Cyan
    
    # Download and extract
    $downloadUrl = "https://chromedriver.storage.googleapis.com/$chromedriverVersion/chromedriver_win32.zip"
    $zipPath = "$env:TEMP\chromedriver.zip"
    $extractPath = "$env:TEMP\chromedriver"
    
    Invoke-WebRequest -Uri $downloadUrl -OutFile $zipPath
    Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force
    
    # Move to system PATH
    Copy-Item "$extractPath\chromedriver.exe" "C:\Windows\System32\chromedriver.exe" -Force
    
    # Cleanup
    Remove-Item $zipPath -Force
    Remove-Item $extractPath -Recurse -Force
    
    Write-Host "✅ ChromeDriver installed successfully" -ForegroundColor Green
}

# Function to install Git
function Install-Git {
    if (Test-Command git) {
        Write-Host "✅ Git already installed" -ForegroundColor Green
        return
    }
    
    Write-Host "📦 Installing Git..." -ForegroundColor Yellow
    choco install git -y
}

# Function to create Python virtual environment
function Create-VirtualEnvironment {
    Write-Host "🐍 Creating Python virtual environment..." -ForegroundColor Yellow
    
    if (Test-Path "venv") {
        Write-Host "✅ Virtual environment already exists" -ForegroundColor Green
        return
    }
    
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Function to install Python dependencies
function Install-PythonDependencies {
    Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
    
    # Activate virtual environment
    & ".\venv\Scripts\Activate.ps1"
    
    # Upgrade pip
    python -m pip install --upgrade pip
    
    # Install requirements
    if (Test-Path "requirements.txt") {
        Write-Host "📦 Installing requirements from requirements.txt..." -ForegroundColor Cyan
        pip install -r requirements.txt
    } else {
        Write-Host "📦 Installing core dependencies..." -ForegroundColor Cyan
        pip install selenium webdriver-manager flask flask-socketio requests beautifulsoup4 lxml psutil
    }
    
    Write-Host "✅ Python dependencies installed" -ForegroundColor Green
}

# Function to create directories
function Create-Directories {
    Write-Host "📁 Creating necessary directories..." -ForegroundColor Yellow
    
    $directories = @(
        "app\state",
        "app\config", 
        "chrome-data",
        "logs",
        "templates"
    )
    
    foreach ($dir in $directories) {
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }
    
    Write-Host "✅ Directories created" -ForegroundColor Green
}

# Function to create launcher scripts
function Create-LauncherScripts {
    Write-Host "🚀 Creating launcher scripts..." -ForegroundColor Yellow
    
    # Dashboard launcher
    @"
@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
python web_dashboard.py --host 0.0.0.0 --port 5000
pause
"@ | Out-File -FilePath "run_dashboard.bat" -Encoding ASCII
    
    # CLI launcher
    @"
@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
python cli_version.py %*
pause
"@ | Out-File -FilePath "run_cli.bat" -Encoding ASCII
    
    Write-Host "✅ Launcher scripts created" -ForegroundColor Green
}

# Function to show final instructions
function Show-FinalInstructions {
    Write-Host ""
    Write-Host "🎉 Installation completed successfully!" -ForegroundColor Green
    Write-Host "======================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Next steps:" -ForegroundColor Yellow
    Write-Host "1. Start the dashboard:" -ForegroundColor White
    Write-Host "   .\run_dashboard.bat" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "2. Access the dashboard:" -ForegroundColor White
    Write-Host "   http://localhost:5000" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "3. Use CLI interface:" -ForegroundColor White
    Write-Host "   .\run_cli.bat --help" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📁 Important directories:" -ForegroundColor Yellow
    Write-Host "   • Chrome profiles: .\chrome-data\" -ForegroundColor White
    Write-Host "   • Application state: .\app\state\" -ForegroundColor White
    Write-Host "   • Logs: .\logs\" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 Useful commands:" -ForegroundColor Yellow
    Write-Host "   • Start dashboard: .\run_dashboard.bat" -ForegroundColor White
    Write-Host "   • CLI interface: .\run_cli.bat --help" -ForegroundColor White
    Write-Host "   • Activate venv: .\venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "📚 Documentation:" -ForegroundColor Yellow
    Write-Host "   • README.md - Complete usage guide" -ForegroundColor White
    Write-Host "   • WSL_SETUP_GUIDE.md - WSL setup guide" -ForegroundColor White
    Write-Host ""
}

# Main installation process
function Main {
    Write-Host "🚀 Starting Windows installation process..." -ForegroundColor Green
    Write-Host ""
    
    # Install Chocolatey
    Install-Chocolatey
    Write-Host ""
    
    # Install Python
    Install-Python
    Write-Host ""
    
    # Install Chrome
    Install-Chrome
    Write-Host ""
    
    # Install ChromeDriver
    Install-ChromeDriver
    Write-Host ""
    
    # Install Git
    Install-Git
    Write-Host ""
    
    # Create directories
    Create-Directories
    Write-Host ""
    
    # Create virtual environment
    Create-VirtualEnvironment
    Write-Host ""
    
    # Install Python dependencies
    Install-PythonDependencies
    Write-Host ""
    
    # Create launcher scripts
    Create-LauncherScripts
    Write-Host ""
    
    # Show final instructions
    Show-FinalInstructions
}

# Run main function
Main 