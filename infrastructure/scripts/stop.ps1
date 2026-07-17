$ErrorActionPreference = "Stop"
$originalPath = Get-Location

# NEVER ADD --volumes OR -v TO THIS COMMAND
# Data must be preserved.

function Stop-AetherInfrastructure {
    $composeDir = Join-Path $PSScriptRoot "..\docker"
    Set-Location $composeDir

    Write-Host "Stopping Aether infrastructure..."
    try {
        docker compose down
    } catch {
        Set-Location $originalPath
        Write-Host "Error stopping containers: $_" -ForegroundColor Red
        exit 1
    }

    $running = docker compose ps -q
    if (-not [string]::IsNullOrWhiteSpace($running)) {
        Set-Location $originalPath
        Write-Host "Error: Some containers are still running!" -ForegroundColor Red
        exit 1
    }

    Write-Host "Aether infrastructure stopped. Data preserved in named volumes." -ForegroundColor Green

    Write-Host "`nStopping Aether background services (python/uv)..."
    Stop-Process -Name "python" -Force -ErrorAction SilentlyContinue
    Stop-Process -Name "uv" -Force -ErrorAction SilentlyContinue

    Write-Host "`nVolume status:"
    docker volume ls --filter name=aether

    Set-Location $originalPath
    exit 0
}

Stop-AetherInfrastructure
