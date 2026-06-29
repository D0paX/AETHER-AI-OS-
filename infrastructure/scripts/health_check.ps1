$ErrorActionPreference = "Stop"
$originalPath = Get-Location

$dockerStatus = "NOT RUNNING"
$redisStatus = "UNHEALTHY"
$redisReason = "Unknown"
$qdrantStatus = "UNHEALTHY"
$qdrantReason = "Unknown"
$isHealthy = $true

try {
    $null = docker info 2>&1
    if ($LASTEXITCODE -eq 0) {
        $dockerStatus = "RUNNING"
    } else {
        $isHealthy = $false
    }
} catch {
    $isHealthy = $false
}

$composeDir = Join-Path $PSScriptRoot "..\docker"
Set-Location $composeDir

try {
    $pong = docker compose exec -T redis redis-cli ping 2>&1
    if ($pong -match "PONG") {
        $redisStatus = "HEALTHY"
        $redisReason = ""
        $keys = docker compose exec -T redis redis-cli DBSIZE 2>&1
        Write-Host "Redis keys: $keys"
    } else {
        $redisReason = "Did not receive PONG"
        $isHealthy = $false
    }
} catch {
    $redisReason = "Container unreachable"
    $isHealthy = $false
}

try {
    $response = Invoke-WebRequest -Uri "http://localhost:6333/readyz" -UseBasicParsing -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200 -and $response.Content -match "ready") {
        $qdrantStatus = "HEALTHY"
        $qdrantReason = ""
        $collections = Invoke-WebRequest -Uri "http://localhost:6333/collections" -UseBasicParsing -ErrorAction SilentlyContinue
        Write-Host "Qdrant collections response: $($collections.Content)"
    } else {
        $qdrantReason = "Bad status code or content"
        $isHealthy = $false
    }
} catch {
    $qdrantReason = "Container unreachable"
    $isHealthy = $false
}

Write-Host "`nInfrastructure Health Summary:"
if ($dockerStatus -eq "RUNNING") {
    Write-Host "  Docker:  $dockerStatus" -ForegroundColor Green
} else {
    Write-Host "  Docker:  $dockerStatus" -ForegroundColor Red
}

if ($redisStatus -eq "HEALTHY") {
    Write-Host "  Redis:   $redisStatus" -ForegroundColor Green
} else {
    Write-Host "  Redis:   $redisStatus ($redisReason)" -ForegroundColor Red
}

if ($qdrantStatus -eq "HEALTHY") {
    Write-Host "  Qdrant:  $qdrantStatus" -ForegroundColor Green
} else {
    Write-Host "  Qdrant:  $qdrantStatus ($qdrantReason)" -ForegroundColor Red
}

if ($isHealthy) {
    Set-Location $originalPath
    exit 0
} else {
    Set-Location $originalPath
    exit 1
}
