[CmdletBinding()]
param(
    [string]$RepoUrl = "https://github.com/shenzc7/ProfitLift.git",
    [string]$Branch = "main",
    [string]$InstallDir = "$env:USERPROFILE\\ProfitLift",
    [switch]$UseLocalRepo,
    [switch]$ForceRebuild
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
Set-StrictMode -Version Latest

# Ensure this process ignores system execution policy (needed for npm.ps1 wrappers).
try { Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force } catch {}

# Marker to avoid re-requesting elevation in child process.
if (-not $env:PROFITLIFT_ELEVATED) { $env:PROFITLIFT_ELEVATED = "" }

$logPath = Join-Path $env:TEMP "profitlift_setup.log"
try { Start-Transcript -Path $logPath -Append -ErrorAction SilentlyContinue } catch {}

function Write-Step { param([string]$Message) Write-Host "`n==> $Message" -ForegroundColor Cyan }
function Write-Info { param([string]$Message) Write-Host "    $Message" }

function Ensure-Admin {
    # Some winget installs (VS Build Tools) require elevation; auto-relaunch as admin if needed.
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($id)
    if ($env:PROFITLIFT_ELEVATED -eq "1" -or $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        $env:PROFITLIFT_ELEVATED = "1"
        return
    }

    Write-Step "Requesting administrator privileges for installs (UAC prompt)..."

    # Always relaunch from canonical remote URL (avoids $MyInvocation.Path issues when invoked via iex).
    $oneLiner = "`$env:PROFITLIFT_ELEVATED='1'; irm 'https://raw.githubusercontent.com/shenzc7/ProfitLift/main/scripts/windows/oneclick_setup.ps1' | iex"
    Start-Process -FilePath "powershell.exe" -Verb RunAs -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", $oneLiner)

    exit
}

function Refresh-EnvPath {
    # Ensure we pick up PATH updates that winget writes to the registry.
    $machine = [Environment]::GetEnvironmentVariable("Path", "Machine")
    $user = [Environment]::GetEnvironmentVariable("Path", "User")
    $env:Path = "$machine;$user"
}

function Assert-Winget {
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        throw "winget is required but not available. Install winget from Microsoft Store, then rerun this script."
    }
}

function Test-Version {
    param(
        [string]$Output,
        [string]$Minimum,
        [string]$Name
    )

    $numeric = $Output -replace '[^0-9\\.]', ''
    $parsed = $null
    if (-not [version]::TryParse($numeric, [ref]$parsed)) {
        Write-Warning "Could not parse $Name version from '$Output'. Continuing."
        return
    }

    if ($parsed -lt [version]$Minimum) {
        throw "$Name $parsed found, but $Minimum or newer is required."
    }
}

function Require-Command {
    param(
        [string]$Name,
        [string]$MinimumVersion = $null
    )

    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if (-not $cmd) {
        throw "$Name not found on PATH. Open a new PowerShell window (to refresh PATH) and rerun."
    }

    if ($MinimumVersion) {
        $verOut = & $cmd.Source --version 2>&1
        Test-Version -Output $verOut -Minimum $MinimumVersion -Name $Name
        Write-Info "$Name $verOut"
    } else {
        Write-Info "$Name found at $($cmd.Source)"
    }

    return $cmd.Source
}

