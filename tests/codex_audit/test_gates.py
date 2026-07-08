"""
Test Gates

Test module for gates.
"""
import importlib




def test_import_module():
    module = "codex_audit.gates"
    try:
        importlib.import_module(module)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")
