from pathlib import Path

from codex.analysis.duplication import analyze_duplication


def test_duplication_detects_duplicate_files(tmp_path: Path):
    base = tmp_path / "project"
    base.mkdir()
    (base / "a.py").write_text("print('x')\n", encoding="utf-8")
    (base / "nested").mkdir()
    (base / "nested" / "a.py").write_text("print('x')\n", encoding="utf-8")

    report = analyze_duplication(base)

    assert report.stats["duplicate_groups_count"] == 1
    assert report.stats["duplicate_count"] >= 1
    assert report.duplicate_groups
    assert any("a.py" in p for group in report.duplicate_groups for p in group["paths"])


def test_duplication_respects_thresholds(tmp_path: Path):
    base = tmp_path / "project"
    base.mkdir()
    for idx in range(5):
        (base / f"file{idx}.py").write_text(f"print({idx})\n", encoding="utf-8")

    report = analyze_duplication(base, acceptable_ratio=0.0)
    assert report.stats["duplication_ratio"] == 0
    assert report.stats["severity"] == "acceptable"
