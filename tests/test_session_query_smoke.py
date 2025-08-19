import importlib


def test_import():
    mod = importlib.import_module("src.codex.logging.query_logs")
    assert hasattr(mod, "main")
