"""
Tests for repository organization monitoring script

Tests candidate identification, category classification, JSON report generation,
and action log integration.
"""

from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path

import pytest


class TestMonitorOffloadCandidates:
    """Test suite for monitor_offload_candidates.py"""

    def test_get_file_age_days(self):
        """Test file age calculation"""
        # Import after path setup
        import sys

        sys.path.insert(
            0, str(Path(__file__).parent.parent.parent / "scripts" / "repository_organization")
        )

        from monitor_offload_candidates import get_file_age_days

        with tempfile.NamedTemporaryFile() as tmp:
            tmp_path = Path(tmp.name)
            age = get_file_age_days(tmp_path)
            assert age == 0, "Newly created file should have age 0"

    def test_get_file_size_mb(self):
        """Test file size calculation"""
        import sys

        sys.path.insert(
            0, str(Path(__file__).parent.parent.parent / "scripts" / "repository_organization")
        )

        from monitor_offload_candidates import get_file_size_mb

        with tempfile.NamedTemporaryFile(mode="w") as tmp:
            tmp_path = Path(tmp.name)
            # Write 1MB of data
            tmp.write("x" * 1024 * 1024)
            tmp.flush()

            size = get_file_size_mb(tmp_path)
            assert 0.9 < size < 1.1, f"1MB file should be ~1.0MB, got {size}"

    def test_matches_pattern(self):
        """Test pattern matching logic"""
        import sys

        sys.path.insert(
            0, str(Path(__file__).parent.parent.parent / "scripts" / "repository_organization")
        )

        from monitor_offload_candidates import matches_pattern

        test_cases = [
            (Path("temp/file.txt"), ["temp/"], True),
            (Path("logs/error.log"), ["*.log"], True),
            (Path("coverage_report.json"), ["coverage_"], True),
            (Path("src/main.py"), ["temp/"], False),
        ]

        for file_path, patterns, expected in test_cases:
            result = matches_pattern(file_path, patterns)
            assert result == expected, f"Pattern match failed for {file_path} with {patterns}"

    def test_categorize_file(self):
        """Test file categorization"""
        import sys

        sys.path.insert(
            0, str(Path(__file__).parent.parent.parent / "scripts" / "repository_organization")
        )

        from monitor_offload_candidates import categorize_file

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)

            test_cases = [
                ("temp/build.log", "temp"),
                ("logs/error.log", "logs"),
                ("coverage_report.json", "coverage"),
                ("artifacts/gates/test.log", "artifacts"),
                ("_codex_reports/status.md", "reports"),
                ("src/main.py", None),
            ]

            for rel_path, expected_category in test_cases:
                file_path = repo_root / rel_path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.touch()

                category = categorize_file(file_path, repo_root)
                assert category == expected_category, f"Categorization failed for {rel_path}"

    def test_scan_repository_basic(self):
        """Test basic repository scanning"""
        import sys

        sys.path.insert(
            0, str(Path(__file__).parent.parent.parent / "scripts" / "repository_organization")
        )

        from monitor_offload_candidates import scan_repository

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)

            # Create test structure
            (repo_root / "temp").mkdir()
            large_file = repo_root / "temp" / "large.log"
            large_file.write_text("x" * 2 * 1024 * 1024)  # 2MB file

            # Scan
            results = scan_repository(repo_root)

            # Verify structure
            assert "metadata" in results, "Result must not be empty"
            assert "summary" in results, "Result must not be empty"
            assert "candidates" in results, "Result must not be empty"
            assert results["metadata"]["repo_root"] == str(repo_root), "Result must not be empty"
            assert isinstance(results["summary"]["total_candidates"], int)

    def test_json_report_generation(self):
        """Test JSON report structure"""
        import sys

        sys.path.insert(
            0, str(Path(__file__).parent.parent.parent / "scripts" / "repository_organization")
        )

        from monitor_offload_candidates import scan_repository

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)

            results = scan_repository(repo_root)

            # Verify JSON serializable
            json_str = json.dumps(results)
            assert json_str, "Results should be JSON serializable"

            # Verify structure
            parsed = json.loads(json_str)
            assert parsed["metadata"]["criteria"]["temp_files_age_days"] == 90, "Data must not be empty"
            assert parsed["metadata"]["criteria"]["large_file_size_mb"] == 1.0, "Data must not be empty"

    @pytest.mark.parametrize(
        "category,age,size,expected",
        [
            ("temp", 100, 0.5, "offload_to_temp-outputs"),
            ("reports", 200, 0.5, "offload_to_deprecated-reports"),
            ("logs", 200, 0.5, "offload_to_historical-logs"),
            ("coverage", 100, 0.5, "offload_to_historical-coverage"),
            ("artifacts", 200, 0.5, "offload_to_historical-artifacts"),
            (None, 10, 6.0, "compress_or_offload"),
            ("unknown", 50, 0.3, "review_manually"),
        ],
    )
    def test_recommendation_generation(self, category, age, size, expected):
        """Test recommendation logic"""
        import sys

        sys.path.insert(
            0, str(Path(__file__).parent.parent.parent / "scripts" / "repository_organization")
        )

        from monitor_offload_candidates import _get_recommendation

        recommendation = _get_recommendation(category, age, size)
        assert recommendation == expected, f"Recommendation mismatch for {category}/{age}d/{size}MB"

    def test_scan_excludes_lock_and_docs_files(self):
        """Large-file rule should exclude lock files and docs paths."""
        module_path = (
            Path(__file__).parent.parent.parent
            / "scripts"
            / "repository_organization"
            / "monitor_offload_candidates.py"
        )
        spec = importlib.util.spec_from_file_location("monitor_offload_candidates", module_path)
        assert spec and spec.loader is not None, "loader must be initialized"
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        scan_repository = module.scan_repository

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            (repo_root / "docs").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs" / "manual.md").write_text("x" * 2 * 1024 * 1024)
            (repo_root / "uv.lock").write_text("x" * 2 * 1024 * 1024)

            results = scan_repository(repo_root)
            candidate_paths = {c["path"] for c in results["candidates"]}
            assert "docs/manual.md" not in candidate_paths, "Condition must be true"
            assert "uv.lock" not in candidate_paths, "Condition must be true"


@pytest.mark.skipif(True, reason="Integration test - requires full repository setup")
def test_integration_scan_real_repo():
    """Integration test with real repository (skipped by default)"""
    import sys

    sys.path.insert(
        0, str(Path(__file__).parent.parent.parent / "scripts" / "repository_organization")
    )

    from monitor_offload_candidates import scan_repository

    repo_root = Path.cwd()
    results = scan_repository(repo_root)

    # Basic sanity checks
    assert results["summary"]["total_candidates"] >= 0, "Value must be greater than zero"
    assert results["metadata"]["repo_root"] == str(repo_root), "Result must not be empty"
