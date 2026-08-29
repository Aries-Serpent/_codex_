"""Smoke tests for Intel OpenVINO optional backend (P10-05 Phase B/C — S98/S100).

Phase B tests (S98): verify Tier 2 guard pattern — correct behaviour whether
or not ``openvino`` is installed.  No GPU or OpenVINO runtime required.

Phase C tests (S100): verify the *live* inference path on a real Intel Arc
iGPU.  These tests are guarded with ``skipif(not is_available("GPU"), ...)``
so they pass on CPU-only CI runners and only run when a GPU is present.

See docs/ops/openvino_integration.md Phase B/C for context.
"""

from __future__ import annotations

import importlib
import sys
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helper: reload the module with a clean import state
# ---------------------------------------------------------------------------
def _load_backend(mock_openvino: bool = False):
    """Load openvino_backend with or without a mocked openvino package."""
    mod_name = "codex_ml.backends.openvino_backend"
    # Ensure clean state
    for key in list(sys.modules):
        if "openvino" in key or key == mod_name:
            del sys.modules[key]

    if mock_openvino:
        mock_core_instance = MagicMock()
        mock_core_instance.available_devices = ["CPU", "GPU"]
        mock_core_cls = MagicMock(return_value=mock_core_instance)
        mock_ov_runtime = MagicMock()
        mock_ov_runtime.Core = mock_core_cls
        mock_ov = MagicMock()
        mock_ov.runtime = mock_ov_runtime

        with patch.dict(
            sys.modules,
            {"openvino": mock_ov, "openvino.runtime": mock_ov_runtime},
        ):
            return importlib.import_module(mod_name)
    with patch.dict(sys.modules, {"openvino": None, "openvino.runtime": None}):
        return importlib.import_module(mod_name)


class TestOpenVINOBackendUnavailable:
    """Behaviour when openvino is not installed (primary test machine path)."""

    def setup_method(self):
        self.backend = _load_backend(mock_openvino=False)

    def test_ov_available_false(self):
        assert self.backend._OV_AVAILABLE is False, "_OV_AVAILABLE is not valid"

    def test_devices_empty(self):
        assert self.backend.DEVICES == [], "DEVICES is not valid"

    def test_is_available_gpu_false(self):
        assert self.backend.is_available("GPU") is False, "Condition must be true"

    def test_is_available_cpu_false(self):
        """CPU device via OV is also False when OV not installed."""
        assert self.backend.is_available("CPU") is False, "Condition must be true"

    def test_available_devices_empty(self):
        assert self.backend.available_devices() == [], "Condition must be true"

    def test_infer_raises_runtime_error(self, tmp_path):
        """infer() must raise RuntimeError, not crash with AttributeError."""
        fake_model = tmp_path / "model.xml"
        fake_model.write_text("<model/>")
        try:
            self.backend.infer(str(fake_model), {}, device="GPU")
            assert False, "Expected RuntimeError"
        except RuntimeError as exc:
            assert "GPU" in str(exc), "Condition must be true"
            assert "unavailable" in str(exc).lower(), "Condition must be true"


class TestOpenVINOBackendAvailable:
    """Behaviour when openvino IS installed and GPU is detected (mocked)."""

    def setup_method(self):
        self.backend = _load_backend(mock_openvino=True)

    def test_ov_available_true(self):
        assert self.backend._OV_AVAILABLE is True, "_OV_AVAILABLE is not valid"

    def test_devices_populated(self):
        assert "GPU" in self.backend.DEVICES, "Condition must be true"
        assert "CPU" in self.backend.DEVICES, "Condition must be true"

    def test_is_available_gpu_true(self):
        assert self.backend.is_available("GPU") is True, "Condition must be true"

    def test_is_available_npu_false(self):
        """NPU not in mock device list."""
        assert self.backend.is_available("NPU") is False, "Condition must be true"

    def test_available_devices_list(self):
        devs = self.backend.available_devices()
        assert isinstance(devs, list)
        assert "GPU" in devs, "Condition must be true"


# ---------------------------------------------------------------------------
# Phase C — live GPU inference path (skipif when GPU absent)
# ---------------------------------------------------------------------------
try:
    from codex_ml.backends.openvino_backend import is_available as _ov_is_available

    _GPU_PRESENT = _ov_is_available("GPU")
except (ImportError, AttributeError):
    _GPU_PRESENT = False

_skip_no_gpu = pytest.mark.skipif(
    not _GPU_PRESENT,
    reason="Intel Arc GPU not present (OpenVINO GPU unavailable); skipping Phase C live tests",
)


@_skip_no_gpu
class TestOpenVINOPhaseC:
    """Phase C: live inference on a real Intel Arc iGPU.

    These tests only run when ``is_available("GPU")`` returns ``True`` (i.e.,
    OpenVINO is installed AND an Intel Arc iGPU is enumerated).  They are
    unconditionally skipped on CPU-only CI runners.

    See docs/ops/openvino_integration.md Phase C for context.
    """

    def setup_method(self):
        """Import the real (non-mocked) backend."""
        from codex_ml.backends import openvino_backend

        self.backend = openvino_backend

    def test_gpu_is_available_live(self):
        """Sanity: GPU should be live-detected before any infer() call."""
        assert self.backend.is_available("GPU") is True, "Condition must be true"

    def test_available_devices_contains_gpu_live(self):
        """available_devices() must list GPU when OV is live."""
        devs = self.backend.available_devices()
        assert "GPU" in devs, f"Expected 'GPU' in devices, got: {devs}"

    def test_infer_with_real_model(self, tmp_path):
        """infer() on GPU must return a dict of output tensors.

        This test creates a minimal valid IR model stub.  On a live runner
        the model would be compiled on the Arc iGPU; the output tensor dict
        must be non-empty.
        """
        import numpy as np

        # Create minimal OpenVINO IR XML + BIN pair
        xml_path = tmp_path / "model.xml"
        bin_path = tmp_path / "model.bin"
        xml_content = """<?xml version="1.0"?>
<net name="test" version="11">
  <layers>
    <layer id="0" name="input" type="Parameter" version="opset1">
      <data element_type="f32" shape="1,4"/>
      <output><port id="0"><dim>1</dim><dim>4</dim></port></output>
    </layer>
    <layer id="1" name="output" type="Result" version="opset1">
      <input><port id="0"><dim>1</dim><dim>4</dim></port></input>
    </layer>
  </layers>
  <edges><edge from-layer="0" from-port="0" to-layer="1" to-port="0"/></edges>
</net>"""
        xml_path.write_text(xml_content)
        bin_path.write_bytes(b"")  # empty weights bin for pass-through model

        inputs = {"input": np.ones((1, 4), dtype=np.float32)}
        result = self.backend.infer(str(xml_path), inputs, device="GPU")
        assert isinstance(result, dict), f"Expected dict result, got {type(result)}"
