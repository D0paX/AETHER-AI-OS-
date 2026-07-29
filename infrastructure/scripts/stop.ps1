$ErrorActionPreference = "Stop"
$originalPath = Get-Location

# NEVER ADD --volumes OR -v TO THIS COMMAND
# Data must be preserved.

function Invoke-NativeCommand {
    <#
    .SYNOPSIS
        Runs a native executable and reports success by EXIT CODE, not by stderr.

    .DESCRIPTION
        docker compose writes its normal progress output - "Container
        aether-redis Stopped", "Container aether-redis Removed", and similar -
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

function Stop-AetherServices {
    <#
    .SYNOPSIS
        Stop ONLY the Python services start.ps1 recorded, each verified by PID
        AND process identity (DEBT-020). Never a blanket name-match kill.

    .DESCRIPTION
        Reads .aether-runtime\service-pids.json (written by start.ps1). For each
        recorded PID it confirms a process with that ID is still running and is
        actually THIS project's venv python.exe before stopping it - a PID can be
        reused by an unrelated process after start.ps1 ran, so the identity check
        is mandatory. If the PID file is missing or unreadable, or a recorded PID
        is no longer that python.exe, it does NOT fall back to killing processes
        by name; it tells the developer to check manually. The previous
        `Stop-Process -Name "python" -Force` matched every python on the machine,
        including an IDE's own host.
    #>
    $repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
    $pidFile = Join-Path $repoRoot ".aether-runtime\service-pids.json"
    $expectedPython = Join-Path $repoRoot ".venv\Scripts\python.exe"

    if (-not (Test-Path $pidFile)) {
        Write-Host "No service PID file at $pidFile." -ForegroundColor Yellow
        Write-Host "NOT falling back to a blanket 'python' kill. If Aether services are still running, stop them manually, e.g.:" -ForegroundColor Yellow
        Write-Host "  Get-Process python -ErrorAction SilentlyContinue | Where-Object { `$_.Path -eq '$expectedPython' }" -ForegroundColor Yellow
        return
    }

    try {
        $records = Get-Content $pidFile -Raw -ErrorAction Stop | ConvertFrom-Json -ErrorAction Stop
    }
    catch {
        Write-Host "Service PID file is unreadable/corrupt: $($_.Exception.Message)" -ForegroundColor Yellow
        Write-Host "NOT falling back to a blanket 'python' kill. Check manually for orphaned Aether Python processes (path '$expectedPython')." -ForegroundColor Yellow
        return
    }

    foreach ($name in $records.PSObject.Properties.Name) {
        $servicePid = [int]$records.$name
        $proc = Get-Process -Id $servicePid -ErrorAction SilentlyContinue
        if (-not $proc) {
            Write-Host "  $name (PID $servicePid): not running (already exited)."
            continue
        }
        # A PID can be reused since start.ps1 ran - verify identity before killing.
        if ($proc.ProcessName -ne "python") {
            Write-Host "  $name (PID $servicePid): now a '$($proc.ProcessName)' process, not python - leaving it alone. Check manually for an orphaned Aether Python process." -ForegroundColor Yellow
            continue
        }
        # Stronger guard when the path is readable: confirm it is THIS venv's python.
        if ($proc.Path -and ($proc.Path -ne $expectedPython)) {
            Write-Host "  $name (PID $servicePid): a python at '$($proc.Path)', not this project's venv - leaving it alone." -ForegroundColor Yellow
            continue
        }
        Stop-Process -Id $servicePid -Force -ErrorAction SilentlyContinue
        Write-Host "  $name (PID $servicePid): stopped." -ForegroundColor Green
    }

    Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
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

    Write-Host "`nStopping Aether background services..."
    Stop-AetherServices

    Write-Host "`nVolume status:"
    Write-Host (Get-NativeOutput { docker volume ls --filter name=aether }).TrimEnd()

    Set-Location $originalPath
    exit 0
}

Stop-AetherInfrastructure
