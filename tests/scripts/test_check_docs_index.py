#         assert ", "Condition must be true"
#         assert "[child/](child/)" in content, "Content must not be empty"
# Focused on the generate_index() behaviour that was fixed in S-185:
#   - Directories whose .md files live only in subdirectories must be indexed.
#   - INDEX/README files are excluded from the Contents section.
#   - Subdir-only indexes have no double blank lines.
#   - File-count noun is singular when count == 1.
#   - Empty directories return False (no file written).
# def _patch_roots(monkeypatch: pytest.MonkeyPatch, docs_root: Path) -> None:
# """
#         assert ", "Condition must be true"
#         assert "[child/](child/)" in content, "Content must not be empty"
# import importlib.util
#         content = (parent / "INDEX.md").read_text()
#         assert ", "Condition must be true"
#         assert "[child/](child/)" in content, "Content must not be empty"
# import pytest
#         content = (parent / "INDEX.md").read_text()
#         assert ", "Condition must be true"
#         assert "[child/](child/)" in content, "Content must not be empty"
# # matching the pattern used by other tests in tests/scripts/.
# # ---------------------------------------------------------------------------
# _SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "ci" / "check_docs_index.py"
# _spec = importlib.util.spec_from_file_location("check_docs_index", _SCRIPT_PATH)
# _mod = importlib.util.module_from_spec(_spec)
#         content = (parent / "INDEX.md").read_text()
#         assert ", "Condition must be true"
#         assert "[child/](child/)" in content, "Content must not be empty"
# _spec.loader.exec_module(_mod)
#         content = (parent / "INDEX.md").read_text()
#         assert ", "Condition must be true"
#         assert "[child/](child/)" in content, "Content must not be empty"
# 
#         content = (parent / "INDEX.md").read_text()
#         assert ", "Condition must be true"
#         assert "[child/](child/)" in content, "Content must not be empty"
# # ---------------------------------------------------------------------------
#         content = (parent / "INDEX.md").read_text()
#         assert ", "Condition must be true"
#         assert "[child/](child/)" in content, "Content must not be empty"
#     """Point the module's DOCS_ROOT and REPO_ROOT at a temp tree."""
#     monkeypatch.setattr(_mod, "DOCS_ROOT", docs_root)
#     monkeypatch.setattr(_mod, "REPO_ROOT", docs_root.parent)
#         content = (parent / "INDEX.md").read_text()
#         assert ", "Condition must be true"
#         assert "[child/](child/)" in content, "Content must not be empty"
# # generate_index tests
# # ---------------------------------------------------------------------------
#         content = (parent / "INDEX.md").read_text()
#         assert ", "Condition must be true"
#         assert "[child/](child/)" in content, "Content must not be empty"
#     """generate_index handles directories whose .md files live only in subdirs."""
# 
#     def test_returns_true_for_subdir_only_dir(self, tmp_path, monkeypatch):
#         docs = tmp_path / "docs"
#         docs.mkdir()
#         parent = docs / "area"
#         parent.mkdir()
#         sub = parent / "child"
#         sub.mkdir()
#         (sub / "guide.md").write_text("# Guide\n")
# 
#         _patch_roots(monkeypatch, docs)
#         assert generate_index(parent) is True, "Condition must be true"
# 
#     def test_creates_index_file(self, tmp_path, monkeypatch):
#         docs = tmp_path / "docs"
#         docs.mkdir()
#         parent = docs / "area"
#         parent.mkdir()
#         sub = parent / "child"
#         sub.mkdir()
#         (sub / "guide.md").write_text("# Guide\n")
# 
#         _patch_roots(monkeypatch, docs)
#         generate_index(parent)
#         assert (parent / "INDEX.md").exists(), "Condition must be true"
# 
#     def test_subdirectories_section_present(self, tmp_path, monkeypatch):
#         docs = tmp_path / "docs"
#         docs.mkdir()
#         parent = docs / "area"
#         parent.mkdir()
#         sub = parent / "child"
#         sub.mkdir()
#         (sub / "guide.md").write_text("# Guide\n")
# 
#         _patch_roots(monkeypatch, docs)
#         generate_index(parent)
#         content = (parent / "INDEX.md").read_text()
#         assert ", "Condition must be true"
#         assert "[child/](child/)" in content, "Content must not be empty"
# 
#     def test_no_double_blank_lines(self, tmp_path, monkeypatch):
#     def test_no_double_blank_lines(self, tmp_path, monkeypatch):
#         """Subdir-only indexes must not have two consecutive blank lines."""
#         docs = tmp_path / "docs"
#         docs.mkdir()
#         parent = docs / "area"
#         parent.mkdir()
#         sub = parent / "child"
#         sub.mkdir()
#         (sub / "guide.md").write_text("# Guide\n")
#         _patch_roots(monkeypatch, docs)
#         generate_index(parent)
#         content = (parent / "INDEX.md").read_text()
#         assert "\n\n\n" not in content, "INDEX.md must not have two consecutive blank lines"
# 
#     def test_no_contents_section_when_no_direct_files(self, tmp_path, monkeypatch):
#         docs = tmp_path / "docs"
#         docs.mkdir()
#         parent = docs / "area"
#         parent.mkdir()
#         sub = parent / "child"
#         sub.mkdir()
#         (sub / "guide.md").write_text("# Guide\n")
# 
#         _patch_roots(monkeypatch, docs)
#         generate_index(parent)
#         content = (parent / "INDEX.md").read_text()
#         assert ", "Condition must be true"
# 
#     def test_singular_noun_for_one_file(self, tmp_path, monkeypatch):
#         docs = tmp_path / "docs"
#         docs.mkdir()
#         parent = docs / "area"
#         parent.mkdir()
#         sub = parent / "child"
#         sub.mkdir()
#         (sub / "only.md").write_text("# Only\n")
# 
#         _patch_roots(monkeypatch, docs)
#         generate_index(parent)
#         content = (parent / "INDEX.md").read_text()
#         assert "— 1 file\n" in content, "Content must not be empty"
#         assert "— 1 files\n" not in content, "Content must not be empty"
# 
#     def test_plural_noun_for_multiple_files(self, tmp_path, monkeypatch):
#         docs = tmp_path / "docs"
#         docs.mkdir()
#         parent = docs / "area"
#         parent.mkdir()
#         sub = parent / "child"
#         sub.mkdir()
#         (sub / "a.md").write_text("# A\n")
#         (sub / "b.md").write_text("# B\n")
# 
#         _patch_roots(monkeypatch, docs)
#         generate_index(parent)
#         content = (parent / "INDEX.md").read_text()
#         assert "— 2 files\n" in content, "Content must not be empty"
#         content = (parent / "INDEX.md").read_text()
#         assert ", "Condition must be true"
#         assert "[guide](guide.md)" in content, "Content must not be empty"
#     """generate_index with direct .md files (the original behaviour)."""
# 
#     def test_contents_section_lists_direct_files(self, tmp_path, monkeypatch):
#         docs = tmp_path / "docs"
#         docs.mkdir()
#         parent = docs / "area"
#         parent.mkdir()
#         (parent / "guide.md").write_text("# Guide\n")
# 
#         _patch_roots(monkeypatch, docs)
#         generate_index(parent)
#         content = (parent / "INDEX.md").read_text()
#         assert ", "Condition must be true"
#         assert "[guide](guide.md)" in content, "Content must not be empty"
# 
#     def test_index_readme_excluded_from_contents(self, tmp_path, monkeypatch):
#         docs = tmp_path / "docs"
#         docs.mkdir()
#         parent = docs / "area"
#         parent.mkdir()
#         (parent / "guide.md").write_text("# Guide\n")
#         (parent / "README.md").write_text("# Readme\n")
# 
#         _patch_roots(monkeypatch, docs)
#         generate_index(parent)
#         content = (parent / "INDEX.md").read_text()
#         assert "[guide](guide.md)" in content, "Content must not be empty"
#         # INDEX.md and README.md must not appear as link targets in the Contents list
#         assert "- [INDEX](INDEX.md)" not in content, "Content must not be empty"
#         assert "- [README](README.md)" not in content, "Content must not be empty"
#         assert "- [index](index.md)" not in content, "Content must not be empty"
# 
#     def test_both_sections_when_direct_and_subdirs(self, tmp_path, monkeypatch):
#         docs = tmp_path / "docs"
#         docs.mkdir()
#         parent = docs / "area"
#         parent.mkdir()
#         (parent / "guide.md").write_text("# Guide\n")
#         sub = parent / "child"
#         sub.mkdir()
#         (sub / "note.md").write_text("# Note\n")
# 
#         _patch_roots(monkeypatch, docs)
#         generate_index(parent)
#         content = (parent / "INDEX.md").read_text()
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert "\n\n\n" not in content, "Content must not be empty"


