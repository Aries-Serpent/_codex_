"""Unit tests for compile_replacements, replace_in_file, and update_references
in tools/workflow_merge.py.

Covers:
- compile_replacements produces correctly-typed tuples with compiled patterns
- whole-word boundary enforcement (no partial-word substitution)
- dot-terminated tokens (attribute-access style) are matched correctly
- replace_in_file writes changes when a match is found and returns 1
- replace_in_file is a no-op when no match is found and returns 0
- replace_in_file handles unreadable files gracefully
- update_references compiles mapping once and returns correct changed/scanned counts
"""

from __future__ import annotations

import re
from pathlib import Path

from tools.workflow_merge import compile_replacements, replace_in_file, update_references

# ---------------------------------------------------------------------------
# compile_replacements
# ---------------------------------------------------------------------------


class TestCompileReplacements:
    def test_returns_list_of_compiled_pattern_replacement_tuples(self):
        result = compile_replacements({"foo": "bar"})
        assert len(result) == 1, "Result must not be empty"
        pattern, replacement = result[0]
        assert isinstance(pattern, re.Pattern)
        assert replacement == "bar", "replacement is not valid"

    def test_empty_mapping_returns_empty_list(self):
        assert compile_replacements({}) == [], "Condition must be true"

    def test_multiple_keys_produce_multiple_tuples(self):
        mapping = {"alpha": "A", "beta": "B", "gamma": "G"}
        result = compile_replacements(mapping)
        assert len(result) == 3, "Result must not be empty"
        replacements = {r for _, r in result}
        assert replacements == {"A", "B", "G"}

    def test_pattern_matches_whole_word_only(self):
        result = compile_replacements({"foo": "bar"})
        pattern, _ = result[0]
        # whole-word match
        assert pattern.search("foo"), "Condition must be true"
        assert pattern.search(" foo "), "Condition must be true"
        # partial-word — must NOT match
        assert not pattern.search("foobar"), "Condition must be true"
        assert not pattern.search("prefoo"), "Condition must be true"

    def test_dot_terminated_key_matches_followed_by_word_char(self):
        """Keys like 'workflow.' (attribute-access tokens) must match 'workflow.something'."""
        result = compile_replacements({"workflow.": "codex_workflow."})
        pattern, _ = result[0]
        # The dot ends the key — the next char is a word char; must still match
        assert pattern.search("workflow.something"), "Condition must be true"
        assert pattern.search("from workflow.util import"), "Condition must be true"

    def test_pattern_does_not_match_embedded_substring(self):
        result = compile_replacements({"import": "use"})
        pattern, _ = result[0]
        assert not pattern.search("reimport"), "Condition must be true"
        assert not pattern.search("importing_thing"), "Condition must be true"

    def test_special_regex_chars_in_key_are_escaped(self):
        """Keys like 'from tools.foo import' contain dots that must be literal."""
        result = compile_replacements({"from tools.foo import": "from tools.bar import"})
        pattern, _ = result[0]
        # literal dot – should match the key verbatim
        assert pattern.search("from tools.foo import something"), "Condition must be true"
        # dot-as-wildcard should NOT substitute a different char
        assert not pattern.search("from toolsXfoo import something"), "Condition must be true"

    def test_pattern_object_is_compiled_re(self):
        result = compile_replacements({"x": "y"})
        pattern, _ = result[0]
        assert hasattr(pattern, "sub"), "Expected a compiled re.Pattern with .sub()"


# ---------------------------------------------------------------------------
# replace_in_file
# ---------------------------------------------------------------------------


