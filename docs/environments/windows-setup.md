# Windows 11 Setup Guide

## 1. Prerequisites
- Windows 11 Operating System
- Intel i7-13700HX or equivalent CPU
- RTX 4050 6GB VRAM (or equivalent Nvidia GPU with 6GB+ VRAM)
- 16GB+ RAM
- Administrator access

## 2. Python Installation
1. Go to the [Python Downloads page](https://www.python.org/downloads/).
2. Download Python 3.12.x for Windows.
3. Check the box "Add Python 3.12 to PATH" during installation.
4. **WARNING:** Do NOT install Python from the Microsoft Store. It causes permissions and pathing issues.

## 3. uv Installation
Install `uv` (the Python package installer and resolver) using `winget`:
```powershell
winget install --id=astral-sh.uv  -e
```

## 4. Microsoft C++ Build Tools Installation
1. Download [Build Tools for Visual Studio](https://visualstudio.microsoft.com/visual-cpp-build-tools/).
2. Run the installer.
3. Select the **Desktop development with C++** workload.
4. Ensure the Windows SDK and MSVC v143 build tools are selected.

## 5. CUDA Toolkit 12.x Installation
1. Download [CUDA Toolkit 12.x](https://developer.nvidia.com/cuda-downloads) for Windows 11.
2. Install with the default options.
3. Verify installation in PowerShell:
```powershell
nvcc --version
```

## 6. Docker Desktop Installation
1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop).
2. Ensure the WSL2 backend is enabled in Docker settings.

## 7. Ollama Installation and Model Download
1. Download [Ollama for Windows](https://ollama.com/download).
2. Start Ollama.
3. Download the required model:
```powershell
ollama run phi4-mini
```

## 8. Python Package Installation
*Note: The actual application dependencies will be installed via `uv sync` after Milestone 1.0. For the validation script to pass, ensure you have the required packages.*

## 9. API Key Configuration
1. Copy `.env.example` to `.env`.
2. Fill in the required keys:
```
AETHER_LLM__ANTHROPIC_API_KEY=your-key-here
AETHER_LLM__GOOGLE_API_KEY=your-key-here
AETHER_VOICE__PORCUPINE_ACCESS_KEY=your-key-here
```
**Never commit the `.env` file!**

## 10. Running Validation
Run the environment validation script to verify all prerequisites:
```powershell
.\scripts\validate_environment.ps1
```

## 11. Common Windows Issues and Resolutions
- **sounddevice fails:** This is often an issue with PortAudio on Windows. Try installing PyAudio or ensuring proper C++ Build Tools are installed before compiling. Ensure microphone permissions are granted in Windows Settings -> Privacy & security -> Microphone.
- **faster-whisper build fails:** Verify Microsoft C++ Build Tools are correctly installed and added to your system PATH.
- **CUDA not found:** Verify that the CUDA bin directory is in your system PATH. Check with `nvcc --version`.
- **Docker Desktop slow:** WSL2 resource limits might be throttling performance. Create a `.wslconfig` file in your Windows user directory to allocate more memory and CPU to WSL2.