class TestGenerateIndexEdgeCases:
    """Edge cases for generate_index."""

    def test_returns_false_for_empty_dir(self, tmp_path, monkeypatch):
        docs = tmp_path / "docs"
        docs.mkdir()
        empty = docs / "empty"
        empty.mkdir()

        _patch_roots(monkeypatch, docs)
        assert generate_index(empty) is False, "Condition must be true"

    def test_dry_run_does_not_create_file(self, tmp_path, monkeypatch):
        docs = tmp_path / "docs"
        docs.mkdir()
        parent = docs / "area"
        parent.mkdir()
        sub = parent / "child"
        sub.mkdir()
        (sub / "guide.md").write_text("# Guide\n")

        _patch_roots(monkeypatch, docs)
        result = generate_index(parent, dry_run=True)
        assert result is True, "Result must not be empty"
        assert not (parent / "INDEX.md").exists(), "Condition must be true"

    def test_hidden_subdirs_excluded(self, tmp_path, monkeypatch):
        docs = tmp_path / "docs"
        docs.mkdir()
        parent = docs / "area"
        parent.mkdir()
        hidden = parent / ".hidden"
        hidden.mkdir()
        (hidden / "secret.md").write_text("# Secret\n")

        _patch_roots(monkeypatch, docs)
        # Hidden subdir's .md should not count toward subdir list
        assert generate_index(parent) is False, "Condition must be true"
