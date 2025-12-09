"""
Tests for structural integrity detector.

Tests split-brain detection, library shadowing detection, and architectural validation.
"""
import pytest
from scripts.space_traversal.detectors import structure_integrity


def test_detect_no_issues():
    """Test detection with no structural issues."""
    file_index = {
        "files": [
            {"path": "src/mymodule/foo.py"},
            {"path": "src/mymodule/bar.py"},
            {"path": "tests/test_foo.py"},
            {"path": "docs/README.md"},
        ]
    }
    
    result = structure_integrity.detect(file_index)
    
    assert result["id"] == "structural-integrity"
    assert result["found_patterns"] == []
    assert result["required_patterns"] == ["split-brain", "lib-shadowing"]
    assert result["meta"]["risk_level"] == "low"
    assert result["meta"]["split_dirs"] == []
    assert result["meta"]["shadow_dirs"] == []


def test_detect_split_brain():
    """Test detection of split-brain architecture."""
    file_index = {
        "files": [
            {"path": "mymodule/foo.py"},
            {"path": "mymodule/bar.py"},
            {"path": "src/mymodule/foo.py"},
            {"path": "src/mymodule/bar.py"},
            {"path": "tests/test_foo.py"},
        ]
    }
    
    result = structure_integrity.detect(file_index)
    
    assert result["id"] == "structural-integrity"
    assert "split-brain" in result["found_patterns"]
    assert result["meta"]["risk_level"] == "high"
    assert "mymodule" in result["meta"]["split_dirs"]
    assert len(result["evidence_files"]) > 0
    # Should have both root and src samples
    assert any("mymodule/" in f for f in result["evidence_files"])
    assert any("src/mymodule/" in f for f in result["evidence_files"])


def test_detect_library_shadowing():
    """Test detection of library shadowing."""
    file_index = {
        "files": [
            {"path": "torch/model.py"},
            {"path": "torch/utils.py"},
            {"path": "numpy/array.py"},
            {"path": "src/myapp/main.py"},
        ]
    }
    
    result = structure_integrity.detect(file_index)
    
    assert result["id"] == "structural-integrity"
    assert "lib-shadowing" in result["found_patterns"]
    assert result["meta"]["risk_level"] == "high"
    assert "torch" in result["meta"]["shadow_dirs"]
    assert "numpy" in result["meta"]["shadow_dirs"]
    assert len(result["evidence_files"]) > 0


def test_detect_both_issues():
    """Test detection of both split-brain and shadowing."""
    file_index = {
        "files": [
            {"path": "mymodule/foo.py"},
            {"path": "src/mymodule/foo.py"},
            {"path": "torch/model.py"},
            {"path": "tests/test_foo.py"},
        ]
    }
    
    result = structure_integrity.detect(file_index)
    
    assert result["id"] == "structural-integrity"
    assert "split-brain" in result["found_patterns"]
    assert "lib-shadowing" in result["found_patterns"]
    assert result["meta"]["risk_level"] == "high"
    assert "mymodule" in result["meta"]["split_dirs"]
    assert "torch" in result["meta"]["shadow_dirs"]


def test_evidence_limit_respected():
    """Test that evidence file limit is respected."""
    # Create many files that would trigger split-brain
    files = []
    for i in range(50):
        files.append({"path": f"mymodule/file{i}.py"})
        files.append({"path": f"src/mymodule/file{i}.py"})
    
    file_index = {"files": files}
    evidence_limit = 5
    
    result = structure_integrity.detect(file_index, evidence_limit=evidence_limit)
    
    assert len(result["evidence_files"]) <= evidence_limit
    assert result["meta"]["evidence_limit"] == evidence_limit


def test_excluded_directories_ignored():
    """Test that standard directories are excluded from checks."""
    file_index = {
        "files": [
            {"path": ".git/config"},
            {"path": ".github/workflows/ci.yml"},
            {"path": "tests/test_foo.py"},
            {"path": "docs/README.md"},
            {"path": "scripts/deploy.sh"},
            {"path": "deploy/manifests.yaml"},
            {"path": "config/settings.yml"},
            {"path": "audit_artifacts/report.json"},
            {"path": "reports/summary.md"},
            {"path": ".copilot-space/workflow.yaml"},
        ]
    }
    
    result = structure_integrity.detect(file_index)
    
    # None of these should be flagged
    assert result["found_patterns"] == []
    assert result["meta"]["risk_level"] == "low"
    assert result["meta"]["split_dirs"] == []
    assert result["meta"]["shadow_dirs"] == []


