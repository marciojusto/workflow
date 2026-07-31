# Workflow Installer Wrapper (PowerShell)
# Invokes the bash installer script on Windows/Git Bash/WSL

param(
    [switch]$Help
)

if ($Help) {
    Write-Host "Workflow Installer v2.0.0" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage: .\Install-Workflow.ps1 [options]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Help     Show this help message"
    Write-Host ""
    Write-Host "This script invokes the bash installer (install-workflow.sh)."
    Write-Host "Ensure you have Git Bash or WSL installed."
    exit 0
}

# Determine bash path
$bashPath = $null

# Check common bash locations
$possiblePaths = @(
    "C:\Program Files\Git\bin\bash.exe",
    "C:\Program Files (x86)\Git\bin\bash.exe",
    "$env:USERPROFILE\AppData\Local\Programs\Git\bin\bash.exe",
    "C:\Windows\System32\bash.exe",
    "C:\Windows\Sysnative\bash.exe"
)

foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $bashPath = $path
        break
    }
}

# Try to find bash in PATH
if (-not $bashPath) {
    $bashInPath = Get-Command bash -ErrorAction SilentlyContinue
    if ($bashInPath) {
        $bashPath = $bashInPath.Source
    }
}

if (-not $bashPath) {
    Write-Host "✗ Bash not found. Please install Git Bash or WSL and try again." -ForegroundColor Red
    Write-Host "  Download Git Bash: https://git-scm.com/downloads" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Bash found: $bashPath" -ForegroundColor Green

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$bashScript = Join-Path $scriptDir "install-workflow.sh"

if (-not (Test-Path $bashScript)) {
    Write-Host "✗ Bash script not found: $bashScript" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Invoking bash installer..." -ForegroundColor Green
Write-Host ""

# Invoke bash script
& $bashPath $bashScript

exit $LASTEXITCODE
