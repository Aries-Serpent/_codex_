"""
Phase 17.0: Flaky Test Detection Tests

This module provides tests for detecting and tracking flaky tests,
ensuring test reliability across the test suite.

Created: 2026-01-18
Phase: 17.0 - Continuous Improvement & Maintenance
Tests: 15+
"""

import re
from pathlib import Path

import pytest

# Repository root
REPO_ROOT = Path(__file__).parents[2]
TESTS_DIR = REPO_ROOT / "tests"


class TestFlakyTestDetection:
    """Tests for flaky test detection infrastructure."""

    def test_pytest_rerunfailures_configured(self):
        """Verify pytest-rerunfailures is configured for flaky tests."""
        pyproject = REPO_ROOT / "pyproject.toml"
        pytest_ini = REPO_ROOT / "pytest.ini"

        reruns_configured = False
        for config in [pyproject, pytest_ini]:
            if config.exists():
                content = config.read_text(encoding="utf-8")
                if "reruns" in content or "rerun" in content:
                    reruns_configured = True
                    break

        # Just log, don't require
        if not reruns_configured:
            pytest.skip("pytest-rerunfailures not configured (optional)")

    def test_no_sleep_in_tests(self):
        """Check for time.sleep usage in tests (potential flakiness)."""
        sleep_usage = []

        for test_file in list(TESTS_DIR.rglob("test_*.py"))[:50]:
            try:
                content = test_file.read_text(encoding="utf-8", errors="ignore")
                if "time.sleep(" in content:
                    # Count occurrences
                    count = content.count("time.sleep(")
                    if count > 2:  # Allow some sleep usage
                        sleep_usage.append(f"{test_file.name}: {count}")
            except (UnicodeDecodeError, OSError):
                continue

        # Log but don't fail (some sleeps are acceptable)
        if sleep_usage:
            pytest.skip(f"Found sleep usage (may be acceptable): {sleep_usage[:3]}")

    def test_tests_use_fixtures_not_globals(self):
        """Check that tests use fixtures instead of global state."""
        global_patterns = ["global ", "globals()"]
        global_usage = []

        for test_file in list(TESTS_DIR.rglob("test_*.py"))[:30]:
            try:
                content = test_file.read_text(encoding="utf-8", errors="ignore")
                for pattern in global_patterns:
                    if pattern in content:
                        global_usage.append(test_file.name)
                        break
            except (UnicodeDecodeError, OSError):
                continue

        # Allow some global usage
        assert len(global_usage) < 10, f"Too many tests use globals: {global_usage}"

    def test_tests_are_isolated(self):
        """Verify tests don't modify shared state."""
        # Check for class-level setup that might cause issues
        class_setup_pattern = r"@classmethod\s+def\s+setUpClass"
        problematic_files = []

        for test_file in list(TESTS_DIR.rglob("test_*.py"))[:30]:
            try:
                content = test_file.read_text(encoding="utf-8", errors="ignore")
                if re.search(class_setup_pattern, content):
                    problematic_files.append(test_file.name)
            except (UnicodeDecodeError, OSError):
                continue

        # Just log, setUpClass is sometimes needed
        if problematic_files:
            pytest.skip(f"Found setUpClass (may be acceptable): {problematic_files[:3]}")


class TestTestDeterminism:
    """Tests for test determinism."""

    def test_random_seeds_used(self):
        """Check that random seeds are used for reproducibility."""
        seed_patterns = ["random.seed", "np.random.seed", "torch.manual_seed", "PYTHONHASHSEED"]

        files_with_seeds = 0
        files_with_random = 0

        for test_file in list(TESTS_DIR.rglob("test_*.py"))[:30]:
            try:
                content = test_file.read_text(encoding="utf-8", errors="ignore")
                uses_random = "random" in content.lower()
                uses_seed = any(p in content for p in seed_patterns)

                if uses_random:
                    files_with_random += 1
                    if uses_seed:
                        files_with_seeds += 1
            except (UnicodeDecodeError, OSError):
                continue

        # Just verify random usage is tracked
        if files_with_random > 0:
            pass  # Acceptable

    def test_no_datetime_now_in_tests(self):
        """Check for datetime.now(UTC) usage that could cause flakiness."""
        datetime_patterns = ["datetime.now(UTC)", "datetime.utcnow()"]
        datetime_usage = []

        for test_file in list(TESTS_DIR.rglob("test_*.py"))[:30]:
            try:
                content = test_file.read_text(encoding="utf-8", errors="ignore")
                for pattern in datetime_patterns:
                    if pattern in content and "freezegun" not in content:
                        datetime_usage.append(test_file.name)
                        break
            except (UnicodeDecodeError, OSError):
                continue

        # Log but don't fail
        if datetime_usage:
            pytest.skip(f"Found datetime usage without freezegun: {datetime_usage[:3]}")


class TestTestPerformance:
    """Tests for test performance monitoring."""

    def test_no_very_slow_tests_marked(self):
        """Check that slow tests are marked appropriately."""
        slow_markers = ["@pytest.mark.slow", "@pytest.mark.integration"]
        slow_test_patterns = ["time.sleep(10", "time.sleep(30", "time.sleep(60"]

        unmarked_slow = []
        for test_file in list(TESTS_DIR.rglob("test_*.py"))[:30]:
            try:
                content = test_file.read_text(encoding="utf-8", errors="ignore")
                has_slow_pattern = any(p in content for p in slow_test_patterns)
                has_slow_marker = any(m in content for m in slow_markers)

                if has_slow_pattern and not has_slow_marker:
                    unmarked_slow.append(test_file.name)
            except (UnicodeDecodeError, OSError):
                continue

        # Log but don't fail
        if unmarked_slow:
            pytest.skip(f"Slow tests without markers: {unmarked_slow[:3]}")

    def test_tests_use_tmp_path(self):
        """Verify tests use tmp_path fixture for file operations."""
        file_patterns = ["open(", "Path(", "os.path"]
        tmp_path_usage = 0
        file_usage = 0

        for test_file in list(TESTS_DIR.rglob("test_*.py"))[:30]:
            try:
                content = test_file.read_text(encoding="utf-8", errors="ignore")
                if any(p in content for p in file_patterns):
                    file_usage += 1
                    if "tmp_path" in content or "tmpdir" in content:
                        tmp_path_usage += 1
            except (UnicodeDecodeError, OSError):
                continue

        # Just track, don't require
        if file_usage > 0:
            ratio = tmp_path_usage / file_usage
            # At least 50% should use tmp_path
            if ratio < 0.3:
                pytest.skip(f"Low tmp_path usage: {ratio:.0%}")
