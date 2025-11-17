"""
Integration Tests for Duplication Detection System

Tests end-to-end workflows combining detection, storage, and CLI.
"""

import json
import tempfile
from pathlib import Path

import pytest

from src.codex.metrics.duplication import calculate_duplication_ratio, detect_duplicates
from src.codex.metrics.storage import MetricStorage


class TestFullWorkflow:
    """Test complete end-to-end duplication detection workflow"""

    def test_detect_calculate_store_workflow(self):
        """Test full workflow: detect → calculate → store"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test Python files with duplicates
            test_dir = Path(tmpdir) / "test_project"
            test_dir.mkdir()

            # File 1 with duplicate code
            file1 = test_dir / "module1.py"
            file1.write_text(
                """
def duplicate_function():
    x = 1
    y = 2
    z = x + y
    return z

def unique_function1():
    return "unique1"
"""
            )

            # File 2 with same duplicate code
            file2 = test_dir / "module2.py"
            file2.write_text(
                """
def another_function():
    x = 1
    y = 2
    z = x + y
    return z

def unique_function2():
    return "unique2"
"""
            )

            # Step 1: Detect duplicates
            duplicates = detect_duplicates(test_dir, min_lines=3)

            # Step 2: Calculate ratio
            total_lines = sum(len(f.read_text().splitlines()) for f in test_dir.glob("*.py"))

            ratio = calculate_duplication_ratio(duplicates, total_lines)
            ratio.files_scanned = len(list(test_dir.glob("*.py")))

            # Step 3: Store metrics
            storage = MetricStorage(
                json_dir=Path(tmpdir) / "metrics",
                sqlite_path=Path(tmpdir) / "metrics.db",
            )

            result = storage.save(ratio, commit_sha="test123")

            # Verify all steps
            assert isinstance(duplicates, list)
            assert ratio.total_lines > 0
            assert "json_path" in result
            assert "sqlite_id" in result

            # Verify storage
            latest = storage.load_latest()
            assert latest is not None
            assert latest["commit_sha"] == "test123"

    def test_baseline_comparison_workflow(self):
        """Test baseline tracking and comparison workflow"""
        with tempfile.TemporaryDirectory() as tmpdir:
            metrics_dir = Path(tmpdir)

            # Create baseline metrics
            baseline = {
                "ratio": 0.10,
                "total_lines": 1000,
                "duplicate_lines": 100,
                "files_scanned": 10,
            }

            baseline_file = metrics_dir / "baseline.json"
            with open(baseline_file, "w") as f:
                json.dump(baseline, f)

            # Simulate current run with higher duplication
            current = {
                "ratio": 0.15,
                "total_lines": 1000,
                "duplicate_lines": 150,
                "files_scanned": 10,
            }

            current_file = metrics_dir / "current.json"
            with open(current_file, "w") as f:
                json.dump(current, f)

            # Compare
            with open(baseline_file) as f:
                baseline_data = json.load(f)
            with open(current_file) as f:
                current_data = json.load(f)

            baseline_ratio = baseline_data["ratio"]
            current_ratio = current_data["ratio"]
            difference = current_ratio - baseline_ratio

            # Verify comparison logic
            assert difference == 0.05
            assert difference > 0.02  # Would fail threshold

            # Simulate improvement (update baseline)
            if current_ratio < baseline_ratio:
                # Update baseline (in real workflow)
                pass

            # In this case, current is worse
            assert current_ratio > baseline_ratio


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
