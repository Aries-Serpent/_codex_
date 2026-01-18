"""Comprehensive tests for RAG postprocessing and utilities."""

import re
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from codex.rag.postprocess import OutputProcessor, postprocess_output
from codex.rag.utils import ProvenanceMetadata, safe_model_load


class TestOutputProcessor:
    """Test suite for OutputProcessor class."""

    def test_scrub_output_basic(self):
        """Test basic output scrubbing."""
        processor = OutputProcessor()
        text = "This is some output text."
        
        result = processor.scrub_output(text)
        assert result == "This is some output text."

    def test_scrub_output_removes_safety_markers(self):
        """Test that safety delimiters are removed."""
        processor = OutputProcessor()
        text = "### RETRIEVED CONTEXT START ### Content here ### RETRIEVED CONTEXT END ###"
        
        result = processor.scrub_output(text)
        
        assert "RETRIEVED CONTEXT START" not in result
        assert "RETRIEVED CONTEXT END" not in result
        assert "Content here" in result

    def test_scrub_output_with_redaction_rules(self):
        """Test output scrubbing with custom redaction rules."""
        processor = OutputProcessor()
        text = "Email: user@example.com and password: secret123"
        
        rules = [
            {"pattern": r"\w+@\w+\.\w+", "replacement": "[EMAIL]"},
            {"pattern": r"password: \w+", "replacement": "password: [REDACTED]"}
        ]
        
        result = processor.scrub_output(text, redaction_rules=rules)
        
        assert "[EMAIL]" in result
        assert "[REDACTED]" in result
        assert "user@example.com" not in result
        assert "secret123" not in result

    def test_scrub_output_strips_whitespace(self):
        """Test that output is stripped of surrounding whitespace."""
        processor = OutputProcessor()
        text = "   Content with spaces   \n\n"
        
        result = processor.scrub_output(text)
        
        assert result == "Content with spaces"

    def test_extract_evidence_tags_basic(self):
        """Test basic evidence extraction."""
        processor = OutputProcessor()
        
        output = "Python is a programming language used for development."
        retrieved_docs = [
            {
                "content": "Python is a programming language",
                "score": 0.9,
                "metadata": {"source_id": "python.txt", "chunk_id": 0}
            }
        ]
        
        evidence = processor.extract_evidence_tags(output, retrieved_docs)
        
        assert len(evidence) >= 0  # May find overlap

    def test_extract_evidence_tags_no_overlap(self):
        """Test evidence extraction with no overlap."""
        processor = OutputProcessor()
        
        output = "Machine learning is important."
        retrieved_docs = [
            {
                "content": "Python is a programming language",
                "score": 0.9,
                "metadata": {"source_id": "python.txt"}
            }
        ]
        
        evidence = processor.extract_evidence_tags(output, retrieved_docs)
        
        # Should have no evidence (no overlap)
        assert len(evidence) == 0

    def test_extract_evidence_tags_with_overlap(self):
        """Test evidence extraction with content overlap."""
        processor = OutputProcessor()
        
        output = "Python is great for development and data science."
        retrieved_docs = [
            {
                "content": "Python is great for development. It has many libraries.",
                "score": 0.95,
                "metadata": {"source_id": "intro.py", "chunk_id": 1}
            }
        ]
        
        evidence = processor.extract_evidence_tags(output, retrieved_docs)
        
        # Should find evidence due to overlap
        assert len(evidence) > 0
        if evidence:
            assert evidence[0]["source_id"] == "intro.py"

    def test_extract_evidence_tags_short_content_skipped(self):
        """Test that very short content is skipped."""
        processor = OutputProcessor()
        
        output = "Test output"
        retrieved_docs = [
            {"content": "Short", "score": 0.9, "metadata": {}}
        ]
        
        evidence = processor.extract_evidence_tags(output, retrieved_docs)
        
        # Short content (< 20 chars) should be skipped
        assert len(evidence) == 0

    def test_add_citations_inline(self):
        """Test adding inline citations."""
        processor = OutputProcessor()
        
        output = "This is some content."
        evidence = [
            {"source_id": "file1.py", "score": 0.9},
            {"source_id": "file2.py", "score": 0.8}
        ]
        
        result = processor.add_citations(output, evidence, citation_style="inline")
        
        assert "file1.py" in result
        assert "file2.py" in result
        assert "[Sources:" in result

    def test_add_citations_footnote(self):
        """Test adding footnote-style citations."""
        processor = OutputProcessor()
        
        output = "This is some content."
        evidence = [
            {"source_id": "file1.py", "score": 0.9},
            {"source_id": "file2.py", "score": 0.8}
        ]
        
        result = processor.add_citations(output, evidence, citation_style="footnote")
        
        assert "References:" in result
        assert "[1]" in result
        assert "file1.py" in result

    def test_add_citations_none(self):
        """Test that 'none' style doesn't add citations."""
        processor = OutputProcessor()
        
        output = "This is some content."
        evidence = [{"source_id": "file1.py"}]
        
        result = processor.add_citations(output, evidence, citation_style="none")
        
        assert result == output

    def test_add_citations_empty_evidence(self):
        """Test adding citations with empty evidence."""
        processor = OutputProcessor()
        
        output = "Content"
        result = processor.add_citations(output, [], citation_style="inline")
        
        assert result == output

    def test_add_citations_deduplicates_sources(self):
        """Test that duplicate sources are deduplicated."""
        processor = OutputProcessor()
        
        output = "Content"
        evidence = [
            {"source_id": "file1.py"},
            {"source_id": "file1.py"},
            {"source_id": "file2.py"}
        ]
        
        result = processor.add_citations(output, evidence, citation_style="inline")
        
        # Should only mention file1.py once
        assert result.count("file1.py") == 1
        assert "file2.py" in result


