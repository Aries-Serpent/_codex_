"""
Comprehensive tests for Pattern 36 (RP-031): Assert Messages Without Context

Tests the detection and auto-fixing of assertions without descriptive messages.
"""

import sys
from pathlib import Path

import pytest

# Add scripts/ci to path so we can import auto_fix_common_issues
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "ci"))

from auto_fix_common_issues import CommonIssueFixer


class TestRP031AssertMessages:
    """Test suite for RP-031: Assert messages without context"""

    @pytest.fixture
    def tmp_repo(self, tmp_path):
        """Create a temporary repository structure for testing."""
        repo_root = tmp_path / "test_repo"
        repo_root.mkdir()
        tests_dir = repo_root / "tests"
        tests_dir.mkdir()
        return repo_root, tests_dir

    def test_detect_assert_without_message(self, tmp_repo):
        """Test detection of assertions without messages."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_example.py"
        test_file.write_text("""
def test_response_handling():
    response = {"status": "ok"}
    assert response, "Response must not be empty"
    assert len(response) > 0, "Response must not be empty"
""")

        fixer = CommonIssueFixer(repo_root, check_only=True, dry_run=False)
        issues = fixer.fix_assert_messages()

        assert len(issues) >= 2, "Issues must not be empty"
        assert any("Missing assertion message" in issue for issue in issues), "in is not valid"

    def test_fix_simple_assert(self, tmp_repo):
        """Test fixing simple assertions."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_example.py"
        test_file.write_text("def test_data():\n    data = [1, 2, 3]\n    assert data\n")

        fixer = CommonIssueFixer(repo_root, check_only=False, dry_run=False)
        issues = fixer.fix_assert_messages()

        content = test_file.read_text()
        assert 'assert data, "Data must not be empty"' in content
        assert len(issues) > 0, "Issues must not be empty"

    def test_fix_len_assertion(self, tmp_repo):
        """Test fixing len() assertions."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_example.py"
        test_file.write_text("def test_list():\n    items = [1, 2]\n    assert len(items) > 0\n")

        fixer = CommonIssueFixer(repo_root, check_only=False, dry_run=False)
        issues = fixer.fix_assert_messages()

        content = test_file.read_text()
        assert 'assert len(items) > 0, "Items must not be empty"' in content

    def test_fix_none_check_assertion(self, tmp_repo):
        """Test fixing 'is not None' assertions."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_example.py"
        test_file.write_text("def test_value():\n    value = 42\n    assert value is not None\n")

        fixer = CommonIssueFixer(repo_root, check_only=False, dry_run=False)
        issues = fixer.fix_assert_messages()

        content = test_file.read_text()
        assert 'assert value is not None, "Value must be initialized"' in content

    def test_skip_assertions_with_messages(self, tmp_repo):
        """Test that assertions with messages are not modified."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_example.py"
        original = 'def test_data():\n    data = []\n    assert data, "Data should not be empty"\n'
        test_file.write_text(original)

        fixer = CommonIssueFixer(repo_root, check_only=False, dry_run=False)
        issues = fixer.fix_assert_messages()

        content = test_file.read_text()
        assert content == original, "Content must not be empty"
        assert len(issues) == 0, "Issues must not be empty"

    def test_skip_noqa_comments(self, tmp_repo):
        """Test that assertions with # noqa are skipped."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_example.py"
        test_file.write_text("def test_data():\n    data = []\n    assert data  # noqa\n")

        fixer = CommonIssueFixer(repo_root, check_only=False, dry_run=False)
        issues = fixer.fix_assert_messages()

        assert len(issues) == 0, "Issues must not be empty"

    def test_skip_complex_assertions(self, tmp_repo):
        """Test that complex assertions are skipped."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_example.py"
        # Very long condition should be skipped
        test_file.write_text(
            "def test_complex():\n"
            "    assert very_long_variable_name and another_long_var and yet_another_long_var and more_stuff\n"
        )

        fixer = CommonIssueFixer(repo_root, check_only=False, dry_run=False)
        issues = fixer.fix_assert_messages()

        # Complex assertions are skipped (> 80 chars)
        assert len(issues) == 0, "Issues must not be empty"

    def test_dry_run_mode(self, tmp_repo):
        """Test that dry-run doesn't modify files."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_example.py"
        original = "def test_data():\n    assert True\n"
        test_file.write_text(original)

        fixer = CommonIssueFixer(repo_root, check_only=False, dry_run=True)
        issues = fixer.fix_assert_messages()

        content = test_file.read_text()
        assert content == original, "Content must not be empty"

    def test_check_only_mode(self, tmp_repo):
        """Test that check-only doesn't modify files."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_example.py"
        original = "def test_response():\n    resp = {}\n    assert resp\n"
        test_file.write_text(original)

        fixer = CommonIssueFixer(repo_root, check_only=True, dry_run=False)
        issues = fixer.fix_assert_messages()

        content = test_file.read_text()
        assert content == original, "Content must not be empty"
        assert len(issues) > 0, "Issues must not be empty"

    def test_multiple_assertions_in_function(self, tmp_repo):
        """Test handling multiple assertions in single function."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_example.py"
        test_file.write_text("""
def test_multi():
    data = [1, 2, 3]
    result = {"key": "value"}
    assert data, "Data must not be empty"
    assert result, "Result must not be empty"
    assert len(data) > 0, "Data must not be empty"
""")

        fixer = CommonIssueFixer(repo_root, check_only=False, dry_run=False)
        issues = fixer.fix_assert_messages()

        assert len(issues) >= 3, "Issues must not be empty"
        content = test_file.read_text()
        # Verify multiple messages were added
        assert content.count('assert ') >= 3, "Value must be greater than zero"
        assert '", "' in content  # Multiple messages added

    def test_preserves_indentation(self, tmp_repo):
        """Test that indentation is preserved."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_example.py"
        test_file.write_text("""
