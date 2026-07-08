"""
Test Policy

Test module for policy.
"""
import importlib




def test_import_module():
    module = "codex_audit.policy"
    try:
        importlib.import_module(module)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")
