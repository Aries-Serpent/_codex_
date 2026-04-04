"""
Tests for src/codex/rag/ingestion/preprocessor.py

Covers DocumentPreprocessor, PreprocessingConfig, PreprocessingResult,
NormalizationLevel, preprocess_text(), and normalize_text().
"""

from codex.rag.ingestion.preprocessor import (
    DocumentPreprocessor,
    NormalizationLevel,
    PreprocessingConfig,
    PreprocessingResult,
    normalize_text,
    preprocess_text,
)


class TestNormalizationLevel:
    def test_all_levels_exist(self):
        assert NormalizationLevel.NONE.value == "none"
        assert NormalizationLevel.MINIMAL.value == "minimal"
        assert NormalizationLevel.STANDARD.value == "standard"
        assert NormalizationLevel.AGGRESSIVE.value == "aggressive"


class TestPreprocessingResult:
    def test_compression_ratio_zero_original(self):
        r = PreprocessingResult(text="", original_length=0, processed_length=0)
        assert r.compression_ratio == 0.0

    def test_compression_ratio_reduction(self):
        r = PreprocessingResult(text="hi", original_length=100, processed_length=50)
        assert r.compression_ratio == 0.5

    def test_compression_ratio_clamped_at_zero(self):
        # processed > original (preprocessing added content)
        r = PreprocessingResult(text="abc", original_length=2, processed_length=10)
        assert r.compression_ratio == 0.0

    def test_default_fields(self):
        r = PreprocessingResult(text="x", original_length=1, processed_length=1)
        assert r.fingerprint == ""
        assert r.metadata == {}
        assert r.changes == []


class TestPreprocessingConfig:
    def test_defaults(self):
        cfg = PreprocessingConfig()
        assert cfg.normalization_level == NormalizationLevel.STANDARD
        assert cfg.normalize_whitespace is True
        assert cfg.remove_html_tags is True
        assert cfg.lowercase is False

    def test_custom_config(self):
        cfg = PreprocessingConfig(
            normalization_level=NormalizationLevel.AGGRESSIVE,
            lowercase=True,
            remove_urls=True,
        )
        assert cfg.normalization_level == NormalizationLevel.AGGRESSIVE
        assert cfg.lowercase is True
        assert cfg.remove_urls is True


