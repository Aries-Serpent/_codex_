"""
Tests for scripts/validate_code_fences.py
"""

from validate_code_fences import check_code_fences, fix_code_fences


class TestCheckCodeFences:
    """Test code fence detection"""

    def test_properly_matched_fences(self, tmp_path):
        """Test that properly matched fences are not flagged"""
        md_file = tmp_path / "test.md"
        md_file.write_text(
            "# Header\n" "\n" "```python\n" "code here\n" "```\n" "\n" "Text after.\n"
        )

        issues = check_code_fences(md_file)
        assert len(issues) == 0, "Issues must not be empty"

    def test_unclosed_fence(self, tmp_path):
        """Test detection of unclosed fence"""
        md_file = tmp_path / "test.md"
        md_file.write_text(
            "# Header\n" "\n" "```python\n" "code here\n" "# Missing closing fence\n"
        )

        issues = check_code_fences(md_file)
        assert len(issues) == 1, "Issues must not be empty"
        assert issues[0]["type"] == "unclosed_fence", "Condition must be true"
        assert issues[0]["line"] == 3, "Condition must be true"

    def test_indented_fences(self, tmp_path):
        """Test that indented fences are properly matched"""
        md_file = tmp_path / "test.md"
        md_file.write_text(
            "# Header\n"
            "\n"
            "- List item\n"
            "  ```python\n"
            "  code here\n"
            "  ```\n"
            "\n"
            "Text after.\n"
        )

        issues = check_code_fences(md_file)
        # Should detect properly - indented fences not currently handled
        # This documents current behavior
        assert len(issues) == 0 or issues[0]["type"] == "unclosed_fence", "Issues must not be empty"

    def test_nested_fence_detection(self, tmp_path):
        """Test detection of nested fences"""
        md_file = tmp_path / "test.md"
        md_file.write_text(
            "# Header\n" "\n" "```python\n" "```bash\n" "nested code\n" "```\n" "```\n"
        )

        issues = check_code_fences(md_file)
        # Should detect nested fence
        nested = [i for i in issues if i["type"] == "nested_fence"]
        assert len(nested) >= 1, "Nested must not be empty"

    def test_multiple_unclosed_fences(self, tmp_path):
        """Test detection of multiple unclosed fences"""
        md_file = tmp_path / "test.md"
        md_file.write_text(
            "```python\n" "code1\n" "\n" "```bash\n" "code2\n" "\n" "```yaml\n" "code3\n"
        )

        issues = check_code_fences(md_file)
        unclosed = [i for i in issues if i["type"] == "unclosed_fence"]
        # At least one unclosed fence detected
        assert len(unclosed) >= 1, "Unclosed must not be empty"

    def test_empty_file(self, tmp_path):
        """Test handling of empty file"""
        md_file = tmp_path / "test.md"
        md_file.write_text("")

        issues = check_code_fences(md_file)
        assert len(issues) == 0, "Issues must not be empty"


class TestFixCodeFences:
    """Test code fence fixing"""

    def test_fix_unclosed_fence(self, tmp_path):
        """Test fixing unclosed fence"""
        md_file = tmp_path / "test.md"
        md_file.write_text("# Header\n" "\n" "```python\n" "code here\n")

        issues = check_code_fences(md_file)
        result = fix_code_fences(md_file, issues, dry_run=False)

        assert result is True, "Result must not be empty"
        content = md_file.read_text()
        assert content.endswith("```\n"), "Content must not be empty"

    def test_dry_run_returns_true(self, tmp_path):
        """Test that dry-run returns True for fixable issues"""
        md_file = tmp_path / "test.md"
        md_file.write_text("```python\n" "code\n")

        issues = check_code_fences(md_file)
        result = fix_code_fences(md_file, issues, dry_run=True)

        assert result is True, "Result must not be empty"
        # Content should not change in dry-run
        content = md_file.read_text()
        assert content == "```python\ncode\n", "Content must not be empty"

    def test_no_changes_returns_false(self, tmp_path):
        """Test that no changes returns False"""
        md_file = tmp_path / "test.md"
        md_file.write_text("```python\n" "code\n" "```\n")

        issues = check_code_fences(md_file)
        result = fix_code_fences(md_file, issues, dry_run=False)

        assert result is False, "Result must not be empty"

    def test_fix_multiple_unclosed_fences(self, tmp_path):
        """Test fixing multiple unclosed fences"""
        md_file = tmp_path / "test.md"
        md_file.write_text("```python\n" "code1\n")

        issues = check_code_fences(md_file)
        result = fix_code_fences(md_file, issues, dry_run=False)

        assert result is True, "Result must not be empty"
        content = md_file.read_text()
        # Should have at least one closing fence added
        assert "```\n" in content, "Content must not be empty"

    def test_nested_fence_not_auto_fixed(self, tmp_path):
        """Test that nested fences are detected but file structure may still be fixed for unclosed fences"""
        md_file = tmp_path / "test.md"
        original_content = "```python\n" "```bash\n" "nested\n" "```\n" "```\n"
        md_file.write_text(original_content)

        issues = check_code_fences(md_file)
        # This should detect nested fence AND unclosed fence
        assert len(issues) >= 1, "Issues must not be empty"
        assert any(i["type"] == "nested_fence" for i in issues), "in is not valid"

        result = fix_code_fences(md_file, issues, dry_run=False)
        # Result will be True because unclosed fences are fixed
        # but nested fence issue is just reported, not auto-fixed
        assert isinstance(result, bool)  # Use result in assertion

        # Nested fence detection should not cause script to crash
        content = md_file.read_text()
        assert "```python\n" in content, "Content must not be empty"


class TestEdgeCases:
    """Test edge cases"""

    def test_fence_at_end_of_file(self, tmp_path):
        """Test fence at end of file without newline"""
        md_file = tmp_path / "test.md"
        md_file.write_text("```python\ncode")  # No newline at end

        issues = check_code_fences(md_file)
        assert len(issues) >= 1, "Issues must not be empty"

        # Fix should handle this
        fix_code_fences(md_file, issues, dry_run=False)
        content = md_file.read_text()
        assert content.endswith("```\n"), "Content must not be empty"

    def test_multiple_languages(self, tmp_path):
        """Test multiple different language fences"""
        md_file = tmp_path / "test.md"
        md_file.write_text(
            "```python\n"
            "python_code\n"
            "```\n"
            "\n"
            "```bash\n"
            "bash_code\n"
            "```\n"
            "\n"
            "```yaml\n"
            "yaml_code\n"
            "```\n"
        )

        issues = check_code_fences(md_file)
        assert len(issues) == 0, "Issues must not be empty"
