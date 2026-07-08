"""
Test Validate Fences Samples

Test module for validate fences samples.
"""

from pathlib import Path

from tools import validate_fences


def write(tmp: Path, name: str, content: str) -> Path:
    p = tmp / name
    p.write_text(content, encoding="utf-8")
    return p


def test_tilde_fences_supported(tmp_path: Path) -> None:
    ok = write(tmp_path, "ok.md", "~~~python\nlogger.info('x')\n~~~\n")
    errs = validate_fences.validate_file(ok, strict_inner=True)
    assert not errs, "Condition must be true"


def test_skips_inner_when_warn_mode(tmp_path: Path) -> None:
    sample = write(tmp_path, "warn.md", "```python\nlogger.info('```')\n```\n")
    errs = validate_fences.validate_file(sample, strict_inner=True, warn_inner=True)
    assert not errs, "Condition must be true"
