"""
Structural validation tests for architecture patterns.

Tests structural integrity patterns, split-brain detection, and namespace validation.
Provides deterministic, reproducible test results with bounded operations.
"""
from scripts.space_traversal.detectors import structure_integrity


class TestStructuralValidation:
    """Test structural validation patterns."""

    def test_empty_file_index(self):
        """Test detection with empty file index."""
        result = structure_integrity.detect({"files": []})
        
        assert result["id"] == "structural-integrity"
        assert result["found_patterns"] == []
        assert result["meta"]["risk_level"] == "low"

    def test_single_file(self):
        """Test detection with single file."""
        file_index = {"files": [{"path": "src/main.py"}]}
        result = structure_integrity.detect(file_index)
        
        assert result["id"] == "structural-integrity"
        assert "split_dirs" in result["meta"]

    def test_deterministic_output(self):
        """Test that detection is deterministic."""
        file_index = {
            "files": [
                {"path": "module/foo.py"},
                {"path": "src/module/foo.py"},
            ]
        }
        
        results = [structure_integrity.detect(file_index) for _ in range(3)]
        
        for i in range(1, len(results)):
            assert results[i]["found_patterns"] == results[0]["found_patterns"]
            assert results[i]["evidence_files"] == results[0]["evidence_files"]

    def test_safeguards_present(self):
        """Test that safeguards metadata is present."""
        result = structure_integrity.detect({"files": []})
        
        assert "safeguards" in result["meta"]
        assert "bounded" in result["meta"]["safeguards"]
        assert "deterministic" in result["meta"]["safeguards"]

    def test_docs_keywords_present(self):
        """Test that docs_keywords are present."""
        result = structure_integrity.detect({"files": []})
        
        assert "docs_keywords" in result
        assert "structural-integrity" in result["docs_keywords"]
        assert "validation" in result["docs_keywords"]
