"""
Comprehensive tests for Pattern 37 (RP-032): Async Tests Without Timeout

Tests the detection and auto-fixing of async tests missing timeout decorators.
"""

import sys
from pathlib import Path

import pytest

# Add scripts/ci to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "ci"))

from auto_fix_common_issues import CommonIssueFixer


class TestRP032AsyncTimeout:
    """Test suite for RP-032: Async tests without timeout"""

    @pytest.fixture
    def tmp_repo(self, tmp_path):
        """Create a temporary repository structure for testing."""
        repo_root = tmp_path / "test_repo"
        repo_root.mkdir()
        tests_dir = repo_root / "tests"
        tests_dir.mkdir()
        return repo_root, tests_dir

    def test_detect_async_without_timeout(self, tmp_repo):
        """Test detection of async tests without timeout."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_async.py"
        test_file.write_text("""
import pytest

@pytest.mark.asyncio
async def test_something():
    await asyncio.sleep(0)
""")

        fixer = CommonIssueFixer(repo_root, check_only=True, dry_run=False)
        issues = fixer.fix_async_tests_without_timeout()

        assert len(issues) >= 1, "Issues must not be empty"
        assert any("Async test missing timeout" in issue for issue in issues), "in is not valid"

    def test_fix_async_without_timeout(self, tmp_repo):
        """Test fixing async tests without timeout."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_async.py"
        test_file.write_text("""@pytest.mark.asyncio
async def test_async_func():
    await asyncio.sleep(0)
""")

        fixer = CommonIssueFixer(repo_root, check_only=False, dry_run=False)
        issues = fixer.fix_async_tests_without_timeout()

        content = test_file.read_text()
        assert "@pytest.mark.timeout(30)" in content, "Content must not be empty"
        assert len(issues) > 0, "Issues must not be empty"

    def test_timeout_injected_after_asyncio(self, tmp_repo):
        """Test that timeout decorator is inserted after asyncio decorator."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_async.py"
        test_file.write_text("""@pytest.mark.asyncio
async def test_func():
    pass
""")

        fixer = CommonIssueFixer(repo_root, check_only=False, dry_run=False)
        issues = fixer.fix_async_tests_without_timeout()

        content = test_file.read_text()
        lines = content.split("\n")

        # Find indices of decorators
        asyncio_line = next(i for i, l in enumerate(lines) if "@pytest.mark.asyncio" in l)
        timeout_line = next(i for i, l in enumerate(lines) if "@pytest.mark.timeout" in l)

        # Timeout should come after asyncio
        assert timeout_line == asyncio_line + 1, "timeout_line is not valid"

    def test_skip_async_with_timeout(self, tmp_repo):
        """Test that async tests with timeout are not modified."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_async.py"
        original = """@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_func():
    pass
"""
        test_file.write_text(original)

        fixer = CommonIssueFixer(repo_root, check_only=False, dry_run=False)
        issues = fixer.fix_async_tests_without_timeout()

        content = test_file.read_text()
        assert content == original, "Content must not be empty"
        assert len(issues) == 0, "Issues must not be empty"

    def test_skip_non_async_tests(self, tmp_repo):
        """Test that regular tests are not modified."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_sync.py"
        test_file.write_text("""
def test_regular():
    assert True, "True is not valid"
""")

        fixer = CommonIssueFixer(repo_root, check_only=False, dry_run=False)
        issues = fixer.fix_async_tests_without_timeout()

        content = test_file.read_text()
        assert "@pytest.mark.timeout" not in content, "Content must not be empty"
        assert len(issues) == 0, "Issues must not be empty"

    def test_multiple_async_tests(self, tmp_repo):
        """Test handling multiple async tests."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_async.py"
        test_file.write_text("""
import pytest

@pytest.mark.asyncio
async def test_one():
    pass

@pytest.mark.asyncio
async def test_two():
    pass

@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_three():
    pass
""")

        fixer = CommonIssueFixer(repo_root, check_only=False, dry_run=False)
        issues = fixer.fix_async_tests_without_timeout()

        content = test_file.read_text()
        # Count timeout decorators
        timeout_count = content.count("@pytest.mark.timeout(30)")
        # Should have added 2 (test_one and test_two, but not test_three)
        assert timeout_count >= 2, "timeout_count must be positive"
        assert len(issues) >= 2, "Issues must not be empty"

    def test_preserves_indentation_in_class(self, tmp_repo):
        """Test that indentation is preserved in class methods."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_async.py"
        test_file.write_text("""
class TestAsync:
    @pytest.mark.asyncio
    async def test_method(self):
        pass
