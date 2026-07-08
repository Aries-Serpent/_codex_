"""
Test Evaluator Optional Deps

Test module for evaluator optional deps.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_evaluator_emits_friendly_optional_dependency_message(tmp_path):
    runner = tmp_path / "runner.py"
    runner.write_text(
        f"""
import importlib.util
import sys

sys.path.insert(0, {str(REPO_ROOT)!r})

original_find_spec = importlib.util.find_spec

def fake_find_spec(name, *args, **kwargs):
    if name in {{"pydantic", "typer"}}:
        return None
    return original_find_spec(name, *args, **kwargs)

importlib.util.find_spec = fake_find_spec

try:
    import tools.codex_evaluator  # noqa: F401  # pragma: no cover
except SystemExit as exc:
    sys.exit(exc.code)
""",
        encoding="utf-8",
    )

    proc = subprocess.run([sys.executable, str(runner)], capture_output=True, text=True)
    assert proc.returncode == 2, "returncode is not valid"
    stderr = proc.stderr
    assert "Missing optional dependency" in stderr, "Condition must be true"
    assert "pip install" in stderr, "Condition must be true"
