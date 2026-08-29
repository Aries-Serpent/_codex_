"""
Test Validate Fences Md

Test module for validate fences md.
"""

from __future__ import annotations

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def run_validator(target: pathlib.Path) -> subprocess.CompletedProcess[str]:
    script = ROOT / "tools" / "validate_fences.py"
    return subprocess.run(
        [sys.executable, str(script), str(target)],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def test_good_file_passes(tmp_path: pathlib.Path) -> None:
    good = ROOT / "tests" / "samples" / "good_fences.md"
    copied = tmp_path / "good.md"
    copied.write_text(good.read_text(encoding="utf-8"), encoding="utf-8")
    result = run_validator(copied)
    assert result.returncode == 0, result.stdout + result.stderr


def test_bad_file_fails(tmp_path: pathlib.Path) -> None:
    bad = ROOT / "tests" / "samples" / "bad_fences.md"
    copied = tmp_path / "bad.md"
    copied.write_text(bad.read_text(encoding="utf-8"), encoding="utf-8")
    result = run_validator(copied)
    assert result.returncode == 1, "Result must not be empty"
    assert "Closing fence shorter than opener" in result.stdout, "Result must not be empty"
    assert "Backticks in info string" in result.stdout, "Result must not be empty"
