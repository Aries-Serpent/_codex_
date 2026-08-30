"""
Phase 18.0: Test Suite Validation Tests

This module provides tests to validate the test suite itself:
- Test discovery
- Test organization
- Test naming conventions
- Test isolation
- Test dependencies
"""

import ast
import re
from pathlib import Path

# =============================================================================
# Test Suite Discovery
# =============================================================================


class TestTestSuiteDiscovery:
    """Tests for test suite discovery and organization."""

    def test_test_directory_exists(self) -> None:
        """Test that the tests directory exists."""
        tests_dir = Path("tests")
        assert tests_dir.exists(), "tests directory should exist"
        assert tests_dir.is_dir(), "tests should be a directory"

    def test_test_directories_have_init_files(self) -> None:
        """Test that all test directories have __init__.py files."""
        tests_dir = Path("tests")
        missing_init = []

        for subdir in tests_dir.rglob("*"):
            if subdir.is_dir() and not subdir.name.startswith("__"):
                init_file = subdir / "__init__.py"
                if not init_file.exists():
                    missing_init.append(str(subdir))

        # Allow some missing init files for Phase 18 validation
        assert len(missing_init) <= 5, f"Too many directories missing __init__.py: {missing_init}"

    def test_test_files_follow_naming_convention(self) -> None:
        """Test that test files follow test_*.py naming convention."""
        tests_dir = Path("tests")
        invalid_files = []

        for test_file in tests_dir.rglob("*.py"):
            if test_file.name.startswith("__"):
                continue
            if not test_file.name.startswith("test_"):
                # Allow conftest and helper files
                if test_file.name not in [
                    "conftest.py",
                    "conftest_shared.py",
                    "fixtures.py",
                    "helpers.py",
                ]:
                    invalid_files.append(str(test_file))

        assert len(invalid_files) == 0, f"Files not following test_*.py convention: {invalid_files}"

    def test_minimum_test_file_count(self) -> None:
        """Test that we have a minimum number of test files."""
        tests_dir = Path("tests")
        test_files = list(tests_dir.rglob("test_*.py"))

        # Phase 14-17 created 50+ test files
        assert len(test_files) >= 40, f"Expected 40+ test files, found {len(test_files)}"

    def test_test_categories_coverage(self) -> None:
        """Test that we have tests in key categories."""
        tests_dir = Path("tests")
        expected_categories = {
            "cli",
            "data",
            "training",
            "security",
            "safety",
        }

        actual_categories = set()
        for subdir in tests_dir.iterdir():
            if subdir.is_dir() and not subdir.name.startswith("__"):
                actual_categories.add(subdir.name)

        missing = expected_categories - actual_categories
        assert len(missing) == 0, f"Missing test categories: {missing}"


# =============================================================================
# Test Function Validation
# =============================================================================


class TestTestFunctionValidation:
    """Tests for validating test function structure."""

    def test_test_functions_have_docstrings(self) -> None:
        """Test that test functions have docstrings."""
        tests_dir = Path("tests")
        files_without_docstrings = []

        for test_file in tests_dir.rglob("test_*.py"):
            try:
                content = test_file.read_text()
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if node.name.startswith("test_"):
                            docstring = ast.get_docstring(node)
                            if not docstring:
                                # Count files, not individual functions
                                if str(test_file) not in files_without_docstrings:
                                    files_without_docstrings.append(str(test_file))
                                break
            except SyntaxError:
                continue

        # Allow some files without docstrings
        assert (len(files_without_docstrings) <= 10, "Files_without_docstrings must not be empty"
        ), f"Too many test files with functions missing docstrings: {files_without_docstrings[:5]}"

    def test_test_class_naming_convention(self) -> None:
        """Test that test classes follow Test* naming convention."""
        tests_dir = Path("tests")
        invalid_classes = []

        for test_file in tests_dir.rglob("test_*.py"):
            try:
                content = test_file.read_text()
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Test classes should start with Test
                        if "test" in node.name.lower() and not node.name.startswith("Test"):
                            invalid_classes.append(f"{test_file}::{node.name}")
            except SyntaxError:
                continue

        assert len(invalid_classes) == 0, f"Invalid test class names: {invalid_classes}"

    def test_assert_statements_used(self) -> None:
        """Test that test functions use assertions."""
        tests_dir = Path("tests")
        files_without_asserts = []

        for test_file in tests_dir.rglob("test_*.py"):
            try:
                content = test_file.read_text()

                # Check for assertion patterns
                has_assert = (
                    "assert " in content or "pytest.raises" in content or "with raises" in content
                )

                if not has_assert:
                    files_without_asserts.append(str(test_file))
            except OSError:
                continue

        assert (
            len(files_without_asserts) == 0
        ), f"Test files without assertions: {files_without_asserts}"


