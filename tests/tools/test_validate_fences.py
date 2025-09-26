from pathlib import Path

from tools import validate_fences


def write(tmp_path: Path, name: str, content: str) -> Path:
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path


def test_reports_missing_language_tag(tmp_path: Path) -> None:
    """GIVEN an unlabeled fence; WHEN scanned; THEN error mentioning 'language tag'."""
    bad = write(tmp_path, "bad.md", "```\ntext\n```\n")
    errors = validate_fences.validate_file(bad, strict_inner=False)
    assert errors
    assert "language tag" in errors[0].message


def test_reports_nested_fence_when_strict(tmp_path: Path) -> None:
    """GIVEN an inner-run collision; WHEN strict; THEN nonzero errors mentioning 'nested code fence'."""
    nested = write(tmp_path, "nested.md", '```python\nprint("```")\n```\n')
    errors = validate_fences.validate_file(nested, strict_inner=True)
    assert any("nested code fence" in error.message for error in errors)


def test_accepts_valid_markdown(tmp_path: Path) -> None:
    """GIVEN a labeled diff fence; WHEN strict; THEN no errors."""
    ok = write(tmp_path, "ok.md", "```diff\n- a\n+ b\n```\n")
    errors = validate_fences.validate_file(ok, strict_inner=True)
    assert not errors
