import importlib
def test_import():
    mod = importlib.import_module("codex.logging.query_logs")
    assert hasattr(mod, "main")