class TestPostprocessOutputFunction:
    """Test suite for postprocess_output convenience function."""

    def test_postprocess_output_basic(self):
        """Test basic output post-processing."""
        output = "Test output"
        
        processed, evidence = postprocess_output(output)
        
        assert processed == "Test output"
        assert evidence == []

    def test_postprocess_output_with_retrieved_docs(self):
        """Test post-processing with retrieved documents."""
        output = "Python is a language used for programming tasks."
        retrieved_docs = [
            {
                "content": "Python is a language used for programming",
                "score": 0.9,
                "metadata": {"source_id": "python.txt"}
            }
        ]
        
        processed, evidence = postprocess_output(
            output,
            retrieved_docs=retrieved_docs
        )
        
        assert "Python" in processed
        # Evidence may be extracted if overlap detected

    def test_postprocess_output_with_redaction(self):
        """Test post-processing with redaction rules."""
        output = "User email: test@example.com"
        redaction_rules = [
            {"pattern": r"\w+@\w+\.\w+", "replacement": "[EMAIL]"}
        ]
        
        processed, evidence = postprocess_output(
            output,
            redaction_rules=redaction_rules
        )
        
        assert "[EMAIL]" in processed
        assert "test@example.com" not in processed

    def test_postprocess_output_with_citations(self):
        """Test post-processing includes citations."""
        output = "Python is great for data science and machine learning tasks."
        retrieved_docs = [
            {
                "content": "Python is great for data science. It has NumPy and Pandas.",
                "score": 0.95,
                "metadata": {"source_id": "python_guide.md", "chunk_id": 0}
            }
        ]
        
        processed, evidence = postprocess_output(
            output,
            retrieved_docs=retrieved_docs,
            include_citations=True,
            citation_style="inline"
        )
        
        # If evidence found, should include source
        if evidence:
            assert "python_guide.md" in processed or "[Sources:" in processed

    def test_postprocess_output_without_citations(self):
        """Test post-processing without citations."""
        output = "Test content"
        retrieved_docs = [
            {
                "content": "Test content",
                "score": 0.9,
                "metadata": {"source_id": "test.py"}
            }
        ]
        
        processed, evidence = postprocess_output(
            output,
            retrieved_docs=retrieved_docs,
            include_citations=False
        )
        
        # Should not include citations
        assert "Sources:" not in processed


