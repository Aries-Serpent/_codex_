"""Tests for scripts/philosophy_parser.py — Phase 6: Philosophy Reading/Writing.

Covers _extract_headings, _count_words, parse_document, cmd_parse,
cmd_write, cmd_status, and main entry point.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# ── Import helper ────────────────────────────────────────────────────────────


def _import():
    """Import philosophy_parser, skipping if unavailable."""
    repo_root = Path(__file__).parent.parent.parent
    scripts_dir = str(repo_root / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    return pytest.importorskip("philosophy_parser", reason="philosophy_parser not importable")


# ── _extract_headings ────────────────────────────────────────────────────────


class TestExtractHeadings:
    def test_empty_text(self):
        mod = _import()
        assert mod._extract_headings("") == [], "Condition must be true"

    def test_single_h1(self):
        mod = _import()
        result = mod._extract_headings("# My Title\nsome content")
        assert len(result) == 1, "Result must not be empty"
        assert result[0]["title"] == "My Title", "Result must not be empty"
        assert result[0]["level"] == 1, "Result must not be empty"

    def test_multiple_headings(self):
        mod = _import()
        text = "# H1\nContent 1\n## H2\nContent 2\n### H3\n"
        result = mod._extract_headings(text)
        assert len(result) == 3, "Result must not be empty"
        assert result[0]["level"] == 1, "Result must not be empty"
        assert result[1]["level"] == 2, "Result must not be empty"
        assert result[2]["level"] == 3, "Result must not be empty"

    def test_content_captured(self):
        mod = _import()
        text = "# Title\nline one\nline two\n"
        result = mod._extract_headings(text)
        assert "line one" in result[0]["content"], "Result must not be empty"

    def test_no_headings_returns_empty(self):
        mod = _import()
        text = "Just some plain text without headings."
        assert mod._extract_headings(text) == [], "Condition must be true"


# ── _count_words ─────────────────────────────────────────────────────────────


class TestCountWords:
    def test_empty_string(self):
        mod = _import()
        assert mod._count_words("") == 0, "Count must be greater than zero"

    def test_basic_sentence(self):
        mod = _import()
        assert mod._count_words("hello world foo bar") == 4, "Count must be greater than zero"

    def test_with_punctuation(self):
        mod = _import()
        assert mod._count_words("hello, world!") == 2

    def test_with_numbers(self):
        mod = _import()
        assert mod._count_words("version 1 2 3") == 4, "Count must be greater than zero"


# ── parse_document ───────────────────────────────────────────────────────────


class TestParseDocument:
    def test_basic_document(self, tmp_path):
        mod = _import()
        doc = tmp_path / "test.md"
        doc.write_text("# Title\n\nContent here.\n\n## Section\nMore content.\n")
        # Need REPO_ROOT to compute relative path
        original = mod.REPO_ROOT
        mod.REPO_ROOT = tmp_path
        try:
            result = mod.parse_document(doc)
        finally:
            mod.REPO_ROOT = original
        assert result["heading_count"] == 2, "Result must not be empty"
        assert result["word_count"] > 0, "Value must be greater than zero"
        assert result["line_count"] > 0, "Value must be greater than zero"

    def test_returns_required_keys(self, tmp_path):
        mod = _import()
        doc = tmp_path / "doc.md"
        doc.write_text("# Hello\n\nWorld.\n")
        original = mod.REPO_ROOT
        mod.REPO_ROOT = tmp_path
        try:
            result = mod.parse_document(doc)
        finally:
            mod.REPO_ROOT = original
        for key in [
            "path",
            "word_count",
            "line_count",
            "heading_count",
            "headings",
            "concepts",
            "action_items",
        ]:
            assert key in result, "Result must not be empty"

    def test_extracts_action_items(self, tmp_path):
        mod = _import()
        doc = tmp_path / "tasks.md"
        doc.write_text("# Tasks\n\n- [ ] Do this\n- [x] Done that\n")
        original = mod.REPO_ROOT
        mod.REPO_ROOT = tmp_path
        try:
            result = mod.parse_document(doc)
        finally:
            mod.REPO_ROOT = original
        assert len(result["action_items"]) == 2, "Collection must not be empty"

    def test_extracts_concepts(self, tmp_path):
        mod = _import()
        doc = tmp_path / "concepts.md"
        doc.write_text(
            "# Machine Learning\n\nDeep Learning is great.\nNeural Networks work well.\n"
        )
        original = mod.REPO_ROOT
        mod.REPO_ROOT = tmp_path
        try:
            result = mod.parse_document(doc)
        finally:
            mod.REPO_ROOT = original
        assert any("Learning" in c or "Networks" in c for c in result["concepts"]), "Result must not be empty"


# ── cmd_parse ────────────────────────────────────────────────────────────────


class TestCmdParse:
    def test_parse_specific_file(self, tmp_path, monkeypatch):
        mod = _import()
        doc = tmp_path / "test.md"
        doc.write_text("# Test\nContent\n")
        monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
        # Parse a specific file
        rc = mod.cmd_parse(str(doc))
        assert rc == 0, "rc is not valid"

    def test_parse_nonexistent_file_returns_1(self, tmp_path, monkeypatch):
        mod = _import()
        monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
        rc = mod.cmd_parse(str(tmp_path / "does_not_exist.md"))
        assert rc == 1, "rc is not valid"

    def test_scan_no_docs_found(self, tmp_path, monkeypatch):
        mod = _import()
        monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(mod, "DOCS_DIR", tmp_path / "docs")
        rc = mod.cmd_parse()  # no path_arg, scan mode
        assert rc == 0, "rc is not valid"

    def test_scan_with_matching_docs(self, tmp_path, monkeypatch):
        mod = _import()
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        roadmap = docs_dir / "ROADMAP_TEST.md"
        roadmap.write_text("# Roadmap\nSome roadmap content.\n")
        monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(mod, "DOCS_DIR", docs_dir)
        monkeypatch.setattr(mod, "PHILOSOPHY_DIR", tmp_path / "philosophy")
        rc = mod.cmd_parse()
        assert rc == 0, "rc is not valid"


# ── cmd_write ────────────────────────────────────────────────────────────────


class TestCmdWrite:
    def test_creates_philosophy_doc(self, tmp_path, monkeypatch):
        mod = _import()
        phil_dir = tmp_path / "philosophy"
        monkeypatch.setattr(mod, "PHILOSOPHY_DIR", phil_dir)
        monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
        rc = mod.cmd_write(topic="Test Topic", template="basic")
        assert rc == 0, "rc is not valid"
        docs = list(phil_dir.glob("*.md"))
        assert len(docs) == 1, "Docs must not be empty"
        assert "Test Topic" in docs[0].read_text(), "Condition must be true"

    def test_structured_template(self, tmp_path, monkeypatch):
        mod = _import()
        phil_dir = tmp_path / "philosophy"
        monkeypatch.setattr(mod, "PHILOSOPHY_DIR", phil_dir)
        monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
        rc = mod.cmd_write(topic="Structured Topic", template="structured")
        assert rc == 0, "rc is not valid"

    def test_unknown_template_falls_back(self, tmp_path, monkeypatch):
        mod = _import()
        phil_dir = tmp_path / "philosophy"
        monkeypatch.setattr(mod, "PHILOSOPHY_DIR", phil_dir)
        monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
        rc = mod.cmd_write(topic="X", template="unknown_template")
        assert rc == 0, "rc is not valid"

    def test_incorporates_session_observations(self, tmp_path, monkeypatch):
        mod = _import()
        phil_dir = tmp_path / "philosophy"
        sessions_dir = tmp_path / "memory" / "sessions"
        sessions_dir.mkdir(parents=True)
        sess = sessions_dir / "sess_001.json"
        sess.write_text(
            json.dumps(
                {
                    "observations": ["item one", "item two"],
                    "summary": "A test session",
                }
            ),
            encoding="utf-8",
        )
        monkeypatch.setattr(mod, "PHILOSOPHY_DIR", phil_dir)
        monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
        rc = mod.cmd_write(topic="Session Synthesis")
        assert rc == 0, "rc is not valid"


# ── cmd_status ───────────────────────────────────────────────────────────────


class TestCmdStatus:
    def test_status_no_docs(self, tmp_path, monkeypatch):
        mod = _import()
        monkeypatch.setattr(mod, "PHILOSOPHY_DIR", tmp_path / "philosophy")
        rc = mod.cmd_status()
        assert rc == 0, "rc is not valid"

    def test_status_with_docs(self, tmp_path, monkeypatch):
        mod = _import()
        phil_dir = tmp_path / "philosophy"
        phil_dir.mkdir()
        (phil_dir / "doc1.md").write_text("# Synthesis\nContent\n")
        (phil_dir / "doc2.md").write_text("# Another\nMore content\n")
        monkeypatch.setattr(mod, "PHILOSOPHY_DIR", phil_dir)
        rc = mod.cmd_status()
        assert rc == 0, "rc is not valid"


# ── main ─────────────────────────────────────────────────────────────────────


class TestMain:
    def test_main_write(self, tmp_path, monkeypatch):
        mod = _import()
        monkeypatch.setattr(mod, "PHILOSOPHY_DIR", tmp_path / "philosophy")
        monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
        with patch("sys.argv", ["philosophy_parser.py", "write", "--topic", "Test"]):
            rc = mod.main()
        assert rc == 0, "rc is not valid"

    def test_main_status(self, tmp_path, monkeypatch):
        mod = _import()
        monkeypatch.setattr(mod, "PHILOSOPHY_DIR", tmp_path / "philosophy")
        with patch("sys.argv", ["philosophy_parser.py", "status"]):
            rc = mod.main()
        assert rc == 0, "rc is not valid"

    def test_main_parse_no_args(self, tmp_path, monkeypatch):
        mod = _import()
        monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(mod, "DOCS_DIR", tmp_path / "docs")
        with patch("sys.argv", ["philosophy_parser.py", "parse"]):
            rc = mod.main()
        assert rc == 0, "rc is not valid"

    def test_main_unknown_command_raises_system_exit(self, tmp_path):
        mod = _import()
        with patch("sys.argv", ["philosophy_parser.py", "unknown_cmd"]):
            with pytest.raises(SystemExit):
                mod.main()
