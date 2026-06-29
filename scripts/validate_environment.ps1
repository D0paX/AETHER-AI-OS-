$ErrorActionPreference = "Stop"
$global:passCount = 0
$global:failCount = 0

function Report-Pass {
    param([string]$Message)
    Write-Host "[PASS] $Message" -ForegroundColor Green
    $global:passCount++
}

function Report-Fail {
    param([string]$Message)
    Write-Host "[FAIL] $Message" -ForegroundColor Red
    $global:failCount++
}

function Test-PythonInstallation {
    Write-Host "`n--- BLOCK 1: Python Installation ---"
    try {
        $pyVer = ""
        try { $pyVer = python --version 2>&1 } catch { }
        if ($LASTEXITCODE -ne 0 -or $pyVer -notmatch "3\.12\.") {
            Report-Fail "Python 3.12.x check failed: $pyVer"
        } else {
            Report-Pass "Python version is 3.12.x ($pyVer)"
        }
        
        $pyPath = ""
        try { $pyPath = (Get-Command python -ErrorAction Stop).Source } catch { }
        if ($pyPath -match "WindowsApps") {
            Report-Fail "Python is the Microsoft Store version: $pyPath"
        } elseif ([string]::IsNullOrEmpty($pyPath)) {
            Report-Fail "Python path not found"
        } else {
            Report-Pass "Python is NOT the Microsoft Store version: $pyPath"
        }

        $uvVer = ""
        try { $uvVer = uv --version 2>&1 } catch { }
        if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrEmpty($uvVer)) { Report-Fail "uv not found" } else { Report-Pass "uv installed: $uvVer" }

        $gitVer = ""
        try { $gitVer = git --version 2>&1 } catch { }
        if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrEmpty($gitVer)) { Report-Fail "Git not found" } else { Report-Pass "Git installed: $gitVer" }
    } catch {
        Report-Fail "Python installation checks encountered an error: $_"
    }
}

function Test-BuildTools {
    Write-Host "`n--- BLOCK 2: Build Tools ---"
    try {
        $clFound = $false
        if (Get-Command cl.exe -ErrorAction SilentlyContinue) { $clFound = $true }
        else {
            $vswhere = "C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe"
            if (Test-Path $vswhere) {
                $vsPath = & $vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
                if ($vsPath) { $clFound = $true }
            }
        }
        if ($clFound) { Report-Pass "Microsoft C++ Build Tools present" } else { Report-Fail "Microsoft C++ Build Tools not found" }

        $nvccFound = $false
        if (Get-Command nvcc -ErrorAction SilentlyContinue) { $nvccFound = $true }
        else {
            $cudaPathBase = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA"
            if (Test-Path $cudaPathBase) {
                $nvccExes = Get-ChildItem -Path $cudaPathBase -Filter nvcc.exe -Recurse -ErrorAction SilentlyContinue
                if ($nvccExes.Count -gt 0) { $nvccFound = $true }
            }
        }
        if ($nvccFound) { Report-Pass "CUDA Toolkit 12.x/13.x installed" } else { Report-Fail "CUDA Toolkit not found" }
    } catch {
        Report-Fail "Build Tools checks encountered an error: $_"
    }
}

function Test-GPUValidation {
    Write-Host "`n--- BLOCK 3: GPU Validation ---"
    try {
        $smi = ""
        try { $smi = nvidia-smi 2>&1 } catch { }
        if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrEmpty($smi)) {
            Report-Fail "nvidia-smi not found or failed"
        } else {
            $smiStr = $smi -join "`n"
            if ($smiStr -match "(?:Driver|KMD) Version:\s*(\d+)") {
                $driverVer = [int]$matches[1]
                if ($driverVer -ge 550) { Report-Pass "Driver version 550+ ($driverVer)" } else { Report-Fail "Driver version too low: $driverVer" }
            } else { Report-Fail "Could not parse Driver Version" }
            
            if ($smiStr -match "6\d{3}MiB") {
                Report-Pass "VRAM ~6GB available"
            } else {
                Report-Fail "Could not verify ~6GB VRAM"
            }
        }
    } catch {
        Report-Fail "GPU Validation checks encountered an error: $_"
    }
}

function Test-DockerValidation {
    Write-Host "`n--- BLOCK 4: Docker Validation ---"
    try {
        $dInfo = ""
        try { $dInfo = docker info 2>&1 } catch { }
        if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrEmpty($dInfo)) { Report-Fail "Docker Desktop not running" } else { Report-Pass "Docker Desktop running" }

        $dcVer = ""
        try { $dcVer = docker compose version 2>&1 } catch { }
        if ($LASTEXITCODE -ne 0 -or $dcVer -notmatch "v\d+\.") { Report-Fail "docker compose not found" } else { Report-Pass "docker compose present" }

        $dRun = ""
        try { $dRun = docker run --rm hello-world 2>&1 } catch { }
        if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrEmpty($dRun)) { Report-Fail "hello-world container failed" } else { Report-Pass "hello-world container ran successfully" }
    } catch {
        Report-Fail "Docker Validation checks encountered an error: $_"
    }
}

