"""
Comprehensive tests for Pattern 38 (RP-033): Mock Object Cleanup Missing

Tests the detection and auto-fixing of mock objects without proper cleanup.
"""

import sys
from pathlib import Path

import pytest

# Add scripts/ci to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "ci"))

from auto_fix_common_issues import CommonIssueFixer


class TestRP033MockCleanup:
    """Test suite for RP-033: Mock object cleanup missing"""

    @pytest.fixture
    def tmp_repo(self, tmp_path):
        """Create a temporary repository structure for testing."""
        repo_root = tmp_path / "test_repo"
        repo_root.mkdir()
        tests_dir = repo_root / "tests"
        tests_dir.mkdir()
        return repo_root, tests_dir

    def test_detect_mock_without_cleanup(self, tmp_repo):
        """Test detection of mock objects without cleanup."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_mock.py"
        test_file.write_text("""
from unittest.mock import Mock

def test_example():
    mock = Mock()
    mock.method()
""")

        fixer = CommonIssueFixer(repo_root, check_only=True, dry_run=False)
        issues = fixer.fix_mock_cleanup()

        assert len(issues) >= 1, "Issues must not be empty"
        assert any("Mock" in issue for issue in issues), "in is not valid"

    def test_detect_magic_mock_without_cleanup(self, tmp_repo):
        """Test detection of MagicMock without cleanup."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_mock.py"
        test_file.write_text("""
from unittest.mock import MagicMock

def test_example():
    magic_mock = MagicMock()
    magic_mock.do_something()
""")

        fixer = CommonIssueFixer(repo_root, check_only=True, dry_run=False)
        issues = fixer.fix_mock_cleanup()

        assert len(issues) >= 1, "Issues must not be empty"

    def test_skip_mock_with_reset_mock(self, tmp_repo):
        """Test that mocks with reset_mock() are not flagged."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_mock.py"
        test_file.write_text("""
def test_example():
    mock = Mock()
    try:
        mock.method()
    finally:
        mock.reset_mock()
""")

        fixer = CommonIssueFixer(repo_root, check_only=True, dry_run=False)
        issues = fixer.fix_mock_cleanup()

        # Should not flag this mock as it has cleanup
        assert len(issues) == 0, "Issues must not be empty"

    def test_skip_mock_with_stop(self, tmp_repo):
        """Test that mocks with .stop() are not flagged."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_mock.py"
        test_file.write_text("""
def test_example():
    mock = Mock()
    mock.start()
    try:
        mock.method()
    finally:
        mock.stop()
""")

        fixer = CommonIssueFixer(repo_root, check_only=True, dry_run=False)
        issues = fixer.fix_mock_cleanup()

        assert len(issues) == 0, "Issues must not be empty"

    def test_skip_mock_with_context_manager(self, tmp_repo):
        """Test that context-managed mocks are not flagged."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_mock.py"
        test_file.write_text("""
def test_example():
    with Mock() as mock:
        mock.method()
""")

        fixer = CommonIssueFixer(repo_root, check_only=True, dry_run=False)
        issues = fixer.fix_mock_cleanup()

        # Context manager handles cleanup
        assert len(issues) == 0, "Issues must not be empty"

    def test_skip_fixture_mocks(self, tmp_repo):
        """Test that fixture-based mocks are not flagged."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_mock.py"
        test_file.write_text("""
@pytest.fixture(autouse=True)
def my_mock():
    return Mock()

def test_example(my_mock):
    my_mock.method()
""")

        fixer = CommonIssueFixer(repo_root, check_only=True, dry_run=False)
        issues = fixer.fix_mock_cleanup()

        # Fixtures handle cleanup automatically
        assert len(issues) == 0, "Issues must not be empty"

    def test_multiple_mocks_in_function(self, tmp_repo):
        """Test handling multiple mocks in same function."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_mock.py"
        test_file.write_text("""
def test_example():
    mock1 = Mock()
    mock2 = Mock()
    mock1.method()
    mock2.other_method()
""")

        fixer = CommonIssueFixer(repo_root, check_only=True, dry_run=False)
        issues = fixer.fix_mock_cleanup()

        # Should detect both uncleaned mocks
        assert len(issues) >= 2, "Issues must not be empty"

    def test_skip_non_mock_variables(self, tmp_repo):
        """Test that non-mock variables are not flagged."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_mock.py"
        test_file.write_text("""
def test_example():
    data = [1, 2, 3]
    result = process_data(data)
    assert result, "Result must not be empty"
""")

        fixer = CommonIssueFixer(repo_root, check_only=True, dry_run=False)
        issues = fixer.fix_mock_cleanup()

        assert len(issues) == 0, "Issues must not be empty"

    def test_dry_run_mode(self, tmp_repo):
        """Test that dry-run doesn't modify files."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_mock.py"
        original = """
