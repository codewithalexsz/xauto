# WSL Setup Script for Windows
# This script helps you set up WSL to get Linux commands in your Windows terminal

Write-Host "🚀 WSL Setup Script for Linux Commands" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "❌ This script requires administrator privileges" -ForegroundColor Red
    Write-Host "Please run PowerShell as Administrator and try again" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Running as administrator" -ForegroundColor Green

# Check if WSL is already enabled
Write-Host "🔍 Checking WSL status..." -ForegroundColor Cyan
$wslEnabled = Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux

if ($wslEnabled.State -eq "Enabled") {
    Write-Host "✅ WSL is already enabled" -ForegroundColor Green
} else {
    Write-Host "🔧 Enabling WSL..." -ForegroundColor Yellow
    Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux -All -NoRestart
    Write-Host "✅ WSL enabled" -ForegroundColor Green
}

# Check if Virtual Machine Platform is enabled
Write-Host "🔍 Checking Virtual Machine Platform..." -ForegroundColor Cyan
$vmPlatformEnabled = Get-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform

if ($vmPlatformEnabled.State -eq "Enabled") {
    Write-Host "✅ Virtual Machine Platform is already enabled" -ForegroundColor Green
} else {
    Write-Host "🔧 Enabling Virtual Machine Platform..." -ForegroundColor Yellow
    Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform -All -NoRestart
    Write-Host "✅ Virtual Machine Platform enabled" -ForegroundColor Green
}

# Check if WSL command is available
Write-Host "🔍 Checking WSL command availability..." -ForegroundColor Cyan
try {
    $wslVersion = wsl --version 2>$null
    Write-Host "✅ WSL command is available" -ForegroundColor Green
} catch {
    Write-Host "⚠️  WSL command not found. You may need to restart your computer first." -ForegroundColor Yellow
}

# List installed distributions
Write-Host "📋 Checking installed Linux distributions..." -ForegroundColor Cyan
try {
    $distributions = wsl --list --verbose 2>$null
    if ($distributions) {
        Write-Host "✅ Found installed distributions:" -ForegroundColor Green
        Write-Host $distributions -ForegroundColor White
    } else {
        Write-Host "📝 No Linux distributions installed yet" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Could not check distributions" -ForegroundColor Yellow
}

# Show available distributions
Write-Host "📋 Available Linux distributions:" -ForegroundColor Cyan
try {
    $availableDistros = wsl --list --online 2>$null
    if ($availableDistros) {
        Write-Host $availableDistros -ForegroundColor White
    } else {
        Write-Host "⚠️  Could not fetch available distributions" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Could not fetch available distributions" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎯 Next Steps:" -ForegroundColor Green
Write-Host "1. Restart your computer (if you just enabled WSL features)" -ForegroundColor White
Write-Host "2. Install a Linux distribution:" -ForegroundColor White
Write-Host "   wsl --install -d Ubuntu" -ForegroundColor Cyan
Write-Host "3. Or list available distributions:" -ForegroundColor White
Write-Host "   wsl --list --online" -ForegroundColor Cyan
Write-Host "4. Set WSL 2 as default:" -ForegroundColor White
Write-Host "   wsl --set-default-version 2" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Yellow
Write-Host "- Ubuntu is recommended for beginners" -ForegroundColor White
Write-Host "- You can install multiple distributions" -ForegroundColor White
Write-Host "- Use 'wsl' command to access your Linux environment" -ForegroundColor White
Write-Host "- Windows files are accessible at /mnt/c, /mnt/d, etc." -ForegroundColor White
Write-Host ""
Write-Host "📚 For more help, see WSL_SETUP_GUIDE.md" -ForegroundColor Cyan 