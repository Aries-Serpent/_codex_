"""
Tests for Document Validator Module.
"""

import pytest
from pathlib import Path
import tempfile
import os

from codex.rag.ingestion.validator import (
    DocumentValidator,
    DocumentFormat,
    ValidationResult,
    ValidationConfig,
    validate_document,
)


class TestDocumentFormat:
    """Tests for DocumentFormat enum."""
    
    def test_from_extension_text(self):
        """Test text file extension detection."""
        assert DocumentFormat.from_extension(".txt") == DocumentFormat.TEXT
        assert DocumentFormat.from_extension(".TXT") == DocumentFormat.TEXT
    
    def test_from_extension_markdown(self):
        """Test markdown file extension detection."""
        assert DocumentFormat.from_extension(".md") == DocumentFormat.MARKDOWN
        assert DocumentFormat.from_extension(".markdown") == DocumentFormat.MARKDOWN
    
    def test_from_extension_html(self):
        """Test HTML file extension detection."""
        assert DocumentFormat.from_extension(".html") == DocumentFormat.HTML
        assert DocumentFormat.from_extension(".htm") == DocumentFormat.HTML
    
    def test_from_extension_pdf(self):
        """Test PDF file extension detection."""
        assert DocumentFormat.from_extension(".pdf") == DocumentFormat.PDF
    
    def test_from_extension_json(self):
        """Test JSON file extension detection."""
        assert DocumentFormat.from_extension(".json") == DocumentFormat.JSON
    
    def test_from_extension_yaml(self):
        """Test YAML file extension detection."""
        assert DocumentFormat.from_extension(".yaml") == DocumentFormat.YAML
        assert DocumentFormat.from_extension(".yml") == DocumentFormat.YAML
    
    def test_from_extension_unknown(self):
        """Test unknown file extension."""
        assert DocumentFormat.from_extension(".xyz") == DocumentFormat.UNKNOWN
        assert DocumentFormat.from_extension("") == DocumentFormat.UNKNOWN
    
    def test_from_mime_type(self):
        """Test MIME type detection."""
        assert DocumentFormat.from_mime_type("text/plain") == DocumentFormat.TEXT
        assert DocumentFormat.from_mime_type("text/html") == DocumentFormat.HTML
        assert DocumentFormat.from_mime_type("application/json") == DocumentFormat.JSON
        assert DocumentFormat.from_mime_type("unknown/type") == DocumentFormat.UNKNOWN


class TestValidationResult:
    """Tests for ValidationResult dataclass."""
    
    def test_add_error(self):
        """Test adding an error."""
        result = ValidationResult(is_valid=True, document_format=DocumentFormat.TEXT)
        assert result.is_valid
        
        result.add_error("Test error")
        assert not result.is_valid
        assert "Test error" in result.errors
    
    def test_add_warning(self):
        """Test adding a warning."""
        result = ValidationResult(is_valid=True, document_format=DocumentFormat.TEXT)
        
        result.add_warning("Test warning")
        assert result.is_valid  # Warnings don't affect validity
        assert "Test warning" in result.warnings


class TestDocumentValidator:
    """Tests for DocumentValidator class."""
    
    @pytest.fixture
    def validator(self):
        """Create a validator instance."""
        return DocumentValidator()
    
    @pytest.fixture
    def temp_text_file(self):
        """Create a temporary text file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is test content.\nSecond line.")
            temp_path = f.name
        yield Path(temp_path)
        os.unlink(temp_path)
    
    @pytest.fixture
    def temp_empty_file(self):
        """Create an empty temporary file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            pass  # Empty file
        yield Path(f.name)
        os.unlink(f.name)
    
    def test_validate_file_success(self, validator, temp_text_file):
        """Test successful file validation."""
        result = validator.validate_file(temp_text_file)
        
        assert result.is_valid
        assert result.document_format == DocumentFormat.TEXT
        assert result.file_size > 0
        assert result.content_hash != ""
        assert result.encoding == "utf-8"
    
    def test_validate_file_not_found(self, validator):
        """Test validation of non-existent file."""
        result = validator.validate_file("/nonexistent/path/file.txt")
        
        assert not result.is_valid
        assert "not found" in result.errors[0].lower()
    
    def test_validate_file_empty(self, validator, temp_empty_file):
        """Test validation of empty file."""
        config = ValidationConfig(min_file_size_bytes=1)
        validator = DocumentValidator(config)
        result = validator.validate_file(temp_empty_file)
        
        assert not result.is_valid
        assert "too small" in result.errors[0].lower()
    
    def test_validate_text(self, validator):
        """Test text content validation."""
        result = validator.validate_text("Hello, this is a test document.")
        
        assert result.is_valid
        assert result.document_format == DocumentFormat.TEXT
        assert result.metadata.get("char_count") > 0
        assert result.metadata.get("word_count") > 0
    
    def test_validate_text_empty(self, validator):
        """Test validation of empty text."""
        result = validator.validate_text("")
        
        assert result.is_valid  # Empty is valid but with warning
        assert len(result.warnings) > 0
    
    def test_validate_bytes(self, validator):
        """Test bytes content validation."""
        content = b"Test document content"
        result = validator.validate_bytes(content, filename="test.txt")
        
        assert result.is_valid
        assert result.file_size == len(content)
    
    def test_validate_malicious_content(self, validator):
        """Test detection of potentially malicious content."""
        config = ValidationConfig(check_malicious=True)
        validator = DocumentValidator(config)
        
        result = validator.validate_text('<script>alert("xss")</script>')
        
        assert result.is_valid  # Malicious content adds warning, not error
        assert len(result.warnings) > 0
        assert "malicious" in result.warnings[0].lower() or "script" in result.warnings[0].lower()
    
    def test_validate_text_too_long(self, validator):
        """Test validation of text exceeding max length."""
        config = ValidationConfig(max_text_length=100)
        validator = DocumentValidator(config)
        
        long_text = "x" * 200
        result = validator.validate_text(long_text)
        
        assert not result.is_valid
        assert "too long" in result.errors[0].lower()
    
    def test_file_size_limit(self):
        """Test file size limit validation."""
        config = ValidationConfig(max_file_size_mb=0.001)  # 1KB
        validator = DocumentValidator(config)
        
        # Create content larger than 1KB
        large_content = b"x" * 2000
        result = validator.validate_bytes(large_content)
        
        assert not result.is_valid
        assert "too large" in result.errors[0].lower()


class TestValidateDocumentFunction:
    """Tests for validate_document convenience function."""
    
    @pytest.fixture
    def temp_file(self):
        """Create a temporary file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content for validation")
            temp_path = f.name
        yield Path(temp_path)
        os.unlink(temp_path)
    
    def test_validate_file_path(self, temp_file):
        """Test validating a file path."""
        result = validate_document(temp_file)
        assert result.is_valid
    
    def test_validate_string_content(self):
        """Test validating string content."""
        result = validate_document("This is text content")
        assert result.is_valid
    
    def test_validate_bytes_content(self):
        """Test validating bytes content."""
        result = validate_document(b"Bytes content", filename="test.txt")
        assert result.is_valid


class TestValidationConfig:
    """Tests for ValidationConfig."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = ValidationConfig()
        
        assert config.max_file_size_mb == 100.0
        assert config.min_file_size_bytes == 1
        assert config.compute_hash is True
        assert config.check_malicious is True
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = ValidationConfig(
            max_file_size_mb=50.0,
            check_malicious=False,
        )
        
        assert config.max_file_size_mb == 50.0
        assert config.check_malicious is False
