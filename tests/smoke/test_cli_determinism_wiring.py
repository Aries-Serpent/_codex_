import importlib

import pytest

pytestmark = pytest.mark.smoke


def test_cli_env_wires_determinism(monkeypatch):
    monkeypatch.setenv("CODEX_DETERMINISM", "1")
    monkeypatch.setenv("CODEX_SEED", "123")
    monkeypatch.setenv("CODEX_NUM_THREADS", "2")
    cs = importlib.import_module("codex_script")
    assert hasattr(cs, "_init_determinism_from_env")
    summary = cs._init_determinism_from_env()
    # Should return a dict when enabled
    assert isinstance(summary, dict)
    assert summary.get("seed") == 123