class TestClass:
    def test_method(self):
        data = []
        assert data, "Data must not be empty"
""")

        fixer = CommonIssueFixer(repo_root, check_only=False, dry_run=False)
        issues = fixer.fix_assert_messages()

        content = test_file.read_text()
        # Check that indentation is preserved (8 spaces for nested assert)
        lines = content.split('\n')
        assert_line = [l for l in lines if 'assert' in l and 'data' in l][0]
        assert assert_line.startswith('        '), "Condition must be true"

    def test_handles_empty_tests_dir(self, tmp_repo):
        """Test handling when tests directory exists but is empty."""
        repo_root, tests_dir = tmp_repo
        # Don't create any test files

        fixer = CommonIssueFixer(repo_root, check_only=False, dry_run=False)
        issues = fixer.fix_assert_messages()

        assert len(issues) == 0, "Issues must not be empty"

    def test_no_tests_dir(self, tmp_path):
        """Test handling when tests directory doesn't exist."""
        repo_root = tmp_path / "test_repo"
        repo_root.mkdir()
        # Don't create tests directory

        fixer = CommonIssueFixer(repo_root, check_only=False, dry_run=False)
        issues = fixer.fix_assert_messages()

        assert len(issues) == 0, "Issues must not be empty"

    def test_context_keyword_detection(self, tmp_repo):
        """Test that context keywords generate appropriate messages."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_example.py"
        test_file.write_text("""
def test_keywords():
    response = None
    result = None
    content = None
    assert response, "Response must not be empty"
    assert result, "Result must not be empty"
    assert content, "Content must not be empty"
""")

        fixer = CommonIssueFixer(repo_root, check_only=False, dry_run=False)
        issues = fixer.fix_assert_messages()

        content = test_file.read_text()
        assert 'Response must not be empty' in content, "Response must not be empty"
        assert 'Result must not be empty' in content, "Result must not be empty"
        assert 'Content must not be empty' in content, "Content must not be empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
