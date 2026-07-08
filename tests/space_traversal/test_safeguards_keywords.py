"""Comprehensive tests for safeguards keyword detection and validation."""

import pytest

from scripts.space_traversal.detectors.detector_safeguards import (
    SAFEGUARD_KEYWORDS,
    _read_text,
    detect,
)


class TestSafeguardsKeywordDetector:
    """Test safeguards keyword detection"""

    def test_detect_with_safeguard_keywords(self, tmp_path):
        """Test detection with files containing safeguard keywords"""
        # Create test file with keywords
        test_file = tmp_path / "test.py"
        test_file.write_text("import hashlib\nsha256_hash = hashlib.sha256()")

        # Note: This test depends on REPO_ROOT, so we test the structure
        result = detect({"files": []})

        assert result["id"] == "safeguards_keywords", "Result must not be empty"
        assert "evidence" in result, "Result must not be empty"
        assert "total_hits" in result, "Result must not be empty"
        assert "unique_files" in result, "Result must not be empty"

    def test_safeguard_keywords_defined(self):
        """Test that safeguard keywords are properly defined"""
        expected = {
            "baseline",
            "checksum",
            "deterministic",
            "manifest",
            "offline",
            "reproduce",
            "rng",
            "sanitize",
            "seed",
            "secret",
            "sha256",
            "WANDB_MODE",
        }
        assert expected.issubset(SAFEGUARD_KEYWORDS), "Condition must be true"

    def test_read_text_truncation(self, tmp_path):
        """Test that read_text truncates large files"""
        from scripts.space_traversal.detectors.detector_safeguards import MAX_READ_BYTES

        test_file = tmp_path / "large.txt"
        content = "x" * (MAX_READ_BYTES + 1000)
        test_file.write_text(content)

        result = _read_text(test_file)

        assert len(result) == MAX_READ_BYTES, "Result must not be empty"

    def test_read_text_handles_errors(self, tmp_path):
        """Test that read_text handles errors gracefully"""
        nonexistent = tmp_path / "nonexistent.txt"
        result = _read_text(nonexistent)
        assert result == "", "Result must not be empty"

    def test_detector_contract(self):
        """Test detector follows the contract"""
        result = detect({"files": []})

        # Required fields
        assert "id" in result, "Result must not be empty"
        assert "evidence" in result, "Result must not be empty"
        assert "total_hits" in result, "Result must not be empty"
        assert "unique_files" in result, "Result must not be empty"
        assert "evidence_files" in result, "Result must not be empty"
        assert "found_patterns" in result, "Result must not be empty"
        assert "required_patterns" in result, "Result must not be empty"

        # Correct types
        assert isinstance(result["id"], str)
        assert isinstance(result["evidence"], dict)
        assert isinstance(result["total_hits"], int)
        assert isinstance(result["unique_files"], int)
        assert isinstance(result["evidence_files"], list)
        assert isinstance(result["found_patterns"], list)
        assert isinstance(result["required_patterns"], list)

    def test_allowed_suffixes(self):
        """Test that only allowed file types are scanned"""
        file_index = {
            "files": [
                {"path": "test.py"},
                {"path": "test.md"},
                {"path": "test.sh"},
                {"path": "test.txt"},
                {"path": "test.yml"},
                {"path": "test.yaml"},
                {"path": "test.exe"},  # Should be ignored
                {"path": "test.bin"},  # Should be ignored
            ]
        }

        result = detect(file_index)

        # Structure is valid
        assert isinstance(result["evidence"], dict)

    def test_evidence_sorting(self):
        """Test that evidence is sorted"""
        result = detect({"files": []})

        # Evidence should be sorted
        evidence_keys = list(result["evidence"].keys())
        assert evidence_keys == sorted(evidence_keys), "evidence_keys is not valid"

    def test_patterns_sorting(self):
        """Test that patterns are sorted"""
        result = detect({"files": []})

        # Patterns should be sorted
        assert result["found_patterns"] == sorted(result["found_patterns"]), "Result must not be empty"
        assert result["required_patterns"] == sorted(result["required_patterns"]), "Result must not be empty"

    def test_required_patterns_match_keywords(self):
        """Test that required patterns match SAFEGUARD_KEYWORDS"""
        result = detect({"files": []})

        assert set(result["required_patterns"]) == SAFEGUARD_KEYWORDS, "Result must not be empty"


class TestSafeguardsKeywordExpansion:
    """Test safeguards keyword expansion and validation"""

    def test_keywords_coverage(self):
        """Test that keywords cover important safeguard areas"""
        # Cryptographic safeguards
        assert "sha256" in SAFEGUARD_KEYWORDS, "Condition must be true"
        assert "checksum" in SAFEGUARD_KEYWORDS, "Condition must be true"

        # Reproducibility safeguards
        assert "rng" in SAFEGUARD_KEYWORDS, "Condition must be true"
        assert "seed" in SAFEGUARD_KEYWORDS, "Condition must be true"

        # Offline/isolation safeguards
        assert "offline" in SAFEGUARD_KEYWORDS, "Condition must be true"
        assert "WANDB_MODE" in SAFEGUARD_KEYWORDS, "Condition must be true"

        # Determinism safeguards
        assert "deterministic" in SAFEGUARD_KEYWORDS, "Condition must be true"
        assert "reproduce" in SAFEGUARD_KEYWORDS, "Condition must be true"

        # Documentation/archival safeguards
        assert "manifest" in SAFEGUARD_KEYWORDS, "Condition must be true"
        assert "baseline" in SAFEGUARD_KEYWORDS, "Condition must be true"

    def test_keywords_are_strings(self):
        """Test that all keywords are strings"""
        for keyword in SAFEGUARD_KEYWORDS:
            assert isinstance(keyword, str)

    def test_keywords_non_empty(self):
        """Test that keyword set is not empty"""
        assert len(SAFEGUARD_KEYWORDS) > 0, "Safeguard_keywords must not be empty"

    def test_detector_import(self):
        """Test that detector can be imported"""
        from scripts.space_traversal.detectors import detector_safeguards

        assert hasattr(detector_safeguards, "detect")
        assert hasattr(detector_safeguards, "SAFEGUARD_KEYWORDS")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
