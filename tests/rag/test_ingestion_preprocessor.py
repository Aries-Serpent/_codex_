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
        assert NormalizationLevel.NONE.value == "none", "Value must be initialized"
        assert NormalizationLevel.MINIMAL.value == "minimal", "Value must be initialized"
        assert NormalizationLevel.STANDARD.value == "standard", "Value must be initialized"
        assert NormalizationLevel.AGGRESSIVE.value == "aggressive", "Value must be initialized"


class TestPreprocessingResult:
    def test_compression_ratio_zero_original(self):
        r = PreprocessingResult(text="", original_length=0, processed_length=0)
        assert r.compression_ratio == 0.0, "compression_ratio is not valid"

    def test_compression_ratio_reduction(self):
        r = PreprocessingResult(text="hi", original_length=100, processed_length=50)
        assert r.compression_ratio == 0.5, "compression_ratio is not valid"

    def test_compression_ratio_clamped_at_zero(self):
        # processed > original (preprocessing added content)
        r = PreprocessingResult(text="abc", original_length=2, processed_length=10)
        assert r.compression_ratio == 0.0, "compression_ratio is not valid"

    def test_default_fields(self):
        r = PreprocessingResult(text="x", original_length=1, processed_length=1)
        assert r.fingerprint == "", "fingerprint is not valid"
        assert r.metadata == {}, "Data must not be empty"
        assert r.changes == [], "changes is not valid"


class TestPreprocessingConfig:
    def test_defaults(self):
        cfg = PreprocessingConfig()
        assert cfg.normalization_level == NormalizationLevel.STANDARD, "normalization_level is not valid"
        assert cfg.normalize_whitespace is True, "normalize_whitespace is not valid"
        assert cfg.remove_html_tags is True, "remove_html_tags is not valid"
        assert cfg.lowercase is False, "lowercase is not valid"

    def test_custom_config(self):
        cfg = PreprocessingConfig(
            normalization_level=NormalizationLevel.AGGRESSIVE,
            lowercase=True,
            remove_urls=True,
        )
        assert cfg.normalization_level == NormalizationLevel.AGGRESSIVE, "normalization_level is not valid"
        assert cfg.lowercase is True, "lowercase is not valid"
        assert cfg.remove_urls is True, "remove_urls is not valid"


