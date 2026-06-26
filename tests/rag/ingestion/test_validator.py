"""
Tests for Document Validator Module.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from codex.rag.ingestion.validator import (
    DocumentFormat,
    DocumentValidator,
    ValidationConfig,
    ValidationResult,
    validate_document,
)


class TestDocumentFormat:
    """Tests for DocumentFormat enum."""

    def test_from_extension_text(self):
        """Test text file extension detection."""
        assert DocumentFormat.from_extension(".txt") == DocumentFormat.TEXT, "DocumentF is not valid"
        assert DocumentFormat.from_extension(".TXT") == DocumentFormat.TEXT, "DocumentF is not valid"

    def test_from_extension_markdown(self):
        """Test markdown file extension detection."""
        assert DocumentFormat.from_extension(".md") == DocumentFormat.MARKDOWN, "DocumentF is not valid"
        assert DocumentFormat.from_extension(".markdown") == DocumentFormat.MARKDOWN, "DocumentF is not valid"

    def test_from_extension_html(self):
        """Test HTML file extension detection."""
        assert DocumentFormat.from_extension(".html") == DocumentFormat.HTML, "DocumentF is not valid"
        assert DocumentFormat.from_extension(".htm") == DocumentFormat.HTML, "DocumentF is not valid"

    def test_from_extension_pdf(self):
        """Test PDF file extension detection."""
        assert DocumentFormat.from_extension(".pdf") == DocumentFormat.PDF, "DocumentF is not valid"

    def test_from_extension_json(self):
        """Test JSON file extension detection."""
        assert DocumentFormat.from_extension(".json") == DocumentFormat.JSON, "DocumentF is not valid"

    def test_from_extension_yaml(self):
        """Test YAML file extension detection."""
        assert DocumentFormat.from_extension(".yaml") == DocumentFormat.YAML, "DocumentF is not valid"
        assert DocumentFormat.from_extension(".yml") == DocumentFormat.YAML, "DocumentF is not valid"

    def test_from_extension_unknown(self):
        """Test unknown file extension."""
        assert DocumentFormat.from_extension(".xyz") == DocumentFormat.UNKNOWN, "DocumentF is not valid"
        assert DocumentFormat.from_extension("") == DocumentFormat.UNKNOWN, "DocumentF is not valid"

    def test_from_mime_type(self):
        """Test MIME type detection."""
        assert DocumentFormat.from_mime_type("text/plain") == DocumentFormat.TEXT, "DocumentF is not valid"
        assert DocumentFormat.from_mime_type("text/html") == DocumentFormat.HTML, "DocumentF is not valid"
        assert DocumentFormat.from_mime_type("application/json") == DocumentFormat.JSON, "DocumentF is not valid"
        assert DocumentFormat.from_mime_type("unknown/type") == DocumentFormat.UNKNOWN, "DocumentF is not valid"


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_add_error(self):
        """Test adding an error."""
        result = ValidationResult(is_valid=True, document_format=DocumentFormat.TEXT)
        assert result.is_valid, "Result must not be empty"

        result.add_error("Test error")
        assert not result.is_valid, "Result must not be empty"
        assert "Test error" in result.errors, "Result must not be empty"

    def test_add_warning(self):
        """Test adding a warning."""
        result = ValidationResult(is_valid=True, document_format=DocumentFormat.TEXT)

        result.add_warning("Test warning")
        assert result.is_valid, "Result must not be empty"
        assert "Test warning" in result.warnings, "Result must not be empty"


class TestDocumentValidator:
    """Tests for DocumentValidator class."""

    @pytest.fixture
    def validator(self):
        """Create a validator instance."""
        return DocumentValidator()

    @pytest.fixture
    def temp_text_file(self):
        """Create a temporary text file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("This is test content.\nSecond line.")
            temp_path = f.name
        yield Path(temp_path)
        os.unlink(temp_path)

    @pytest.fixture
    def temp_empty_file(self):
        """Create an empty temporary file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            pass  # Empty file
        yield Path(f.name)
        os.unlink(f.name)

    def test_validate_file_success(self, validator, temp_text_file):
        """Test successful file validation."""
        result = validator.validate_file(temp_text_file)

        assert result.is_valid, "Result must not be empty"
        assert result.document_format == DocumentFormat.TEXT, "Result must not be empty"
        assert result.file_size > 0, "file_size must be greater than zero"
        assert result.content_hash != "", "Result must not be empty"
        assert result.encoding == "utf-8", "Result must not be empty"

    def test_validate_file_not_found(self, validator):
        """Test validation of non-existent file."""
        result = validator.validate_file("/nonexistent/path/file.txt")

        assert not result.is_valid, "Result must not be empty"
        assert "not found" in result.errors[0].lower(), "Result must not be empty"

    def test_validate_file_empty(self, validator, temp_empty_file):
        """Test validation of empty file."""
        config = ValidationConfig(min_file_size_bytes=1)
        validator = DocumentValidator(config)
        result = validator.validate_file(temp_empty_file)

        assert not result.is_valid, "Result must not be empty"
        assert "too small" in result.errors[0].lower(), "Result must not be empty"

    def test_validate_text(self, validator):
        """Test text content validation."""
        result = validator.validate_text("Hello, this is a test document.")

        assert result.is_valid, "Result must not be empty"
        assert result.document_format == DocumentFormat.TEXT, "Result must not be empty"
        assert result.metadata.get("char_count") > 0, "Value must be greater than zero"
        assert result.metadata.get("word_count") > 0, "Value must be greater than zero"

    def test_validate_text_empty(self, validator):
        """Test validation of empty text."""
        result = validator.validate_text("")

        assert result.is_valid, "Result must not be empty"
        assert len(result.warnings) > 0, "Collection must not be empty"

    def test_validate_bytes(self, validator):
        """Test bytes content validation."""
        content = b"Test document content"
        result = validator.validate_bytes(content, filename="test.txt")

        assert result.is_valid, "Result must not be empty"
        assert result.file_size == len(content), "Content must not be empty"

    def test_validate_malicious_content(self, validator):
        """Test detection of potentially malicious content."""
        config = ValidationConfig(check_malicious=True)
        validator = DocumentValidator(config)

        result = validator.validate_text('<script>alert("xss")</script>')

        assert result.is_valid, "Result must not be empty"
        assert len(result.warnings) > 0, "Collection must not be empty"
        assert "malicious" in result.warnings[0].lower() or "script" in result.warnings[0].lower()

    def test_validate_text_too_long(self, validator):
        """Test validation of text exceeding max length."""
        config = ValidationConfig(max_text_length=100)
        validator = DocumentValidator(config)

        long_text = "x" * 200
        result = validator.validate_text(long_text)

        assert not result.is_valid, "Result must not be empty"
        assert "too long" in result.errors[0].lower(), "Result must not be empty"

    def test_file_size_limit(self):
        """Test file size limit validation."""
        config = ValidationConfig(max_file_size_mb=0.001)  # 1KB
        validator = DocumentValidator(config)

        # Create content larger than 1KB
        large_content = b"x" * 2000
        result = validator.validate_bytes(large_content)

        assert not result.is_valid, "Result must not be empty"
        assert "too large" in result.errors[0].lower(), "Result must not be empty"


class TestValidateDocumentFunction:
    """Tests for validate_document convenience function."""

    @pytest.fixture
    def temp_file(self):
        """Create a temporary file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Test content for validation")
            temp_path = f.name
        yield Path(temp_path)
        os.unlink(temp_path)

    def test_validate_file_path(self, temp_file):
        """Test validating a file path."""
        result = validate_document(temp_file)
        assert result.is_valid, "Result must not be empty"

    def test_validate_string_content(self):
        """Test validating string content."""
        result = validate_document("This is text content")
        assert result.is_valid, "Result must not be empty"

    def test_validate_bytes_content(self):
        """Test validating bytes content."""
        result = validate_document(b"Bytes content", filename="test.txt")
        assert result.is_valid, "Result must not be empty"


