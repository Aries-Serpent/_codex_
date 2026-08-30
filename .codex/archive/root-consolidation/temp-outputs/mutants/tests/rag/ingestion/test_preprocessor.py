"""
Tests for Document Preprocessor Module.
"""

import pytest

from codex.rag.ingestion.preprocessor import (
    DocumentPreprocessor,
    NormalizationLevel,
    PreprocessingConfig,
    PreprocessingResult,
    normalize_text,
    preprocess_text,
)


class TestPreprocessingConfig:
    """Tests for PreprocessingConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = PreprocessingConfig()

        assert config.normalization_level == NormalizationLevel.STANDARD, "normalization_level is not valid"
        assert config.normalize_whitespace is True, "normalize_whitespace is not valid"
        assert config.remove_html_tags is True, "remove_html_tags is not valid"
        assert config.compute_fingerprint is True, "compute_fingerprint is not valid"

    def test_custom_config(self):
        """Test custom configuration."""
        config = PreprocessingConfig(
            normalization_level=NormalizationLevel.AGGRESSIVE,
            lowercase=True,
            remove_urls=True,
        )

        assert config.normalization_level == NormalizationLevel.AGGRESSIVE, "normalization_level is not valid"
        assert config.lowercase is True, "lowercase is not valid"
        assert config.remove_urls is True, "remove_urls is not valid"


class TestPreprocessingResult:
    """Tests for PreprocessingResult."""

    def test_compression_ratio(self):
        """Test compression ratio calculation."""
        result = PreprocessingResult(
            text="short",
            original_length=100,
            processed_length=50,
        )

        assert result.compression_ratio == 0.5, "Result must not be empty"

    def test_compression_ratio_zero_original(self):
        """Test compression ratio with zero original length."""
        result = PreprocessingResult(
            text="",
            original_length=0,
            processed_length=0,
        )

        assert result.compression_ratio == 0.0, "Result must not be empty"


class TestDocumentPreprocessor:
    """Tests for DocumentPreprocessor class."""

    @pytest.fixture
    def preprocessor(self):
        """Create a preprocessor instance."""
        return DocumentPreprocessor()

    def test_preprocess_empty_text(self, preprocessor):
        """Test preprocessing empty text."""
        result = preprocessor.preprocess("")

        assert result.text == "", "Result must not be empty"
        assert result.original_length == 0, "Result must not be empty"
        assert result.processed_length == 0, "Result must not be empty"

    def test_preprocess_simple_text(self, preprocessor):
        """Test preprocessing simple text."""
        text = "Hello, world!"
        result = preprocessor.preprocess(text)

        assert result.text == text, "Result must not be empty"
        assert result.original_length == len(text), "Text must not be empty"
        assert result.processed_length == len(text), "Text must not be empty"

    def test_normalize_whitespace(self, preprocessor):
        """Test whitespace normalization."""
        text = "Hello    world   with   spaces"
        result = preprocessor.preprocess(text)

        assert "    " not in result.text, "Result must not be empty"
        assert "whitespace_normalized" in result.changes, "Result must not be empty"

    def test_remove_html_tags(self, preprocessor):
        """Test HTML tag removal."""
        text = "<p>Hello <b>world</b></p>"
        result = preprocessor.preprocess(text)

        assert "<p>" not in result.text, "Result must not be empty"
        assert "<b>" not in result.text, "Result must not be empty"
        assert "Hello" in result.text, "Result must not be empty"
        assert "world" in result.text, "Result must not be empty"

    def test_normalize_newlines(self, preprocessor):
        """Test multiple newline normalization."""
        text = "Line 1\n\n\n\n\nLine 2"
        result = preprocessor.preprocess(text)

        assert "\n\n\n" not in result.text, "Result must not be empty"
        assert "Line 1" in result.text, "Result must not be empty"
        assert "Line 2" in result.text, "Result must not be empty"

    def test_remove_control_chars(self, preprocessor):
        """Test control character removal."""
        text = "Hello\x00world\x1ftest"
        result = preprocessor.preprocess(text)

        assert "\x00" not in result.text, "Result must not be empty"
        assert "\x1f" not in result.text, "Result must not be empty"
        assert "Hello" in result.text, "Result must not be empty"

    def test_preserve_newlines(self, preprocessor):
        """Test that newlines are preserved."""
        text = "Line 1\nLine 2"
        result = preprocessor.preprocess(text)

        assert "\n" in result.text, "Result must not be empty"

    def test_compute_fingerprint(self, preprocessor):
        """Test fingerprint computation."""
        text = "Test document"
        result = preprocessor.preprocess(text)

        assert result.fingerprint != "", "Result must not be empty"
        assert len(result.fingerprint) == 16, "Collection must not be empty"

    def test_fingerprint_deterministic(self, preprocessor):
        """Test that fingerprint is deterministic."""
        text = "Same content"
        result1 = preprocessor.preprocess(text)
        result2 = preprocessor.preprocess(text)

        assert result1.fingerprint == result2.fingerprint, "Result must not be empty"

    def test_extract_title_markdown(self, preprocessor):
        """Test title extraction from markdown."""
        text = "# Document Title\n\nContent here"
        result = preprocessor.preprocess(text)

        assert "title" in result.metadata, "Result must not be empty"
        assert "Document Title" in result.metadata["title"], "Result must not be empty"

    def test_extract_title_html(self, preprocessor):
        """Test title extraction from HTML."""
        text = "<title>HTML Title</title><body>Content</body>"
        result = preprocessor.preprocess(text)

        # Title extracted before HTML removal
        assert "title" in result.metadata, "Result must not be empty"

    def test_extract_headers(self, preprocessor):
        """Test header extraction."""
        text = "# H1 Title\n## H2 Section\n### H3 Subsection"
        result = preprocessor.preprocess(text)

        assert "headers" in result.metadata, "Result must not be empty"
        headers = result.metadata["headers"]
        assert len(headers) == 3, "Headers must not be empty"
        assert headers[0]["level"] == 1, "Condition must be true"
        assert headers[1]["level"] == 2, "Condition must be true"
        assert headers[2]["level"] == 3, "Condition must be true"

    def test_no_normalization(self):
        """Test with normalization disabled."""
        config = PreprocessingConfig(normalization_level=NormalizationLevel.NONE)
        preprocessor = DocumentPreprocessor(config)

        text = "<p>Hello    world</p>"
        result = preprocessor.preprocess(text)

        assert result.text == text, "Result must not be empty"
        assert len(result.changes) == 0, "Collection must not be empty"

    def test_url_removal(self):
        """Test URL removal when enabled."""
        config = PreprocessingConfig(remove_urls=True)
        preprocessor = DocumentPreprocessor(config)

        text = "Visit https://example.com for more info"
        result = preprocessor.preprocess(text)

        assert "https://" not in result.text, "Result must not be empty"
        assert "urls_removed" in result.changes, "Result must not be empty"

    def test_email_removal(self):
        """Test email removal when enabled."""
        config = PreprocessingConfig(remove_emails=True)
        preprocessor = DocumentPreprocessor(config)

        text = "Contact us at test@example.com"
        result = preprocessor.preprocess(text)

        assert "@" not in result.text, "Result must not be empty"
        assert "emails_removed" in result.changes, "Result must not be empty"

    def test_lowercase(self):
        """Test lowercase conversion."""
        config = PreprocessingConfig(lowercase=True)
        preprocessor = DocumentPreprocessor(config)

        text = "Hello WORLD"
        result = preprocessor.preprocess(text)

        assert result.text == "hello world", "Result must not be empty"
        assert "lowercased" in result.changes, "Result must not be empty"


class TestPreprocessTextFunction:
    """Tests for preprocess_text convenience function."""

    def test_basic_preprocessing(self):
        """Test basic preprocessing."""
        result = preprocess_text("Hello   world")

        assert isinstance(result, PreprocessingResult)
        assert "    " not in result.text, "Result must not be empty"

    def test_with_config(self):
        """Test preprocessing with config."""
        config = PreprocessingConfig(lowercase=True)
        result = preprocess_text("HELLO", config)

        assert result.text == "hello", "Result must not be empty"


class TestNormalizeTextFunction:
    """Tests for normalize_text convenience function."""

    def test_standard_normalization(self):
        """Test standard normalization."""
        text = "Hello   <b>world</b>"
        result = normalize_text(text, NormalizationLevel.STANDARD)

        assert "   " not in result, "Result must not be empty"
        assert "<b>" not in result, "Result must not be empty"

    def test_no_normalization(self):
        """Test no normalization."""
        text = "Hello   world"
        result = normalize_text(text, NormalizationLevel.NONE)

        assert result == text, "Result must not be empty"


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

        assert "unicode_normalized" in str(result.changes), "Result must not be empty"

    def test_non_ascii_text(self, preprocessor):
        """Test handling of non-ASCII text."""
        text = "日本語 テスト"
        result = preprocessor.preprocess(text)

        assert result.is_valid if hasattr(result, "is_valid") else True
        assert "日本語" in result.text, "Result must not be empty"


# ---------------------------------------------------------------------------
# Targeted gap-fill tests
# ---------------------------------------------------------------------------


class TestPreprocessorAllFlagsFalse:
    """Covers False branches for each per-flag if-check in preprocess() (many arcs)."""

    def test_all_optional_flags_disabled(self):
        """With all optional flags False, every if-guard False branch is hit."""
        config = PreprocessingConfig(
            normalization_level=NormalizationLevel.STANDARD,
            normalize_unicode=False,  # 145->149
            remove_control_chars=False,  # 149->153
            remove_html_tags=False,  # 153->157
            remove_urls=False,
            remove_emails=False,
            normalize_whitespace=False,  # 165->169
            remove_extra_newlines=False,  # 169->173
            strip_leading_trailing=False,  # 173->177
            lowercase=False,
            extract_title=False,  # 182->185
            extract_headers=False,  # 185->189
            compute_fingerprint=False,  # 189->192
        )
        preprocessor = DocumentPreprocessor(config)
        text = "<p>Hello   world\n\n\nLine2</p>"
        result = preprocessor.preprocess(text)
        # Nothing changed because all transforms disabled
        assert result.text == text, "Result must not be empty"
        assert result.changes == [], "Result must not be empty"
        assert result.fingerprint == "", "Result must not be empty"
        assert "title" not in result.metadata, "Result must not be empty"
        assert "headers" not in result.metadata, "Result must not be empty"


class TestPreprocessorPreserveNewlinesFalse:
    """Covers else branch in _remove_control_chars (line 215)."""

    def test_preserve_newlines_false_uses_pattern(self):
        """preserve_newlines=False → CONTROL_CHAR_PATTERN removes all control chars (line 215)."""
        config = PreprocessingConfig(
            preserve_newlines=False,
            remove_control_chars=True,
        )
        preprocessor = DocumentPreprocessor(config)
        # \x0b (vertical tab) is a control char not caught by the newline-preserving regex
        text = "Hello\x0bworld"
        result = preprocessor.preprocess(text)
        assert "\x0b" not in result.text, "Result must not be empty"
        assert "control_chars_removed" in result.changes, "Result must not be empty"


class TestPreprocessorRemoveWithNoMatch:
    """Covers False branches when remove_urls/remove_emails find nothing (lines 231->233, 238->240)."""

    def test_remove_urls_no_urls_present(self):
        """remove_urls=True but no URLs → cleaned == text → no change logged (line 231->233)."""
        config = PreprocessingConfig(remove_urls=True)
        preprocessor = DocumentPreprocessor(config)
        result = preprocessor.preprocess("No URLs in this text at all.")
        assert "urls_removed" not in result.changes, "Result must not be empty"

    def test_remove_emails_no_emails_present(self):
        """remove_emails=True but no emails → no change logged (line 238->240)."""
        config = PreprocessingConfig(remove_emails=True)
        preprocessor = DocumentPreprocessor(config)
        result = preprocessor.preprocess("No email addresses here.")
        assert "emails_removed" not in result.changes, "Result must not be empty"


class TestExtractTitleEdgeCases:
    """Covers edge cases in _extract_title (lines 275->exit, 277->275)."""

    def test_extract_title_empty_lines_before_content(self):
        """Empty lines before non-empty line → loop skips empties (line 277->275)."""
        preprocessor = DocumentPreprocessor()
        # No HTML title, no markdown header, first non-empty line after blank lines
        text = "\n\nActual content line here"
        result = preprocessor.preprocess(text)
        assert result.metadata.get("title") == "Actual content line here", "Result must not be empty"

    def test_extract_title_all_empty_lines(self):
        """All lines empty → for loop exits without setting title (line 275->exit)."""
        preprocessor = DocumentPreprocessor()
        # "\n\n\n" has no non-empty lines, no HTML title, no markdown header
        text = "\n\n\n"
        result = preprocessor.preprocess(text)
        # title should NOT be set (loop completes without finding content)
        assert "title" not in result.metadata, "Result must not be empty"