class TestReplaceInFile:
    def test_replaces_matching_token_and_returns_1(self, tmp_path: Path):
        f = tmp_path / "test.py"
        f.write_text("import old_module\n", encoding="utf-8")
        compiled = compile_replacements({"old_module": "new_module"})
        result = replace_in_file(f, compiled)
        assert result == 1, "Result must not be empty"
        assert f.read_text(encoding="utf-8") == "import new_module\n", "Condition must be true"

    def test_no_match_leaves_file_unchanged_and_returns_0(self, tmp_path: Path):
        f = tmp_path / "test.py"
        original = "import something_else\n"
        f.write_text(original, encoding="utf-8")
        compiled = compile_replacements({"old_module": "new_module"})
        result = replace_in_file(f, compiled)
        assert result == 0, "Result must not be empty"
        assert f.read_text(encoding="utf-8") == original, "Condition must be true"

    def test_whole_word_only_does_not_replace_partial_match(self, tmp_path: Path):
        f = tmp_path / "test.py"
        f.write_text("from old_module_extended import Foo\n", encoding="utf-8")
        compiled = compile_replacements({"old_module": "new_module"})
        replace_in_file(f, compiled)
        # "old_module_extended" should NOT be touched because "old_module" is not whole-word here
        assert "old_module_extended" in f.read_text(encoding="utf-8"), "Condition must be true"

    def test_multiple_replacements_applied_in_one_pass(self, tmp_path: Path):
        f = tmp_path / "test.py"
        f.write_text("import alpha\nimport beta\n", encoding="utf-8")
        compiled = compile_replacements({"alpha": "A", "beta": "B"})
        result = replace_in_file(f, compiled)
        assert result == 1, "Result must not be empty"
        text = f.read_text(encoding="utf-8")
        assert "import A" in text, "Condition must be true"
        assert "import B" in text, "Condition must be true"

    def test_unreadable_file_returns_0_without_raising(self, tmp_path: Path):
        f = tmp_path / "ghost.py"
        # File does not exist — read_text will raise; replace_in_file must swallow it
        compiled = compile_replacements({"x": "y"})
        result = replace_in_file(f, compiled)
        assert result == 0, "Result must not be empty"

    def test_preserves_encoding_utf8(self, tmp_path: Path):
        f = tmp_path / "unicode.py"
        content = "# café module\nimport old_module\n"
        f.write_text(content, encoding="utf-8")
        compiled = compile_replacements({"old_module": "new_module"})
        replace_in_file(f, compiled)
        assert "café" in f.read_text(encoding="utf-8"), "Condition must be true"

    def test_empty_compiled_mapping_is_no_op(self, tmp_path: Path):
        f = tmp_path / "test.py"
        original = "import something\n"
        f.write_text(original, encoding="utf-8")
        result = replace_in_file(f, [])
        assert result == 0, "Result must not be empty"
        assert f.read_text(encoding="utf-8") == original, "Condition must be true"


# ---------------------------------------------------------------------------
# update_references
# ---------------------------------------------------------------------------


class TestUpdateReferences:
    def test_compiles_mapping_once_and_updates_matching_files(self, tmp_path: Path, monkeypatch):
        """update_references must scan every file in REPO and apply replacements."""
        (tmp_path / "a.py").write_text("import old_mod\n", encoding="utf-8")
        (tmp_path / "b.py").write_text("import other\n", encoding="utf-8")

        monkeypatch.setattr("tools.workflow_merge.REPO", tmp_path)
        changed, scanned = update_references({"old_mod": "new_mod"})

        assert changed == 1, "changed is not valid"
        assert scanned == 2, "scanned is not valid"
        assert (tmp_path / "a.py").read_text(encoding="utf-8") == "import new_mod\n", "Condition must be true"
        assert (tmp_path / "b.py").read_text(encoding="utf-8") == "import other\n", "Condition must be true"

    def test_empty_mapping_changes_nothing(self, tmp_path: Path, monkeypatch):
        (tmp_path / "x.py").write_text("some content\n", encoding="utf-8")
        monkeypatch.setattr("tools.workflow_merge.REPO", tmp_path)
        changed, scanned = update_references({})
        assert changed == 0, "changed is not valid"
        assert scanned == 1, "scanned is not valid"
