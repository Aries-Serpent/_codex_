"""
Structural patterns test suite.

Comprehensive tests for structural integrity patterns and validation.
"""

from scripts.space_traversal.detectors import structure_integrity


class TestStructuralPatterns:
    """Test structural pattern detection."""

    def test_known_shadow_risks(self):
        """Test that known shadow risks are defined."""
        assert hasattr(structure_integrity, "KNOWN_SHADOW_RISKS")
        assert "torch" in structure_integrity.KNOWN_SHADOW_RISKS, "Condition must be true"
        assert "numpy" in structure_integrity.KNOWN_SHADOW_RISKS, "Condition must be true"

    def test_related_files(self):
        """Test that related files are defined."""
        assert hasattr(structure_integrity, "RELATED_FILES")
        assert len(structure_integrity.RELATED_FILES) > 0, "Collection must not be empty"

    def test_detect_function_exists(self):
        """Test that detect function exists."""
        assert hasattr(structure_integrity, "detect")
        assert callable(structure_integrity.detect), "Condition must be true"

    def test_detector_output_contract(self):
        """Test detector output follows contract."""
        result = structure_integrity.detect({"files": []})

        assert "id" in result, "Result must not be empty"
        assert "evidence_files" in result, "Result must not be empty"
        assert "found_patterns" in result, "Result must not be empty"
        assert "required_patterns" in result, "Result must not be empty"
        assert "meta" in result, "Result must not be empty"

    def test_bounded_evidence_collection(self):
        """Test that evidence collection is bounded."""
        # Create many files
        files = [{"path": f"module/file{i}.py"} for i in range(100)]
        files.extend([{"path": f"src/module/file{i}.py"} for i in range(100)])

        file_index = {"files": files}
        result = structure_integrity.detect(file_index, evidence_limit=10)

        # Evidence should be bounded
        assert len(result["evidence_files"]) <= 20, "Collection must not be empty"
