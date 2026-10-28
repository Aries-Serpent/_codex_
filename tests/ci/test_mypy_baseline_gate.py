"""The mypy ratchet must fail closed when source discovery is incomplete."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def gate() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "mypy_baseline_gate", ROOT / "scripts" / "ci" / "mypy_baseline.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    ("returncode", "stdout", "stderr", "count"),
    [
        (0, "Success: no issues found\n", "", 0),
        (1, "src/example.py:3: error: Bad argument [arg-type]\n", "", 1),
        (
            1,
            "src/a.py:1: error: First [assignment]\n" "src/b.py:2: error: Second [return-value]\n",
            "",
            2,
        ),
    ],
)
def test_completed_checks_count_real_errors(
    gate: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    returncode: int,
    stdout: str,
    stderr: str,
    count: int,
) -> None:
    def run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        assert command[:3] == [sys.executable, "-m", "mypy"]
        assert Path(command[3]) == ROOT / "src"
        assert kwargs["cwd"] == ROOT
        return subprocess.CompletedProcess(command, returncode, stdout, stderr)

    monkeypatch.setattr(gate.subprocess, "run", run)
    assert gate.run_mypy() == count


@pytest.mark.parametrize(
    ("returncode", "stdout", "stderr"),
    [
        (2, "", "self-healing contains __init__.py but is not a valid Python package name"),
        (2, "src/a.py: error: Source file found twice under different module names", ""),
        (1, "", "No module named mypy"),
        (-9, "", ""),
    ],
)
def test_incomplete_checks_cannot_become_zero_error_baselines(
    gate: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    returncode: int,
    stdout: str,
    stderr: str,
) -> None:
    monkeypatch.setattr(
        gate.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args, returncode, stdout, stderr),
    )
    with pytest.raises(RuntimeError, match="mypy did not complete"):
        gate.run_mypy()


@pytest.mark.parametrize("arguments", [[], ["--update"], ["--require-baseline"]])
def test_fatal_checks_leave_the_baseline_untouched(
    gate: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    arguments: list[str],
) -> None:
    baseline = tmp_path / ".mypy_baseline"
    baseline.write_text("0\n")
    monkeypatch.setattr(gate, "BASELINE_FILE", baseline)
    monkeypatch.setattr(sys, "argv", ["mypy_baseline.py", *arguments])

    def fail() -> int:
        raise RuntimeError("mypy did not complete (exit 2)")

    monkeypatch.setattr(gate, "run_mypy", fail)
    assert gate.main() == 2
    assert baseline.read_text() == "0\n"
    assert "::error::mypy did not complete" in capsys.readouterr().err
