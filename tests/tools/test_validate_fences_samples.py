from pathlib import Path

from tools import validate_fences


def write(tmp: Path, name: str, content: str) -> Path:
    p = tmp / name
    p.write_text(content, encoding="utf-8")
    return p


def test_tilde_fences_supported(tmp_path: Path) -> None:
    ok = write(tmp_path, "ok.md", "~~~python\nprint('x')\n~~~\n")
    errs = validate_fences.validate_file(ok, strict_inner=True)
    assert not errs


def test_skips_inner_when_warn_mode(tmp_path: Path) -> None:
    sample = write(tmp_path, "warn.md", "```python\nprint('```')\n```\n")
    errs = validate_fences.validate_file(sample, strict_inner=True, warn_inner=True)
    assert not errs  # treated as warnings by caller
