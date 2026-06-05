"""Tests for EnvironmentFingerprint and environment_summary in codex_ml.utils.env."""

from __future__ import annotations

import hashlib
import json
import logging
import platform
import sys
from unittest.mock import MagicMock, patch

import pytest

from codex_ml.utils.env import EnvironmentFingerprint, environment_summary


# ---------------------------------------------------------------------------
# EnvironmentFingerprint.capture()
# ---------------------------------------------------------------------------


class TestCapture:
    def test_returns_fingerprint_instance(self):
        fp = EnvironmentFingerprint.capture()
        assert isinstance(fp, EnvironmentFingerprint)

    def test_python_version_matches_runtime(self):
        fp = EnvironmentFingerprint.capture()
        assert fp.python_version == platform.python_version()

    def test_os_platform_non_empty(self):
        fp = EnvironmentFingerprint.capture()
        assert isinstance(fp.os_platform, str)
        assert len(fp.os_platform) > 0

    def test_cpu_count_positive_or_none(self):
        fp = EnvironmentFingerprint.capture()
        if fp.cpu_count is not None:
            assert fp.cpu_count > 0

    def test_gpu_devices_is_list(self):
        fp = EnvironmentFingerprint.capture()
        assert isinstance(fp.gpu_devices, list)

    def test_captures_without_torch(self):
        import codex_ml.utils.env as env_mod

        with patch.object(env_mod, "torch", None):
            fp = EnvironmentFingerprint.capture()
        assert fp.python_version == platform.python_version()
        assert fp.cuda_version is None
        assert fp.gpu_devices == []

    def test_captures_with_mock_torch(self):
        import codex_ml.utils.env as env_mod

        mock_torch = MagicMock()
        mock_torch.version.cuda = "12.1"
        mock_torch.cuda.device_count.return_value = 1
        mock_torch.cuda.get_device_name.return_value = "Tesla T4"
        mock_torch.cuda.get_device_properties.return_value = MagicMock(
            total_memory=16 * 1024 * 1024 * 1024,
            major=8,
            minor=0,
        )

        with patch.object(env_mod, "torch", mock_torch):
            fp = EnvironmentFingerprint.capture()

        assert fp.cuda_version == "12.1"
        assert len(fp.gpu_devices) == 1
        assert fp.gpu_devices[0]["name"] == "Tesla T4"
        assert fp.gpu_devices[0]["compute_capability"] == "8.0"

    def test_no_torch_no_gpu_devices(self):
        import codex_ml.utils.env as env_mod

        with patch.object(env_mod, "torch", None), patch.object(env_mod, "_pynvml", None):
            fp = EnvironmentFingerprint.capture()

        assert fp.gpu_devices == []
        assert fp.cuda_version is None


# ---------------------------------------------------------------------------
# EnvironmentFingerprint.to_dict()
# ---------------------------------------------------------------------------


class TestToDict:
    def test_returns_dict(self):
        fp = EnvironmentFingerprint.capture()
        d = fp.to_dict()
        assert isinstance(d, dict)

    def test_contains_required_keys(self):
        d = EnvironmentFingerprint.capture().to_dict()
        for key in ("python_version", "os_platform", "cpu_count", "gpu_devices"):
            assert key in d, f"Missing key: {key}"

    def test_serialisable_to_json(self):
        d = EnvironmentFingerprint.capture().to_dict()
        # Should not raise
        json.dumps(d)


# ---------------------------------------------------------------------------
# EnvironmentFingerprint.digest()
# ---------------------------------------------------------------------------


class TestDigest:
    def test_returns_16_char_hex(self):
        fp = EnvironmentFingerprint.capture()
        digest = fp.digest()
        assert len(digest) == 16
        int(digest, 16)  # valid hex

    def test_stable_across_instances_same_hardware(self):
        """Two fingerprints on the same machine should produce the same digest."""
        fp1 = EnvironmentFingerprint.capture()
        fp2 = EnvironmentFingerprint.capture()
        # git_commit may differ between two fast captures only if a commit lands mid-run;
        # digest excludes git_commit so it must be identical.
        assert fp1.digest() == fp2.digest()

    def test_excludes_git_commit(self):
        fp = EnvironmentFingerprint(
            python_version="3.12.0",
            os_platform="Linux",
            git_commit="abc123",
        )
        fp_no_commit = EnvironmentFingerprint(
            python_version="3.12.0",
            os_platform="Linux",
            git_commit=None,
        )
        assert fp.digest() == fp_no_commit.digest()

    def test_differs_across_different_hardware(self):
        fp_a = EnvironmentFingerprint(
            python_version="3.12.0",
            os_platform="Linux",
            cpu_count=4,
        )
        fp_b = EnvironmentFingerprint(
            python_version="3.12.0",
            os_platform="Linux",
            cpu_count=8,
        )
        assert fp_a.digest() != fp_b.digest()


# ---------------------------------------------------------------------------
# EnvironmentFingerprint.log()
# ---------------------------------------------------------------------------


class TestLog:
    def test_emits_info_message(self, caplog):
        fp = EnvironmentFingerprint(
            python_version="3.12.0",
            os_platform="Linux",
        )
        with caplog.at_level(logging.INFO, logger="codex_ml.utils.env"):
            fp.log()
        assert any("fingerprint" in rec.message.lower() for rec in caplog.records)

    def test_uses_custom_logger(self):
        mock_logger = MagicMock()
        fp = EnvironmentFingerprint(python_version="3.12.0", os_platform="Linux")
        fp.log(logger=mock_logger)
        mock_logger.info.assert_called_once()


# ---------------------------------------------------------------------------
# environment_summary() — backward-compatibility shim
# ---------------------------------------------------------------------------


class TestEnvironmentSummary:
    def test_returns_dict(self):
        summary = environment_summary()
        assert isinstance(summary, dict)

    def test_has_os_key(self):
        assert "os" in environment_summary()

    def test_has_python_key(self):
        assert "python" in environment_summary()

    def test_python_matches_runtime(self):
        assert environment_summary()["python"] == platform.python_version()

    def test_no_torch_omits_gpu_keys(self):
        import codex_ml.utils.env as env_mod

        with patch.object(env_mod, "torch", None):
            summary = environment_summary()
        assert "gpu" not in summary
        assert "cuda_version" not in summary

    def test_with_torch_includes_cuda_version(self):
        import codex_ml.utils.env as env_mod

        mock_torch = MagicMock()
        mock_torch.version.cuda = "12.1"
        mock_torch.cuda.device_count.return_value = 0

        with patch.object(env_mod, "torch", mock_torch):
            summary = environment_summary()
        assert summary.get("cuda_version") == "12.1"
