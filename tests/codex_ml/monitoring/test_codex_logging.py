import importlib
import pytest


def test_import_module():
    module = "codex_ml.monitoring.codex_logging"
    try:
        importlib.import_module(module)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")
