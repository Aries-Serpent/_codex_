"""
Test Validate Fences Sample

Test module for validate fences sample.
"""

from pathlib import Path

import tools.validate_fences as vf


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_validate_file_ok(tmp_path: Path):
    good = tmp_path / "good.md"
    write(
        good,
        """\
```bash
echo hello
```
""",
    )
    ok, problems = vf.validate_file(str(good))
    assert ok, problems


def test_validate_file_mixed_fence(tmp_path: Path):
    bad = tmp_path / "bad.md"
    write(
        bad,
        """\
```bash
echo hello
~~~  # wrong fence closing on purpose
""",
    )
    ok, problems = vf.validate_file(str(bad))
    assert not ok, "Condition must be true"
    assert any("mixed fence types" in p for p in problems), "Condition must be true"


def test_repo_sample_is_broken_when_present():
    sample = Path("samples/broken_fence.sample.md")
    if sample.exists():
        ok, problems = vf.validate_file(str(sample))
        assert not ok, "Condition must be true"
        assert any("mixed fence types" in p for p in problems), "Condition must be true"