class TestValidationConfig:
    """Tests for ValidationConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = ValidationConfig()

        assert config.max_file_size_mb == 100.0, "max_file_size_mb is not valid"
        assert config.min_file_size_bytes == 1, "min_file_size_bytes is not valid"
        assert config.compute_hash is True, "compute_hash is not valid"
        assert config.check_malicious is True, "check_malicious is not valid"

    def test_custom_config(self):
        """Test custom configuration."""
        config = ValidationConfig(
            max_file_size_mb=50.0,
            check_malicious=False,
        )

        assert config.max_file_size_mb == 50.0, "max_file_size_mb is not valid"
        assert config.check_malicious is False, "check_malicious is not valid"


# ---------------------------------------------------------------------------
# Coverage-gap tests for file-validation edge cases and branch handling
# ---------------------------------------------------------------------------


class TestValidateFileDirectoryPath:
    """Lines 176-177: path exists but is a directory, not a file."""

    def test_validate_file_path_is_directory(self, tmp_path):
        validator = DocumentValidator()
        result = validator.validate_file(tmp_path)
        assert not result.is_valid, "Result must not be empty"
        assert any("not a file" in e.lower() for e in result.errors), "Result must not be empty"


class TestValidateFileMimeTypeDetection:
    """Lines 192-194: MIME type detection when extension gives UNKNOWN format."""

    def test_mime_type_used_for_unknown_extension(self, tmp_path):
        f = tmp_path / "data.xyz"
        f.write_text("text content here for mime type detection test")
        validator = DocumentValidator()
        with patch(
            "codex.rag.ingestion.validator.mimetypes.guess_type", return_value=("text/plain", None)
        ):
            result = validator.validate_file(f)
        assert result.document_format == DocumentFormat.TEXT, "Result must not be empty"

    def test_mime_type_none_for_unknown_extension(self, tmp_path):
        """Line 192-193: mime_type is None — format stays UNKNOWN."""
        f = tmp_path / "data.xyz"
        f.write_text("text content with no mime type")
        validator = DocumentValidator()
        with patch("codex.rag.ingestion.validator.mimetypes.guess_type", return_value=(None, None)):
            result = validator.validate_file(f)
        # UNKNOWN is not in default allowed_formats → validation fails
        assert not result.is_valid, "Result must not be empty"


class TestValidateFileFormatNotAllowed:
    """Lines 198-202: format not in allowed_formats."""

    def test_json_not_allowed_when_only_text_allowed(self, tmp_path):
        f = tmp_path / "data.json"
        f.write_text('{"key": "value"}')
        config = ValidationConfig(allowed_formats=[DocumentFormat.TEXT])
        validator = DocumentValidator(config)
        result = validator.validate_file(f)
        assert not result.is_valid, "Result must not be empty"
        assert any("not allowed" in e.lower() for e in result.errors), "Result must not be empty"


class TestValidateFileHashAndFormatBranches:
    """Lines 210->214, 214->223: compute_hash and text-format branches."""

    def test_compute_hash_false_skips_hash(self, tmp_path):
        """Lines 210->214: compute_hash=False leaves content_hash empty."""
        f = tmp_path / "nohash.txt"
        f.write_text("Content for hash skip test")
        config = ValidationConfig(compute_hash=False)
        validator = DocumentValidator(config)
        result = validator.validate_file(f)
        assert result.is_valid, "Result must not be empty"
        assert result.content_hash == "", "Result must not be empty"

    def test_non_text_format_skips_decoding(self, tmp_path):
        """Lines 214->223: non-text format (PDF) skips text decoding."""
        f = tmp_path / "doc.pdf"
        f.write_bytes(b"%PDF-1.4 binary content here for pdf test")
        validator = DocumentValidator()
        result = validator.validate_file(f)
        assert result.document_format == DocumentFormat.PDF, "Result must not be empty"
        assert result.is_valid, "Result must not be empty"

    def test_decode_failure_skips_text_validation(self, tmp_path):
        """Lines 216->223: _decode_content returns None → text validation skipped."""
        f = tmp_path / "fail.txt"
        f.write_bytes(b"some bytes content here")
        validator = DocumentValidator()
        with patch.object(
            validator,
            "_decode_content",
            side_effect=lambda c, r: r.add_error("Decode failed") or None,
        ):
            result = validator.validate_file(f)
        assert not result.is_valid, "Result must not be empty"
        assert any("decode" in e.lower() for e in result.errors), "Result must not be empty"


class TestValidateFileIOError:
    """Lines 219-220: IOError during binary file read."""

    def test_ioerror_on_open(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("Content")
        validator = DocumentValidator()
        original_open = open

        def patched_open(path, *args, **kwargs):
            mode = args[0] if args else kwargs.get("mode", "r")
            if mode == "rb":
                raise IOError("read error")
            return original_open(path, *args, **kwargs)

        with patch("builtins.open", side_effect=patched_open):
            result = validator.validate_file(f)
        assert not result.is_valid, "Result must not be empty"
        assert any("failed to read" in e.lower() for e in result.errors), "Result must not be empty"


class TestValidateBytesExtraBranches:
    """Covers missing branches in validate_bytes."""

    def test_no_filename_stays_unknown(self):
        """Lines 258->262: filename=None — format stays UNKNOWN."""
        content = b"Some bytes content here for no filename test"
        validator = DocumentValidator()
        result = validator.validate_bytes(content)
        assert result.document_format == DocumentFormat.UNKNOWN, "Result must not be empty"

    def test_mime_type_used_when_format_unknown(self):
        """Line 263: mime_type provided and format is still UNKNOWN."""
        content = b"text content for mime test"
        validator = DocumentValidator()
        result = validator.validate_bytes(content, mime_type="text/plain")
        assert result.document_format == DocumentFormat.TEXT, "Result must not be empty"

    def test_compute_hash_false(self):
        """Lines 266->270: compute_hash=False leaves content_hash empty in validate_bytes."""
        content = b"Content for bytes no-hash test"
        config = ValidationConfig(compute_hash=False)
        validator = DocumentValidator(config)
        result = validator.validate_bytes(content, filename="test.txt")
        assert result.is_valid, "Result must not be empty"
        assert result.content_hash == "", "Result must not be empty"

    def test_non_text_format_skips_decoding(self):
        """Lines 270->276: non-text format skips text decoding in validate_bytes."""
        content = b"%PDF binary content here"
        validator = DocumentValidator()
        result = validator.validate_bytes(content, filename="doc.pdf")
        assert result.document_format == DocumentFormat.PDF, "Result must not be empty"
        assert result.is_valid, "Result must not be empty"

    def test_empty_content_falsy_text_skips_text_validation(self):
        """Lines 272->276: empty bytes decode to '' → if condition False."""
        config = ValidationConfig(min_file_size_bytes=0)
        validator = DocumentValidator(config)
        result = validator.validate_bytes(b"", filename="empty.txt")
        # is_valid stays True but text_content is "" (falsy) so _validate_text_content skipped
        assert result.is_valid, "Result must not be empty"

    def test_no_filename_metadata_not_stored(self):
        """Lines 276->279: no filename → metadata 'filename' key not added."""
        content = b"bytes content for metadata test"
        validator = DocumentValidator()
        result = validator.validate_bytes(content)
        assert "filename" not in result.metadata, "Result must not be empty"


class TestValidateTextComputeHashFalse:
    """Lines 300->304: compute_hash=False in validate_text."""

    def test_no_hash_in_validate_text(self):
        config = ValidationConfig(compute_hash=False)
        validator = DocumentValidator(config)
        result = validator.validate_text("Some text content here for hash test")
        assert result.is_valid, "Result must not be empty"
        assert result.content_hash == "", "Result must not be empty"


class TestDecodeContentAllFail:
    """Lines 348-352: all encodings fail → add_error and return None."""

    def test_all_encodings_fail(self):
        validator = DocumentValidator()
        result = ValidationResult(is_valid=True, document_format=DocumentFormat.TEXT)
        mock_content = MagicMock(spec=bytes)
        mock_content.decode.side_effect = UnicodeDecodeError("ascii", b"", 0, 1, "always fails")
        text = validator._decode_content(mock_content, result)
        assert text is None, "text is not valid"
        assert not result.is_valid, "Result must not be empty"
        assert any("encoding" in e.lower() or "decode" in e.lower() for e in result.errors), "Result must not be empty"


class TestValidateTextContentNoMaliciousCheck:
    """Lines 368->374: check_malicious=False skips malicious-pattern scan."""

    def test_script_tag_no_warning_when_check_disabled(self):
        config = ValidationConfig(check_malicious=False)
        validator = DocumentValidator(config)
        result = validator.validate_text('<script>alert("xss")</script>')
        assert result.is_valid, "Result must not be empty"
        assert len(result.warnings) == 0, "Collection must not be empty"


class TestValidateDocumentUnsupportedType:
    """Lines 404-406: unsupported source type falls through to else branch."""

    def test_integer_source_is_invalid(self):
        result = validate_document(12345)  # type: ignore[arg-type]
        assert not result.is_valid, "Result must not be empty"
        assert any("unsupported" in e.lower() for e in result.errors), "Result must not be empty"
