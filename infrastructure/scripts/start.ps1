$ErrorActionPreference = "Stop"

function Invoke-NativeCommand {
    <#
    .SYNOPSIS
        Runs a native executable and reports success by EXIT CODE, not by stderr.

    .DESCRIPTION
        docker compose writes its normal progress output — "Container
        aether-redis Started", image pulls, and similar — to STDERR, not stdout.
        Under $ErrorActionPreference = 'Stop', PowerShell 5.1 wraps every stderr
        line from a native executable in a NativeCommandError and raises it as a
        TERMINATING error. The result was that a completely successful
        `docker compose up -d` aborted this script with "Error starting
        containers", which is why start.ps1 and stop.ps1 both had to be bypassed
        manually throughout the Phase 2 remediation arc (DEBT-006).

        Exit code is the only reliable success signal for a native command, so
        this helper suppresses the stderr-to-terminating-error behaviour for the
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

    .DESCRIPTION
        Same underlying problem as Invoke-NativeCommand (see above), but for the
        health probes, which need to inspect the command's OUTPUT ("PONG",
        "accepting connections") rather than its exit code. Returns a single
        string; never throws on stderr.
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

function Test-RedisHealth {
    Write-Host "Waiting for Redis to be ready..."
    $attempts = 0
    while ($attempts -lt 15) {
        # Matches on output exactly as before; Get-NativeOutput only stops
        # redis-cli's stderr from aborting the probe.
        $pong = Get-NativeOutput { docker compose exec -T redis redis-cli ping }
        if ($pong -match "PONG") {
            return
        }
        Start-Sleep -Seconds 2
        $attempts++
    }
    Write-Host "Error: Redis failed to become ready within 30 seconds." -ForegroundColor Red
    exit 1
}

function Test-QdrantHealth {
    Write-Host "Waiting for Qdrant to be ready..."
    $attempts = 0
    while ($attempts -lt 15) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:6333/readyz" -UseBasicParsing -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                return
            }
        }
        catch {
            # Ignore and wait
        }
        Start-Sleep -Seconds 2
        $attempts++
    }
    Write-Host "Error: Qdrant failed to become ready within 30 seconds." -ForegroundColor Red
    exit 1
}

function Test-PostgresHealth {
    Write-Host "Waiting for PostgreSQL to be ready..."
    $attempts = 0
    while ($attempts -lt 15) {
        $ready = Get-NativeOutput { docker compose exec -T postgres pg_isready -U aether -d aether }
        if ($ready -match "accepting connections") {
            return
        }
        Start-Sleep -Seconds 2
        $attempts++
    }
    Write-Host "Error: PostgreSQL failed to become ready within 30 seconds." -ForegroundColor Red
    exit 1
}

function Test-ServiceHealth {
    param([int]$Port, [string]$Name)
    Write-Host "Waiting for $Name on port $Port to be ready..."
    $attempts = 0
    while ($attempts -lt 60) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:$Port/health" -UseBasicParsing -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Host "$Name is READY" -ForegroundColor Green
                return
            }
        }
        catch {
            # Ignore and wait
        }
        Start-Sleep -Seconds 2
        $attempts++
    }
    Write-Host "Error: $Name failed to become ready within 120 seconds." -ForegroundColor Red
}

function Start-AetherInfrastructure {
    $originalPath = Get-Location

    $dockerInfo = Invoke-NativeCommand { docker info *> $null }
    if ($dockerInfo -ne 0) {
        Write-Host "Error: Docker Desktop is not running. Please start Docker and try again." -ForegroundColor Red
        exit 1
    }

    $composeDir = Join-Path $PSScriptRoot "..\docker"
    Set-Location $composeDir

    Write-Host "Starting Docker containers..."
    # Progress output arrives on stderr; only a non-zero exit code means failure.
    $composeExit = Invoke-NativeCommand { docker compose up -d }
    if ($composeExit -ne 0) {
        Write-Host "Error starting containers (docker compose exited $composeExit)." -ForegroundColor Red
        Set-Location $originalPath
        exit 1
    }

    Test-RedisHealth
    Test-QdrantHealth
    Test-PostgresHealth

    Write-Host "`nGPU VRAM Status:"
    $gpu = Get-NativeOutput { nvidia-smi --query-gpu=memory.used,memory.free --format=csv,noheader }
    if ([string]::IsNullOrWhiteSpace($gpu) -or $gpu -match "not recognized|CommandNotFound") {
        Write-Host "Could not fetch GPU status (nvidia-smi not found or failed)." -ForegroundColor Yellow
    } else {
        Write-Host $gpu.Trim()
    }

    Write-Host "`nRedis: READY at localhost:6379" -ForegroundColor Green
    Write-Host "Qdrant: READY at localhost:6333 (gRPC: 6334)" -ForegroundColor Green
    Write-Host "PostgreSQL: READY at localhost:5432" -ForegroundColor Green
    
    Set-Location $originalPath

    Write-Host "`nStarting Aether Services..."
    # Start core and voice services in the background using uv run
    Start-Process powershell -ArgumentList "-NoExit -Command `"uv run python -m aether`"" -WindowStyle Hidden
    Start-Process powershell -ArgumentList "-NoExit -Command `"uv run python -m services.voice.main`"" -WindowStyle Hidden

    Test-ServiceHealth -Port 8000 -Name "Aether Core"
    Test-ServiceHealth -Port 8001 -Name "Aether Voice"

    Write-Host "Aether infrastructure and services started successfully." -ForegroundColor Green
}

Start-AetherInfrastructure
