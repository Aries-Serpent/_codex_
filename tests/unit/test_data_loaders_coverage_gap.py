"""Gap-fill tests for data/loaders.py module - comprehensive coverage for data loading helpers.

This test suite covers:
- Safe line loading from files
- Input validation and sanitization
- Record validation for JSON-like dictionaries
- Error handling for missing files
- Edge cases for special characters and encoding
"""

from __future__ import annotations

import pytest

from data.loaders import safe_line_loader, validate_records


class TestSafeLineLoader:
    """Test safe_line_loader function."""

    def test_safe_line_loader_read_file(self, tmp_path):
        """Test reading lines from a file."""
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("line1\nline2\nline3\n", encoding="utf-8")

        # Load lines
        lines = list(safe_line_loader(test_file))

        assert len(lines) == 3
        assert lines[0] == "line1"
        assert lines[1] == "line2"
        assert lines[2] == "line3"

    def test_safe_line_loader_with_string_path(self, tmp_path):
        """Test reading lines with string path."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("line1\nline2\n", encoding="utf-8")

        lines = list(safe_line_loader(str(test_file)))

        assert len(lines) == 2

    def test_safe_line_loader_with_pathlib_path(self, tmp_path):
        """Test reading lines with pathlib.Path."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("line1\nline2\n", encoding="utf-8")

        lines = list(safe_line_loader(test_file))

        assert len(lines) == 2

    def test_safe_line_loader_empty_file(self, tmp_path):
        """Test reading empty file."""
        test_file = tmp_path / "empty.txt"
        test_file.write_text("", encoding="utf-8")

        lines = list(safe_line_loader(test_file))

        assert len(lines) == 0

    def test_safe_line_loader_file_not_found(self, tmp_path):
        """Test error when file does not exist."""
        test_file = tmp_path / "nonexistent.txt"

        with pytest.raises(FileNotFoundError):
            list(safe_line_loader(test_file))

    def test_safe_line_loader_with_special_characters(self, tmp_path):
        """Test reading lines with special characters."""
        test_file = tmp_path / "special.txt"
        test_file.write_text("line1: @#$%\nline2: <html>\n", encoding="utf-8")

        lines = list(safe_line_loader(test_file))

        assert len(lines) == 2
        assert "@#$%" in lines[0]
        assert "<html>" in lines[1]

    def test_safe_line_loader_with_unicode(self, tmp_path):
        """Test reading lines with unicode characters."""
        test_file = tmp_path / "unicode.txt"
        test_file.write_text("café\n日本語\némoji😀\n", encoding="utf-8")

        lines = list(safe_line_loader(test_file))

        assert len(lines) == 3
        assert "café" in lines[0]
        assert "日本語" in lines[1]
        assert "😀" in lines[2]

    def test_safe_line_loader_iterator(self, tmp_path):
        """Test that safe_line_loader returns an iterator."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("line1\nline2\nline3\n", encoding="utf-8")

        loader = safe_line_loader(test_file)

        # Test iterator protocol
        line1 = next(loader)
        assert line1 == "line1"

        line2 = next(loader)
        assert line2 == "line2"

        line3 = next(loader)
        assert line3 == "line3"

        with pytest.raises(StopIteration):
            next(loader)

    def test_safe_line_loader_with_newlines_in_content(self, tmp_path):
        """Test reading file where lines have trailing newlines."""
        test_file = tmp_path / "test.txt"
        # Write with explicit newlines
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("line1\n")
            f.write("line2\n")
            f.write("line3")  # Last line without newline

        lines = list(safe_line_loader(test_file))

        assert len(lines) == 3
        # Lines might contain newlines depending on validation function
        assert "line1" in lines[0]
        assert "line2" in lines[1]
        assert "line3" in lines[2]

    def test_safe_line_loader_with_long_lines(self, tmp_path):
        """Test reading file with very long lines."""
        test_file = tmp_path / "long.txt"
        long_line = "x" * 10000
        test_file.write_text(f"{long_line}\n", encoding="utf-8")

        lines = list(safe_line_loader(test_file))

        assert len(lines) == 1
        assert len(lines[0]) >= 10000


class TestValidateRecords:
    """Test validate_records function."""

    def test_validate_records_basic(self):
        """Test basic record validation."""
        records = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
        ]

        validated = validate_records(records)

        assert len(validated) == 2
        assert validated[0]["name"] == "Alice"
        assert validated[0]["age"] == 30

    def test_validate_records_empty_list(self):
        """Test validating empty list."""
        records = []

        validated = validate_records(records)

        assert len(validated) == 0

    def test_validate_records_with_special_characters(self):
        """Test validating records with special characters."""
        records = [
            {"key": "value@#$%"},
            {"key": "<html>content</html>"},
        ]

        validated = validate_records(records)

        assert len(validated) == 2

    def test_validate_records_with_numeric_values(self):
        """Test validating records with numeric values."""
        records = [
            {"id": 123, "score": 45.67},
            {"id": 456, "score": 89.10},
        ]

        validated = validate_records(records)

        assert len(validated) == 2
        assert validated[0]["id"] == 123
        assert validated[0]["score"] == 45.67

    def test_validate_records_with_boolean_values(self):
        """Test validating records with boolean values."""
        records = [
            {"active": True, "verified": False},
            {"active": False, "verified": True},
        ]

        validated = validate_records(records)

        assert len(validated) == 2
        assert validated[0]["active"] is True
        assert validated[0]["verified"] is False

    def test_validate_records_with_null_values(self):
        """Test validating records with null/None values."""
        records = [
            {"name": "Alice", "middle_name": None},
            {"name": "Bob", "middle_name": "Ray"},
        ]

        validated = validate_records(records)

        assert len(validated) == 2

    def test_validate_records_with_nested_dicts(self):
        """Test validating records with nested dictionaries."""
        records = [
            {"user": {"name": "Alice", "age": 30}},
            {"user": {"name": "Bob", "age": 25}},
        ]

        validated = validate_records(records)

        assert len(validated) == 2

    def test_validate_records_with_lists(self):
        """Test validating records with list values."""
        records = [
            {"tags": ["tag1", "tag2"]},
            {"tags": ["tag3", "tag4"]},
        ]

        validated = validate_records(records)

        assert len(validated) == 2

    def test_validate_records_with_unicode_keys(self):
        """Test validating records with unicode keys."""
        records = [
            {"名前": "太郎", "年齢": 30},
            {"名前": "花子", "年齢": 25},
        ]

        validated = validate_records(records)

        assert len(validated) == 2

    def test_validate_records_large_dataset(self):
        """Test validating large dataset."""
        records = [{"id": i, "value": i * 10} for i in range(1000)]

        validated = validate_records(records)

        assert len(validated) == 1000
        assert validated[0]["id"] == 0
        assert validated[999]["id"] == 999

    def test_validate_records_with_mixed_types(self):
        """Test validating records with mixed data types."""
        records = [
            {
                "string": "text",
                "number": 42,
                "float": 3.14,
                "bool": True,
                "none": None,
                "list": [1, 2, 3],
                "dict": {"nested": "value"},
            }
        ]

        validated = validate_records(records)

        assert len(validated) == 1
        record = validated[0]
        assert isinstance(record["string"], str)
        assert isinstance(record["number"], int)
        assert isinstance(record["float"], float)
        assert isinstance(record["bool"], bool)