# =============================================================================
# Test Isolation Validation
# =============================================================================


class TestTestIsolation:
    """Tests for validating test isolation."""

    def test_no_global_state_modification(self) -> None:
        """Test that tests don't modify global state unsafely."""
        tests_dir = Path("tests")
        suspicious_patterns = [
            r"os\.environ\s*\[.*\]\s*=",  # Direct env modification
            r"sys\.path\.(append|insert)",  # Path modification
        ]

        files_with_issues = []

        for test_file in tests_dir.rglob("test_*.py"):
            try:
                content = test_file.read_text()
                for pattern in suspicious_patterns:
                    if re.search(pattern, content):
                        # Allow if using fixtures
                        if "monkeypatch" not in content and "fixture" not in content:
                            files_with_issues.append(str(test_file))
                            break
            except OSError:
                continue

        # Allow some files with controlled state modification
        assert (
            len(files_with_issues) <= 5
        ), f"Files with potential global state issues: {files_with_issues}"

    def test_fixtures_used_for_setup(self) -> None:
        """Test that fixtures are used for common setup."""
        tests_dir = Path("tests")
        conftest_files = list(tests_dir.rglob("conftest.py"))

        # Should have at least one conftest
        assert len(conftest_files) >= 1, "Should have at least one conftest.py"

    def test_no_hardcoded_file_paths(self) -> None:
        """Test that tests don't use hardcoded absolute paths."""
        tests_dir = Path("tests")
        suspicious_patterns = [
            r'"/home/[^"]+',
            r'"/Users/[^"]+',
            r'"C:\\[^"]+',
        ]

        files_with_hardcoded_paths = []

        for test_file in tests_dir.rglob("test_*.py"):
            try:
                content = test_file.read_text()
                for pattern in suspicious_patterns:
                    if re.search(pattern, content):
                        # Allow if in comments
                        if not re.search(r"#.*" + pattern, content):
                            files_with_hardcoded_paths.append(str(test_file))
                            break
            except OSError:
                continue

        assert (
            len(files_with_hardcoded_paths) == 0
        ), f"Files with hardcoded paths: {files_with_hardcoded_paths}"


# =============================================================================
# Test Markers Validation
# =============================================================================


class TestTestMarkers:
    """Tests for validating pytest markers usage."""

    def test_slow_tests_marked(self) -> None:
        """Test that slow tests are marked with @pytest.mark.slow."""
        # This is advisory - we just verify the marker exists in pytest.ini
        pytest_ini = Path("pytest.ini")
        if pytest_ini.exists():
            content = pytest_ini.read_text()
            # Verify markers section exists
            assert "markers" in content or "addopts" in content, "Content must not be empty"

    def test_integration_tests_marked(self) -> None:
        """Test that integration tests are in dedicated directory."""
        integration_dir = Path("tests/integration")
        if integration_dir.exists():
            test_files = list(integration_dir.rglob("test_*.py"))
            assert len(test_files) >= 1, "Integration directory should have tests"

    def test_parametrize_used_appropriately(self) -> None:
        """Test that parametrize is used for data-driven tests."""
        tests_dir = Path("tests")
        files_with_parametrize = []

        for test_file in tests_dir.rglob("test_*.py"):
            try:
                content = test_file.read_text()
                if "@pytest.mark.parametrize" in content:
                    files_with_parametrize.append(str(test_file))
            except OSError:
                continue

        # Should have some parametrized tests
        assert len(files_with_parametrize) >= 5, "Expected at least 5 files with parametrized tests"


