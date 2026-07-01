#         assert fixed_content == (, "Content must not be empty"
# """Tests for scripts/validate_table_spacing.py"""
#         assert fixed_content == (, "Content must not be empty"
# import pytest
#         assert fixed_content == (, "Content must not be empty"
# 
#         assert fixed_content == (, "Content must not be empty"
# class TestCheckTableSpacing:
#     """Tests for check_table_spacing function"""
#     def test_detects_missing_blank_line(self, tmp_path):
#     def test_detects_missing_blank_line(self, tmp_path):
#         """Test detection of table without blank line"""
#         test_file = tmp_path / "test.md"
#         test_file.write_text(
#             "# Header\n"
#             "Some text\n"
#             "| Column 1 | Column 2 |\n"
#             "|----------|----------|\n"
#             "| Data 1   | Data 2   |\n"
#         )
#         issues = check_table_spacing(test_file)
#         assert len(issues) == 1, "Issues must not be empty"
#         assert issues[0]["line"] == 2, "Condition must be true"
#         assert "Some text" in issues[0]["text"], "in is not valid"
# 
#     def test_no_issues_with_blank_line(self, tmp_path):
#     def test_no_issues_with_blank_line(self, tmp_path):
#         """Test that properly spaced table passes"""
#         test_file = tmp_path / "test.md"
#         test_file.write_text(
#             "# Header\n"
#             "Some text\n"
#             "\n"
#             "| Column 1 | Column 2 |\n"
#             "|----------|----------|\n"
#             "| Data 1   | Data 2   |\n"
#         )
#         issues = check_table_spacing(test_file)
#         assert len(issues) == 0, "Issues must not be empty"
# 
#     def test_skips_code_blocks(self, tmp_path):
#     def test_skips_code_blocks(self, tmp_path):
#         """Test that tables inside code blocks are ignored"""
#         test_file = tmp_path / "test.md"
#         test_file.write_text(
#             "Example code:\n"
#             "```python\n"
#             "# This is code\n"
#             "| Column 1 | Column 2 |\n"
#             "|----------|----------|\n"
#             "```\n"
#             "\n"
#             "Real table:\n"
#             "\n"
#             "| Column 1 | Column 2 |\n"
#         )
#         issues = check_table_spacing(test_file)
#         assert len(issues) == 0, "Issues must not be empty"
# 
#     def test_skips_indented_code_blocks(self, tmp_path):
#     def test_skips_indented_code_blocks(self, tmp_path):
#         """Test that tables inside indented code blocks are ignored"""
#         test_file = tmp_path / "test.md"
#         test_file.write_text(
#             "In a list:\n"
#             "- Item 1\n"
#             "    ```python\n"
#             "    # Indented code\n"
#             "    | Table | In | Code |\n"
#             "    ```\n"
#             "\n"
#             "Real table:\n"
#             "\n"
#             "| Column 1 | Column 2 |\n"
#         )
#         issues = check_table_spacing(test_file)
#         assert len(issues) == 0, "Issues must not be empty"
# 
#     def test_detects_multiple_issues(self, tmp_path):
#     def test_detects_multiple_issues(self, tmp_path):
#         """Test detection of multiple table spacing issues"""
#         test_file = tmp_path / "test.md"
#         test_file.write_text("First section\n| Table 1 |\n\nSecond section\n| Table 2 |\n")
#         issues = check_table_spacing(test_file)
#         assert len(issues) == 2, "Issues must not be empty"
#         assert issues[0]["line"] == 1, "Condition must be true"
#         assert issues[1]["line"] == 4, "Condition must be true"
# 
#     def test_handles_empty_file(self, tmp_path):
#     def test_handles_empty_file(self, tmp_path):
#         """Test handling of empty file"""
#         test_file = tmp_path / "test.md"
#         test_file.write_text("")
#         issues = check_table_spacing(test_file)
#         assert len(issues) == 0, "Issues must not be empty"
# 
#     def test_handles_table_after_table(self, tmp_path):
#     def test_handles_table_after_table(self, tmp_path):
#         """Test that consecutive table rows are not flagged"""
#         test_file = tmp_path / "test.md"
#         test_file.write_text(
#             "| Column 1 | Column 2 |\n"
#             "|----------|----------|\n"
#             "| Data 1   | Data 2   |\n"
#             "| Data 3   | Data 4   |\n"
#         )
#         issues = check_table_spacing(test_file)
#         assert len(issues) == 0, "Issues must not be empty"
#         fixed_content = test_file.read_text()
#         assert fixed_content == (, "Content must not be empty"
# 
#         assert fixed_content == (, "Content must not be empty"
#     """Tests for fix_table_spacing function"""
#     def test_fixes_missing_blank_line(self, tmp_path):
#     def test_fixes_missing_blank_line(self, tmp_path):
#         """Test fixing of missing blank line"""
#         test_file = tmp_path / "test.md"
#         content = "Section header\n| Column 1 | Column 2 |\n| Data     | Data     |\n"
#         test_file.write_text(content)
#         issues = check_table_spacing(test_file)
#         result = fix_table_spacing(test_file, issues, dry_run=False)
# 
#         assert result is True, "Result must not be empty"
#         fixed_content = test_file.read_text()
#         assert fixed_content == (, "Content must not be empty"
#         assert fixed_content == (, "Content must not be empty"
#             "Section header\n\n| Column 1 | Column 2 |\n| Data     | Data     |\n"
#         )
#     def test_dry_run_returns_true(self, tmp_path):
#     def test_dry_run_returns_true(self, tmp_path):
#         """Test that dry_run mode returns True for counting"""
#         test_file = tmp_path / "test.md"
#         test_file.write_text("Text\n| Table |\n")
#         issues = check_table_spacing(test_file)
#         result = fix_table_spacing(test_file, issues, dry_run=True)
# 
#         assert result is True, "Result must not be empty"
#         # Verify file wasn't modified
#         assert test_file.read_text() == "Text\n| Table |\n", "Condition must be true"
# 
#     def test_fixes_multiple_issues(self, tmp_path):
#     def test_fixes_multiple_issues(self, tmp_path):
#         """Test fixing multiple issues in one file"""
#         test_file = tmp_path / "test.md"
#         test_file.write_text("First\n| Table 1 |\n\nSecond\n| Table 2 |\n")
#         issues = check_table_spacing(test_file)
#         result = fix_table_spacing(test_file, issues, dry_run=False)
# 
#         assert result is True, "Result must not be empty"
#         fixed_content = test_file.read_text()
#         lines = fixed_content.split("\n")
#         # Blank lines should be inserted at correct positions
#         assert lines[1] == "", "Condition must be true"
#         assert lines[5] == "", "Condition must be true"
# 
#     def test_handles_no_issues(self, tmp_path):
#     def test_handles_no_issues(self, tmp_path):
#         """Test handling when no issues to fix"""
#         test_file = tmp_path / "test.md"
#         test_file.write_text("Text\n\n| Table |\n")
#         issues = check_table_spacing(test_file)
#         assert len(issues) == 0, "Issues must not be empty"
#         # Should not call fix_table_spacing with empty issues


class TestCodeBlockHandling:
    """Tests for code block detection"""

    def test_nested_code_blocks(self, tmp_path):
        """Test handling of nested code blocks (markdown in code)"""
        test_file = tmp_path / "test.md"
        test_file.write_text("Example:\n```markdown\nText before table\n| Column |\n```\n")

        issues = check_table_spacing(test_file)
        assert len(issues) == 0, "Issues must not be empty"

    def test_code_block_toggle(self, tmp_path):
        """Test that code block state toggles correctly"""
        test_file = tmp_path / "test.md"
        test_file.write_text(
            "Before code\n"
            "```\n"
            "Inside code\n"
            "| Table in code |\n"
            "```\n"
            "After code\n"
            "| Real table |\n"
        )

        issues = check_table_spacing(test_file)
        # Should detect issue after code block
        assert len(issues) == 1, "Issues must not be empty"
        assert issues[0]["line"] == 6, "Condition must be true"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
