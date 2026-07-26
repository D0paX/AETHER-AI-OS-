# Windows Environment Validation Log

**Date validated:** _______________
**Validated by:** Developer
**Script version:** validate_environment.ps1 v1.0

> **NOTE (M2.1.10, 2026-07-17):** the checklist below was never filled in — every
> box is still blank and no date was recorded, so there is no evidence M0's
> environment validation was ever actually executed. That matters: Block 6
> (`torch.cuda.is_available() == True`) is exactly the check that would have
> caught DEBT-013 years earlier than it surfaced. See the CUDA entry under
> "Issues Encountered and Resolutions".

## Block 1: Python Installation
- [ ] Python 3.12.x (non-Store): PASS / FAIL
- [ ] uv installed: PASS / FAIL
- [ ] Git installed: PASS / FAIL

## Block 2: Build Tools
- [ ] Microsoft C++ Build Tools: PASS / FAIL
- [ ] CUDA Toolkit 12.x: PASS / FAIL

## Block 3: GPU
- [ ] nvidia-smi: Driver 550+: PASS / FAIL
- [ ] VRAM ~6GB available: PASS / FAIL

## Block 4: Docker
- [ ] Docker Desktop running: PASS / FAIL
- [ ] docker compose 2.x: PASS / FAIL
- [ ] hello-world container: PASS / FAIL

## Block 5: Python Packages
- [ ] faster-whisper: PASS / FAIL
- [ ] qdrant-client: PASS / FAIL
- [ ] litellm: PASS / FAIL
- [ ] sentence-transformers: PASS / FAIL
- [ ] sounddevice: PASS / FAIL

## Block 6: CUDA Python
- [ ] torch.cuda.is_available() == True: PASS / FAIL

## Block 7: Ollama
- [ ] Ollama service reachable: PASS / FAIL
- [ ] phi4-mini model downloaded: PASS / FAIL

## Block 8: API Keys (SET/NOT SET only)
- [ ] ANTHROPIC_API_KEY: SET / NOT SET
- [ ] GOOGLE_API_KEY: SET / NOT SET
- [ ] PORCUPINE_ACCESS_KEY: SET / NOT SET

## Audio Hardware Test
- [ ] test_audio.py: PASS / FAIL
- Microphone used: _______________
- Speaker used: _______________

## Issues Encountered and Resolutions
(fill in any failures and how they were resolved)

### 2026-07-17 — CUDA torch silently reverted to the CPU-only build (M2.1.10 / DEBT-013)

**Symptom.** The entire voice pipeline was inoperative. Every transcription
failed with `STT failed: Library cublas64_12.dll is not found or cannot be
loaded`. Found during M2.1.9's required Voice Milestone regression attempt.

**Cause.** The project virtualenv had been rebuilt at some point (a `.venv.old/`
directory was left behind), and `pyproject.toml` pinned only a bare
`torch>=2.0,<3` with no CUDA index. PyPI's default Windows wheel is the
**CPU-only** build, so the rebuild resolved `torch==2.12.1+cpu`
(`torch.version.cuda = None`, `torch.cuda.is_available() = False`).
`cublas64_12.dll` ships **only inside `torch/lib`** in the CUDA build, so a
CPU-only torch leaves ctranslate2/faster-whisper with no cuBLAS to load.

**Why it was invisible.** Nothing failed at install or import time — every
dependency resolved and `import torch` succeeded. The failure only surfaced deep
inside the first real transcription call, which no automated gate exercised.

**Resolution.** `pyproject.toml` now binds torch and torchaudio to PyTorch's
CUDA 12.x index (`cu126`) using uv's documented per-package index mechanism
(`[[tool.uv.index]]` + `[tool.uv.sources]`, `explicit = true`). cu126 was chosen
because it is the CUDA 12.x index (matching this document's Block 2 and the V1
spec's "CUDA Toolkit 12.x") **and** verified to be the only 12.x index
publishing torch 2.12+/torchaudio 2.11+ for cp312 on win_amd64 — cu121, cu124,
cu128 and cu129 do not. CUDA 12.6 wheels run fine on this machine's newer driver.

**Verified after the fix:**
- `torch.cuda.is_available()` → `True` (torch 2.13.0+cu126, `torch.version.cuda` 12.6)
- Whisper `medium.en` on CUDA: VRAM **1494 MiB → 3499 MiB (+2005 MiB)** on load
- faster-whisper load **and** transcribe succeed on `device="cuda"`
- Fresh clean-environment `uv sync --extra voice` (dry-run into an empty venv)
  resolves `torch==2.13.0+cu126` and `torchaudio==2.11.0+cu126`; `uv.lock`
  records `source = { registry = "https://download.pytorch.org/whl/cu126" }`
  with **zero** CPU-torch references — so a future rebuild cannot silently
  regress to CPU again.

**For future rebuilds:** do not `pip install torch` ad hoc — run `uv sync
--extra voice`, then confirm Block 6 (`torch.cuda.is_available() == True`)
before trusting the voice pipeline. Machine of record: RTX 4050 Laptop (6GB),
driver 610.74, local CUDA Toolkit 13.3, Python 3.12.

## Final Result
- Total checks: ___
- Passed: ___
- Failed: ___
- Overall: ENVIRONMENT VALIDATED / ENVIRONMENT FAILED
