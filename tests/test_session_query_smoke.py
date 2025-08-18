import importlib
import subprocess
import sys

def test_import():
    mod = importlib.import_module("codex.logging.session_query")
    assert hasattr(mod, "main")

def test_help_invocation():
    proc = subprocess.run(
        [sys.executable, "-m", "codex.logging.session_query", "--help"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert "Query session events" in proc.stdout
