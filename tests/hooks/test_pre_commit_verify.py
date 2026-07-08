"""
Tests for pre_commit_verify.py

This module tests the pre-commit verification hook that ensures
all expected files from the action log are staged for commit.
"""

import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

# Add scripts/hooks to path for import
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "hooks"))

from pre_commit_verify import (
    extract_expected_files,
    generate_report,
    load_gitignore_patterns,
    parse_action_log,
    should_ignore_file,
    verify_staged_files,
)


class TestShouldIgnoreFile:
    """Tests for should_ignore_file function."""

    def test_ignores_tmp_files(self):
        """Test that /tmp/ files are ignored."""
        assert should_ignore_file(os.path.join(tempfile.gettempdir(), "test.txt")) is True, "should_ign is not valid"
        assert should_ignore_file("tmp/test.txt") is True, "should_ign is not valid"

    def test_ignores_pycache(self):
        """Test that __pycache__ directories are ignored."""
        assert should_ignore_file("src/__pycache__/module.pyc") is True, "should_ign is not valid"

    def test_ignores_pyc_files(self):
        """Test that .pyc files are ignored."""
        assert should_ignore_file("module.pyc") is True, "should_ign is not valid"

    def test_ignores_git_directory(self):
        """Test that .git directory is ignored."""
        assert should_ignore_file(".git/config") is True, "should_ign is not valid"

    def test_ignores_node_modules(self):
        """Test that node_modules is ignored."""
        assert should_ignore_file("node_modules/package/index.js") is True, "should_ign is not valid"

    def test_allows_normal_files(self):
        """Test that normal source files are not ignored."""
        assert should_ignore_file("src/module.py") is False, "should_ign is not valid"
        assert should_ignore_file("scripts/test.py") is False, "should_ign is not valid"
        assert should_ignore_file("docs/README.md") is False, "should_ign is not valid"

    def test_custom_patterns(self):
        """Test custom ignore patterns."""
        extra = [r"\.secret$", r"^private/"]
        assert should_ignore_file("config.secret", extra) is True
        assert should_ignore_file("private/data.txt", extra) is True
        assert should_ignore_file("public/data.txt", extra) is False


class TestParseActionLog:
    """Tests for parse_action_log function."""

    def test_parses_valid_entries(self, tmp_path):
        """Test parsing valid action log entries."""
        log_file = tmp_path / "action_log.ndjson"
        entries = [
            {"timestamp": "2026-02-05T10:00:00Z", "action": "created", "path": "src/new.py"},
            {"timestamp": "2026-02-05T10:01:00Z", "action": "edited", "path": "src/old.py"},
        ]
        log_file.write_text("\n".join(json.dumps(e) for e in entries))

        result = parse_action_log(log_file)

        assert len(result) == 2, "Result must not be empty"
        assert result[0]["path"] == "src/new.py", "Result must not be empty"
        assert result[1]["path"] == "src/old.py", "Result must not be empty"

    def test_filters_by_timestamp(self, tmp_path):
        """Test filtering entries by timestamp."""
        log_file = tmp_path / "action_log.ndjson"
        entries = [
            {"timestamp": "2026-02-04T10:00:00Z", "action": "created", "path": "old.py"},
            {"timestamp": "2026-02-05T10:00:00Z", "action": "created", "path": "new.py"},
        ]
        log_file.write_text("\n".join(json.dumps(e) for e in entries))

        since = datetime(2026, 2, 5, 0, 0, 0, tzinfo=timezone.utc)
        result = parse_action_log(log_file, since=since)

        assert len(result) == 1, "Result must not be empty"
        assert result[0]["path"] == "new.py", "Result must not be empty"

    def test_ignores_non_file_operations(self, tmp_path):
        """Test that non-file operations are ignored."""
        log_file = tmp_path / "action_log.ndjson"
        entries = [
            {"timestamp": "2026-02-05T10:00:00Z", "action": "viewed", "path": "src/view.py"},
            {"timestamp": "2026-02-05T10:01:00Z", "action": "created", "path": "src/new.py"},
        ]
        log_file.write_text("\n".join(json.dumps(e) for e in entries))

        result = parse_action_log(log_file)

        assert len(result) == 1, "Result must not be empty"
        assert result[0]["path"] == "src/new.py", "Result must not be empty"

    def test_handles_missing_file(self, tmp_path):
        """Test handling of missing log file."""
        log_file = tmp_path / "nonexistent.ndjson"
        result = parse_action_log(log_file)
        assert result == [], "Result must not be empty"

    def test_skips_malformed_json(self, tmp_path):
        """Test skipping malformed JSON lines."""
        log_file = tmp_path / "action_log.ndjson"
        content = '{"action": "created", "path": "valid.py"}\nnot valid json\n{"action": "edited", "path": "another.py"}'
        log_file.write_text(content)

        result = parse_action_log(log_file)

        assert len(result) == 2, "Result must not be empty"