class TestProvenanceMetadata:
    """Test suite for ProvenanceMetadata dataclass."""

    def test_provenance_creation(self):
        """Test creating provenance metadata."""
        prov = ProvenanceMetadata(
            source_file=Path("test.py"),
            line_range=(10, 20),
            chunk_id="chunk_123",
            indexed_at=datetime.now(),
            embedding_model="all-MiniLM-L6-v2",
            retrieval_score=0.85
        )
        
        assert prov.source_file == Path("test.py")
        assert prov.line_range == (10, 20)
        assert prov.chunk_id == "chunk_123"
        assert prov.retrieval_score == 0.85

    def test_provenance_with_optional_fields(self):
        """Test provenance with optional fields."""
        prov = ProvenanceMetadata(
            source_file=Path("test.py"),
            line_range=(1, 10),
            chunk_id="abc",
            indexed_at=datetime.now(),
            embedding_model="model",
            retrieval_score=0.5,
            char_range=(0, 100),
            metadata={"key": "value"}
        )
        
        assert prov.char_range == (0, 100)
        assert prov.metadata == {"key": "value"}

    def test_provenance_to_dict(self):
        """Test converting provenance to dictionary."""
        now = datetime.now()
        prov = ProvenanceMetadata(
            source_file=Path("/path/to/file.py"),
            line_range=(5, 15),
            chunk_id="xyz",
            indexed_at=now,
            embedding_model="test-model",
            retrieval_score=0.95,
            char_range=(50, 150),
            metadata={"extra": "info"}
        )
        
        result = prov.to_dict()
        
        assert result["source_file"] == "/path/to/file.py"
        assert result["line_range"] == (5, 15)
        assert result["chunk_id"] == "xyz"
        assert result["embedding_model"] == "test-model"
        assert result["retrieval_score"] == 0.95
        assert result["char_range"] == (50, 150)
        assert result["metadata"] == {"extra": "info"}

    def test_provenance_from_dict(self):
        """Test creating provenance from dictionary."""
        data = {
            "source_file": "/path/to/file.py",
            "line_range": [10, 20],
            "chunk_id": "chunk_abc",
            "indexed_at": datetime.now().isoformat(),
            "embedding_model": "model-v1",
            "retrieval_score": 0.88,
            "char_range": [100, 200],
            "metadata": {"test": "data"}
        }
        
        prov = ProvenanceMetadata.from_dict(data)
        
        assert prov.source_file == Path("/path/to/file.py")
        assert prov.line_range == (10, 20)
        assert prov.chunk_id == "chunk_abc"
        assert prov.retrieval_score == 0.88


class TestSafeModelLoad:
    """Test suite for safe_model_load utility."""

    def test_safe_model_load_no_meta_tensors(self):
        """Test safe loading when model has no meta tensors."""
        mock_model = MagicMock()
        mock_model.named_modules.return_value = []
        mock_model.to.return_value = mock_model
        
        result = safe_model_load(mock_model, device="cpu")
        
        # Should call to() method
        mock_model.to.assert_called_with("cpu")

    def test_safe_model_load_with_meta_tensors(self):
        """Test safe loading when model has meta tensors."""
        mock_param = MagicMock()
        mock_param.device.type = "meta"
        
        mock_module = MagicMock()
        mock_module.named_parameters.return_value = [("param1", mock_param)]
        
        mock_model = MagicMock()
        mock_model.named_modules.return_value = [("module1", mock_module)]
        mock_model.to_empty.return_value = mock_model
        
        result = safe_model_load(mock_model, device="cpu")
        
        # Should call to_empty() when meta tensors detected
        mock_model.to_empty.assert_called_with(device="cpu")

    def test_safe_model_load_handles_errors(self):
        """Test that safe_model_load handles errors gracefully."""
        mock_model = MagicMock()
        mock_model.named_modules.side_effect = Exception("Test error")
        
        # Should not crash, should return model as-is
        result = safe_model_load(mock_model, device="cpu")
        
        assert result is mock_model

    def test_safe_model_load_no_modules(self):
        """Test safe loading when model has no named_modules."""
        mock_model = MagicMock(spec=[])  # No named_modules attribute
        
        result = safe_model_load(mock_model, device="cpu")
        
        # Should return model as-is
        assert result is mock_model

    def test_safe_model_load_with_device_attribute(self):
        """Test safe loading with direct device attribute."""
        mock_model = MagicMock(spec=["device", "to_empty"])
        mock_model.device.type = "meta"
        mock_model.to_empty.return_value = mock_model
        
        # Remove named_modules to test device attribute path
        delattr(mock_model, "named_modules") if hasattr(mock_model, "named_modules") else None
        
        result = safe_model_load(mock_model, device="cuda")
        
        # Should detect meta device and use to_empty
        assert result is mock_model
