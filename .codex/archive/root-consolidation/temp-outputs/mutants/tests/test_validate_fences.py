"""
Test Validate Fences

Test module for validate fences.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from tools import validate_fences

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "validate_fences.py"
FIXTURES = ROOT / "tests" / "fixtures" / "markdown"
NESTED_SAMPLE = '```python\nlogger.info("```")\n```\n'


@pytest.fixture(name="ok_markdown")
def _ok_markdown() -> Path:
    return FIXTURES / "ok.md"


@pytest.fixture(name="bad_markdown")
def _bad_markdown() -> Path:
    return FIXTURES / "bad.md"


def _copy_fixture(tmp_path: Path, fixture: Path) -> Path:
    target = tmp_path / fixture.name
    target.write_text(fixture.read_text(encoding="utf-8"), encoding="utf-8")
    return target


def test_validate_file_default_shape(tmp_path: Path, ok_markdown: Path) -> None:
    """Default mode returns the legacy (ok, problems) tuple."""

    target = _copy_fixture(tmp_path, ok_markdown)
    ok, problems = validate_fences.validate_file(target)
    assert ok is True, "ok is not valid"
    assert problems == [], "problems is not valid"


def test_iter_files_skips_known_paths(tmp_path: Path) -> None:
    """iter_files omits directories and files listed in the skip sets."""

    allowed = tmp_path / "notes.md"
    allowed.write_text("```text\nhello\n```\n", encoding="utf-8")

    skipped_dir = tmp_path / ".git"
    skipped_dir.mkdir()
    (skipped_dir / "ignored.md").write_text("```\nignored\n```\n", encoding="utf-8")

    skipped_file = tmp_path / "tests" / "samples"
    skipped_file.mkdir(parents=True)
    (skipped_file / "bad_fences.md").write_text("```\nignored\n```\n", encoding="utf-8")

    discovered = {Path(path) for path in validate_fences.iter_files(tmp_path)}

    assert allowed in discovered, "Condition must be true"
    assert all(tmp_path in path.parents for path in discovered), "Condition must be true"
    assert not any(path.name == "ignored.md" for path in discovered), "name is not valid"
    assert not any("bad_fences.md" in str(path) for path in discovered), "Condition must be true"


def test_warn_inner_emits_warning(tmp_path: Path, bad_markdown: Path) -> None:
    """Warn mode reports nested fences without failing the process."""

    target = _copy_fixture(tmp_path, bad_markdown)
    target.write_text(NESTED_SAMPLE, encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--warn-inner", str(target)],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0, "Result must not be empty"
    assert "WARN — nested code fence detected" in result.stdout, "Result must not be empty"
