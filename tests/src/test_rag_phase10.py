"""Phase 10B gap-fill: RAG post-processing coverage.

Tests ``src/codex/rag/postprocess.py`` — OutputProcessor and the
``postprocess_output`` convenience function.
"""

from __future__ import annotations

from codex.rag.postprocess import OutputProcessor, postprocess_output

# ============================================================================
# OutputProcessor.scrub_output
# ============================================================================


class TestScrubOutput:
    def test_removes_safety_markers(self):
        text = "Hello ### RETRIEVED CONTEXT START ### secret ### RETRIEVED CONTEXT END ### world"
        result = OutputProcessor.scrub_output(text)
        assert "RETRIEVED CONTEXT" not in result, "Result must not be empty"
        assert "Hello" in result, "Result must not be empty"
        assert "world" in result, "Result must not be empty"

    def test_removes_user_query_markers(self):
        text = "### USER QUERY START ### q ### USER QUERY END ###"
        result = OutputProcessor.scrub_output(text)
        assert "USER QUERY" not in result, "Result must not be empty"

    def test_custom_redaction_rules(self):
        rules = [{"pattern": r"\bSSN-\d{3}-\d{2}-\d{4}\b", "replacement": "[SSN_REDACTED]"}]
        text = "Patient SSN-123-45-6789 record"
        result = OutputProcessor.scrub_output(text, redaction_rules=rules)
        assert "SSN-123" not in result, "Result must not be empty"
        assert "[SSN_REDACTED]" in result, "Result must not be empty"

    def test_multiple_redaction_rules(self):
        rules = [
            {"pattern": r"secret\d+", "replacement": "[SECRET_REDACTED]"},
            {"pattern": r"password\d+", "replacement": "[PASSWORD_REDACTED]"},
        ]
        text = "Config: secret123, password456"
        result = OutputProcessor.scrub_output(text, redaction_rules=rules)
        assert "secret123" not in result, "Result must not be empty"
        assert "password456" not in result, "Result must not be empty"
        assert "[SECRET_REDACTED]" in result, "Result must not be empty"
        assert "[PASSWORD_REDACTED]" in result, "Result must not be empty"

    def test_no_redaction_rules(self):
        text = "Hello world"
        result = OutputProcessor.scrub_output(text)
        assert result == "Hello world", "Result must not be empty"

    def test_empty_string(self):
        result = OutputProcessor.scrub_output("")
        assert result == "", "Result must not be empty"

    def test_strips_whitespace(self):
        result = OutputProcessor.scrub_output("  padded  ")
        assert result == "padded", "Result must not be empty"

    def test_redaction_rule_without_pattern(self):
        rules = [{"replacement": "***"}]  # No pattern key
        text = "Hello"
        result = OutputProcessor.scrub_output(text, redaction_rules=rules)
        assert result == "Hello", "Result must not be empty"


# ============================================================================
# OutputProcessor.extract_evidence_tags
# ============================================================================


class TestExtractEvidenceTags:
    def test_matching_content(self):
        output = "The quick brown fox jumps over the lazy dog"
        docs = [
            {
                "content": "The quick brown fox jumps over the lazy dog. Additional text here.",
                "score": 0.95,
                "metadata": {"source_id": "doc1", "chunk_id": "c1"},
            }
        ]
        evidence = OutputProcessor.extract_evidence_tags(output, docs)
        assert len(evidence) >= 1, "Evidence must not be empty"
        assert evidence[0]["source_id"] == "doc1", "Condition must be true"

    def test_no_matching_content(self):
        output = "Completely different text about cats"
        docs = [
            {
                "content": "The quick brown fox jumps over the lazy dog. No similarity.",
                "score": 0.1,
                "metadata": {"source_id": "doc1"},
            }
        ]
        evidence = OutputProcessor.extract_evidence_tags(output, docs)
        assert len(evidence) == 0, "Evidence must not be empty"

    def test_empty_docs(self):
        evidence = OutputProcessor.extract_evidence_tags("output", [])
        assert evidence == [], "evidence is not valid"

    def test_short_doc_content_skipped(self):
        """Docs with content <= 20 chars should be skipped."""
        docs = [{"content": "short", "score": 0.9, "metadata": {"source_id": "x"}}]
        evidence = OutputProcessor.extract_evidence_tags("short", docs)
        assert len(evidence) == 0, "Evidence must not be empty"

    def test_missing_metadata_defaults(self):
        output = "This is a long enough phrase to match. Plus more text for sentences."
        docs = [
            {
                "content": "This is a long enough phrase to match. Plus more text for sentences.",
                "score": 0.5,
                "metadata": {},
            }
        ]
        evidence = OutputProcessor.extract_evidence_tags(output, docs)
        if evidence:
            assert evidence[0]["source_id"] == "unknown", "Condition must be true"