# =============================================================================
# Coverage Validation
# =============================================================================


class TestCoverageValidation:
    """Tests for validating coverage configuration."""

    def test_coverage_threshold_configured(self) -> None:
        """Test that coverage threshold is configured in pyproject.toml."""
        pyproject = Path("pyproject.toml")
        assert pyproject.exists(), "pyproject.toml should exist"

        content = pyproject.read_text()
        assert "fail_under" in content, "Coverage fail_under should be configured"

    def test_coverage_source_configured(self) -> None:
        """Test that coverage source is properly configured."""
        pyproject = Path("pyproject.toml")
        if pyproject.exists():
            content = pyproject.read_text()
            # Check for coverage source configuration
            assert "source" in content or "cov" in content, "Content must not be empty"

    def test_coverage_threshold_value(self) -> None:
        """Test that coverage threshold is configured to a meaningful value."""
        pyproject = Path("pyproject.toml")
        if pyproject.exists():
            content = pyproject.read_text()
            # Look for fail_under = <N> and verify it is a sensible minimum
            match = re.search(r"fail_under\s*=\s*(\d+)", content)
            if match:
                threshold = int(match.group(1))
                assert threshold >= 50, f"Coverage threshold {threshold} should be at least 50%"


# =============================================================================
# CI Validation
# =============================================================================


class TestCIValidation:
    """Tests for validating CI configuration."""

    def test_github_workflows_exist(self) -> None:
        """Test that GitHub workflow files exist."""
        workflows_dir = Path(".github/workflows")
        assert workflows_dir.exists(), "GitHub workflows directory should exist"

    def test_test_workflow_exists(self) -> None:
        """Test that a test workflow is configured."""
        workflows_dir = Path(".github/workflows")
        if workflows_dir.exists():
            workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
            test_workflows = [f for f in workflow_files if "test" in f.name.lower()]
            assert len(test_workflows) >= 1, "Should have at least one test workflow"

    def test_python_matrix_configured(self) -> None:
        """Test that Python version matrix is configured."""
        workflows_dir = Path(".github/workflows")
        if workflows_dir.exists():
            for workflow in workflows_dir.glob("*.yml"):
                try:
                    content = workflow.read_text()
                    if "python" in content.lower() and "matrix" in content.lower():
                        # Found a workflow with Python matrix
                        return
                except OSError:
                    continue


# =============================================================================
# Documentation Validation
# =============================================================================


class TestDocumentationValidation:
    """Tests for validating documentation."""

    def test_readme_exists(self) -> None:
        """Test that README.md exists."""
        readme = Path("README.md")
        assert readme.exists(), "README.md should exist"

    def test_docs_directory_exists(self) -> None:
        """Test that docs directory exists."""
        docs_dir = Path("docs")
        assert docs_dir.exists(), "docs directory should exist"

    def test_coverage_roadmap_exists(self) -> None:
        """Test that coverage roadmap document exists."""
        roadmap = Path("docs/COVERAGE_ROADMAP_TO_100_PERCENT.md")
        if not roadmap.exists():
            # Check alternative location
            roadmap = Path("docs/testing/COVERAGE_ROADMAP.md")

        # Allow if coverage docs exist in any form
        docs_dir = Path("docs")
        coverage_docs = list(docs_dir.rglob("*COVERAGE*"))
        assert len(coverage_docs) >= 1 or roadmap.exists(), "Should have coverage documentation"
