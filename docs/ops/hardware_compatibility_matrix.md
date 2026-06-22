# Hardware Compatibility Matrix — Primary Test Machine

**Last Updated:** 2026-06-22

> **Policy**: The codebase MUST function as intended on the primary test machine.
> Components that require hardware not present on this machine MUST be optional
> and/or deferred — **never** forced. The workstation does not bend to fit the
> codebase; the codebase bends to fit the workstation.

---

## Primary Test Machine Specifications

| Component | Value |
|-----------|-------|
| **CPU** | Intel® Core™ Ultra 5 135U vPro® (12 cores, up to 4.4 GHz) |
| **RAM** | 16 GB DDR5-5600 |
| **Storage** | 512 GB PCIe Gen 4 NVMe SSD |
| **OS** | Windows 11 Pro (primary) / Ubuntu 22.04 (CI runner) |
| **GPU** | Intel® Arc™ integrated graphics (Xe-LP) — **no discrete GPU** |
| **CUDA** | ❌ Not available (`torch.cuda.is_available()` → `False`) |
| **NPU** | Intel® AI Boost NPU (OpenVINO path only — not PyTorch CUDA) |
| **TPU** | ❌ Not available |

---

## Compatibility Tiers

### Tier 1 — Fully Supported ✅
All code paths in this tier run on the primary test machine without modification.

| Component | Status | Notes |
|-----------|--------|-------|
| Python 3.11+ runtime | ✅ Full | All tests |
| PyTorch CPU | ✅ Full | `device="cpu"` default |
| Transformers (CPU inference) | ✅ Full | Tiny models only (memory bound at 16 GB) |
| SQLite / JSONL backends | ✅ Full | File-based storage |
| NDJSON logging | ✅ Full | |
| Hydra / OmegaConf config | ✅ Full | |
| MLflow tracking (local) | ✅ Full | File-backend only |
| Ruff / Bandit security gates | ✅ Full | 0 issues |
| rvs_env_preflight (22 packages) | ✅ Full | CPU extras only |
| BatchScanRunner API | ✅ Full | |
| BridgeLock (POSIX + Windows) | ✅ Full | msvcrt.locking on Windows |
| sandbox.py (enforce_limits=False) | ✅ Full | resource guards apply |
| fcntl (POSIX) / msvcrt (Windows) | ✅ Full | Platform-guarded in all modules |

### Tier 2 — Conditional / Graceful Degradation ⚠️
These components work but skip GPU-accelerated paths, or log a warning.

| Component | Status | Guard | Behaviour on Primary Machine |
|-----------|--------|-------|------------------------------|
| `torch.cuda.*` calls | ⚠️ Guarded | `if torch.cuda.is_available():` | No-op, CPU path used |
| `torch.backends.cudnn.*` | ⚠️ Guarded | same | No-op |
| `torch.cuda.amp.autocast` | ⚠️ Guarded | `if cuda_available:` | CPU autocast used instead |
| Mixed-precision fp16/bf16 | ⚠️ Skipped | device_strategy.py | Falls back to fp32 on CPU |
| AMP GradScaler | ⚠️ Skipped | `if cuda_available:` | Scaler disabled on CPU |
| `DataLoader(pin_memory=True)` | ⚠️ Auto-off | `torch.cuda.is_available()` | pin_memory silently no-op |
| `@skip_if_no_cuda` tests | ⚠️ Skipped | pytest mark | 147+ tests skip — correct |
| `@skip_real_st_models` tests | ⚠️ Skipped | pytest mark | SentenceTransformer CPU guard |
| `sandbox.py(enforce_limits=False)` | ⚠️ Warning | resource module check | Logs warning; runs without limits |

### Tier 3 — Deferred / N/A ❌
These components require hardware NOT present on the primary test machine.
They are **optional** and MUST NOT cause import errors or test failures.

| Component | Reason | Deferral Plan |
|-----------|--------|---------------|
| CUDA training (`device="cuda"`) | No NVIDIA GPU | S95: cloud GPU runner |
| Multi-GPU / DDP / FSDP | No NVIDIA GPU | S95: cloud GPU runner |
| NCCL distributed backend | Requires NVIDIA GPU | Deferred |
| `nvidia-*` Python wheels | Not installed | `CODEX_ABORT_ON_GPU_PULL=1` guard |
| Triton JIT kernels | Requires CUDA | Deferred |
| GPU smoke tests (B-03 GPU) | No CUDA device | **CLOSED as N/A for primary machine** |
| `torch.cuda.amp.GradScaler` (GPU) | No CUDA | Deferred to cloud runner |
| Intel Arc GPU via IPEX | Optional enhancement | Not blocking; S96+ roadmap |
| TPU / XLA training | No TPU | Deferred to cloud |
| `pgvector` extension | Requires PostgreSQL + pgvector | Deferred (no DB server) |

---

## Platform Guards — Implemented

All platform-specific imports have been guarded against Windows/CPU-only failures:

| File | Import | Guard Type |
|------|--------|-----------|
| `src/bridge_manager.py` | `import fcntl` | `if sys.platform != "win32":` + `msvcrt.locking` fallback |
| `src/codex_ml/safety/sandbox.py` | `import resource` | `try/except ImportError` |
| `src/codex/agents/memory/backends.py` | `import fcntl` | `if sys.platform != "win32":` + `_flock()` no-op on Windows |
| `src/codex/logging/import_ndjson.py` | `import fcntl` | `try/except` block |
| `src/training/data_utils.py` | `import fcntl` | `try/except` block |
| `src/codex_ml/monitoring/system_metrics.py` | `import resource` | `try/except` block |
| All CUDA paths in `src/codex_ml/training/` | `torch.cuda.*` | `if torch.cuda.is_available():` |

---

## B-03 Smoke Test — Formal Closure Decision

**Original requirement (B-03)**: "End-to-end smoke test on GPU / model endpoint"

**Hardware reality**: The primary test machine has Intel Arc integrated graphics.
`torch.cuda.is_available()` returns `False`. There is no CUDA runtime available.

**Resolution (S95)**:
- **CPU smoke suite** (20 tests in `tests/smoke/test_cpu_integration_smoke.py`) — ✅ FULLY SATISFIES B-03 for the primary test machine
- **GPU smoke suite** — marked **N/A for primary test machine**; tracked in S95 backlog as a cloud-runner-only item, NOT a blocking deployment gate for the primary machine
- **B-03 is now CLOSED** for the primary test machine. GPU testing is an enhancement, not a requirement, for `0.9.0-rc1` on this hardware.

---

## Intel Arc iGPU — OpenVINO Path (Optional S96+)

The Intel Core Ultra 5 135U includes an Intel Arc Xe-LP GPU with Intel® AI Boost NPU.
This hardware CAN accelerate inference via Intel's OpenVINO toolkit — but this is
**separate from PyTorch CUDA** and is out of scope for the current release.

Roadmap item: `S96-OV` — Intel OpenVINO backend for CPU/iGPU inference acceleration.

---

## Environment Validation

Run to confirm all Tier 1 components are present on the current machine:

```bash
# Full environment preflight
python scripts/ci/rvs_env_preflight.py

# CPU smoke suite (Tier 1 + Tier 2 verification)
python -m pytest tests/smoke/test_cpu_integration_smoke.py -v

# Windows platform compat smoke
python -c "import src.bridge_manager; import src.codex_ml.safety.sandbox; print('Platform guards OK')"

# Confirm no CUDA hard-dependency slips through
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
# Expected: CUDA available: False
```

---

*Document created: S95 (2026-02-28) — Hardware-first policy formalised.*
*Owner: @mbaetiong*
