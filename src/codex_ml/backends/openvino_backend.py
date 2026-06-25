"""Optional Intel OpenVINO inference backend (P10-05 Phase B — S98).

Tier 2 (guarded): falls back silently to CPU-only PyTorch when OpenVINO is
not installed or the requested device is unavailable.

Usage
-----
    from codex_ml.backends.openvino_backend import is_available, infer

    if is_available("GPU"):
        result = infer(model_path, inputs, device="GPU")
    else:
        # Fall back to PyTorch CPU path
        ...

See Also
--------
docs/ops/openvino_integration.md — full Phase A/B/C integration plan.
docs/ops/hardware_compatibility_matrix.md — Tier 2 guard policy.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional OpenVINO import — Tier 2 guard
# ---------------------------------------------------------------------------
try:
    from openvino.runtime import Core

    _OV_AVAILABLE = True
except ImportError:
    _OV_AVAILABLE = False

DEVICES: list[str] = []

if _OV_AVAILABLE:
    try:
        _core = Core()
        DEVICES = _core.available_devices  # e.g. ['CPU', 'GPU', 'NPU']
        logger.debug("OpenVINO available. Devices: %s", DEVICES)
    except (IOError, OSError):
        logger.debug("OpenVINO installed but Core() init failed; disabling.")
        _OV_AVAILABLE = False


def is_available(device: str = "GPU") -> bool:
    """Return True if OpenVINO is installed and *device* is present.

    Parameters
    ----------
    device:
        OpenVINO device string, e.g. ``"GPU"``, ``"CPU"``, ``"NPU"``.
        Defaults to ``"GPU"`` (Intel Arc iGPU target per primary test machine).
    """
    return _OV_AVAILABLE and device in DEVICES


def available_devices() -> list[str]:
    """Return the list of OpenVINO-detected devices (empty when OV absent)."""
    return list(DEVICES)


def infer(
    model_path: str | Path,
    inputs: dict[str, Any],
    *,
    device: str = "GPU",
) -> dict[str, Any]:
    """Run inference via OpenVINO on *device*.

    Falls back to raising ``RuntimeError`` if OpenVINO is unavailable; callers
    should check :func:`is_available` first and route to the PyTorch CPU path.

    Parameters
    ----------
    model_path:
        Path to an OpenVINO IR model (``.xml`` file).
    inputs:
        Dictionary mapping input tensor names to numpy arrays.
    device:
        OpenVINO device string (default ``"GPU"``).

    Returns
    -------
    dict[str, Any]
        Output tensor dictionary from the compiled model.

    Raises
    ------
    RuntimeError
        If OpenVINO is not installed or the device is unavailable.
    """
    if not is_available(device):
        raise RuntimeError(
            f"OpenVINO device '{device}' unavailable. "
            f"Available: {DEVICES or ['(none — openvino not installed)']}. "
            "Use PyTorch CPU path instead."
        )

    model_path = Path(model_path)
    compiled = _core.compile_model(str(model_path), device)
    infer_request = compiled.create_infer_request()
    infer_request.infer(inputs)
    return {
        output.any_name: infer_request.get_output_tensor(i).data
        for i, output in enumerate(compiled.outputs)
    }
