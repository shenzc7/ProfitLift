[CmdletBinding()]
param(
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"

function Get-RepoRoot {
    $here = Split-Path -Parent $MyInvocation.MyCommand.Path
    return Resolve-Path (Join-Path $here "..\\..")
}

function Is-PortBusy {
    param([int]$TargetPort)
    return @(Get-NetTCPConnection -LocalPort $TargetPort -ErrorAction SilentlyContinue).Count -gt 0
}

function Start-Backend {
    param([string]$Root, [int]$TargetPort)

    if (Is-PortBusy -TargetPort $TargetPort) {
        Write-Host "Backend already listening on port $TargetPort. Skipping new start."
        return
    }

    $backendExe = Join-Path $Root "dist\\ProfitLift\\ProfitLift.exe"
    $venvPython = Join-Path $Root ".venv\\Scripts\\python.exe"

    if (Test-Path $backendExe) {
        Write-Host "Starting packaged backend ..."
        Start-Process -FilePath $backendExe -WindowStyle Hidden
    }
    elseif (Test-Path $venvPython) {
        Write-Host "Starting backend with uvicorn from virtualenv ..."
        $args = @("-m", "uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", $TargetPort)
        Start-Process -FilePath $venvPython -ArgumentList $args -WindowStyle Hidden
    }
    else {
        throw "No backend executable or virtualenv found. Run scripts/windows/oneclick_setup.ps1 first."
    }
}

function Start-Frontend {
    param([string]$Root)

    $frontendExe = Join-Path $Root "app\\frontend\\src-tauri\\target\\release\\profitlift.exe"
    $frontendDir = Join-Path $Root "app\\frontend"

    if (Test-Path $frontendExe) {
        Write-Host "Launching Tauri desktop app ..."
        Start-Process -FilePath $frontendExe
        return
    }

    if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
        throw "npm not found. Please rerun scripts/windows/oneclick_setup.ps1."
    }

    Write-Host "Tauri build not found; falling back to Vite dev server."
    Start-Process -FilePath "npm.cmd" -WorkingDirectory $frontendDir -ArgumentList @("run", "dev") -WindowStyle Hidden
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:5173"
}

$repoRoot = Get-RepoRoot
Write-Host "Using ProfitLift repo at $repoRoot"

Start-Backend -Root $repoRoot -TargetPort $Port
Start-Sleep -Seconds 4
Start-Frontend -Root $repoRoot

Write-Host "ProfitLift launcher complete. To stop, close the Tauri window and end the backend process from Task Manager if it remains running."
