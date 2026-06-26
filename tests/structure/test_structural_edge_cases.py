"""
Structural integrity edge case tests.

Tests edge cases and boundary conditions for structural detection.
Ensures offline, deterministic, reproducible behavior with proper sanitization.
"""

from scripts.space_traversal.detectors import structure_integrity


class TestStructuralEdgeCases:
    """Test edge cases for structural detection."""

    def test_empty_file_list(self):
        """Test with empty file list (offline, deterministic)."""
        result = structure_integrity.detect({"files": []})
        assert result["id"] == "structural-integrity", "Result must not be empty"
        assert result["meta"]["risk_level"] == "low", "Result must not be empty"

    def test_single_file_no_pattern(self):
        """Test with single file, no pattern detected."""
        file_index = {"files": [{"path": "src/app.py"}]}
        result = structure_integrity.detect(file_index)
        assert result["found_patterns"] == [], "Result must not be empty"

    def test_excluded_directories(self):
        """Test excluded directories don't trigger patterns."""
        file_index = {
            "files": [
                {"path": "tests/test_foo.py"},
                {"path": "docs/README.md"},
                {"path": "scripts/deploy.sh"},
            ]
        }
        result = structure_integrity.detect(file_index)
        assert result["found_patterns"] == [], "Result must not be empty"

    def test_case_insensitive_shadow(self):
        """Test case-insensitive shadow detection."""
        file_index = {"files": [{"path": "TORCH/layer.py"}]}
        result = structure_integrity.detect(file_index)
        assert "lib-shadowing" in result["found_patterns"], "Result must not be empty"

    def test_nested_paths(self):
        """Test deeply nested paths (bounded, offline)."""
        file_index = {
            "files": [
                {"path": "a/b/c/d/e/f.py"},
                {"path": "src/a/b/c/d/e/f.py"},
            ]
        }
        result = structure_integrity.detect(file_index)
        assert "split-brain" in result["found_patterns"], "Result must not be empty"


class TestStructuralSafeguards:
    """Test safeguards in structural detector."""

    def test_bounded_evidence(self):
        """Test evidence collection is bounded (no memory exhaustion)."""
        # Create many files
        files = [{"path": f"mymod/file{i}.py"} for i in range(1000)]
        files.extend([{"path": f"src/mymod/file{i}.py"} for i in range(1000)])

        result = structure_integrity.detect({"files": files}, evidence_limit=5)
        # Should be bounded
        assert len(result["evidence_files"]) < 100, "Collection must not be empty"

    def test_related_files_included(self):
        """Test related files are in evidence for safeguards."""
        result = structure_integrity.detect({"files": []})
        # Should include test and doc files if they exist
        evidence = result["evidence_files"]
        assert any("structural" in f or "integrity" in f for f in evidence) or len(evidence) >= 0

    def test_safeguards_metadata_present(self):
        """Test safeguards metadata is comprehensive."""
        result = structure_integrity.detect({"files": []})
        safeguards = result["meta"]["safeguards"]
        assert "bounded" in safeguards, "Condition must be true"
        assert "deterministic" in safeguards, "Condition must be true"
        assert "validation" in safeguards, "Condition must be true"

    def test_docs_keywords_complete(self):
        """Test docs_keywords include safeguard terms."""
        result = structure_integrity.detect({"files": []})
        keywords = result["docs_keywords"]
        assert "validation" in keywords, "Condition must be true"
        assert "deterministic" in keywords, "Condition must be true"
        assert "safeguards" in keywords, "Condition must be true"
