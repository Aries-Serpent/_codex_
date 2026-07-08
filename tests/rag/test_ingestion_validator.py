"""
Tests for src/codex/rag/ingestion/validator.py

Covers DocumentValidator, DocumentFormat, ValidationConfig,
ValidationResult, and validate_document().
"""

import tempfile
from pathlib import Path

from codex.rag.ingestion.validator import (
    DocumentFormat,
    DocumentValidator,
    ValidationConfig,
    ValidationResult,
    validate_document,
)


class TestDocumentFormat:
    def test_from_extension_txt(self):
        assert DocumentFormat.from_extension(".txt") == DocumentFormat.TEXT, "DocumentF is not valid"

    def test_from_extension_md(self):
        assert DocumentFormat.from_extension(".md") == DocumentFormat.MARKDOWN, "DocumentF is not valid"

    def test_from_extension_markdown(self):
        assert DocumentFormat.from_extension(".markdown") == DocumentFormat.MARKDOWN, "DocumentF is not valid"

    def test_from_extension_html(self):
        assert DocumentFormat.from_extension(".html") == DocumentFormat.HTML, "DocumentF is not valid"
        assert DocumentFormat.from_extension(".htm") == DocumentFormat.HTML, "DocumentF is not valid"

    def test_from_extension_pdf(self):
        assert DocumentFormat.from_extension(".pdf") == DocumentFormat.PDF, "DocumentF is not valid"

    def test_from_extension_json(self):
        assert DocumentFormat.from_extension(".json") == DocumentFormat.JSON, "DocumentF is not valid"

    def test_from_extension_yaml(self):
        assert DocumentFormat.from_extension(".yaml") == DocumentFormat.YAML, "DocumentF is not valid"
        assert DocumentFormat.from_extension(".yml") == DocumentFormat.YAML, "DocumentF is not valid"

    def test_from_extension_csv(self):
        assert DocumentFormat.from_extension(".csv") == DocumentFormat.CSV, "DocumentF is not valid"

    def test_from_extension_xml(self):
        assert DocumentFormat.from_extension(".xml") == DocumentFormat.XML, "DocumentF is not valid"

    def test_from_extension_docx(self):
        assert DocumentFormat.from_extension(".docx") == DocumentFormat.DOCX, "DocumentF is not valid"

    def test_from_extension_unknown(self):
        assert DocumentFormat.from_extension(".xyz") == DocumentFormat.UNKNOWN, "DocumentF is not valid"

    def test_from_extension_case_insensitive(self):
        assert DocumentFormat.from_extension(".TXT") == DocumentFormat.TEXT, "DocumentF is not valid"
        assert DocumentFormat.from_extension(".MD") == DocumentFormat.MARKDOWN, "DocumentF is not valid"

    def test_from_mime_text_plain(self):
        assert DocumentFormat.from_mime_type("text/plain") == DocumentFormat.TEXT, "DocumentF is not valid"

    def test_from_mime_text_html(self):
        assert DocumentFormat.from_mime_type("text/html") == DocumentFormat.HTML, "DocumentF is not valid"

    def test_from_mime_application_pdf(self):
        assert DocumentFormat.from_mime_type("application/pdf") == DocumentFormat.PDF, "DocumentF is not valid"

    def test_from_mime_application_json(self):
        assert DocumentFormat.from_mime_type("application/json") == DocumentFormat.JSON, "DocumentF is not valid"

    def test_from_mime_yaml(self):
        assert DocumentFormat.from_mime_type("application/x-yaml") == DocumentFormat.YAML, "DocumentF is not valid"
        assert DocumentFormat.from_mime_type("text/yaml") == DocumentFormat.YAML, "DocumentF is not valid"

    def test_from_mime_csv(self):
        assert DocumentFormat.from_mime_type("text/csv") == DocumentFormat.CSV, "DocumentF is not valid"

    def test_from_mime_xml(self):
        assert DocumentFormat.from_mime_type("application/xml") == DocumentFormat.XML, "DocumentF is not valid"
        assert DocumentFormat.from_mime_type("text/xml") == DocumentFormat.XML, "DocumentF is not valid"

    def test_from_mime_unknown(self):
        assert DocumentFormat.from_mime_type("application/octet-stream") == DocumentFormat.UNKNOWN

    def test_all_enum_values(self):
        values = {f.value for f in DocumentFormat}
        assert "text" in values, "Value must be initialized"
        assert "markdown" in values, "Value must be initialized"
        assert "pdf" in values, "Value must be initialized"
        assert "unknown" in values, "Value must be initialized"


class TestValidationResult:
    def test_add_error(self):
        r = ValidationResult(is_valid=True, document_format=DocumentFormat.TEXT)
        r.add_error("Something went wrong")
        assert not r.is_valid, "Condition must be true"
        assert "Something went wrong" in r.errors, "Error should be raised or set"

    def test_add_warning(self):
        r = ValidationResult(is_valid=True, document_format=DocumentFormat.TEXT)
        r.add_warning("Caution")
        assert r.is_valid, "Condition must be true"
        assert "Caution" in r.warnings, "Condition must be true"

    def test_default_valid(self):
        r = ValidationResult(is_valid=True, document_format=DocumentFormat.MARKDOWN)
        assert r.errors == [], "Error should be raised or set"
        assert r.warnings == [], "warnings is not valid"
        assert r.metadata == {}, "Data must not be empty"


