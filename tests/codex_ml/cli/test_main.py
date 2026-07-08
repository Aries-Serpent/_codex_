"""
Test Main

Test module for main.
"""
import importlib




def test_import_module():
    module = "codex_ml.cli.main"
    try:
        importlib.import_module(module)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")
