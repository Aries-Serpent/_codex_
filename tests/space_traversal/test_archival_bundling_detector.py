"""
Tests for archival_bundling detector (v1.4.0)
"""
import pytest
from scripts.space_traversal.detectors.archival_bundling import detect


def test_archival_bundling_detector_basic():
    """Test basic archival bundling detection."""
    file_index = {
        "files": [
            {"path": "scripts/archive/bundle.py", "ext": ".py"},
            {"path": "scripts/archive/validate_prefixes.py", "ext": ".py"},
            {"path": "audit_artifacts/manifest.json", "ext": ".json"},
        ]
    }
    
    result = detect(file_index)
    
    assert result["id"] == "archival-bundling"
    assert len(result["evidence_files"]) > 0
    assert "archive" in result["found_patterns"] or "manifest" in result["found_patterns"]
    assert result["required_patterns"] == ["archive", "bundle", "manifest"]
    assert result["meta"]["layer"] == "storage"


def test_archival_bundling_detector_no_evidence():
    """Test archival bundling detector with no evidence."""
    file_index = {"files": [{"path": "src/utils/helper.py", "ext": ".py"}]}
    
    result = detect(file_index)
    
    assert result["id"] == "archival-bundling"
    assert len(result["evidence_files"]) == 0
    assert len(result["found_patterns"]) == 0


def test_archival_bundling_detector_pointer_files():
    """Test archival bundling detector with pointer files."""
    file_index = {
        "files": [
            {"path": "bundles/archive_v1.pointer.json", "ext": ".json"},
            {"path": "bundles/bundle_v2.pointer.json", "ext": ".json"},
        ]
    }
    
    result = detect(file_index)
    
    assert result["id"] == "archival-bundling"
    assert "manifest" in result["found_patterns"]
    assert len(result["evidence_files"]) > 0


def test_archival_bundling_detector_validation():
    """Test archival bundling detector with validation scripts."""
    file_index = {
        "files": [
            {"path": "scripts/archive/validate_prefixes.py", "ext": ".py"},
            {"path": "scripts/archive/prefix_validation.py", "ext": ".py"},
        ]
    }
    
    result = detect(file_index)
    
    assert result["id"] == "archival-bundling"
    assert "archive" in result["found_patterns"]
    assert len(result["evidence_files"]) > 0


def test_archival_bundling_detector_sorted_output():
    """Test that detector returns sorted results."""
    file_index = {
        "files": [
            {"path": "z_archive.py", "ext": ".py"},
            {"path": "a_bundle.py", "ext": ".py"},
            {"path": "m_manifest.json", "ext": ".json"},
        ]
    }
    
    result = detect(file_index)
    
    # Check that evidence files are sorted
    assert result["evidence_files"] == sorted(result["evidence_files"])
    # Check that found patterns are sorted
    assert result["found_patterns"] == sorted(result["found_patterns"])
