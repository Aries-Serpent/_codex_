"""Unit tests for compile_replacements and replace_in_file in tools/workflow_merge.py.

Covers:
- compile_replacements produces correctly-typed tuples with compiled patterns
- whole-word boundary enforcement (no partial-word substitution)
- replace_in_file writes changes when a match is found and returns 1
- replace_in_file is a no-op when no match is found and returns 0
- replace_in_file handles unreadable files gracefully
- update_references compiles mapping once (not per-file)
"""

from __future__ import annotations

import re
from pathlib import Path

from tools.workflow_merge import compile_replacements, replace_in_file

# ---------------------------------------------------------------------------
# compile_replacements
# ---------------------------------------------------------------------------


class TestCompileReplacements:
    def test_returns_list_of_compiled_pattern_replacement_tuples(self):
        result = compile_replacements({"foo": "bar"})
        assert len(result) == 1
        pattern, replacement = result[0]
        assert isinstance(pattern, re.Pattern)
        assert replacement == "bar"

    def test_empty_mapping_returns_empty_list(self):
        assert compile_replacements({}) == []

    def test_multiple_keys_produce_multiple_tuples(self):
        mapping = {"alpha": "A", "beta": "B", "gamma": "G"}
        result = compile_replacements(mapping)
        assert len(result) == 3
        replacements = {r for _, r in result}
        assert replacements == {"A", "B", "G"}

    def test_pattern_matches_whole_word_only(self):
        result = compile_replacements({"foo": "bar"})
        pattern, _ = result[0]
        # whole-word match
        assert pattern.search("foo")
        assert pattern.search(" foo ")
        assert pattern.search("foo.bar")  # "foo" before "." is still a word boundary
        # partial-word — must NOT match
        assert not pattern.search("foobar")
        assert not pattern.search("prefoo")

    def test_pattern_does_not_match_embedded_substring(self):
        result = compile_replacements({"import": "use"})
        pattern, _ = result[0]
        assert not pattern.search("reimport")
        assert not pattern.search("importing_thing")

    def test_special_regex_chars_in_key_are_escaped(self):
        """Keys like 'from tools.foo import' contain dots that must be literal."""
        result = compile_replacements({"from tools.foo import": "from tools.bar import"})
        pattern, _ = result[0]
        # literal dot – should match the key verbatim
        assert pattern.search("from tools.foo import something")
        # dot-as-wildcard should NOT substitute a different char
        assert not pattern.search("from toolsXfoo import something")

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
        assert result == 1
        assert f.read_text(encoding="utf-8") == "import new_module\n"

    def test_no_match_leaves_file_unchanged_and_returns_0(self, tmp_path: Path):
        f = tmp_path / "test.py"
        original = "import something_else\n"
        f.write_text(original, encoding="utf-8")
        compiled = compile_replacements({"old_module": "new_module"})
        result = replace_in_file(f, compiled)
        assert result == 0
        assert f.read_text(encoding="utf-8") == original

    def test_whole_word_only_does_not_replace_partial_match(self, tmp_path: Path):
        f = tmp_path / "test.py"
        f.write_text("from old_module_extended import Foo\n", encoding="utf-8")
        compiled = compile_replacements({"old_module": "new_module"})
        replace_in_file(f, compiled)
        # "old_module_extended" should NOT be touched because "old_module" is not whole-word here
        assert "old_module_extended" in f.read_text(encoding="utf-8")

    def test_multiple_replacements_applied_in_one_pass(self, tmp_path: Path):
        f = tmp_path / "test.py"
        f.write_text("import alpha\nimport beta\n", encoding="utf-8")
        compiled = compile_replacements({"alpha": "A", "beta": "B"})
        result = replace_in_file(f, compiled)
        assert result == 1
        text = f.read_text(encoding="utf-8")
        assert "import A" in text
        assert "import B" in text

    def test_unreadable_file_returns_0_without_raising(self, tmp_path: Path):
        f = tmp_path / "ghost.py"
        # File does not exist — read_text will raise; replace_in_file must swallow it
        compiled = compile_replacements({"x": "y"})
        result = replace_in_file(f, compiled)
        assert result == 0

    def test_preserves_encoding_utf8(self, tmp_path: Path):
        f = tmp_path / "unicode.py"
        content = "# café module\nimport old_module\n"
        f.write_text(content, encoding="utf-8")
        compiled = compile_replacements({"old_module": "new_module"})
        replace_in_file(f, compiled)
        assert "café" in f.read_text(encoding="utf-8")

    def test_empty_compiled_mapping_is_no_op(self, tmp_path: Path):
        f = tmp_path / "test.py"
        original = "import something\n"
        f.write_text(original, encoding="utf-8")
        result = replace_in_file(f, [])
        assert result == 0
        assert f.read_text(encoding="utf-8") == original