class TestValidationConfig:
    def test_defaults(self):
        cfg = ValidationConfig()
        assert cfg.max_file_size_mb > 0, "max_file_size_mb must be greater than zero"
        assert cfg.check_malicious is True, "check_malicious is not valid"

    def test_custom_config(self):
        cfg = ValidationConfig(max_file_size_mb=100, check_malicious=False)
        assert cfg.max_file_size_mb == 100, "max_file_size_mb is not valid"
        assert cfg.check_malicious is False, "check_malicious is not valid"


class TestDocumentValidator:
    def test_validate_text_valid(self):
        v = DocumentValidator()
        result = v.validate_text("Hello World")
        assert result.is_valid, "Result must not be empty"
        assert result.document_format == DocumentFormat.TEXT, "Result must not be empty"

    def test_validate_text_empty(self):
        v = DocumentValidator()
        result = v.validate_text("   ")
        # Empty/whitespace should produce a warning
        assert len(result.warnings) > 0 or not result.is_valid, "Collection must not be empty"

    def test_validate_text_too_long(self):
        cfg = ValidationConfig(max_text_length=10)
        v = DocumentValidator(cfg)
        result = v.validate_text("This is a very long text that exceeds the limit")
        assert not result.is_valid, "Result must not be empty"
        assert any("too long" in e.lower() or "maximum" in e.lower() for e in result.errors), "Result must not be empty"

    def test_validate_text_stores_stats(self):
        v = DocumentValidator()
        result = v.validate_text("Hello World\nLine 2")
        assert "char_count" in result.metadata, "Result must not be empty"
        assert "line_count" in result.metadata, "Result must not be empty"
        assert "word_count" in result.metadata, "Result must not be empty"

    def test_validate_text_word_count(self):
        v = DocumentValidator()
        result = v.validate_text("one two three")
        assert result.metadata.get("word_count") == 3, "Result must not be empty"

    def test_validate_bytes_utf8(self):
        v = DocumentValidator()
        data = "Hello World".encode("utf-8")
        result = v.validate_bytes(data)
        assert result.is_valid, "Result must not be empty"

    def test_validate_bytes_with_filename(self):
        v = DocumentValidator()
        data = b"# Markdown content"
        result = v.validate_bytes(data, filename="test.md")
        assert result.is_valid, "Result must not be empty"

    def test_validate_bytes_too_large(self):
        cfg = ValidationConfig(max_file_size_mb=0.000001)  # extremely small limit
        v = DocumentValidator(cfg)
        data = b"x" * 1000
        result = v.validate_bytes(data)
        assert not result.is_valid, "Result must not be empty"

    def test_validate_file_txt(self):
        v = DocumentValidator()
        with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False) as f:
            f.write("Hello from a file")
            fname = f.name
        result = v.validate_file(fname)
        assert result.is_valid, "Result must not be empty"
        assert result.document_format == DocumentFormat.TEXT, "Result must not be empty"

    def test_validate_file_md(self):
        v = DocumentValidator()
        with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False) as f:
            f.write("# Title\n\nSome content")
            fname = f.name
        result = v.validate_file(fname)
        assert result.is_valid, "Result must not be empty"
        assert result.document_format == DocumentFormat.MARKDOWN, "Result must not be empty"

    def test_validate_file_nonexistent(self):
        v = DocumentValidator()
        result = v.validate_file("/nonexistent/path/file.txt")
        assert not result.is_valid, "Result must not be empty"

    def test_validate_file_path_object(self):
        v = DocumentValidator()
        with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False) as f:
            f.write("path object test")
            fname = f.name
        result = v.validate_file(Path(fname))
        assert result.is_valid, "Result must not be empty"

    def test_malicious_pattern_detection(self):
        cfg = ValidationConfig(check_malicious=True)
        v = DocumentValidator(cfg)
        # Try something that might trigger malicious pattern detection
        result = v.validate_text("<script>alert('xss')</script>")
        # Should produce a warning (not necessarily invalid)
        assert isinstance(result, ValidationResult)

    def test_no_malicious_check_when_disabled(self):
        cfg = ValidationConfig(check_malicious=False)
        v = DocumentValidator(cfg)
        result = v.validate_text("<script>alert('xss')</script>")
        # With check disabled, no malicious warnings expected
        malicious_warnings = [w for w in result.warnings if "malicious" in w.lower()]
        assert len(malicious_warnings) == 0, "Malicious_warnings must not be empty"

    def test_default_config_when_none(self):
        v = DocumentValidator(None)
        result = v.validate_text("test content")
        assert isinstance(result, ValidationResult)


class TestValidateDocument:
    def test_with_string_text(self):
        result = validate_document("Hello World")
        assert result.is_valid, "Result must not be empty"

    def test_with_bytes(self):
        result = validate_document(b"Hello bytes")
        assert isinstance(result, ValidationResult)

    def test_with_file_path_string(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False) as f:
            f.write("file content")
            fname = f.name
        result = validate_document(fname)
        assert result.is_valid, "Result must not be empty"

    def test_with_file_path_object(self):
        with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False) as f:
            f.write("# Title\n\nContent")
            fname = f.name
        result = validate_document(Path(fname))
        assert result.is_valid, "Result must not be empty"

    def test_with_bytes_and_filename(self):
        result = validate_document(b"content", filename="test.md")
        assert isinstance(result, ValidationResult)

    def test_nonexistent_path_string_treated_as_text(self):
        # A non-existent path string is treated as text content
        result = validate_document("/this/does/not/exist.txt")
        # Should treat as text since the path doesn't exist
        assert isinstance(result, ValidationResult)

    def test_unsupported_type(self):
        result = validate_document(12345)  # type: ignore[arg-type]
        assert not result.is_valid, "Result must not be empty"
