<!-- BEGIN: PRIMARY_TEST_MACHINE -->

# Primary Test Machine — Hardware Registration

## Table of Contents

- [Hardware Specifications](#hardware-specifications)
- [Capability Assessment](#capability-assessment)
  - [1. Python Runtime & Core Dependencies](#1-python-runtime--core-dependencies)
  - [2. GPU / CUDA — ❌ Not Available](#2-gpu--cuda---not-available)
- [PowerShell — set for current session](#powershell--set-for-current-session)
- [3. TPU — ❌ Not Available](#3-tpu---not-available)
  - [4. Distributed / Multi-GPU Training — ❌ Not Available](#4-distributed--multi-gpu-training---not-available)
  - [5. Mixed Precision / Quantization — ❌ / ⚠️](#5-mixed-precision--quantization----)
  - [6. Windows OS Compatibility](#6-windows-os-compatibility)
    - [6a. Shell Scripts — ❌ Not Directly Runnable](#6a-shell-scripts---not-directly-runnable)
    - [6b. POSIX-Only Python APIs](#6b-posix-only-python-apis)
    - [6c. PyTorch on Windows](#6c-pytorch-on-windows)
    - [6d. File Paths](#6d-file-paths)
  - [7. Memory — 16 GB RAM](#7-memory--16-gb-ram)
  - [8. Storage — 512 GB PCIe SSD](#8-storage--512-gb-pcie-ssd)
  - [9. CPU Performance — Intel Core Ultra 5 135U](#9-cpu-performance--intel-core-ultra-5-135u)
  - [10. What Is Fully Deferred on This Machine](#10-what-is-fully-deferred-on-this-machine)
- [Recommended Local Environment Setup (Windows 11)](#recommended-local-environment-setup-windows-11)
- [1. Install Python 3.12 for Windows from python.org](#1-install-python-312-for-windows-from-pythonorg)
- [2. Clone the repo and create a venv](#2-clone-the-repo-and-create-a-venv)
- [3. Install CPU-only torch first (avoids pulling CUDA wheels)](#3-install-cpu-only-torch-first-avoids-pulling-cuda-wheels)
- [4. Install the project in editable mode](#4-install-the-project-in-editable-mode)
- [5. Set machine-specific env vars (add to your shell profile)](#5-set-machine-specific-env-vars-add-to-your-shell-profile)
- [6. Run the baseline test suite (no GPU/ML deps)](#6-run-the-baseline-test-suite-no-gpuml-deps)
- [Environment Variables Summary](#environment-variables-summary)

**Last Updated:** 2026-06-22

> **Registered:** 2026-02-28  
> **Status:** Active — primary local development and test runner  
> **Maintained by:** @mbaetiong

## Hardware Specifications

| Component | Specification |
|-----------|--------------|
| **Processor** | 1× Intel® Core™ Ultra 5 135U vPro® |
| **CPU Cores** | 12 cores (2 Performance + 8 Efficient + 2 Low-Power Efficient), ~15 W TDP |
| **Memory** | 2× 8 GB DDR5-5600 (16 GB total, dual-channel) |
| **Operating System** | Windows 11 Pro (EN: English) |
| **Storage** | 1× 512 GB SSD PCIe |
| **GPU** | Intel® Arc™ integrated graphics (no discrete NVIDIA/AMD GPU) |
| **Accelerators** | None — no TPU, no NPU for ML inference beyond Intel® AI Boost |

---

## Capability Assessment

The sections below catalogue every codebase feature against this machine.
Each item is rated **✅ Works** · **⚠️ Degraded** · **❌ Will Not Work**.

---

### 1. Python Runtime & Core Dependencies

| Feature | Status | Notes |
|---------|--------|-------|
| Python ≥ 3.12 (`requires-python = ">=3.12"`) | ✅ Works | Install Python 3.12 for Windows from python.org |
| `pip install -e .[dev]` | ✅ Works | Windows-native wheels available for all core deps |
| `pytest` test suite (baseline, non-ML) | ✅ Works | Full baseline suite runnable |
| `black` / `ruff` / `isort` / `mypy` | ✅ Works | Pure-Python; cross-platform |
| `nox -s tests` (baseline session) | ✅ Works | No GPU deps in baseline session |

---

### 2. GPU / CUDA — ❌ Not Available

This machine has **no NVIDIA GPU and no CUDA runtime**. The integrated Intel Arc
graphics does **not** expose a CUDA interface.

| Feature | Status | Notes |
|---------|--------|-------|
| `torch.cuda.is_available()` | ❌ Returns `False` | No NVIDIA driver |
| CUDA-accelerated training (`device="cuda"`) | ❌ Will Not Work | Falls back to CPU automatically where guarded |
| `torch.cuda.amp.GradScaler` / mixed-precision fp16/bf16 | ❌ Will Not Work | AMP requires CUDA; CPU path skips scaler |
| `nvidia-*` Python wheels (nvidia-cublas, etc.) | ❌ Not installed | `CODEX_ABORT_ON_GPU_PULL=1` prevents accidental pull |
| `triton` JIT kernels | ❌ Will Not Work | Triton requires CUDA; CPU-only builds have no Triton |
| `torch.compile` with Triton/Inductor backend | ❌ Will Not Work | Falls back to eager mode |
| `pin_memory=True` in DataLoaders | ⚠️ No-op | `torch.cuda.is_available()` is `False`; code auto-disables |
| CUDA-guarded tests (`@skip_if_no_cuda`) | ⚠️ Skipped | 147+ tests will be skipped, not failed — correct behaviour |

**Mitigation already in codebase:**  
Set `CODEX_FORCE_CPU=1` in your environment. The training stack checks
`torch.cuda.is_available()` before enabling any GPU path; all production paths
have CPU fallbacks.

```powershell
# PowerShell — set for current session
$env:CODEX_FORCE_CPU = "1"
$env:CODEX_ALLOW_TRITON_CPU = "1"
```

---

## 3. TPU — ❌ Not Available

There is no Google Cloud TPU, TPU Pod, or `torch_xla` runtime on this machine.

| Feature | Status | Notes |
|---------|--------|-------|
| `device="tpu"` in `ModelConfig` | ❌ Will Not Work | No `torch_xla` installed; model loader raises |
| `torch_xla` / XLA compilation | ❌ Will Not Work | Not installable without TPU hardware or GCP VM |
| JAX with TPU backend | ❌ Will Not Work | JAX is not a declared dependency; TPU unavailable |

**Affected code:**  
- `tests/codex_ml/test_inference_server.py:87` — `device="tpu"` test path  
- `tests/serving/test_model_loader.py:56` — TPU device config test  

Both test files use stub `ModelConfig` and do not require real TPU hardware, but
any path that actually attempts to move tensors to a TPU device will fail at
runtime. Ensure these tests remain stub-only or are skipped under
`pytest.mark.skipif(not tpu_available(), ...)`.

---

### 4. Distributed / Multi-GPU Training — ❌ Not Available

| Feature | Status | Notes |
|---------|--------|-------|
| NCCL backend (`backend="nccl"`) | ❌ Will Not Work | NCCL requires NVIDIA GPUs |
| `torch.distributed.init_process_group` (NCCL) | ❌ Will Not Work | Falls back to `gloo` on CPU-only — single process only |
| `DistributedDataParallel` (DDP) | ❌ Will Not Work | Requires multiple CUDA devices |
| FSDP (`src/codex_ml/training/fsdp_wrapper.py`) | ❌ Will Not Work | Requires CUDA; `FSDP = None` fallback activates |
| Multi-node orchestration (`multi_node_orchestration.py`) | ❌ Will Not Work | Requires cluster GPUs + NCCL |
| `gloo` backend (CPU distributed) | ⚠️ Degraded | Usable for local multi-process CPU experiments only; not for production training |

---

### 5. Mixed Precision / Quantization — ❌ / ⚠️

| Feature | Status | Notes |
|---------|--------|-------|
| `fp16` / `bf16` training (`--fp16`, `--bf16` CLI flags) | ❌ Will Not Work | Requires CUDA AMP; CPU training uses `fp32` only |
| `bitsandbytes` INT8/INT4 quantization | ❌ Will Not Work | `bitsandbytes` has no CPU-only mode; CUDA required |
| `torch.quantization` (static/dynamic, CPU) | ✅ Works | PyTorch's native CPU quantization works on x86 |

---

### 6. Windows OS Compatibility

The codebase targets Linux as its primary platform. The following items need
attention when running on Windows 11.

#### 6a. Shell Scripts — ❌ Not Directly Runnable

There are **192 `.sh` scripts** in the repository (CI helpers, Docker entrypoints,
setup scripts, pre-commit hooks). None run natively in CMD or PowerShell.

| Script area | Status | Workaround |
|-------------|--------|-----------|
| `.github/scripts/*.sh`, `.github/workflows` | ⚠️ CI-only | Run in GitHub Actions (Linux runners) |
| `docker/entrypoint.sh`, `docker/ci_run.sh` | ⚠️ Docker | Run inside Docker container |
| `deploy/setup_universal.sh` | ⚠️ Linux | Use WSL 2 or Docker |
| `scripts/gpu/check_gpu.sh` | ❌ N/A | No NVIDIA GPU; skip |
| `.pre-commit-scripts/*.sh` | ⚠️ WSL/Git Bash | Install Git for Windows (provides bash) or WSL 2 |

**Recommended fix:** Install **WSL 2** (Windows Subsystem for Linux) or run all
shell-dependent operations inside Docker.

#### 6b. POSIX-Only Python APIs

| Module / API | Status | Notes |
|-------------|--------|-------|
| `fcntl` (file locking) | ⚠️ Gracefully degraded | `training/data_utils.py` and `src/training/data_utils.py` catch `ImportError` and fall back to unlocked write — safe for single-process use |
| `src/bridge_manager.py:17 import fcntl` | ✅ Fixed (S92) | Wrapped in `try/except ImportError`; `BridgeLock.acquire()` returns `True` (no-op) on Windows — safe for single-process use |
| `resource` module (`RLIMIT_*`) | ✅ Fixed (S92) | `src/codex_ml/safety/sandbox.py` now guards `import resource` with `try/except ImportError`; `_limits()` is a no-op when `_HAS_RESOURCE=False` |
| `signal.SIGHUP` | ❌ Not on Windows | `tests/cli/test_cli_edge_cases_phase26.py` skips when SIGHUP unavailable |
| `os.symlink` (checkpoint best-symlink) | ⚠️ Requires admin | `training/checkpoint_manager.py` uses `os.symlink`; Windows requires Developer Mode or elevated prompt |
| `psutil` | ✅ Works | Cross-platform; available for Windows |

#### 6c. PyTorch on Windows

| Item | Status | Notes |
|------|--------|-------|
| `torch` CPU-only wheel | ✅ Works | Use `--extra-index-url https://download.pytorch.org/whl/cpu` |
| `torch` with CUDA on Windows | ❌ N/A | No NVIDIA GPU |
| `torch` extras marked `platform_system != 'Windows'` | ⚠️ Skipped by pip | Three optional dependency groups exclude Windows — this is intentional |
| `DataLoader num_workers > 0` | ⚠️ Requires guard | On Windows, multiprocessing DataLoaders require `if __name__ == "__main__"` guard; tests using `num_workers=4` may hang without it |

#### 6d. File Paths

Windows uses backslashes and has reserved filenames (`CON`, `PRN`, `AUX`, `NUL`,
`COM*`, `LPT*`) and illegal characters (`< > : " / \ | ? *`).

| Item | Status | Notes |
|------|--------|-------|
| Path separators | ✅ Works | Codebase uses `pathlib.Path` throughout |
| Windows-illegal filenames in generated artifacts | ✅ Validated | `tests/integration/test_cross_platform_filenames.py` enforces this |
| `windows_safe_timestamp()` utility | ✅ Works | Use `codex.utils.path_utils.windows_safe_timestamp()` for timestamp filenames |

---

### 7. Memory — 16 GB RAM

| Workload | Status | Notes |
|----------|--------|-------|
| Unit / integration tests | ✅ Works | Baseline tests use < 2 GB |
| Small model fine-tuning (< 1 B params, CPU) | ✅ Works | `sshleifer/tiny-gpt2` and stub models fit easily |
| Medium model inference (7 B params, CPU) | ⚠️ Degraded | 7 B model in `fp32` needs ~28 GB; **exceeds 16 GB RAM** — use quantized or smaller models |
| Large model training (≥ 1 B params) | ❌ Will Not Work | OOM; requires GPU VRAM or machine with ≥ 32 GB RAM |
| RAG with large embedding indexes (FAISS) | ⚠️ Degraded | Large corpora may exhaust RAM; limit index size |
| `pin_memory=True` DataLoader | ⚠️ No-op | Silently disabled when CUDA unavailable |

**Recommendation:** For local development, use `sshleifer/tiny-gpt2` or other
sub-125 M parameter stubs. Set `CODEX_FORCE_CPU=1` and avoid loading production
model weights locally.

---

### 8. Storage — 512 GB PCIe SSD

| Item | Estimated Size | Status |
|------|---------------|--------|
| Repository + Python venv | ~2–4 GB | ✅ Fine |
| PyTorch CPU wheel | ~200 MB | ✅ Fine |
| Transformers model cache (one 7B model) | ~14 GB | ⚠️ Cumulative risk |
| FAISS index for large corpus | 1–10 GB | ⚠️ Monitor |
| Full HuggingFace model cache (several models) | 30–100 GB | ⚠️ Set `HF_HOME` to a managed path |
| CI artifact history | Managed by GitHub | ✅ Not local |

**Recommendation:** Set `HF_HOME` and `TRANSFORMERS_CACHE` to a dedicated
folder and periodically prune unused model weights.

---

### 9. CPU Performance — Intel Core Ultra 5 135U

This is a **mobile (laptop) processor** with a 15 W TDP, designed for battery
life and responsiveness, not sustained compute throughput.

| Task | Status | Notes |
|------|--------|-------|
| Running Python tests | ✅ Works | Fast for unit tests; slow tests may take longer than on desktop |
| CPU training (small models, dev loops) | ⚠️ Degraded | Training throughput is roughly 10–50× slower than a GPU workstation |
| Inference with small models | ✅ Works | Acceptable latency for < 125 M param models |
| `torch.compile` (eager fallback) | ✅ Works | Torch compile falls back to eager without Triton |
| Parallelism — `num_workers` > 0 in DataLoader | ⚠️ Limited | 12 logical cores; cap `num_workers` at 4–6 to avoid thermal throttling |
| Long nox / pytest sessions | ⚠️ Thermal throttle risk | The 135U will throttle under sustained load; use test selection (`-k`) to keep sessions short |

---

### 10. What Is Fully Deferred on This Machine

The table below is the canonical list of codebase features that are **deferred
to a GPU workstation or CI** for this primary test machine.

| Feature | Reason Deferred | Where to Run Instead |
|---------|----------------|---------------------|
| CUDA-accelerated training | No NVIDIA GPU | GitHub Actions (GPU runner) or cloud VM |
| Mixed-precision training (fp16/bf16) | No CUDA AMP | GitHub Actions / cloud VM |
| TPU execution (`device="tpu"`) | No TPU hardware | Google Cloud TPU VM |
| NCCL multi-GPU distributed training | No multi-GPU | Multi-GPU cloud instance |
| FSDP large-model sharding | No GPU / RAM | Multi-GPU cloud instance |
| `bitsandbytes` INT8/INT4 quantization | CUDA required | GPU instance |
| `triton` JIT kernels | CUDA required | GitHub Actions / GPU runner |
| Shell script execution (`.sh` files) | Windows OS | WSL 2 or GitHub Actions |
| `src/bridge_manager.py` (hard `fcntl` import) | ✅ Fixed S92 | Guarded with `try/except ImportError` + `_HAS_FCNTL` flag |
| `src/codex_ml/safety/sandbox.py` (bare `resource` import) | ✅ Fixed S92 | Guarded with `try/except ImportError` + `_HAS_RESOURCE` flag |
| GPU vendor wheel validation (`nvidia-*` / `triton` guard) | No GPU | CI vendor-guard session |
| Sustained long-running training runs | Mobile CPU thermal limits | Workstation / cloud |

---

## Recommended Local Environment Setup (Windows 11)

```powershell
# 1. Install Python 3.12 for Windows from python.org

# 2. Clone the repo and create a venv
python -m venv .venv
.venv\Scripts\Activate.ps1

# 3. Install CPU-only torch first (avoids pulling CUDA wheels)
pip install torch==2.6.0+cpu --extra-index-url https://download.pytorch.org/whl/cpu

# 4. Install the project in editable mode
pip install -e ".[dev]"

# 5. Set machine-specific env vars (add to your shell profile)
$env:CODEX_FORCE_CPU    = "1"
$env:CODEX_ALLOW_TRITON_CPU = "1"
$env:HF_HOME            = "C:\Users\<you>\.cache\huggingface"

# 6. Run the baseline test suite (no GPU/ML deps)
python -m pytest -m "not slow and not cuda" --tb=short -q
```

> **WSL 2 (recommended for shell scripts and POSIX compatibility):**  
> Install WSL 2 with Ubuntu 22.04 from the Microsoft Store. All `.sh` scripts
> and POSIX-only APIs run without modification inside WSL 2.

---

## Environment Variables Summary

| Variable | Recommended Value | Purpose |
|----------|------------------|---------|
| `CODEX_FORCE_CPU` | `1` | Force CPU execution everywhere |
| `CODEX_ALLOW_TRITON_CPU` | `1` | Allow residual triton package without aborting |
| `CODEX_ABORT_ON_GPU_PULL` | `0` | Don't abort on detection (no GPU wheels present) |
| `HF_HOME` | `C:\Users\<you>\.cache\huggingface` | Prevent model cache from filling OS drive |
| `TRANSFORMERS_CACHE` | same as `HF_HOME` | Legacy alias |

<!-- END: PRIMARY_TEST_MACHINE -->
