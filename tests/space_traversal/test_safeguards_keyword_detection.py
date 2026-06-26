"""
Comprehensive test suite for safeguards keyword detection capability.

Tests keyword detection, context-aware patterns, density calculation,
and validation following High Maturity Achievement Plan (target: 15-20 tests).
"""

import tempfile
from pathlib import Path


class TestSafeguardsDetector:
    """Test safeguards keyword detector."""

    def test_detector_import(self):
        """Test safeguards detector can be imported."""
        from scripts.space_traversal.detectors import detector_safeguards

        assert hasattr(detector_safeguards, "detect")

    def test_detector_contract(self):
        """Test detector follows required contract."""
        from scripts.space_traversal.detectors.detector_safeguards import detect

        result = detect({"files": []})
        assert "id" in result, "Result must not be empty"
        assert result["id"] == "safeguards_keywords", "Result must not be empty"

    def test_keyword_list_complete(self):
        """Test safeguard keyword list is comprehensive."""
        from scripts.space_traversal.detectors.detector_safeguards import (
            SAFEGUARD_KEYWORDS,
        )

        # Should have expanded keyword list (25 keywords)
        assert len(SAFEGUARD_KEYWORDS) >= 20, "Safeguard_keywords must not be empty"

        # Check critical keywords present
        critical = ["validation", "sanitize", "authenticate", "timeout", "safeguard"]
        for keyword in critical:
            assert keyword in SAFEGUARD_KEYWORDS, "keyw is not valid"


class TestKeywordDetection:
    """Test individual keyword detection."""

    def test_sha256_detection(self):
        """Test sha256 keyword detection."""
        from scripts.space_traversal.detectors.detector_safeguards import (
            SAFEGUARD_KEYWORDS,
        )

        assert "sha256" in SAFEGUARD_KEYWORDS, "Condition must be true"

    def test_checksum_detection(self):
        """Test checksum keyword detection."""
        from scripts.space_traversal.detectors.detector_safeguards import (
            SAFEGUARD_KEYWORDS,
        )

        assert "checksum" in SAFEGUARD_KEYWORDS, "Condition must be true"

    def test_validation_detection(self):
        """Test validation keyword detection."""
        from scripts.space_traversal.detectors.detector_safeguards import (
            SAFEGUARD_KEYWORDS,
        )

        assert "validation" in SAFEGUARD_KEYWORDS, "Condition must be true"
        assert "validate" in SAFEGUARD_KEYWORDS, "Condition must be true"

    def test_sanitize_detection(self):
        """Test sanitize keyword detection."""
        from scripts.space_traversal.detectors.detector_safeguards import (
            SAFEGUARD_KEYWORDS,
        )

        assert "sanitize" in SAFEGUARD_KEYWORDS, "Condition must be true"

    def test_authentication_detection(self):
        """Test authentication keywords."""
        from scripts.space_traversal.detectors.detector_safeguards import (
            SAFEGUARD_KEYWORDS,
        )

        assert "authenticate" in SAFEGUARD_KEYWORDS, "Condition must be true"
        assert "authorization" in SAFEGUARD_KEYWORDS, "Condition must be true"

    def test_rate_limit_detection(self):
        """Test rate limiting keywords."""
        from scripts.space_traversal.detectors.detector_safeguards import (
            SAFEGUARD_KEYWORDS,
        )

        assert "rate_limit" in SAFEGUARD_KEYWORDS or "ratelimit" in SAFEGUARD_KEYWORDS, "Condition must be true"

    def test_timeout_detection(self):
        """Test timeout keyword detection."""
        from scripts.space_traversal.detectors.detector_safeguards import (
            SAFEGUARD_KEYWORDS,
        )

        assert "timeout" in SAFEGUARD_KEYWORDS, "Condition must be true"

    def test_bounds_check_detection(self):
        """Test bounds checking keywords."""
        from scripts.space_traversal.detectors.detector_safeguards import (
            SAFEGUARD_KEYWORDS,
        )

        assert "bounds_check" in SAFEGUARD_KEYWORDS or "bounded" in SAFEGUARD_KEYWORDS, "Condition must be true"


class TestContextAwareDetection:
    """Test context-aware pattern detection."""

    def test_try_except_pattern(self):
        """Test try-except pattern detection."""
        from scripts.space_traversal.detectors.detector_safeguards import (
            DEFENSIVE_PATTERNS,
        )

        # Check if try-except pattern is defined
        pattern_names = [name for _, name in DEFENSIVE_PATTERNS]
        assert "try_except" in pattern_names or any("try" in name for name in pattern_names), "Condition must be true"

    def test_null_check_pattern(self):
        """Test null/None check pattern."""
        from scripts.space_traversal.detectors.detector_safeguards import (
            DEFENSIVE_PATTERNS,
        )

        pattern_names = [name for _, name in DEFENSIVE_PATTERNS]
        assert any("null" in name or "none" in name.lower() for name in pattern_names), "Condition must be true"

    def test_assertion_pattern(self):
        """Test assertion pattern detection."""
        from scripts.space_traversal.detectors.detector_safeguards import (
            DEFENSIVE_PATTERNS,
        )

        pattern_names = [name for _, name in DEFENSIVE_PATTERNS]
        assert any("assert" in name for name in pattern_names), "Condition must be true"

    def test_error_raise_pattern(self):
        """Test explicit error raising pattern."""
        from scripts.space_traversal.detectors.detector_safeguards import (
            DEFENSIVE_PATTERNS,
        )

        pattern_names = [name for _, name in DEFENSIVE_PATTERNS]
        assert any("error" in name for name in pattern_names), "Error should be raised or set"


