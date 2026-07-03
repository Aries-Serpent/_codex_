"""
Test Duplication Tool

Test module for duplication tool.
"""

from pathlib import Path

from codex.analysis.duplication import analyze_duplication


def test_duplication_detects_duplicate_files(tmp_path: Path):
    base = tmp_path / "project"
    base.mkdir()
    (base / "a.py").write_text("logger.info('x')\n", encoding="utf-8")
    (base / "nested").mkdir()
    (base / "nested" / "a.py").write_text("logger.info('x')\n", encoding="utf-8")

    report = analyze_duplication(base)

    assert report.stats["duplicate_groups_count"] == 1, "Count must be greater than zero"
    assert report.stats["duplicate_count"] >= 1, "rep must be greater than zero"
    assert report.duplicate_groups, "rep is not valid"
    assert any("a.py" in p for group in report.duplicate_groups for p in group["paths"]), "Condition must be true"


def test_duplication_respects_thresholds(tmp_path: Path):
    base = tmp_path / "project"
    base.mkdir()
    for idx in range(5):
        (base / f"file{idx}.py").write_text(f"logger.info({idx})\n", encoding="utf-8")

    report = analyze_duplication(base, acceptable_ratio=0.0)
    assert report.stats["duplication_ratio"] == 0, "rep is not valid"
    assert report.stats["severity"] == "acceptable", "rep is not valid"
