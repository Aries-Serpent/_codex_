"""
Tests for PR Size Analyzer workflow functionality.

Tests the logic for categorizing PRs by size and determining
the appropriate validation strategy.
"""

import pytest


def calculate_pr_size(changed_files: int) -> tuple[str, str]:
    """Calculate PR size category and validation strategy.

    This replicates the logic from pr-size-analyzer.yml workflow.

    Args:
        changed_files: Number of files changed in the PR

    Returns:
        Tuple of (size_category, validation_strategy)
    """
    if changed_files < 20:
        return "small", "full_validation"
    if changed_files < 100:
        return "medium", "targeted_tests"
    if changed_files < 500:
        return "large", "smoke_tests"
    return "refactor", "import_validation"


class TestPRSizeAnalyzer:
    """Test suite for PR size analysis logic."""

    def test_small_pr_classification(self):
        """Test that PRs with < 20 files are classified as small."""
        size, strategy = calculate_pr_size(10)
        assert size == "small", "size is not valid"
        assert strategy == "full_validation", "strategy is not valid"

    def test_small_pr_boundary(self):
        """Test boundary condition at 19 files."""
        size, strategy = calculate_pr_size(19)
        assert size == "small", "size is not valid"
        assert strategy == "full_validation", "strategy is not valid"

    def test_medium_pr_lower_boundary(self):
        """Test boundary condition at 20 files."""
        size, strategy = calculate_pr_size(20)
        assert size == "medium", "size is not valid"
        assert strategy == "targeted_tests", "strategy is not valid"

    def test_medium_pr_classification(self):
        """Test that PRs with 20-99 files are classified as medium."""
        size, strategy = calculate_pr_size(50)
        assert size == "medium", "size is not valid"
        assert strategy == "targeted_tests", "strategy is not valid"

    def test_medium_pr_upper_boundary(self):
        """Test boundary condition at 99 files."""
        size, strategy = calculate_pr_size(99)
        assert size == "medium", "size is not valid"
        assert strategy == "targeted_tests", "strategy is not valid"

    def test_large_pr_lower_boundary(self):
        """Test boundary condition at 100 files."""
        size, strategy = calculate_pr_size(100)
        assert size == "large", "size is not valid"
        assert strategy == "smoke_tests", "strategy is not valid"

    def test_large_pr_classification(self):
        """Test that PRs with 100-499 files are classified as large."""
        size, strategy = calculate_pr_size(250)
        assert size == "large", "size is not valid"
        assert strategy == "smoke_tests", "strategy is not valid"

    def test_large_pr_upper_boundary(self):
        """Test boundary condition at 499 files."""
        size, strategy = calculate_pr_size(499)
        assert size == "large", "size is not valid"
        assert strategy == "smoke_tests", "strategy is not valid"

    def test_refactor_pr_lower_boundary(self):
        """Test boundary condition at 500 files."""
        size, strategy = calculate_pr_size(500)
        assert size == "refactor", "size is not valid"
        assert strategy == "import_validation", "strategy is not valid"

    def test_refactor_pr_classification(self):
        """Test that PRs with 500+ files are classified as refactor."""
        size, strategy = calculate_pr_size(1000)
        assert size == "refactor", "size is not valid"
        assert strategy == "import_validation", "strategy is not valid"

    def test_extreme_large_pr(self):
        """Test extremely large PR (edge case)."""
        size, strategy = calculate_pr_size(10000)
        assert size == "refactor", "size is not valid"
        assert strategy == "import_validation", "strategy is not valid"

    def test_zero_files(self):
        """Test edge case with zero files changed."""
        size, strategy = calculate_pr_size(0)
        assert size == "small", "size is not valid"
        assert strategy == "full_validation", "strategy is not valid"

    def test_single_file(self):
        """Test edge case with single file changed."""
        size, strategy = calculate_pr_size(1)
        assert size == "small", "size is not valid"
        assert strategy == "full_validation", "strategy is not valid"

    @pytest.mark.parametrize(
        "files,expected_size,expected_strategy",
        [
            (5, "small", "full_validation"),
            (19, "small", "full_validation"),
            (20, "medium", "targeted_tests"),
            (50, "medium", "targeted_tests"),
            (99, "medium", "targeted_tests"),
            (100, "large", "smoke_tests"),
            (250, "large", "smoke_tests"),
            (499, "large", "smoke_tests"),
            (500, "refactor", "import_validation"),
            (1000, "refactor", "import_validation"),
        ],
    )
    def test_size_classification_table(
        self, files: int, expected_size: str, expected_strategy: str
    ):
        """Test PR size classification with comprehensive test table."""
        size, strategy = calculate_pr_size(files)
        assert size == expected_size, f"Expected {expected_size} for {files} files"
        assert strategy == expected_strategy, f"Expected {expected_strategy} for {files} files"


class TestValidationStrategyMapping:
    """Test validation strategy mappings."""

    def test_full_validation_requires_all_tests(self):
        """Verify full_validation strategy means all tests run."""
        _, strategy = calculate_pr_size(10)
        assert strategy == "full_validation", "strategy is not valid"
        # In actual workflow, this would trigger all test suites

    def test_targeted_tests_for_medium_prs(self):
        """Verify targeted_tests strategy for medium PRs."""
        _, strategy = calculate_pr_size(50)
        assert strategy == "targeted_tests", "strategy is not valid"
        # In actual workflow, this would analyze changed files and run related tests

    def test_smoke_tests_for_large_prs(self):
        """Verify smoke_tests strategy for large PRs."""
        _, strategy = calculate_pr_size(200)
        assert strategy == "smoke_tests", "strategy is not valid"
        # In actual workflow, this would run only smoke tests

    def test_import_validation_for_refactor(self):
        """Verify import_validation strategy for refactor PRs."""
        _, strategy = calculate_pr_size(600)
        assert strategy == "import_validation", "strategy is not valid"
        # In actual workflow, this would verify imports only