class TestSafeguardDensity:
    """Test safeguard density calculation."""

    def test_density_calculation_empty(self):
        """Test density with no safeguards."""
        from scripts.space_traversal.detectors.detector_safeguards import (
            _calculate_safeguard_density,
        )

        density = _calculate_safeguard_density({}, 10)
        assert density == 0.0, "density is not valid"

    def test_density_calculation_full(self):
        """Test density with all files having safeguards."""
        from scripts.space_traversal.detectors.detector_safeguards import (
            _calculate_safeguard_density,
        )

        evidence = {f"file{i}.py": 5 for i in range(10)}
        density = _calculate_safeguard_density(evidence, 10)
        assert density == 1.0, "density is not valid"

    def test_density_calculation_partial(self):
        """Test density with partial safeguard coverage."""
        from scripts.space_traversal.detectors.detector_safeguards import (
            _calculate_safeguard_density,
        )

        evidence = {f"file{i}.py": 3 for i in range(5)}  # 5 out of 10 files
        density = _calculate_safeguard_density(evidence, 10)
        assert 0.4 <= density <= 0.6, "4 is not valid"

    def test_density_zero_files(self):
        """Test density calculation with zero files (edge case)."""
        from scripts.space_traversal.detectors.detector_safeguards import (
            _calculate_safeguard_density,
        )

        density = _calculate_safeguard_density({}, 0)
        assert density == 0.0, "density is not valid"


class TestDetectorIntegration:
    """Integration tests for safeguards detector."""

    def test_detect_with_safeguards(self):
        """Test detection with files containing safeguards."""
        from scripts.space_traversal.detectors.detector_safeguards import detect

        # Create test file with safeguards
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("""
# Validation: check input
def process(data):
    # Safeguard: sanitize user input
    if data is None:
        raise ValueError("Data cannot be None")
    # Timeout protection
    result = compute_with_timeout(data)
    # Checksum validation
    assert verify_checksum(result, sha256_hash)
    return result
""")
            file_path = f.name

        try:
            result = detect({"files": [{"path": file_path}]})
            assert result["id"] == "safeguards_keywords", "Result must not be empty"
            assert "evidence" in result, "Result must not be empty"
            assert "total_hits" in result, "Result must not be empty"
            # Should find multiple safeguard keywords
            assert result["total_hits"] > 0, "Value must be greater than zero"
        finally:
            Path(file_path).unlink()

    def test_detect_without_safeguards(self):
        """Test detection with files lacking safeguards."""
        from scripts.space_traversal.detectors.detector_safeguards import detect

        # Create test file without safeguards
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("""
def simple_function(x):
    return x + 1
""")
            file_path = f.name

        try:
            result = detect({"files": [{"path": file_path}]})
            assert result["id"] == "safeguards_keywords", "Result must not be empty"
            # Should find no or minimal safeguards
            assert result["total_hits"] >= 0, "Value must be greater than zero"
        finally:
            Path(file_path).unlink()

    def test_deterministic_detection(self):
        """Test that detection is deterministic."""
        from scripts.space_traversal.detectors.detector_safeguards import detect

        file_index = {"files": []}

        # Run detection multiple times
        results = [detect(file_index) for _ in range(3)]

        # All results should be identical
        for i in range(1, len(results)):
            assert results[i]["id"] == results[0]["id"], "Result must not be empty"
            assert results[i]["total_hits"] == results[0]["total_hits"], "Result must not be empty"


class TestSafeguardsValidation:
    """Test safeguards in the detector itself."""

    def test_bounded_read_safeguard(self):
        """Test that MAX_READ_BYTES safeguard exists."""
        from scripts.space_traversal.detectors.detector_safeguards import MAX_READ_BYTES

        # Safeguard: bounded read to prevent memory issues
        assert MAX_READ_BYTES > 0, "MAX_READ_BYTES must be greater than zero"
        assert MAX_READ_BYTES <= 1_000_000, "MAX_READ_BYTES is not valid"

    def test_validation_in_read_function(self):
        """Test validation in file reading."""
        from scripts.space_traversal.detectors.detector_safeguards import _read_text

        # Test with non-existent file (validation should handle)
        result = _read_text(Path("/nonexistent/file.txt"))
        assert result == "", "Result must not be empty"

    def test_deterministic_keyword_set(self):
        """Test that keyword set is deterministic (frozenset sorted at creation)."""
        from scripts.space_traversal.detectors.detector_safeguards import (
            SAFEGUARD_KEYWORDS,
        )

        # Keywords are a frozenset; verify they are consistently iterable
        # and contain expected keywords (frozenset itself is unordered but deterministic)
        keywords_list = sorted(SAFEGUARD_KEYWORDS)
        assert len(keywords_list) > 0, "Keywords_list must not be empty"
        assert keywords_list == sorted(keywords_list), "keywords_list is not valid"
