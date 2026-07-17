$ErrorActionPreference = "Stop"

# Configuration
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupRoot = Join-Path $PSScriptRoot "..\..\backups\$timestamp"
$dataDir = Join-Path $PSScriptRoot "..\..\data"
$configDir = Join-Path $PSScriptRoot "..\..\config"

# Create backup directory
New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
Write-Host "Starting Aether backup to $backupRoot" -ForegroundColor Cyan

# 1. Health Checks
Write-Host "`n[1/7] Performing Live Health Checks..."
function Check-Endpoint {
    param([string]$Url, [string]$Name)
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "  [OK] $Name is healthy." -ForegroundColor Green
            return $true
        }
    } catch {
        Write-Host "  [FAIL] $Name at $Url is unreachable: $_" -ForegroundColor Red
        return $false
    }
}

$coreHealthy = Check-Endpoint "http://localhost:8000/health" "Aether Core"
$voiceHealthy = Check-Endpoint "http://localhost:8001/health" "Aether Voice"
$qdrantHealthy = Check-Endpoint "http://localhost:6333/readyz" "Qdrant"

if (-not ($coreHealthy -and $voiceHealthy -and $qdrantHealthy)) {
    Write-Host "Aborting backup due to unhealthy services. Ensure all services are running." -ForegroundColor Red
    Remove-Item -Path $backupRoot -Recurse -Force
    exit 1
}

# 2. SQLite Backup
Write-Host "`n[2/7] Backing up SQLite Database..."
$dbPath = Join-Path $dataDir "aether.db"
if (Test-Path $dbPath) {
    Copy-Item $dbPath -Destination $backupRoot
    Write-Host "  [OK] Copied aether.db" -ForegroundColor Green
} else {
    Write-Host "  [WARN] aether.db not found at $dbPath" -ForegroundColor Yellow
}

# 3. Qdrant Backup
Write-Host "`n[3/7] Backing up Qdrant Vector Memory..."
try {
    $snapshotUrl = "http://localhost:6333/collections/episodic_memory/snapshots"
    $response = Invoke-RestMethod -Method Post -Uri $snapshotUrl -UseBasicParsing
    if ($response.status -eq "ok") {
        $snapshotName = $response.result.name
        Write-Host "  [OK] Qdrant snapshot created: $snapshotName" -ForegroundColor Green
        
        # Download the snapshot
        $downloadUrl = "http://localhost:6333/collections/episodic_memory/snapshots/$snapshotName"
        $qdrantBackupPath = Join-Path $backupRoot $snapshotName
        Invoke-WebRequest -Uri $downloadUrl -OutFile $qdrantBackupPath -UseBasicParsing
        Write-Host "  [OK] Qdrant snapshot downloaded." -ForegroundColor Green
    } else {
        throw "Failed to create snapshot."
    }
} catch {
    Write-Host "  [WARN] Qdrant snapshot failed. Collection might not exist yet: $_" -ForegroundColor Yellow
}

# 4. Redis Backup
Write-Host "`n[4/7] Backing up Redis State..."
try {
    docker exec aether-redis redis-cli BGSAVE | Out-Null
    
    # Wait for BGSAVE to finish
    $saveDone = $false
    for ($i = 0; $i -lt 10; $i++) {
        $info = docker exec aether-redis redis-cli info persistence
        if ($info -match "rdb_bgsave_in_progress:0") {
            $saveDone = $true
            break
        }
        Start-Sleep -Seconds 1
    }
    
    if ($saveDone) {
        $redisBackupPath = Join-Path $backupRoot "dump.rdb"
        docker cp aether-redis:/data/dump.rdb $redisBackupPath
        Write-Host "  [OK] Copied Redis dump.rdb" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] Redis BGSAVE timed out." -ForegroundColor Red
    }
} catch {
    Write-Host "  [FAIL] Redis backup failed: $_" -ForegroundColor Red
}

# 5. Configuration Backup
Write-Host "`n[5/7] Backing up YAML Configuration..."
if (Test-Path $configDir) {
    $configBackupDir = Join-Path $backupRoot "config"
    New-Item -ItemType Directory -Path $configBackupDir | Out-Null
    Copy-Item -Path "$configDir\*.yaml" -Destination $configBackupDir -ErrorAction SilentlyContinue
    Write-Host "  [OK] Copied YAML configurations." -ForegroundColor Green
}

# 6. Integrity Check
Write-Host "`n[6/7] Performing Integrity Checks..."
$isVerified = $true

# Check DB size
$copiedDbPath = Join-Path $backupRoot "aether.db"
if (Test-Path $copiedDbPath) {
    $dbSize = (Get-Item $copiedDbPath).Length
    if ($dbSize -eq 0) {
        Write-Host "  [FAIL] aether.db is 0 bytes!" -ForegroundColor Red
        $isVerified = $false
    } else {
        # Check if queryable
        try {
            $queryCode = "import sqlite3; c=sqlite3.connect('$($copiedDbPath.Replace('\', '\\'))'); c.execute('SELECT name FROM sqlite_master LIMIT 1'); c.close()"
            $env:VIRTUAL_ENV = Join-Path $PSScriptRoot "..\..\.venv"
            $pythonPath = Join-Path $env:VIRTUAL_ENV "Scripts\python.exe"
            & $pythonPath -c $queryCode 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  [OK] SQLite DB is queryable." -ForegroundColor Green
            } else {
                Write-Host "  [FAIL] SQLite DB is corrupt or not queryable." -ForegroundColor Red
                $isVerified = $false
            }
        } catch {
            Write-Host "  [FAIL] SQLite DB check script failed." -ForegroundColor Red
            $isVerified = $false
        }
    }
}

# 7. Generate Manifest & Checksums
Write-Host "`n[7/7] Generating Manifest and Checksums..."
$files = Get-ChildItem -Path $backupRoot -File -Recurse
$manifest = @{
    timestamp = $timestamp
    verified = $isVerified
    files = @{}
}

foreach ($file in $files) {
    $hash = (Get-FileHash -Path $file.FullName -Algorithm SHA256).Hash
    $relativePath = $file.FullName.Replace($backupRoot + '\', '')
    $manifest.files[$relativePath] = $hash
}

$manifestPath = Join-Path $backupRoot "backup_manifest.json"
$manifest | ConvertTo-Json -Depth 5 | Out-File -FilePath $manifestPath

if ($isVerified) {
    Write-Host "`nBackup completed successfully and VERIFIED." -ForegroundColor Green
} else {
    Write-Host "`nBackup completed with ERRORS. Manifest verified=false." -ForegroundColor Yellow
}
Write-Host "Location: $backupRoot"
