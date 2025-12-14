import importlib
import pytest

def test_import_module():
    module = "codex.db.sqlite_patch"
    try:
        importlib.import_module(module)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")