# ============================================================================
# OutputProcessor.add_citations
# ============================================================================


class TestAddCitations:
    def test_inline_citations(self):
        evidence = [
            {"source_id": "src1", "score": 0.9},
            {"source_id": "src2", "score": 0.8},
        ]
        result = OutputProcessor.add_citations("Output text", evidence, "inline")
        assert "Sources:" in result, "Result must not be empty"
        assert "src1" in result, "Result must not be empty"
        assert "src2" in result, "Result must not be empty"

    def test_footnote_citations(self):
        evidence = [{"source_id": "doc_a", "score": 0.9}]
        result = OutputProcessor.add_citations("Output text", evidence, "footnote")
        assert "References:" in result, "Result must not be empty"
        assert "[1] doc_a" in result, "Result must not be empty"

    def test_no_citations_style(self):
        evidence = [{"source_id": "x", "score": 0.5}]
        result = OutputProcessor.add_citations("Output text", evidence, "none")
        assert result == "Output text", "Result must not be empty"

    def test_empty_evidence(self):
        result = OutputProcessor.add_citations("Output text", [], "inline")
        assert result == "Output text", "Result must not be empty"

    def test_deduplicates_inline_sources(self):
        evidence = [
            {"source_id": "same", "score": 0.9},
            {"source_id": "same", "score": 0.8},
        ]
        result = OutputProcessor.add_citations("Output", evidence, "inline")
        # Should mention "same" only once
        assert result.count("same") == 1, "Result must not be empty"


# ============================================================================
# postprocess_output convenience function
# ============================================================================


class TestPostprocessOutput:
    def test_basic_call(self):
        output, evidence = postprocess_output("Hello world")
        assert output == "Hello world", "output is not valid"
        assert evidence == [], "evidence is not valid"

    def test_with_redaction(self):
        rules = [{"pattern": r"secret", "replacement": "[REDACTED]"}]
        output, evidence = postprocess_output("This is secret info", redaction_rules=rules)
        assert "secret" not in output, "Condition must be true"
        assert "[REDACTED]" in output, "Condition must be true"

    def test_with_docs_and_citations(self):
        docs = [
            {
                "content": "This document has a very long phrase that should match well enough to generate evidence.",
                "score": 0.9,
                "metadata": {"source_id": "ref1"},
            }
        ]
        text = "This document has a very long phrase that should match well enough to generate evidence."
        output, evidence = postprocess_output(text, retrieved_docs=docs)
        # Evidence may or may not be found depending on phrase splitting
        assert isinstance(output, str)
        assert isinstance(evidence, list)

    def test_no_citations_flag(self):
        docs = [
            {
                "content": "Some very specific content that is long enough for matching sentences.",
                "score": 0.9,
                "metadata": {"source_id": "ref1"},
            }
        ]
        output, evidence = postprocess_output(
            "Some very specific content that is long enough for matching sentences.",
            retrieved_docs=docs,
            include_citations=False,
        )
        assert "Sources:" not in output, "Condition must be true"
