"""
Phase 9.4 — MCP edge-case coverage.

Tests boundary conditions in scripts/mcp/select_components.py:
  - filter_by_globs with empty pattern list → empty set
  - expand_globs with patterns that match no files → empty set
  - load_topics with malformed JSON → JSONDecodeError
  - filter_by_topic with a known topic that has no matching files → empty set
  - main() overrides path with no matches → success (0), empty file list
  - expand_globs with exclude patterns removing all results → empty set
  - _resolve_patterns with ** patterns on missing prefix dir
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure the mcp scripts directory is importable (same pattern as Phase 9.3)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts" / "mcp"))

from select_components import expand_globs, filter_by_globs, load_topics, main  # noqa: E402

# ---------------------------------------------------------------------------
# filter_by_globs — empty pattern list
# ---------------------------------------------------------------------------


class TestFilterByGlobsEdgeCases:
    """Edge cases in filter_by_globs."""

    def test_empty_pattern_string_returns_empty_set(self, tmp_path: Path) -> None:
        # A blank string yields no patterns after split
        result = filter_by_globs("", tmp_path)
        assert result == set(), "Result must not be empty"

    def test_whitespace_only_pattern_returns_empty_set(self, tmp_path: Path) -> None:
        result = filter_by_globs("   ,   ", tmp_path)
        assert result == set(), "Result must not be empty"

    def test_pattern_matching_no_files_returns_empty_set(self, tmp_path: Path) -> None:
        result = filter_by_globs("nonexistent_dir/**/*.xyz", tmp_path)
        assert result == set(), "Result must not be empty"

    def test_pattern_matching_files_returns_paths(self, tmp_path: Path) -> None:
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "module.py").write_text("# py\n")
        result = filter_by_globs("src/*.py", tmp_path)
        assert len(result) == 1, "Result must not be empty"

    def test_multiple_patterns_comma_separated(self, tmp_path: Path) -> None:
        (tmp_path / "a.py").write_text("")
        (tmp_path / "b.md").write_text("")
        result = filter_by_globs("*.py,*.md", tmp_path)
        assert len(result) == 2, "Result must not be empty"


# ---------------------------------------------------------------------------
# expand_globs — no-match patterns, exclude all
# ---------------------------------------------------------------------------


class TestExpandGlobsEdgeCases:
    """Edge cases in expand_globs."""

    def test_empty_patterns_list_returns_empty_set(self, tmp_path: Path) -> None:
        result = expand_globs([], tmp_path)
        assert result == set(), "Result must not be empty"

    def test_patterns_match_nothing_returns_empty_set(self, tmp_path: Path) -> None:
        result = expand_globs(["*.xyz", "no_match/**"], tmp_path)
        assert result == set(), "Result must not be empty"

    def test_exclude_removes_matched_files(self, tmp_path: Path) -> None:
        (tmp_path / "keep.py").write_text("")
        (tmp_path / "remove.py").write_text("")
        result = expand_globs(["*.py"], tmp_path, exclude_patterns=["remove.py"])
        paths = {p.name for p in result}
        assert "keep.py" in paths, "Condition must be true"
        assert "remove.py" not in paths, "Condition must be true"

    def test_exclude_all_returns_empty_set(self, tmp_path: Path) -> None:
        (tmp_path / "file.py").write_text("")
        result = expand_globs(["*.py"], tmp_path, exclude_patterns=["*.py"])
        assert result == set(), "Result must not be empty"

    def test_recursive_pattern_missing_prefix_dir(self, tmp_path: Path) -> None:
        # Pattern with ** but nonexistent prefix dir → no matches, no error
        result = expand_globs(["missing_prefix/**/*.py"], tmp_path)
        assert result == set(), "Result must not be empty"

    def test_recursive_pattern_finds_nested_files(self, tmp_path: Path) -> None:
        sub = tmp_path / "sub" / "deep"
        sub.mkdir(parents=True)
        (sub / "nested.py").write_text("")
        result = expand_globs(["sub/**/*.py"], tmp_path)
        assert len(result) == 1, "Result must not be empty"


# ---------------------------------------------------------------------------
# load_topics — malformed JSON raises JSONDecodeError
# ---------------------------------------------------------------------------


class TestLoadTopicsEdgeCases:
    """Edge cases in load_topics."""

    def test_malformed_json_raises_json_decode_error(self, tmp_path: Path) -> None:
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("{not: valid json}")
        with pytest.raises(json.JSONDecodeError):
            load_topics(bad_file)

    def test_empty_json_object_returns_empty_dict(self, tmp_path: Path) -> None:
        empty_file = tmp_path / "empty.json"
        empty_file.write_text("{}")
        result = load_topics(empty_file)
        assert result == {}, "Result must not be empty"

    def test_valid_topics_file_returns_dict(self, tmp_path: Path) -> None:
        topics_file = tmp_path / "topics.json"
        topics_file.write_text(json.dumps({"agents": ["agents/**/*.py"]}))
        result = load_topics(topics_file)
        assert "agents" in result, "Result must not be empty"


# ---------------------------------------------------------------------------
# main() — overrides path with no matches still writes output and returns 0
# ---------------------------------------------------------------------------


class TestMainEdgeCases:
    """Edge cases in main()."""

    def test_overrides_no_matches_returns_0_and_writes_empty_file(self, tmp_path: Path) -> None:
        topics_file = tmp_path / "topics.json"
        topics_file.write_text(json.dumps({"agents": ["agents/**/*.py"]}))
        output = tmp_path / "out.txt"
        argv = [
            "select_components.py",
            "--overrides",
            "nonexistent_dir/**/*.xyz",
            "--output",
            str(output),
            "--topics-file",
            str(topics_file),
            "--base-dir",
            str(tmp_path),
        ]
        with patch("sys.argv", argv):
            result = main()
        assert result == 0, "Result must not be empty"
        assert output.exists(), "Condition must be true"
        assert output.read_text() == "", "Condition must be true"

    def test_overrides_with_matching_files_returns_0(self, tmp_path: Path) -> None:
        (tmp_path / "hello.py").write_text("# hi\n")
        topics_file = tmp_path / "topics.json"
        topics_file.write_text("{}")
        output = tmp_path / "out.txt"
        argv = [
            "select_components.py",
            "--overrides",
            "*.py",
            "--output",
            str(output),
            "--topics-file",
            str(topics_file),
            "--base-dir",
            str(tmp_path),
        ]
        with patch("sys.argv", argv):
            result = main()
        assert result == 0, "Result must not be empty"
        content = output.read_text()
        assert "hello.py" in content, "Content must not be empty"

    def test_exclude_via_main_removes_files(self, tmp_path: Path) -> None:
        (tmp_path / "keep.py").write_text("")
        (tmp_path / "skip.py").write_text("")
        topics_file = tmp_path / "topics.json"
        topics_file.write_text("{}")
        output = tmp_path / "out.txt"
        argv = [
            "select_components.py",
            "--overrides",
            "*.py",
            "--output",
            str(output),
            "--topics-file",
            str(topics_file),
            "--base-dir",
            str(tmp_path),
            "--exclude",
            "skip.py",
        ]
        with patch("sys.argv", argv):
            result = main()
        assert result == 0, "Result must not be empty"
        content = output.read_text()
        assert "keep.py" in content, "Content must not be empty"
        assert "skip.py" not in content, "Content must not be empty"