def test_case_insensitive_shadowing():
    """Test that shadowing detection is case-insensitive."""
    file_index = {
        "files": [
            {"path": "Torch/model.py"},
            {"path": "NUMPY/array.py"},
            {"path": "MlFlOw/tracking.py"},
        ]
    }
    
    result = structure_integrity.detect(file_index)
    
    assert "lib-shadowing" in result["found_patterns"]
    # shadow_dirs should contain the actual case from filesystem
    assert "Torch" in result["meta"]["shadow_dirs"] or "torch" in result["meta"]["shadow_dirs"]


def test_multiple_split_brain_modules():
    """Test detection with multiple split-brain modules."""
    file_index = {
        "files": [
            {"path": "module_a/foo.py"},
            {"path": "src/module_a/foo.py"},
            {"path": "module_b/bar.py"},
            {"path": "src/module_b/bar.py"},
            {"path": "module_c/baz.py"},
            {"path": "src/module_c/baz.py"},
        ]
    }
    
    result = structure_integrity.detect(file_index)
    
    assert "split-brain" in result["found_patterns"]
    assert len(result["meta"]["split_dirs"]) == 3
    assert "module_a" in result["meta"]["split_dirs"]
    assert "module_b" in result["meta"]["split_dirs"]
    assert "module_c" in result["meta"]["split_dirs"]


def test_docs_keywords_present():
    """Test that required docs_keywords are present."""
    file_index = {"files": [{"path": "src/app/main.py"}]}
    
    result = structure_integrity.detect(file_index)
    
    assert "docs_keywords" in result
    expected_keywords = [
        "structural-integrity", "architecture", "split-brain", "shadowing",
        "namespace", "validation", "detection", "consistency", "safeguards"
    ]
    for keyword in expected_keywords:
        assert keyword in result["docs_keywords"]


def test_safeguards_metadata():
    """Test that safeguards metadata is present."""
    file_index = {"files": [{"path": "src/app/main.py"}]}
    
    result = structure_integrity.detect(file_index)
    
    assert "safeguards" in result["meta"]
    expected_safeguards = ["bounded", "validation", "deterministic", "error-handling"]
    for safeguard in expected_safeguards:
        assert safeguard in result["meta"]["safeguards"]


def test_deterministic_output():
    """Test that detector produces deterministic output."""
    file_index = {
        "files": [
            {"path": "torch/model.py"},
            {"path": "mymodule/foo.py"},
            {"path": "src/mymodule/foo.py"},
            {"path": "numpy/array.py"},
        ]
    }
    
    # Run detection multiple times
    results = [structure_integrity.detect(file_index) for _ in range(3)]
    
    # All results should be identical
    for i in range(1, len(results)):
        assert results[i]["found_patterns"] == results[0]["found_patterns"]
        assert results[i]["evidence_files"] == results[0]["evidence_files"]
        assert results[i]["meta"]["split_dirs"] == results[0]["meta"]["split_dirs"]
        assert results[i]["meta"]["shadow_dirs"] == results[0]["meta"]["shadow_dirs"]


def test_sorted_output():
    """Test that output lists are sorted for consistency."""
    file_index = {
        "files": [
            {"path": "z_module/foo.py"},
            {"path": "src/z_module/foo.py"},
            {"path": "a_module/bar.py"},
            {"path": "src/a_module/bar.py"},
            {"path": "torch/model.py"},
            {"path": "numpy/array.py"},
        ]
    }
    
    result = structure_integrity.detect(file_index)
    
    # found_patterns should be sorted
    assert result["found_patterns"] == sorted(result["found_patterns"])
    # split_dirs should be sorted
    assert result["meta"]["split_dirs"] == sorted(result["meta"]["split_dirs"])
    # shadow_dirs should be sorted
    assert result["meta"]["shadow_dirs"] == sorted(result["meta"]["shadow_dirs"])
    # evidence_files should be sorted
    assert result["evidence_files"] == sorted(result["evidence_files"])


def test_evidence_deduplication():
    """Test that evidence files are deduplicated."""
    # Create scenario where same file might be added multiple times
    file_index = {
        "files": [
            {"path": "mymodule/foo.py"},
            {"path": "mymodule/bar.py"},
            {"path": "src/mymodule/foo.py"},
            {"path": "src/mymodule/bar.py"},
        ]
    }
    
    result = structure_integrity.detect(file_index, evidence_limit=20)
    
    # Check no duplicates in evidence_files
    assert len(result["evidence_files"]) == len(set(result["evidence_files"]))


def test_empty_file_index():
    """Test detection with empty file index."""
    file_index = {"files": []}
    
    result = structure_integrity.detect(file_index)
    
    assert result["id"] == "structural-integrity"
    assert result["found_patterns"] == []
    assert result["meta"]["risk_level"] == "low"
    assert result["evidence_files"] == []
