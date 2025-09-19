import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def run_module(module: str, *args, extra_env: dict | None = None, check: bool = True):
    """Run a Python module as a subprocess with a controlled environment.

    Ensures PYTHONPATH includes the repo 'src' directory so in-repo packages are importable.
    Uses the current Python interpreter (sys.executable).
    Captures stdout/stderr for assertions in tests.
    """
    env = dict(os.environ)
    env.update(extra_env or {})
    env.setdefault("PYTHONPATH", str(PROJECT_ROOT / "src"))
    cmd = [sys.executable, "-m", module, *map(str, args)]
    return subprocess.run(cmd, capture_output=True, text=True, env=env, check=check)
