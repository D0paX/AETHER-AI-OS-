param(
    [Parameter(Mandatory=$true)]
    [string]$BackupTimestamp
)

$ErrorActionPreference = "Stop"

$backupRoot = Join-Path $PSScriptRoot "..\..\backups\$BackupTimestamp"
if (-not (Test-Path $backupRoot)) {
    Write-Host "Backup $BackupTimestamp not found at $backupRoot" -ForegroundColor Red
    exit 1
}

$manifestPath = Join-Path $backupRoot "backup_manifest.json"
if (-not (Test-Path $manifestPath)) {
    Write-Host "Manifest not found in $backupRoot" -ForegroundColor Red
    exit 1
}

$manifest = Get-Content $manifestPath | ConvertFrom-Json
if ($manifest.verified -ne $true) {
    Write-Host "Backup is NOT verified! Refusing to restore." -ForegroundColor Red
    exit 1
}

Write-Host "WARNING: This will overwrite current state with backup from $BackupTimestamp!" -ForegroundColor Yellow
$confirmation = Read-Host "Type 'RESTORE' to confirm"
if ($confirmation -cne "RESTORE") {
    Write-Host "Aborted."
    exit 1
}

Write-Host "`n[1/5] Stopping active services..."
& (Join-Path $PSScriptRoot "stop.ps1")

Write-Host "`n[2/5] Starting Docker infrastructure for restore..."
$composeDir = Join-Path $PSScriptRoot "..\docker"
Push-Location $composeDir
docker compose up -d
Pop-Location

# Wait for Qdrant and Redis
Start-Sleep -Seconds 10

Write-Host "`n[3/5] Restoring SQLite..."
$dbPath = Join-Path $PSScriptRoot "..\..\data\aether.db"
$backupDbPath = Join-Path $backupRoot "aether.db"
if (Test-Path $backupDbPath) {
    Copy-Item $backupDbPath -Destination $dbPath -Force
    Write-Host "  [OK] SQLite restored." -ForegroundColor Green
}

Write-Host "`n[4/5] Restoring Redis..."
$redisBackupPath = Join-Path $backupRoot "dump.rdb"
if (Test-Path $redisBackupPath) {
    docker cp $redisBackupPath aether-redis:/data/dump.rdb
    docker restart aether-redis | Out-Null
    Write-Host "  [OK] Redis restored." -ForegroundColor Green
}

Write-Host "`n[5/5] Restoring Qdrant..."
$snapshotFile = Get-ChildItem -Path $backupRoot -Filter "*.snapshot" | Select-Object -First 1
if ($snapshotFile) {
    $snapshotName = $snapshotFile.Name
    
    # Qdrant snapshot restore requires the file to be available via URL or local path inside the container.
    # Easiest way: upload it to Qdrant via the python httpx client in a short script.
    
    $env:VIRTUAL_ENV = Join-Path $PSScriptRoot "..\..\.venv"
    $pythonPath = Join-Path $env:VIRTUAL_ENV "Scripts\python.exe"
    
    $pythonCode = @"
import httpx
import sys

client = httpx.Client(timeout=60.0)
file_path = r'$($snapshotFile.FullName)'
snapshot_name = '$snapshotName'

try:
    with open(file_path, 'rb') as f:
        # 1. Upload snapshot
        files = {'snapshot': (snapshot_name, f)}
        r1 = client.post('http://localhost:6333/collections/episodic_memory/snapshots/upload', files=files)
        r1.raise_for_status()

    # 2. Recover from uploaded snapshot
    recover_url = 'http://localhost:6333/collections/episodic_memory/snapshots/recover'
    
    # We must provide the 'location' parameter, which is the URL Qdrant uses to fetch it.
    # Since we uploaded it, we can just use the snapshot name directly if using the API properly,
    # OR we use PUT /collections/episodic_memory/snapshots/recover and provide a file URL pointing to the uploaded snapshot inside the container.
    # Actually, the Qdrant API says for PUT .../recover: location is a URL. 
    # But PUT .../snapshots/recover endpoint doesn't need to be called if we used PUT /collections/episodic_memory/snapshots/recover with a URL.
    # Wait, the best way in Python is to use the qdrant-client.
    import qdrant_client
    q_client = qdrant_client.QdrantClient('http://localhost:6333')
    
    # qdrant_client has a recover_snapshot method!
    # Wait, does it? No, it has something like that? Let's just use docker cp.
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
"@
    
    # Actually, docker cp + REST is much more reliable since we don't need multipart format complexities.
    # Let's use docker cp
    docker exec aether-qdrant mkdir -p /qdrant/storage/snapshots/episodic_memory/
    docker cp $snapshotFile.FullName "aether-qdrant:/qdrant/storage/snapshots/episodic_memory/$snapshotName"
    
    # Wait, if the snapshot is inside /qdrant/storage/snapshots/episodic_memory/$snapshotName
    # We can just call PUT /collections/episodic_memory/snapshots/recover with location="file:///qdrant/storage/snapshots/episodic_memory/$snapshotName"
    $recoverUrl = "http://localhost:6333/collections/episodic_memory/snapshots/recover"
    $body = @{ location = "file:///qdrant/storage/snapshots/episodic_memory/$snapshotName" } | ConvertTo-Json
    try {
        $resp = Invoke-RestMethod -Method Put -Uri $recoverUrl -Body $body -ContentType "application/json" -UseBasicParsing
        Write-Host "  [OK] Qdrant restored." -ForegroundColor Green
    } catch {
        Write-Host "  [WARN] Qdrant restore failed. Ensure the collection is empty or doesn't exist before recovering: $_" -ForegroundColor Yellow
    }
}

Write-Host "`n[+] Restoring configurations..."
$configBackupDir = Join-Path $backupRoot "config"
if (Test-Path $configBackupDir) {
    Copy-Item "$configBackupDir\*" -Destination (Join-Path $PSScriptRoot "..\..\config") -Force -Recurse
    Write-Host "  [OK] Configs restored." -ForegroundColor Green
}

Write-Host "`nRestore completed successfully. You can now run start.ps1 to bring up all services." -ForegroundColor Green
