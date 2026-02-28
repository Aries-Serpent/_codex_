"""Smoke tests for Intel OpenVINO optional backend (P10-05 Phase B — S98).

These tests verify the Tier 2 guard pattern — the backend must behave
correctly whether or not ``openvino`` is installed.  No GPU or OpenVINO
runtime is required; all paths exercise the fallback / unavailable branch.

See docs/ops/openvino_integration.md Phase B for context.
"""
from __future__ import annotations

import importlib
import sys
from unittest.mock import MagicMock, patch


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
            mod = importlib.import_module(mod_name)
        return mod
    else:
        with patch.dict(sys.modules, {"openvino": None, "openvino.runtime": None}):
            mod = importlib.import_module(mod_name)
        return mod


class TestOpenVINOBackendUnavailable:
    """Behaviour when openvino is not installed (primary test machine path)."""

    def setup_method(self):
        self.backend = _load_backend(mock_openvino=False)

    def test_ov_available_false(self):
        assert self.backend._OV_AVAILABLE is False

    def test_devices_empty(self):
        assert self.backend.DEVICES == []

    def test_is_available_gpu_false(self):
        assert self.backend.is_available("GPU") is False

    def test_is_available_cpu_false(self):
        """CPU device via OV is also False when OV not installed."""
        assert self.backend.is_available("CPU") is False

    def test_available_devices_empty(self):
        assert self.backend.available_devices() == []

    def test_infer_raises_runtime_error(self, tmp_path):
        """infer() must raise RuntimeError, not crash with AttributeError."""
        fake_model = tmp_path / "model.xml"
        fake_model.write_text("<model/>")
        try:
            self.backend.infer(str(fake_model), {}, device="GPU")
            assert False, "Expected RuntimeError"  # noqa: B011
        except RuntimeError as exc:
            assert "GPU" in str(exc)
            assert "unavailable" in str(exc).lower()


class TestOpenVINOBackendAvailable:
    """Behaviour when openvino IS installed and GPU is detected (mocked)."""

    def setup_method(self):
        self.backend = _load_backend(mock_openvino=True)

    def test_ov_available_true(self):
        assert self.backend._OV_AVAILABLE is True

    def test_devices_populated(self):
        assert "GPU" in self.backend.DEVICES
        assert "CPU" in self.backend.DEVICES

    def test_is_available_gpu_true(self):
        assert self.backend.is_available("GPU") is True

    def test_is_available_npu_false(self):
        """NPU not in mock device list."""
        assert self.backend.is_available("NPU") is False

    def test_available_devices_list(self):
        devs = self.backend.available_devices()
        assert isinstance(devs, list)
        assert "GPU" in devs
