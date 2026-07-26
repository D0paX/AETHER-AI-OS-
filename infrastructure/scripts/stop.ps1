$ErrorActionPreference = "Stop"
$originalPath = Get-Location

# NEVER ADD --volumes OR -v TO THIS COMMAND
# Data must be preserved.

function Invoke-NativeCommand {
    <#
    .SYNOPSIS
        Runs a native executable and reports success by EXIT CODE, not by stderr.

    .DESCRIPTION
        docker compose writes its normal progress output — "Container
        aether-redis Stopped", "Container aether-redis Removed", and similar —
        to STDERR, not stdout. Under $ErrorActionPreference = 'Stop',
        PowerShell 5.1 wraps every stderr line from a native executable in a
        NativeCommandError and raises it as a TERMINATING error, so a completely
        successful `docker compose down` aborted this script with "Error
        stopping containers". That is why start.ps1 and stop.ps1 both had to be
        bypassed manually throughout the Phase 2 remediation arc (DEBT-006).

        Exit code is the only reliable success signal for a native command, so
        this helper relaxes the stderr-to-terminating-error behaviour for the
        duration of the call, lets output through to the console untouched, and
        returns the process exit code.
    #>
    param(
        [Parameter(Mandatory = $true)][scriptblock]$Command
    )

    $previous = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        # Merge stderr into the output stream and render every line as plain
        # text. Without this, PowerShell formats each stderr line as a red
        # NativeCommandError block ("At line:N char:M ... CategoryInfo ..."),
        # which reads as a failure even though the command succeeded.
        & $Command 2>&1 | ForEach-Object { Write-Host $_ }
        return $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previous
    }
}

function Get-NativeOutput {
    <#
    .SYNOPSIS
        Captures a native command's combined output as text, without letting its
        stderr become a terminating error.
    #>
    param(
        [Parameter(Mandatory = $true)][scriptblock]$Command
    )

    $previous = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        return (& $Command 2>&1 | Out-String)
    }
    finally {
        $ErrorActionPreference = $previous
    }
}

function Stop-AetherInfrastructure {
    $composeDir = Join-Path $PSScriptRoot "..\docker"
    Set-Location $composeDir

    Write-Host "Stopping Aether infrastructure..."
    # Progress output arrives on stderr; only a non-zero exit code means failure.
    $downExit = Invoke-NativeCommand { docker compose down }
    if ($downExit -ne 0) {
        Set-Location $originalPath
        Write-Host "Error stopping containers (docker compose exited $downExit)." -ForegroundColor Red
        exit 1
    }

    $running = (Get-NativeOutput { docker compose ps -q }).Trim()
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
    Write-Host (Get-NativeOutput { docker volume ls --filter name=aether }).TrimEnd()

    Set-Location $originalPath
    exit 0
}

Stop-AetherInfrastructure