class TestDocumentPreprocessor:
    def test_basic_preprocess(self):
        pp = DocumentPreprocessor()
        result = pp.preprocess("Hello world")
        assert isinstance(result, PreprocessingResult)
        assert "Hello" in result.text or "hello" in result.text, "Result must not be empty"

    def test_empty_text(self):
        pp = DocumentPreprocessor()
        result = pp.preprocess("")
        assert result.text == "", "Result must not be empty"
        assert result.original_length == 0, "Result must not be empty"

    def test_whitespace_normalization(self):
        cfg = PreprocessingConfig(normalize_whitespace=True)
        pp = DocumentPreprocessor(cfg)
        result = pp.preprocess("Hello    world\t\there")
        assert "  " not in result.text, "Result must not be empty"

    def test_remove_html_tags(self):
        cfg = PreprocessingConfig(remove_html_tags=True)
        pp = DocumentPreprocessor(cfg)
        result = pp.preprocess("<p>Hello <b>world</b></p>")
        assert "<" not in result.text, "Result must not be empty"
        assert "Hello" in result.text, "Result must not be empty"
        assert "world" in result.text, "Result must not be empty"

    def test_remove_urls(self):
        cfg = PreprocessingConfig(remove_urls=True)
        pp = DocumentPreprocessor(cfg)
        result = pp.preprocess("Visit https://example.com for more info")
        assert "https://example.com" not in result.text, "Result must not be empty"

    def test_remove_emails(self):
        cfg = PreprocessingConfig(remove_emails=True)
        pp = DocumentPreprocessor(cfg)
        result = pp.preprocess("Contact user@example.com for help")
        assert "user@example.com" not in result.text, "Result must not be empty"

    def test_lowercase(self):
        cfg = PreprocessingConfig(lowercase=True)
        pp = DocumentPreprocessor(cfg)
        result = pp.preprocess("HELLO WORLD")
        assert result.text == result.text.lower(), "Result must not be empty"

    def test_unicode_normalization(self):
        cfg = PreprocessingConfig(normalize_unicode=True, unicode_form="NFKC")
        pp = DocumentPreprocessor(cfg)
        # Ligature fi should be normalized
        result = pp.preprocess("The \ufb01le")
        assert isinstance(result.text, str)

    def test_unicode_nfc_nfd_cafe_equivalence(self):
        """NFC precomposed and NFD decomposed café produce identical output under NFKC."""
        import unicodedata

        cfg = PreprocessingConfig(normalize_unicode=True, unicode_form="NFKC", lowercase=False)
        pp = DocumentPreprocessor(cfg)

        # NFC: é as single precomposed code point U+00E9
        nfc_text = "Visit the caf\u00e9 today."
        # NFD: e followed by combining acute accent U+0301 (decomposed)
        nfd_text = "Visit the cafe\u0301 today."

        assert nfc_text != nfd_text, "nfc_text is not valid"

        result_nfc = pp.preprocess(nfc_text)
        result_nfd = pp.preprocess(nfd_text)

        # Both forms must produce the same normalized text
        assert result_nfc.text == result_nfd.text, (
            f"NFC and NFD café produced different output: "
            f"{repr(result_nfc.text)} vs {repr(result_nfd.text)}"
        )
        # Output must be in NFC (NFKC is a superset of NFC)
        assert unicodedata.is_normalized("NFC", result_nfc.text)

    def test_unicode_nfd_change_tracked(self):
        """Preprocessing records unicode_normalized change for NFD input under NFKC."""
        cfg = PreprocessingConfig(normalize_unicode=True, unicode_form="NFKC")
        pp = DocumentPreprocessor(cfg)

        # NFD decomposed form will differ from NFKC — change must be recorded
        nfd_text = "cafe\u0301"  # decomposed é
        result = pp.preprocess(nfd_text)

        assert any(
            "unicode_normalized" in c for c in result.changes
        ), f"Expected 'unicode_normalized_NFKC' in changes, got: {result.changes}"

    def test_unicode_nfc_no_change_when_already_normalized(self):
        """NFC input with NFKC form records no change when text is already NFKC."""
        import unicodedata

        cfg = PreprocessingConfig(
            normalize_unicode=True,
            unicode_form="NFKC",
            normalize_whitespace=False,
            remove_extra_newlines=False,
            strip_leading_trailing=False,
            remove_control_chars=False,
            remove_html_tags=False,
            compute_fingerprint=False,
        )
        pp = DocumentPreprocessor(cfg)

        # Already-NFKC ASCII text — normalization is a no-op
        text = "hello world"
        assert unicodedata.is_normalized("NFKC", text)
        result = pp.preprocess(text)

        assert "unicode_normalized_NFKC" not in result.changes, "Result must not be empty"

    def test_control_chars_removed(self):
        cfg = PreprocessingConfig(remove_control_chars=True)
        pp = DocumentPreprocessor(cfg)
        result = pp.preprocess("Hello\x00\x01World")
        assert "\x00" not in result.text, "Result must not be empty"
        assert "\x01" not in result.text, "Result must not be empty"

    def test_fingerprint_computed(self):
        cfg = PreprocessingConfig(compute_fingerprint=True)
        pp = DocumentPreprocessor(cfg)
        result = pp.preprocess("Some text to fingerprint")
        assert result.fingerprint != "", "Result must not be empty"
        assert len(result.fingerprint) == 16, "Collection must not be empty"

    def test_fingerprint_deterministic(self):
        cfg = PreprocessingConfig(compute_fingerprint=True)
        pp = DocumentPreprocessor(cfg)
        r1 = pp.preprocess("Same text")
        r2 = pp.preprocess("Same text")
        assert r1.fingerprint == r2.fingerprint, "fingerprint is not valid"

    def test_extract_title_markdown(self):
        cfg = PreprocessingConfig(extract_title=True)
        pp = DocumentPreprocessor(cfg)
        result = pp.preprocess("# My Document\n\nSome content here.")
        assert result.metadata.get("title") == "My Document", "Result must not be empty"

    def test_extract_headers(self):
        cfg = PreprocessingConfig(extract_headers=True)
        pp = DocumentPreprocessor(cfg)
        result = pp.preprocess("# Header 1\n## Header 2\nSome text")
        assert "headers" in result.metadata, "Result must not be empty"

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
        assert result.text.count("\n\n\n") == 0, "Result must not be empty"

    def test_original_length_preserved(self):
        pp = DocumentPreprocessor()
        text = "Hello World"
        result = pp.preprocess(text)
        assert result.original_length == len(text), "Text must not be empty"

    def test_default_config_used_when_none(self):
        pp = DocumentPreprocessor(None)
        result = pp.preprocess("test")
        assert isinstance(result, PreprocessingResult)


class TestPreprocessText:
    def test_convenience_function(self):
        result = preprocess_text("Hello World")
        assert isinstance(result, PreprocessingResult)
        assert "Hello" in result.text or "hello" in result.text, "Result must not be empty"

    def test_with_custom_config(self):
        cfg = PreprocessingConfig(lowercase=True)
        result = preprocess_text("HELLO", config=cfg)
        assert result.text == "hello", "Result must not be empty"

    def test_empty_input(self):
        result = preprocess_text("")
        assert result.text == "", "Result must not be empty"


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
        assert "<p>" not in out, "Condition must be true"

    def test_minimal_level(self):
        out = normalize_text("  Hello  ", NormalizationLevel.MINIMAL)
        assert isinstance(out, str)