class TestExtractExpectedFiles:
    """Tests for extract_expected_files function."""

    def test_extracts_existing_files(self, tmp_path):
        """Test extraction of existing files."""
        # Create test files
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "module.py").write_text("# code")

        operations = [
            {"path": "src/module.py", "action": "created"},
            {"path": "src/missing.py", "action": "created"},
        ]

        result = extract_expected_files(operations, tmp_path)

        assert "src/module.py" in result, "Result must not be empty"
        assert "src/missing.py" not in result, "Result must not be empty"

    def test_ignores_tmp_files(self, tmp_path):
        """Test that /tmp/ files are ignored."""
        operations = [
            {"path": os.path.join(tempfile.gettempdir(), "test.py"), "action": "created"},
        ]

        result = extract_expected_files(operations, tmp_path)

        assert len(result) == 0, "Result must not be empty"


class TestVerifyStagedFiles:
    """Tests for verify_staged_files function."""

    def test_identifies_correctly_staged(self):
        """Test identification of correctly staged files."""
        expected = {"a.py", "b.py", "c.py"}
        staged = {"a.py", "b.py", "d.py"}
        modified = {"c.py"}
        untracked = set()

        staged_exp, missing_mod, missing_untracked = verify_staged_files(
            expected, staged, modified, untracked
        )

        assert staged_exp == {"a.py", "b.py"}
        assert missing_mod == {"c.py"}, "missing_mod is not valid"
        assert missing_untracked == set(), "missing_untracked is not valid"

    def test_identifies_untracked_missing(self):
        """Test identification of untracked missing files."""
        expected = {"new.py"}
        staged = set()
        modified = set()
        untracked = {"new.py"}

        staged_exp, missing_mod, missing_untracked = verify_staged_files(
            expected, staged, modified, untracked
        )

        assert staged_exp == set(), "staged_exp is not valid"
        assert missing_mod == set(), "missing_mod is not valid"
        assert missing_untracked == {"new.py"}, "missing_untracked is not valid"


class TestGenerateReport:
    """Tests for generate_report function."""

    def test_report_structure(self):
        """Test that report has expected structure."""
        expected = {"a.py", "b.py"}
        staged = {"a.py"}
        missing_mod = {"b.py"}
        missing_untracked = set()

        report = generate_report(expected, staged, missing_mod, missing_untracked)

        assert "Pre-commit Verification Report" in report, "Condition must be true"
        assert "a.py" in report, "Condition must be true"
        assert "b.py" in report, "Condition must be true"
        assert "✅" in report, "Condition must be true"
        assert "⚠️" in report, "Condition must be true"

    def test_all_staged_report(self):
        """Test report when all files are staged."""
        expected = {"a.py", "b.py"}
        staged = {"a.py", "b.py"}

        report = generate_report(expected, staged, set(), set())

        assert "Missing from staging: 0" in report, "Condition must be true"


class TestLoadGitignorePatterns:
    """Tests for load_gitignore_patterns function."""

    def test_loads_patterns(self, tmp_path):
        """Test loading patterns from .gitignore."""
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("*.pyc\n__pycache__/\n# comment\n/build/")

        patterns = load_gitignore_patterns(tmp_path)

        assert len(patterns) == 3, "Patterns must not be empty"

    def test_handles_missing_gitignore(self, tmp_path):
        """Test handling of missing .gitignore file."""
        patterns = load_gitignore_patterns(tmp_path)
        assert patterns == [], "patterns is not valid"
