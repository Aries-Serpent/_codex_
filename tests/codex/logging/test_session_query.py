import importlib
import pytest

def test_import_module():
    module = "codex.logging.session_query"
    try:
        importlib.import_module(module)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")