def test_example():
    mock = Mock()
    mock.method()
"""
        test_file.write_text(original)

        fixer = CommonIssueFixer(repo_root, check_only=False, dry_run=True)
        issues = fixer.fix_mock_cleanup()

        content = test_file.read_text()
        # File should not be modified
        assert 'reset_mock' not in content, "Content must not be empty"

    def test_check_only_mode(self, tmp_repo):
        """Test that check-only doesn't modify files."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_mock.py"
        original = """
def test_example():
    mock = Mock()
    mock.method()
"""
        test_file.write_text(original)

        fixer = CommonIssueFixer(repo_root, check_only=True, dry_run=False)
        issues = fixer.fix_mock_cleanup()

        content = test_file.read_text()
        assert content == original, "Content must not be empty"
        assert len(issues) > 0, "Issues must not be empty"

    def test_mock_types_recognized(self, tmp_repo):
        """Test that different mock types are recognized."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_mock.py"
        test_file.write_text("""
from unittest.mock import Mock, MagicMock, AsyncMock, PropertyMock

def test_mocks():
    mock = Mock()
    magic = MagicMock()
    async_mock = AsyncMock()
    prop = PropertyMock()
    
    mock.method()
    magic.method()
    async_mock.method()
    prop.method()
""")

        fixer = CommonIssueFixer(repo_root, check_only=True, dry_run=False)
        issues = fixer.fix_mock_cleanup()

        # Should detect all 4 mock types
        assert len(issues) >= 4, "Issues must not be empty"

    def test_nested_test_functions(self, tmp_repo):
        """Test handling nested function scopes."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_mock.py"
        test_file.write_text("""
def test_outer():
    mock = Mock()
    
    def inner():
        return mock.method()
    
    result = inner()
    assert result, "Result must not be empty"
""")

        fixer = CommonIssueFixer(repo_root, check_only=True, dry_run=False)
        issues = fixer.fix_mock_cleanup()

        # Should detect uncleaned mock
        assert len(issues) >= 1, "Issues must not be empty"

    def test_class_based_tests(self, tmp_repo):
        """Test handling class-based test methods."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_mock.py"
        test_file.write_text("""
class TestExample:
    def test_method(self):
        mock = Mock()
        mock.call()
    
    def test_another(self):
        other_mock = MagicMock()
        other_mock.call()
""")

        fixer = CommonIssueFixer(repo_root, check_only=True, dry_run=False)
        issues = fixer.fix_mock_cleanup()

        # Should detect both uncleaned mocks
        assert len(issues) >= 2, "Issues must not be empty"

    def test_mock_with_clear(self, tmp_repo):
        """Test that mocks with .clear() are recognized as cleaned."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_mock.py"
        test_file.write_text("""
def test_example():
    mock = Mock()
    mock.method()
    mock.clear()
""")

        fixer = CommonIssueFixer(repo_root, check_only=True, dry_run=False)
        issues = fixer.fix_mock_cleanup()

        # Mock has cleanup via .clear()
        assert len(issues) == 0, "Issues must not be empty"

    def test_mock_with_close(self, tmp_repo):
        """Test that mocks with .close() are recognized as cleaned."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_mock.py"
        test_file.write_text("""
def test_example():
    mock = Mock()
    mock.method()
    mock.close()
""")

        fixer = CommonIssueFixer(repo_root, check_only=True, dry_run=False)
        issues = fixer.fix_mock_cleanup()

        # Mock has cleanup via .close()
        assert len(issues) == 0, "Issues must not be empty"

    def test_handles_empty_tests_dir(self, tmp_repo):
        """Test handling when tests directory is empty."""
        repo_root, tests_dir = tmp_repo
        # Don't create any test files

        fixer = CommonIssueFixer(repo_root, check_only=False, dry_run=False)
        issues = fixer.fix_mock_cleanup()

        assert len(issues) == 0, "Issues must not be empty"

    def test_no_tests_dir(self, tmp_path):
        """Test handling when tests directory doesn't exist."""
        repo_root = tmp_path / "test_repo"
        repo_root.mkdir()
        # Don't create tests directory

        fixer = CommonIssueFixer(repo_root, check_only=False, dry_run=False)
        issues = fixer.fix_mock_cleanup()

        assert len(issues) == 0, "Issues must not be empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
