"""
Test Cli Determinism Wiring

Test module for cli determinism wiring.
"""

import pytest

pytestmark = pytest.mark.smoke


def test_cli_env_wires_determinism(monkeypatch):
    """Test that determinism can be configured via environment variables."""
    monkeypatch.setenv("CODEX_DETERMINISM", "1")
    monkeypatch.setenv("CODEX_SEED", "123")
    monkeypatch.setenv("CODEX_NUM_THREADS", "2")

    # Import module with environment set
    # Force reimport to pick up environment variables
    import sys

    if "codex_ml.codex_script" in sys.modules:
        del sys.modules["codex_ml.codex_script"]

    cs = pytest.importorskip("codex_ml.codex_script")

    assert hasattr(cs, "_init_determinism_from_env")
    summary = cs._init_determinism_from_env()
    # Should return a dict when enabled
    assert isinstance(summary, dict)
    assert summary.get("seed") == 123, "Condition must be true"