""")

        fixer = CommonIssueFixer(repo_root, check_only=False, dry_run=False)
        issues = fixer.fix_async_tests_without_timeout()

        content = test_file.read_text()
        lines = content.split("\n")

        # Check that timeout decorator has same indentation as asyncio
        asyncio_line = next(l for l in lines if "@pytest.mark.asyncio" in l)
        timeout_line = next(l for l in lines if "@pytest.mark.timeout" in l)

        asyncio_indent = len(asyncio_line) - len(asyncio_line.lstrip())
        timeout_indent = len(timeout_line) - len(timeout_line.lstrip())

        assert asyncio_indent == timeout_indent, "asyncio_indent is not valid"
        assert content.count("@pytest.mark.timeout") == 1, "exactly one timeout expected"
        assert len(issues) == 1, "one issue expected"

    def test_idempotent_for_indented_methods(self, tmp_repo):
        """Running the fixer twice must not stack duplicate timeout decorators."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_async.py"
        test_file.write_text(
            "class TestAsync:\n"
            "    @pytest.mark.asyncio\n"
            "    async def test_method(self):\n"
            "        pass\n"
        )

        CommonIssueFixer(
            repo_root, check_only=False, dry_run=False
        ).fix_async_tests_without_timeout()
        second = CommonIssueFixer(
            repo_root, check_only=False, dry_run=False
        ).fix_async_tests_without_timeout()

        assert test_file.read_text().count("@pytest.mark.timeout(30)") == 1, "decorator stacked"
        assert second == [], "second run must report nothing"

    def test_string_literal_fixtures_untouched(self, tmp_repo):
        """Decorators inside string literals are data and must not be rewritten."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_fixture_writer.py"
        original = (
            "def test_writer(tmp_path):\n"
            '    (tmp_path / "t.py").write_text("""\n'
            "@pytest.mark.asyncio\n"
            "async def test_inner():\n"
            "    pass\n"
            '""")\n'
        )
        test_file.write_text(original)

        issues = CommonIssueFixer(
            repo_root, check_only=False, dry_run=False
        ).fix_async_tests_without_timeout()

        assert test_file.read_text() == original, "string literal content was modified"
        assert issues == [], "no issues expected for decorators inside strings"

    def test_existing_timeout_before_asyncio_is_preserved(self, tmp_repo):
        repo_root, tests_dir = tmp_repo
        test_file = tests_dir / "test_async.py"
        original = (
            "@pytest.mark.timeout(60)\n"
            "@pytest.mark.asyncio\n"
            "async def test_method():\n"
            "    pass\n"
        )
        test_file.write_text(original)

        issues = CommonIssueFixer(
            repo_root, check_only=False, dry_run=False
        ).fix_async_tests_without_timeout()

        assert test_file.read_text() == original
        assert issues == []

    def test_unterminated_string_fails_closed(self, tmp_repo):
        repo_root, tests_dir = tmp_repo
        test_file = tests_dir / "test_async.py"
        original = "fixture = '''\n@pytest.mark.asyncio\nasync def test_inner():\n    pass\n"
        test_file.write_text(original)

        with pytest.raises(ValueError, match="Cannot safely scan tests/test_async.py"):
            CommonIssueFixer(
                repo_root, check_only=False, dry_run=False
            ).fix_async_tests_without_timeout()

        assert test_file.read_text() == original

    def test_dry_run_mode(self, tmp_repo):
        """Test that dry-run doesn't modify files."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_async.py"
        original = """@pytest.mark.asyncio
async def test_func():
    pass
"""
        test_file.write_text(original)

        fixer = CommonIssueFixer(repo_root, check_only=False, dry_run=True)
        issues = fixer.fix_async_tests_without_timeout()

        content = test_file.read_text()
        assert content == original, "Content must not be empty"

    def test_check_only_mode(self, tmp_repo):
        """Test that check-only doesn't modify files."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_async.py"
        original = """@pytest.mark.asyncio
async def test_func():
    pass
"""
        test_file.write_text(original)

        fixer = CommonIssueFixer(repo_root, check_only=True, dry_run=False)
        issues = fixer.fix_async_tests_without_timeout()

        content = test_file.read_text()
        assert content == original, "Content must not be empty"
        assert len(issues) > 0, "Issues must not be empty"

    def test_default_timeout_value(self, tmp_repo):
        """Test that default timeout value is 30 seconds."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_async.py"
        test_file.write_text("""@pytest.mark.asyncio
async def test_func():
    pass
""")

        fixer = CommonIssueFixer(repo_root, check_only=False, dry_run=False)
        issues = fixer.fix_async_tests_without_timeout()

        content = test_file.read_text()
        assert "@pytest.mark.timeout(30)" in content, "Content must not be empty"

    def test_custom_timeout_preserved(self, tmp_repo):
        """Test that custom timeout values are preserved."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_async.py"
        test_file.write_text("""@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_slow():
    pass
""")

        fixer = CommonIssueFixer(repo_root, check_only=False, dry_run=False)
        issues = fixer.fix_async_tests_without_timeout()

        content = test_file.read_text()
        # Should not add another timeout
        assert content.count("@pytest.mark.timeout") == 1, "Content must not be empty"
        assert "@pytest.mark.timeout(60)" in content, "Content must not be empty"
        assert len(issues) == 0, "Issues must not be empty"

    def test_handles_empty_tests_dir(self, tmp_repo):
        """Test handling when tests directory is empty."""
        repo_root, tests_dir = tmp_repo
        # Don't create any test files

        fixer = CommonIssueFixer(repo_root, check_only=False, dry_run=False)
        issues = fixer.fix_async_tests_without_timeout()

        assert len(issues) == 0, "Issues must not be empty"

    def test_no_tests_dir(self, tmp_path):
        """Test handling when tests directory doesn't exist."""
        repo_root = tmp_path / "test_repo"
        repo_root.mkdir()
        # Don't create tests directory

        fixer = CommonIssueFixer(repo_root, check_only=False, dry_run=False)
        issues = fixer.fix_async_tests_without_timeout()

        assert len(issues) == 0, "Issues must not be empty"

    def test_mixed_sync_and_async(self, tmp_repo):
        """Test handling mix of sync and async tests."""
        repo_root, tests_dir = tmp_repo

        test_file = tests_dir / "test_mixed.py"
        test_file.write_text("""
def test_sync():
    assert True, "True is not valid"

@pytest.mark.asyncio
async def test_async():
    await asyncio.sleep(0)

def test_sync_2():
    assert True, "True is not valid"
""")

        fixer = CommonIssueFixer(repo_root, check_only=False, dry_run=False)
        issues = fixer.fix_async_tests_without_timeout()

        content = test_file.read_text()
        # Should add timeout only to async test
        assert content.count("@pytest.mark.timeout") == 1, "Content must not be empty"
        assert len(issues) == 1, "Issues must not be empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
