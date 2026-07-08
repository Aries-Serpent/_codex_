"""
Phase 9.3 — MCP error-path coverage.

Tests error paths in scripts/mcp/select_components.py:
  - filter_by_topic with unknown topic → ValueError
  - main() with missing topics file → returns 1
  - main() with ValueError from filter_by_topic → returns 1
  - main() with KeyboardInterrupt → returns 130
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure the mcp scripts directory is importable (same pattern as Phase 9.2)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts" / "mcp"))

from select_components import filter_by_topic, main  # noqa: E402

# ---------------------------------------------------------------------------
# filter_by_topic — unknown topic raises ValueError
# ---------------------------------------------------------------------------


class TestFilterByTopicErrors:
    """Error paths in filter_by_topic."""

    def test_unknown_topic_raises_value_error(self, tmp_path: Path) -> None:
        topics_map = {"agents": ["agents/**/*.py"], "docs": ["docs/**/*.md"]}
        with pytest.raises(ValueError, match="Unknown topic: nonexistent"):
            filter_by_topic("nonexistent", topics_map, tmp_path)

    def test_unknown_topic_lists_available_in_message(self, tmp_path: Path) -> None:
        topics_map = {"alpha": ["src/**/*.py"], "beta": ["tests/**/*.py"]}
        with pytest.raises(ValueError, match="Available topics"):
            filter_by_topic("gamma", topics_map, tmp_path)

    def test_known_topic_returns_set(self, tmp_path: Path) -> None:
        (tmp_path / "src").mkdir()
        py_file = tmp_path / "src" / "module.py"
        py_file.write_text("# module\n")
        topics_map = {"src": ["src/**/*.py"]}
        result = filter_by_topic("src", topics_map, tmp_path)
        assert isinstance(result, set)


# ---------------------------------------------------------------------------
# main() — missing topics file returns 1
# ---------------------------------------------------------------------------


class TestMainMissingTopicsFile:
    """main() returns 1 when the topics file does not exist."""

    def test_missing_topics_file_returns_1(self, tmp_path: Path) -> None:
        output = tmp_path / "out.txt"
        missing_topics = tmp_path / "no_such_topics.json"
        argv = [
            "select_components.py",
            "--topic",
            "docs",
            "--output",
            str(output),
            "--topics-file",
            str(missing_topics),
        ]
        with patch("sys.argv", argv):
            result = main()
        assert result == 1, "Result must not be empty"


# ---------------------------------------------------------------------------
# main() — ValueError from filter_by_topic returns 1
# ---------------------------------------------------------------------------


class TestMainValueErrorReturns1:
    """main() catches ValueError and returns 1."""

    def test_unknown_topic_via_main_returns_1(self, tmp_path: Path) -> None:
        topics_file = tmp_path / "topics.json"
        topics_file.write_text(json.dumps({"known_topic": ["src/**/*.py"]}))
        output = tmp_path / "out.txt"
        argv = [
            "select_components.py",
            "--topic",
            "unknown_topic_xyz",
            "--output",
            str(output),
            "--topics-file",
            str(topics_file),
            "--base-dir",
            str(tmp_path),
        ]
        with patch("sys.argv", argv):
            result = main()
        assert result == 1, "Result must not be empty"


# ---------------------------------------------------------------------------
# main() — KeyboardInterrupt returns 130
# ---------------------------------------------------------------------------


class TestMainKeyboardInterruptReturns130:
    """main() catches KeyboardInterrupt and returns 130."""

    def test_keyboard_interrupt_returns_130(self, tmp_path: Path) -> None:
        topics_file = tmp_path / "topics.json"
        topics_file.write_text(json.dumps({"agents": ["agents/**/*.py"]}))
        output = tmp_path / "out.txt"
        argv = [
            "select_components.py",
            "--topic",
            "agents",
            "--output",
            str(output),
            "--topics-file",
            str(topics_file),
            "--base-dir",
            str(tmp_path),
        ]
        with patch("sys.argv", argv):
            with patch(
                "select_components.filter_by_topic",
                side_effect=KeyboardInterrupt,
            ):
                result = main()
        assert result == 130, "Result must not be empty"