function Normalize-NpmPath {
    param([string]$Path)
    if ($Path -and ($Path.ToLower().EndsWith("npm.ps1"))) {
        $cmd = [System.IO.Path]::ChangeExtension($Path, ".cmd")
        if (Test-Path $cmd) { return $cmd }
    }
    return $Path
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

function Preflight-Checks {
    Write-Step "Preflight: verifying required tools are on PATH"
    $pythonPath = $null

    try {
        $pythonPath = Require-Command -Name "python" -MinimumVersion "3.11"
    } catch {
        $pythonPath = $null
    }

    if (-not $pythonPath) {
        $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
        if ($pyLauncher) {
            $verOut = & $pyLauncher.Source -3 --version 2>&1
            Test-Version -Output $verOut -Minimum "3.11" -Name "Python"
            $pythonPath = (& $pyLauncher.Source -3 -c "import sys; print(sys.executable)") -replace "`n","" -replace "`r",""
        }
    }

    if (-not $pythonPath) {
        throw "Python 3.11 not found on PATH. Open a new PowerShell session and rerun the script."
    }

    $nodePath = Require-Command -Name "node" -MinimumVersion "18.0"
    $npmPath = Normalize-NpmPath (Require-Command -Name "npm" -MinimumVersion "9.0")
    Require-Command -Name "git" -MinimumVersion "2.30" | Out-Null
    Require-Command -Name "rustc" -MinimumVersion "1.72" | Out-Null
    Require-Command -Name "cargo" -MinimumVersion "1.72" | Out-Null

    return @{
        PythonExe = $pythonPath.Trim()
        NodeExe   = $nodePath
        NpmExe    = $npmPath
    }
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
    param(
        [string]$Root,
        [string]$PythonExeHint
    )

    $venvPath = Join-Path $Root ".venv"
    $pythonExe = $PythonExeHint

    if (-not $pythonExe) {
        $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
        if (-not $pythonCmd) {
            $pythonCmd = Get-Command py -ErrorAction SilentlyContinue
        }
        if (-not $pythonCmd) {
            throw "Python executable not found on PATH. Confirm Python 3.11 is installed and restart PowerShell."
        }
        $pythonExe = $pythonCmd.Source
    }

    if (-not (Test-Path $venvPath)) {
        Write-Step "Creating Python virtual environment ..."
        & $pythonExe -m venv $venvPath
    }

    $venvPython = Join-Path $venvPath "Scripts\\python.exe"
    Write-Step "Installing backend dependencies ..."
    & $venvPython -m pip install --upgrade pip setuptools wheel
    & $venvPython -m pip install -r (Join-Path $Root "requirements.txt")
    return $venvPython
}

function Build-Frontend {
    param(
        [string]$Root,
        [string]$NpmExe,
        [switch]$Force
    )

    $frontendDir = Join-Path $Root "app\\frontend"
    if (-not (Test-Path $frontendDir)) {
        throw "Frontend directory not found at $frontendDir"
    }

    $desktopExe = Join-Path $frontendDir "src-tauri\\target\\release\\profitlift.exe"
    if ((Test-Path $desktopExe) -and -not $Force) {
        Write-Host "Tauri desktop bundle already exists. Skipping rebuild (use -ForceRebuild to force)."
        return
    }

    if (-not $NpmExe) {
        $npmCmd = Get-Command npm -ErrorAction SilentlyContinue
        if (-not $npmCmd) {
            throw "npm not found on PATH. Restart PowerShell so winget additions take effect, then rerun."
        }
        $NpmExe = Normalize-NpmPath $npmCmd.Source
    }
    $NpmExe = Normalize-NpmPath $NpmExe

    Write-Step "Installing frontend dependencies ..."
    pushd $frontendDir
    & $NpmExe install --no-fund --no-audit
    if ($LASTEXITCODE -ne 0) { throw "npm install failed." }

    Write-Step "Building Tauri desktop bundle ..."
    $env:VITE_API_URL = "http://localhost:8000"
    & $NpmExe run tauri build
    $exit = $LASTEXITCODE
    Remove-Item Env:VITE_API_URL -ErrorAction SilentlyContinue
    popd

    if ($exit -ne 0) { throw "npm run tauri build failed." }
}

function Build-Backend {
    param(
        [string]$Root,
        [string]$PythonExe,
        [switch]$Force
    )

    $backendExe = Join-Path $Root "dist\\ProfitLift\\ProfitLift.exe"
    if ((Test-Path $backendExe) -and -not $Force) {
        Write-Host "Backend executable already exists. Skipping rebuild (use -ForceRebuild to force)."
        return
    }

    Write-Step "Packaging backend with PyInstaller ..."
    pushd $Root
    & $PythonExe -m PyInstaller ProfitLift.spec
    if ($LASTEXITCODE -ne 0) {
        popd
        throw "PyInstaller build failed."
    }
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

function Postflight-Verify {
    param([string]$Root)

    $backendExe = Join-Path $Root "dist\\ProfitLift\\ProfitLift.exe"
    $frontendExe = Join-Path $Root "app\\frontend\\src-tauri\\target\\release\\profitlift.exe"
    $missing = @()

    if (-not (Test-Path $backendExe)) { $missing += $backendExe }
    if (-not (Test-Path $frontendExe)) { $missing += $frontendExe }

    if ($missing.Count -gt 0) {
        Write-Warning "Build artifacts missing: $($missing -join ', '). Review $logPath for errors."
    } else {
        Write-Step "Verification complete: backend and desktop bundles are present."
    }
}

Write-Host "=== ProfitLift One-Click Windows Setup ==="
Write-Host "Repo URL: $RepoUrl"
Write-Host "Target directory: $InstallDir"
Write-Host "Log: $logPath"
Write-Host ""

try {
    Ensure-Admin
    Write-Step "Installing prerequisites with winget (idempotent)"
    Write-Info "This step may take several minutes (Visual Studio Build Tools download is ~2 GB)."
    Ensure-Prereqs
    Refresh-EnvPath

    $tools = Preflight-Checks
    $repoRoot = Resolve-RepoRoot
    $pythonExe = Ensure-Venv -Root $repoRoot -PythonExeHint $tools.PythonExe
    Build-Frontend -Root $repoRoot -NpmExe $tools.NpmExe -Force:$ForceRebuild
    Build-Backend -Root $repoRoot -PythonExe $pythonExe -Force:$ForceRebuild
    Create-Shortcut -Root $repoRoot
    Postflight-Verify -Root $repoRoot

    Write-Host ""
    Write-Host "Setup complete. Double-click the 'ProfitLift' icon on your desktop to launch the backend and Tauri app."
    Write-Host "If anything fails, check the log at $logPath and rerun with -ForceRebuild to rebuild everything."
}
finally {
    try { Stop-Transcript | Out-Null } catch {}
}
