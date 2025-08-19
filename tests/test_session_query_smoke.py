import importlib
import subprocess
import sys

def test_import():
    mod = importlib.import_module("src.codex.logging.query_logs")
    assert hasattr(mod, "main")

def test_help_invocation():
    proc = subprocess.run(
        [sys.executable, "-m", "src.codex.logging.query_logs", "--help"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert "usage" in proc.stdout
