import pytest

pytest.importorskip("tensorboard")
"""
Test Telemetry Degrade

Test module for telemetry degrade.
"""

from unittest.mock import patch

from codex_ml.monitoring.codex_logging import init_telemetry


def test_full_profile_degrades_without_nvml():
    original_import = __import__

    def fake_import(name, *args, **kwargs):
        if name == "pynvml":
            raise ImportError("no nvml")
        return original_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=fake_import):
        init_telemetry(profile="full")  # should not raise
