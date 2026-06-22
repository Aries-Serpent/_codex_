# Intel OpenVINO Optional iGPU Acceleration Path

**Last Updated:** 2026-06-22

**Status**: 🟢 Phase C Complete — S100 (P10-05 / P11-03)
- Phase A ✅ (architecture doc — S97)
- Phase B ✅ (backend skeleton `src/codex_ml/backends/openvino_backend.py` + 11 smoke tests — S98)
- Phase C ✅ (CI iGPU smoke test on Intel Arc runner — S100; `TestOpenVINOPhaseC` + `openvino-phase-c.yml`)
**Tier**: Tier 2 (Optional / Gracefully Degraded)  
**Hardware target**: Intel Core Ultra 5 135U vPro — Intel Arc iGPU + AI Boost NPU  
**Dependency**: `openvino` (optional; not installed by default)

---

## Overview

The primary test machine includes an **Intel Arc integrated GPU** (Xe-LPG architecture)
and an **Intel AI Boost NPU** via the Core Ultra (Meteor Lake) platform.
Neither of these accelerators supports CUDA.  OpenVINO is Intel's cross-platform
inference acceleration toolkit that targets:

| Device | OpenVINO plugin | Notes |
|--------|----------------|-------|
| CPU | `CPU` | Always available; already active |
| Intel Arc iGPU | `GPU` | Xe-LPG via OpenCL |
| AI Boost NPU | `NPU` | INT8/INT4 quantised models only |

---

## Hardware Tier Policy

Per `docs/ops/hardware_compatibility_matrix.md`:

| Feature | Tier | Guard |
|---------|------|-------|
| CPU inference | 1 | None needed |
| OpenVINO GPU inference | 2 | `try: import openvino except ImportError` |
| OpenVINO NPU inference | 2 | `try: import openvino except ImportError` + device availability check |
| CUDA / NVIDIA GPU | 3 | Deferred — N/A for primary test machine |

---

## Integration Plan

### Phase A — Package guard (prerequisite)

Add `openvino` as an optional dependency in `pyproject.toml`:

```toml
[project.optional-dependencies]
openvino = ["openvino>=2024.0"]
```

Install with: `pip install -e ".[openvino]"`

### Phase B — Backend detection helper

Create `src/codex_ml/backends/openvino_backend.py`:

```python
"""Optional Intel OpenVINO inference backend.

Falls back to CPU-only PyTorch when OpenVINO is not installed or
the requested device is unavailable.
"""
from __future__ import annotations

try:
    from openvino.runtime import Core  # type: ignore[import]
    _OV_AVAILABLE = True
except ImportError:
    _OV_AVAILABLE = False

DEVICES: list[str] = []

if _OV_AVAILABLE:
    try:
        _core = Core()
        DEVICES = _core.available_devices  # e.g. ['CPU', 'GPU', 'NPU']
    except Exception:  # noqa: BLE001 – OpenVINO init can raise various errors
        pass


def is_available(device: str = "GPU") -> bool:
    """Return True if the specified OpenVINO device is present."""
    return _OV_AVAILABLE and device in DEVICES
```

### Phase C — CI smoke test

Add `tests/smoke/test_openvino_optional.py`:

```python
import pytest

try:
    from codex_ml.backends.openvino_backend import DEVICES, is_available
    _HAS_OV = True
except ImportError:
    _HAS_OV = False

pytestmark = pytest.mark.skipif(not _HAS_OV, reason="openvino not installed")


def test_openvino_cpu_always_present() -> None:
    """OpenVINO CPU plugin is always available when openvino is installed."""
    assert is_available("CPU")


def test_openvino_gpu_detection() -> None:
    """GPU device detection does not raise — result depends on hardware."""
    result = is_available("GPU")
    assert isinstance(result, bool)
```

### Phase D — Model inference integration (future)

Wire the backend into `src/codex_ml/inference/` dispatcher once
the backend is validated on the primary test machine.

---

## Validation Commands

```bash
# Install optional dependency
pip install openvino>=2024.0

# Verify device discovery
python -c "
from openvino.runtime import Core
c = Core()
print('OpenVINO devices:', c.available_devices)
"

# Run smoke test (skipped if openvino absent)
python -m pytest tests/smoke/test_openvino_optional.py -v
```

---

## References

- OpenVINO documentation: <https://docs.openvino.ai>
- Hardware compatibility matrix: `docs/ops/hardware_compatibility_matrix.md`
- Primary test machine spec: `docs/ops/primary_test_machine.md`
- Deployment readiness: `docs/ops/DEPLOYMENT_READINESS_S92.md`
