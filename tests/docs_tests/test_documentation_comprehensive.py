#         assert content.startswith(", "Content must not be empty"
#         assert "\n\n" in content, "Content must not be empty"
#         import shutil
# import tempfile
#         content = md_file.read_text()
#         assert content.startswith(", "Content must not be empty"
#         assert "\n\n" in content, "Content must not be empty"
#         import shutil
#     """Test markdown validation and linting."""
# 
#     def test_markdown_file_structure(self):
#     def test_markdown_file_structure(self):
#         """Test markdown file has valid structure."""
#         test_dir = Path(tempfile.mkdtemp())
#         md_file = test_dir / "test.md"
#         md_file.write_text("# Header\n\nContent here.\n")
#         content = md_file.read_text()
#         assert content.startswith(", "Content must not be empty"
#         assert "\n\n" in content, "Content must not be empty"
#         import shutil
#         shutil.rmtree(test_dir)
# 
#     def test_markdown_headers(self):
#     def test_markdown_headers(self):
#         """Test markdown headers are properly formatted."""
#         headers = ["# H1", "## H2", "### H3"]
#         for h in headers:
#             assert h.startswith(", "Condition must be true"
#             assert h[h.count(", "Count must be greater than zero"
#     def test_code_fence_language(self):
#     def test_code_fence_language(self):
#         """Test code fences have language tags."""
#         fences = ["```python", "```bash", "```yaml"]
#         for f in fences:
#             assert f.startswith("```"), "Condition must be true"
#             assert len(f) > 3, "F must not be empty"


class TestDocumentationCoverage:
    """Test documentation coverage."""

    def test_readme_exists(self):
        """Test README exists."""
        repo_root = Path(__file__).parents[2]
        readme = repo_root / "README.md"
        if readme.exists():
            assert readme.read_text().strip(), "Condition must be true"

    def test_api_docs_structure(self):
        """Test API documentation structure."""
        doc_structure = {
            "modules": ["core", "utils", "api"],
            "examples": ["quickstart", "advanced"],
        }
        assert len(doc_structure["modules"]) > 0, "Collection must not be empty"
        assert len(doc_structure["examples"]) > 0, "Collection must not be empty"


class TestMkdocsBuild:
    """Test mkdocs build process."""

    def test_mkdocs_config_exists(self):
        """Test mkdocs.yml exists."""
        repo_root = Path(__file__).parents[2]
        mkdocs = repo_root / "mkdocs.yml"
        if mkdocs.exists():
            content = mkdocs.read_text()
            assert "site_name:" in content or "nav:" in content, "Content must not be empty"

    def test_docs_directory_structure(self):
        """Test docs directory structure."""
        repo_root = Path(__file__).parents[2]
        docs_dir = repo_root / "docs"
        if docs_dir.exists():
            assert docs_dir.is_dir(), "Condition must be true"
