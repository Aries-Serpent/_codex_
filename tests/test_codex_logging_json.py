import pytest

pytest.importorskip("tensorboard")
"""
Test Codex Logging Json

Test module for codex logging json.
"""

from codex_ml.monitoring.codex_logging import init_logger


def test_json_logger_format(monkeypatch, capsys):
    monkeypatch.setenv("CODEX_JSON_LOGGING", "1")
    logger = init_logger("test_json")
    logger.handlers.clear()
    logger = init_logger("test_json")
    logger.info("hello")
    captured = capsys.readouterr()
    combined = (captured.out + captured.err).strip()
    assert '"msg": "hello"' in combined, "Condition must be true"


def test_nvml_disabled(monkeypatch):
    monkeypatch.setenv("CODEX_DISABLE_NVML", "1")
    # Re-import module to trigger guard
    import importlib

    mod = importlib.reload(importlib.import_module("codex_ml.monitoring.codex_logging"))
    assert mod.pynvml is None, "pynvml is not valid"