function Test-PythonPackageValidation {
    Write-Host "`n--- BLOCK 5: Python Package Validation ---"
    $packages = @("faster_whisper", "qdrant_client", "litellm", "sentence_transformers", "sounddevice")
    foreach ($pkg in $packages) {
        try {
            $out = ""
            try { $out = python -c "import $pkg; print('OK')" 2>&1 } catch { }
            if ($LASTEXITCODE -ne 0 -or $out -notmatch "OK") { Report-Fail "$pkg failed to import" } else { Report-Pass "$pkg imported successfully" }
        } catch {
            Report-Fail "$pkg check encountered an error: $_"
        }
    }
}

function Test-CUDAPythonValidation {
    Write-Host "`n--- BLOCK 6: CUDA Python Validation ---"
    try {
        $out = ""
        try { $out = python -c "import torch; print(torch.cuda.is_available())" 2>&1 } catch { }
        if ($LASTEXITCODE -ne 0 -or $out -notmatch "True") { Report-Fail "torch.cuda.is_available() is not True" } else { Report-Pass "torch.cuda.is_available() is True" }
    } catch {
        Report-Fail "CUDA Python Validation checks encountered an error: $_"
    }
}

function Test-OllamaValidation {
    Write-Host "`n--- BLOCK 7: Ollama Validation ---"
    try {
        $tags = ""
        try { $tags = curl.exe -s http://localhost:11434/api/tags 2>&1 } catch { }
        if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrEmpty($tags)) { 
            Report-Fail "Ollama service unreachable" 
        } else { 
            Report-Pass "Ollama service reachable"
            if ($tags -match "llama3.2:3b") { Report-Pass "llama3.2:3b model downloaded" } else { Report-Fail "llama3.2:3b model not found in tags" }
        }
    } catch {
        Report-Fail "Ollama Validation checks encountered an error: $_"
    }
}

function Test-APIKeyValidation {
    Write-Host "`n--- BLOCK 8: API Key Validation ---"
    try {
        if (Test-Path ".env") {
            Get-Content ".env" | ForEach-Object {
                if ($_ -match '^\s*([^#\s][^=]*)\s*=\s*(.*)\s*$') {
                    $name = $matches[1].Trim()
                    $value = $matches[2].Trim()
                    if ($value -match '^"(.*)"$') { $value = $matches[1] }
                    [Environment]::SetEnvironmentVariable($name, $value, "Process")
                }
            }
        }
        if ([string]::IsNullOrWhiteSpace($env:AETHER_LLM__ANTHROPIC_API_KEY)) { Report-Fail "ANTHROPIC_API_KEY is NOT SET" } else { Report-Pass "ANTHROPIC_API_KEY is SET" }
        if ([string]::IsNullOrWhiteSpace($env:AETHER_LLM__GOOGLE_API_KEY)) { Report-Fail "GOOGLE_API_KEY is NOT SET" } else { Report-Pass "GOOGLE_API_KEY is SET" }
        if ([string]::IsNullOrWhiteSpace($env:AETHER_VOICE__PORCUPINE_ACCESS_KEY)) { Report-Fail "PORCUPINE_ACCESS_KEY is NOT SET" } else { Report-Pass "PORCUPINE_ACCESS_KEY is SET" }
    } catch {
        Report-Fail "API Key Validation checks encountered an error: $_"
    }
}

Write-Host "Starting Environment Validation..."
Test-PythonInstallation
Test-BuildTools
Test-GPUValidation
Test-DockerValidation
Test-PythonPackageValidation
Test-CUDAPythonValidation
Test-OllamaValidation
Test-APIKeyValidation

Write-Host "`n--- FINAL SUMMARY ---"
Write-Host "Total checks: $($global:passCount + $global:failCount)"
Write-Host "Passed: $($global:passCount)" -ForegroundColor Green
if ($global:failCount -gt 0) {
    Write-Host "Failed: $($global:failCount)" -ForegroundColor Red
    Write-Host "Environment validation FAILED. Fix all FAIL items before proceeding." -ForegroundColor Red
    exit 1
} else {
    Write-Host "Environment validation PASSED. Proceed to M1.0." -ForegroundColor Green
    exit 0
}
