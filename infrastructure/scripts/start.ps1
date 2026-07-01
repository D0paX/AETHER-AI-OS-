$ErrorActionPreference = "Stop"

function Test-RedisHealth {
    Write-Host "Waiting for Redis to be ready..."
    $attempts = 0
    while ($attempts -lt 15) {
        try {
            $pong = docker compose exec -T redis redis-cli ping 2>&1
            if ($pong -match "PONG") {
                return
            }
        }
        catch {
            # Ignore and wait
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

function Start-AetherInfrastructure {
    $originalPath = Get-Location

    try {
        docker info | Out-Null
    } catch {
        Write-Host "Error: Docker Desktop is not running. Please start Docker and try again." -ForegroundColor Red
        exit 1
    }

    $composeDir = Join-Path $PSScriptRoot "..\docker"
    Set-Location $composeDir

    Write-Host "Starting Docker containers..."
    try {
        docker compose up -d
    } catch {
        Write-Host "Error starting containers: $_" -ForegroundColor Red
        Set-Location $originalPath
        exit 1
    }

    Test-RedisHealth
    Test-QdrantHealth

    Write-Host "`nGPU VRAM Status:"
    try {
        nvidia-smi --query-gpu=memory.used,memory.free --format=csv,noheader
    } catch {
        Write-Host "Could not fetch GPU status (nvidia-smi not found or failed)." -ForegroundColor Yellow
    }

    Write-Host "`nRedis: READY at localhost:6379" -ForegroundColor Green
    Write-Host "Qdrant: READY at localhost:6333 (gRPC: 6334)" -ForegroundColor Green
    Write-Host "Aether infrastructure started successfully." -ForegroundColor Green
    
    Set-Location $originalPath
}

Start-AetherInfrastructure
