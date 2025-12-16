import importlib

import pytest

pytestmark = pytest.mark.smoke


def test_cli_env_wires_determinism(monkeypatch):
    """Test that determinism can be configured via environment variables."""
    monkeypatch.setenv("CODEX_DETERMINISM", "1")
    monkeypatch.setenv("CODEX_SEED", "123")
    monkeypatch.setenv("CODEX_NUM_THREADS", "2")

    # Import module with environment set
    try:
        # Force reimport to pick up environment variables
        import sys

        if "codex_ml.codex_script" in sys.modules:
            del sys.modules["codex_ml.codex_script"]

        from codex_ml import codex_script as cs
    except ImportError:
        pytest.skip("codex_script module not available")

    assert hasattr(cs, "_init_determinism_from_env")
    summary = cs._init_determinism_from_env()
    # Should return a dict when enabled
    assert isinstance(summary, dict)
    assert summary.get("seed") == 123
