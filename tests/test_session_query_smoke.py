import importlib
import subprocess
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

def test_import():
    mod = importlib.import_module("codex.logging.session_query")
    assert hasattr(mod, "main")

def test_help_invocation():
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    proc = subprocess.run(
        [sys.executable, "-m", "codex.logging.session_query", "--help"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert proc.returncode == 0
    assert "Query session events" in proc.stdout

