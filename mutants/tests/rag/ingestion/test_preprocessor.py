"""
Tests for Document Preprocessor Module.
"""

import pytest

from codex.rag.ingestion.preprocessor import (
    DocumentPreprocessor,
    PreprocessingConfig,
    PreprocessingResult,
    NormalizationLevel,
    preprocess_text,
    normalize_text,
)


class TestPreprocessingConfig:
    """Tests for PreprocessingConfig."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = PreprocessingConfig()
        
        assert config.normalization_level == NormalizationLevel.STANDARD
        assert config.normalize_whitespace is True
        assert config.remove_html_tags is True
        assert config.compute_fingerprint is True
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = PreprocessingConfig(
            normalization_level=NormalizationLevel.AGGRESSIVE,
            lowercase=True,
            remove_urls=True,
        )
        
        assert config.normalization_level == NormalizationLevel.AGGRESSIVE
        assert config.lowercase is True
        assert config.remove_urls is True


class TestPreprocessingResult:
    """Tests for PreprocessingResult."""
    
    def test_compression_ratio(self):
        """Test compression ratio calculation."""
        result = PreprocessingResult(
            text="short",
            original_length=100,
            processed_length=50,
        )
        
        assert result.compression_ratio == 0.5
    
    def test_compression_ratio_zero_original(self):
        """Test compression ratio with zero original length."""
        result = PreprocessingResult(
            text="",
            original_length=0,
            processed_length=0,
        )
        
        assert result.compression_ratio == 0.0


class TestDocumentPreprocessor:
    """Tests for DocumentPreprocessor class."""
    
    @pytest.fixture
    def preprocessor(self):
        """Create a preprocessor instance."""
        return DocumentPreprocessor()
    
    def test_preprocess_empty_text(self, preprocessor):
        """Test preprocessing empty text."""
        result = preprocessor.preprocess("")
        
        assert result.text == ""
        assert result.original_length == 0
        assert result.processed_length == 0
    
    def test_preprocess_simple_text(self, preprocessor):
        """Test preprocessing simple text."""
        text = "Hello, world!"
        result = preprocessor.preprocess(text)
        
        assert result.text == text
        assert result.original_length == len(text)
        assert result.processed_length == len(text)
    
    def test_normalize_whitespace(self, preprocessor):
        """Test whitespace normalization."""
        text = "Hello    world   with   spaces"
        result = preprocessor.preprocess(text)
        
        assert "    " not in result.text
        assert "whitespace_normalized" in result.changes
    
    def test_remove_html_tags(self, preprocessor):
        """Test HTML tag removal."""
        text = "<p>Hello <b>world</b></p>"
        result = preprocessor.preprocess(text)
        
        assert "<p>" not in result.text
        assert "<b>" not in result.text
        assert "Hello" in result.text
        assert "world" in result.text
    
    def test_normalize_newlines(self, preprocessor):
        """Test multiple newline normalization."""
        text = "Line 1\n\n\n\n\nLine 2"
        result = preprocessor.preprocess(text)
        
        assert "\n\n\n" not in result.text
        assert "Line 1" in result.text
        assert "Line 2" in result.text
    
    def test_remove_control_chars(self, preprocessor):
        """Test control character removal."""
        text = "Hello\x00world\x1ftest"
        result = preprocessor.preprocess(text)
        
        assert "\x00" not in result.text
        assert "\x1f" not in result.text
        assert "Hello" in result.text
    
    def test_preserve_newlines(self, preprocessor):
        """Test that newlines are preserved."""
        text = "Line 1\nLine 2"
        result = preprocessor.preprocess(text)
        
        assert "\n" in result.text
    
    def test_compute_fingerprint(self, preprocessor):
        """Test fingerprint computation."""
        text = "Test document"
        result = preprocessor.preprocess(text)
        
        assert result.fingerprint != ""
        assert len(result.fingerprint) == 16
    
    def test_fingerprint_deterministic(self, preprocessor):
        """Test that fingerprint is deterministic."""
        text = "Same content"
        result1 = preprocessor.preprocess(text)
        result2 = preprocessor.preprocess(text)
        
        assert result1.fingerprint == result2.fingerprint
    
    def test_extract_title_markdown(self, preprocessor):
        """Test title extraction from markdown."""
        text = "# Document Title\n\nContent here"
        result = preprocessor.preprocess(text)
        
        assert "title" in result.metadata
        assert "Document Title" in result.metadata["title"]
    
    def test_extract_title_html(self, preprocessor):
        """Test title extraction from HTML."""
        text = "<title>HTML Title</title><body>Content</body>"
        result = preprocessor.preprocess(text)
        
        # Title extracted before HTML removal
        assert "title" in result.metadata
    
    def test_extract_headers(self, preprocessor):
        """Test header extraction."""
        text = "# H1 Title\n## H2 Section\n### H3 Subsection"
        result = preprocessor.preprocess(text)
        
        assert "headers" in result.metadata
        headers = result.metadata["headers"]
        assert len(headers) == 3
        assert headers[0]["level"] == 1
        assert headers[1]["level"] == 2
        assert headers[2]["level"] == 3
    
    def test_no_normalization(self):
        """Test with normalization disabled."""
        config = PreprocessingConfig(normalization_level=NormalizationLevel.NONE)
        preprocessor = DocumentPreprocessor(config)
        
        text = "<p>Hello    world</p>"
        result = preprocessor.preprocess(text)
        
        assert result.text == text  # Unchanged
        assert len(result.changes) == 0
    
    def test_url_removal(self):
        """Test URL removal when enabled."""
        config = PreprocessingConfig(remove_urls=True)
        preprocessor = DocumentPreprocessor(config)
        
        text = "Visit https://example.com for more info"
        result = preprocessor.preprocess(text)
        
        assert "https://" not in result.text
        assert "urls_removed" in result.changes
    
    def test_email_removal(self):
        """Test email removal when enabled."""
        config = PreprocessingConfig(remove_emails=True)
        preprocessor = DocumentPreprocessor(config)
        
        text = "Contact us at test@example.com"
        result = preprocessor.preprocess(text)
        
        assert "@" not in result.text
        assert "emails_removed" in result.changes
    
    def test_lowercase(self):
        """Test lowercase conversion."""
        config = PreprocessingConfig(lowercase=True)
        preprocessor = DocumentPreprocessor(config)
        
        text = "Hello WORLD"
        result = preprocessor.preprocess(text)
        
        assert result.text == "hello world"
        assert "lowercased" in result.changes


class TestPreprocessTextFunction:
    """Tests for preprocess_text convenience function."""
    
    def test_basic_preprocessing(self):
        """Test basic preprocessing."""
        result = preprocess_text("Hello   world")
        
        assert isinstance(result, PreprocessingResult)
        assert "    " not in result.text
    
    def test_with_config(self):
        """Test preprocessing with config."""
        config = PreprocessingConfig(lowercase=True)
        result = preprocess_text("HELLO", config)
        
        assert result.text == "hello"


class TestNormalizeTextFunction:
    """Tests for normalize_text convenience function."""
    
    def test_standard_normalization(self):
        """Test standard normalization."""
        text = "Hello   <b>world</b>"
        result = normalize_text(text, NormalizationLevel.STANDARD)
        
        assert "   " not in result
        assert "<b>" not in result
    
    def test_no_normalization(self):
        """Test no normalization."""
        text = "Hello   world"
        result = normalize_text(text, NormalizationLevel.NONE)
        
        assert result == text


class TestUnicodeNormalization:
    """Tests for Unicode handling."""
    
    @pytest.fixture
    def preprocessor(self):
        return DocumentPreprocessor()
    
    def test_unicode_normalization(self, preprocessor):
        """Test Unicode normalization."""
        # NFKC normalizes compatibility characters
        text = "ﬁ ﬂ"  # Ligatures
        result = preprocessor.preprocess(text)
        
        assert "unicode_normalized" in str(result.changes)
    
    def test_non_ascii_text(self, preprocessor):
        """Test handling of non-ASCII text."""
        text = "日本語 テスト"
        result = preprocessor.preprocess(text)
        
        assert result.is_valid if hasattr(result, 'is_valid') else True
        assert "日本語" in result.text
