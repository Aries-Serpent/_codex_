"""
Structural detector comprehensive tests.

Full coverage tests for structural integrity detection.
"""

from scripts.space_traversal.detectors import structure_integrity


def test_structural_split_brain_basic():
    """Test basic split-brain detection."""
    file_index = {
        "files": [
            {"path": "myapp/core.py"},
            {"path": "src/myapp/core.py"},
        ]
    }
    result = structure_integrity.detect(file_index)
    assert "split-brain" in result["found_patterns"], "Result must not be empty"


def test_structural_no_split_brain():
    """Test no false positive for split-brain."""
    file_index = {
        "files": [
            {"path": "src/myapp/core.py"},
            {"path": "src/myapp/utils.py"},
        ]
    }
    result = structure_integrity.detect(file_index)
    assert "split-brain" not in result["found_patterns"], "Result must not be empty"


def test_structural_lib_shadowing():
    """Test library shadowing detection."""
    file_index = {
        "files": [
            {"path": "torch/custom.py"},
            {"path": "src/app.py"},
        ]
    }
    result = structure_integrity.detect(file_index)
    assert "lib-shadowing" in result["found_patterns"], "Result must not be empty"


def test_structural_risk_level_high():
    """Test high risk level when issues found."""
    file_index = {
        "files": [
            {"path": "numpy/array.py"},
        ]
    }
    result = structure_integrity.detect(file_index)
    assert result["meta"]["risk_level"] == "high", "Result must not be empty"


def test_structural_risk_level_low():
    """Test low risk level when no issues."""
    file_index = {
        "files": [
            {"path": "src/app/main.py"},
        ]
    }
    result = structure_integrity.detect(file_index)
    assert result["meta"]["risk_level"] == "low", "Result must not be empty"


def test_structural_evidence_sorting():
    """Test evidence files are sorted."""
    file_index = {
        "files": [
            {"path": "z_module/a.py"},
            {"path": "src/z_module/a.py"},
            {"path": "a_module/z.py"},
            {"path": "src/a_module/z.py"},
        ]
    }
    result = structure_integrity.detect(file_index)
    assert result["evidence_files"] == sorted(result["evidence_files"]), "Result must not be empty"
