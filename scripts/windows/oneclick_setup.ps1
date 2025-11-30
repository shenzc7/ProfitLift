[CmdletBinding()]
param(
    [string]$RepoUrl = "https://github.com/nonshenz007/ProfitLift.git",
    [string]$Branch = "main",
    [string]$InstallDir = "$env:USERPROFILE\\ProfitLift",
    [switch]$UseLocalRepo
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

function Assert-Winget {
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        throw "winget is required but not available. Install winget from Microsoft Store, then rerun this script."
    }
}

function Install-WingetPackage {
    param(
        [string]$Id,
        [string]$Name,
        [string]$ExtraArgs = ""
    )

    $alreadyInstalled = winget list --id $Id --exact 2>$null | Select-String $Id
    if ($alreadyInstalled) {
        Write-Host "$Name already installed."
        return
    }

    Write-Host "Installing $Name ..."
    winget install --id $Id --exact --silent --accept-package-agreements --accept-source-agreements $ExtraArgs
}

function Ensure-Prereqs {
    Assert-Winget
    Install-WingetPackage -Id "Git.Git" -Name "Git"
    Install-WingetPackage -Id "Python.Python.3.11" -Name "Python 3.11"
    Install-WingetPackage -Id "OpenJS.NodeJS.LTS" -Name "Node.js LTS"
    Install-WingetPackage -Id "Rustlang.Rust.MSVC" -Name "Rust (MSVC toolchain)"
    Install-WingetPackage -Id "Microsoft.VisualStudio.2022.BuildTools" -Name "Visual Studio Build Tools (for Tauri/Rust)" -ExtraArgs '--override "--add Microsoft.VisualStudio.Workload.VCTools --includeRecommended --passive --norestart"'
}

function Resolve-RepoRoot {
    $localRoot = $null
    if ($PSScriptRoot -and (Test-Path (Join-Path $PSScriptRoot "..\\..\\requirements.txt"))) {
        $localRoot = Resolve-Path (Join-Path $PSScriptRoot "..\\..")
    }

    if ($UseLocalRepo -or $localRoot) {
        $root = $localRoot
        if (-not $root) {
            $root = Resolve-Path "."
        }
        Write-Host "Using existing repository at $root"
        return $root
    }

    if (Test-Path (Join-Path $InstallDir ".git")) {
        Write-Host "Existing clone detected at $InstallDir. Pulling latest changes ..."
        git -C $InstallDir fetch --all
        git -C $InstallDir checkout $Branch
        git -C $InstallDir pull origin $Branch
        return Resolve-Path $InstallDir
    }

    if (Test-Path $InstallDir) {
        throw "Target directory $InstallDir exists but is not a git clone. Remove or change -InstallDir to continue."
    }

    Write-Host "Cloning ProfitLift from $RepoUrl to $InstallDir ..."
    git clone --branch $Branch $RepoUrl $InstallDir
    return Resolve-Path $InstallDir
}

function Ensure-Venv {
    param([string]$Root)
    $venvPath = Join-Path $Root ".venv"
    $pythonExe = ""

    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCmd) {
        $pythonCmd = Get-Command py -ErrorAction SilentlyContinue
    }
    if (-not $pythonCmd) {
        throw "Python executable not found on PATH. Confirm Python 3.11 is installed and restart PowerShell."
    }

    if (-not (Test-Path $venvPath)) {
        Write-Host "Creating Python virtual environment ..."
        & $pythonCmd.Source -m venv $venvPath
    }

    $pythonExe = Join-Path $venvPath "Scripts\\python.exe"
    & $pythonExe -m pip install --upgrade pip
    & $pythonExe -m pip install -r (Join-Path $Root "requirements.txt")
    return $pythonExe
}

function Build-Frontend {
    param([string]$Root)

    $frontendDir = Join-Path $Root "app\\frontend"
    if (-not (Test-Path $frontendDir)) {
        throw "Frontend directory not found at $frontendDir"
    }

    if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
        throw "npm not found on PATH. Restart PowerShell so winget additions take effect, then rerun."
    }

    Write-Host "Installing frontend dependencies ..."
    pushd $frontendDir
    npm install
    Write-Host "Building Tauri desktop bundle ..."
    $env:VITE_API_URL = "http://localhost:8000"
    npm run tauri build
    Remove-Item Env:VITE_API_URL -ErrorAction SilentlyContinue
    popd
}

function Build-Backend {
    param(
        [string]$Root,
        [string]$PythonExe
    )

    Write-Host "Packaging backend with PyInstaller ..."
    pushd $Root
    & $PythonExe -m PyInstaller ProfitLift.spec
    popd
}

function Create-Shortcut {
    param(
        [string]$Root
    )

    $launcher = Join-Path $Root "scripts\\windows\\launch_profitlift.ps1"
    if (-not (Test-Path $launcher)) {
        throw "Launcher script missing at $launcher"
    }

    $desktop = [Environment]::GetFolderPath("Desktop")
    $shortcutPath = Join-Path $desktop "ProfitLift.lnk"
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = "powershell.exe"
    $shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$launcher`""
    $shortcut.WorkingDirectory = $Root

    $iconPath = Join-Path $Root "app\\frontend\\src-tauri\\icons\\icon.ico"
    if (Test-Path $iconPath) {
        $shortcut.IconLocation = $iconPath
    }

    $shortcut.Save()
    Write-Host "Desktop shortcut created at $shortcutPath"
}

Write-Host "=== ProfitLift One-Click Windows Setup ==="
Write-Host "Repo URL: $RepoUrl"
Write-Host "Target directory: $InstallDir"
Write-Host ""

Ensure-Prereqs
$repoRoot = Resolve-RepoRoot
$pythonExe = Ensure-Venv -Root $repoRoot
Build-Frontend -Root $repoRoot
Build-Backend -Root $repoRoot -PythonExe $pythonExe
Create-Shortcut -Root $repoRoot

Write-Host ""
Write-Host "Setup complete. Double-click the 'ProfitLift' icon on your desktop to launch the backend and Tauri app."