class TestDocumentPreprocessor:
    def test_basic_preprocess(self):
        pp = DocumentPreprocessor()
        result = pp.preprocess("Hello world")
        assert isinstance(result, PreprocessingResult)
        assert "Hello" in result.text or "hello" in result.text

    def test_empty_text(self):
        pp = DocumentPreprocessor()
        result = pp.preprocess("")
        assert result.text == ""
        assert result.original_length == 0

    def test_whitespace_normalization(self):
        cfg = PreprocessingConfig(normalize_whitespace=True)
        pp = DocumentPreprocessor(cfg)
        result = pp.preprocess("Hello    world\t\there")
        assert "  " not in result.text

    def test_remove_html_tags(self):
        cfg = PreprocessingConfig(remove_html_tags=True)
        pp = DocumentPreprocessor(cfg)
        result = pp.preprocess("<p>Hello <b>world</b></p>")
        assert "<" not in result.text
        assert "Hello" in result.text
        assert "world" in result.text

    def test_remove_urls(self):
        cfg = PreprocessingConfig(remove_urls=True)
        pp = DocumentPreprocessor(cfg)
        result = pp.preprocess("Visit https://example.com for more info")
        assert "https://example.com" not in result.text

    def test_remove_emails(self):
        cfg = PreprocessingConfig(remove_emails=True)
        pp = DocumentPreprocessor(cfg)
        result = pp.preprocess("Contact user@example.com for help")
        assert "user@example.com" not in result.text

    def test_lowercase(self):
        cfg = PreprocessingConfig(lowercase=True)
        pp = DocumentPreprocessor(cfg)
        result = pp.preprocess("HELLO WORLD")
        assert result.text == result.text.lower()

    def test_unicode_normalization(self):
        cfg = PreprocessingConfig(normalize_unicode=True, unicode_form="NFKC")
        pp = DocumentPreprocessor(cfg)
        # Ligature fi should be normalized
        result = pp.preprocess("The \ufb01le")
        assert isinstance(result.text, str)

    def test_control_chars_removed(self):
        cfg = PreprocessingConfig(remove_control_chars=True)
        pp = DocumentPreprocessor(cfg)
        result = pp.preprocess("Hello\x00\x01World")
        assert "\x00" not in result.text
        assert "\x01" not in result.text

    def test_fingerprint_computed(self):
        cfg = PreprocessingConfig(compute_fingerprint=True)
        pp = DocumentPreprocessor(cfg)
        result = pp.preprocess("Some text to fingerprint")
        assert result.fingerprint != ""
        assert len(result.fingerprint) == 16

    def test_fingerprint_deterministic(self):
        cfg = PreprocessingConfig(compute_fingerprint=True)
        pp = DocumentPreprocessor(cfg)
        r1 = pp.preprocess("Same text")
        r2 = pp.preprocess("Same text")
        assert r1.fingerprint == r2.fingerprint

    def test_extract_title_markdown(self):
        cfg = PreprocessingConfig(extract_title=True)
        pp = DocumentPreprocessor(cfg)
        result = pp.preprocess("# My Document\n\nSome content here.")
        assert result.metadata.get("title") == "My Document"

    def test_extract_headers(self):
        cfg = PreprocessingConfig(extract_headers=True)
        pp = DocumentPreprocessor(cfg)
        result = pp.preprocess("# Header 1\n## Header 2\nSome text")
        assert "headers" in result.metadata

    def test_normalization_level_none(self):
        cfg = PreprocessingConfig(normalization_level=NormalizationLevel.NONE)
        pp = DocumentPreprocessor(cfg)
        text = "  Hello   World  "
        result = pp.preprocess(text)
        # With NONE level minimal processing should occur
        assert isinstance(result, PreprocessingResult)

    def test_normalization_level_minimal(self):
        cfg = PreprocessingConfig(normalization_level=NormalizationLevel.MINIMAL)
        pp = DocumentPreprocessor(cfg)
        result = pp.preprocess("  Hello World  ")
        assert isinstance(result, PreprocessingResult)

    def test_normalization_level_aggressive(self):
        cfg = PreprocessingConfig(normalization_level=NormalizationLevel.AGGRESSIVE)
        pp = DocumentPreprocessor(cfg)
        result = pp.preprocess("Hello  <b>World</b>  https://url.com  test@email.com")
        assert isinstance(result, PreprocessingResult)

    def test_extra_newlines_removed(self):
        cfg = PreprocessingConfig(remove_extra_newlines=True, max_consecutive_newlines=2)
        pp = DocumentPreprocessor(cfg)
        result = pp.preprocess("Line 1\n\n\n\n\nLine 2")
        assert result.text.count("\n\n\n") == 0

    def test_original_length_preserved(self):
        pp = DocumentPreprocessor()
        text = "Hello World"
        result = pp.preprocess(text)
        assert result.original_length == len(text)

    def test_default_config_used_when_none(self):
        pp = DocumentPreprocessor(None)
        result = pp.preprocess("test")
        assert isinstance(result, PreprocessingResult)


class TestPreprocessText:
    def test_convenience_function(self):
        result = preprocess_text("Hello World")
        assert isinstance(result, PreprocessingResult)
        assert "Hello" in result.text or "hello" in result.text

    def test_with_custom_config(self):
        cfg = PreprocessingConfig(lowercase=True)
        result = preprocess_text("HELLO", config=cfg)
        assert result.text == "hello"

    def test_empty_input(self):
        result = preprocess_text("")
        assert result.text == ""


class TestNormalizeText:
    def test_default_level(self):
        out = normalize_text("Hello  World")
        assert isinstance(out, str)

    def test_none_level(self):
        out = normalize_text("Hello", NormalizationLevel.NONE)
        assert isinstance(out, str)

    def test_aggressive_level(self):
        out = normalize_text("<p>Hello</p>", NormalizationLevel.AGGRESSIVE)
        assert isinstance(out, str)
        assert "<p>" not in out

    def test_minimal_level(self):
        out = normalize_text("  Hello  ", NormalizationLevel.MINIMAL)
        assert isinstance(out, str)
