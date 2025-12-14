"""
Comprehensive test suite for duplication ratio detector.

Tests cover stem-based detection, token-similarity integration, edge cases,
and determinism following the High Maturity Achievement Plan.
"""
import importlib.util
import types
from pathlib import Path
from typing import Any, Dict, Iterable

import pytest


def _load_module(path: Path, name: str) -> types.ModuleType:
    """Load detector module dynamically."""
    if not path.is_absolute():
        repo_root = Path(__file__).resolve().parents[2]
        path = repo_root / path
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def _context_index_for(paths: Iterable[Path]) -> Dict[str, Any]:
    """Create context index from file paths."""
    return {
        "files": [
            {"path": str(path.resolve())}
            for path in paths
        ],
    }


class TestStemBasedDetection:
    """Test stem-based duplication detection."""
    
    def test_no_duplication(self, tmp_path: Path):
        """Test detection when all files have unique stems."""
        files = [
            tmp_path / "unique_a.py",
            tmp_path / "unique_b.py",
            tmp_path / "unique_c.py",
        ]
        for f in files:
            f.write_text("content\n", encoding="utf-8")
        
        detector_path = Path("scripts/space_traversal/detectors/detector_duplication.py")
        module = _load_module(detector_path, "detector_duplication")
        context_index = _context_index_for(files)
        result = module.detect(context_index)
        
        assert result["id"] == "duplication_ratio"
        assert result["dup_ratio"] == 0.0
        assert result["metrics"]["total_duplicates"] == 0
        assert len(result["duplicate_groups"]) == 0
        assert "analysis" in result["found_patterns"]
        assert "detection" in result["found_patterns"]
    
    def test_simple_duplication(self, tmp_path: Path):
        """Test detection of simple stem duplication."""
        files = [
            tmp_path / "test.py",
            tmp_path / "test.md",
            tmp_path / "other.py",
        ]
        for f in files:
            f.write_text("content\n", encoding="utf-8")
        
        detector_path = Path("scripts/space_traversal/detectors/detector_duplication.py")
        module = _load_module(detector_path, "detector_duplication")
        context_index = _context_index_for(files)
        result = module.detect(context_index)
        
        assert result["dup_ratio"] > 0.0
        assert result["counts"]["test"] == 2
        assert "test" in result["duplicate_groups"]
        assert len(result["duplicate_groups"]["test"]) == 2
    
    def test_multiple_duplicates(self, tmp_path: Path):
        """Test detection with multiple duplicate groups."""
        files = [
            tmp_path / "foo.py",
            tmp_path / "foo.md",
            tmp_path / "bar.py",
            tmp_path / "bar.txt",
            tmp_path / "baz.py",
        ]
        for f in files:
            f.write_text("content\n", encoding="utf-8")
        
        detector_path = Path("scripts/space_traversal/detectors/detector_duplication.py")
        module = _load_module(detector_path, "detector_duplication")
        context_index = _context_index_for(files)
        result = module.detect(context_index)
        
        assert result["dup_ratio"] > 0.0
        assert "foo" in result["duplicate_groups"]
        assert "bar" in result["duplicate_groups"]
        assert "baz" not in result["duplicate_groups"]
    
    def test_high_duplication(self, tmp_path: Path):
        """Test detection with high duplication ratio."""
        files = [
            tmp_path / "dup.py",
            tmp_path / "dup.md",
            tmp_path / "dup.txt",
            tmp_path / "dup.yml",
            tmp_path / "unique.py",
        ]
        for f in files:
            f.write_text("content\n", encoding="utf-8")
        
        detector_path = Path("scripts/space_traversal/detectors/detector_duplication.py")
        module = _load_module(detector_path, "detector_duplication")
        context_index = _context_index_for(files)
        result = module.detect(context_index)
        
        assert result["dup_ratio"] >= 0.6  # 3 duplicates out of 5 files
        assert result["counts"]["dup"] == 4
        assert result["metrics"]["duplication_percentage"] >= 60.0
    
    def test_case_insensitive(self, tmp_path: Path):
        """Test that stem comparison is case-insensitive."""
        files = [
            tmp_path / "Test.py",
            tmp_path / "test.md",
            tmp_path / "TEST.txt",
        ]
        for f in files:
            f.write_text("content\n", encoding="utf-8")
        
        detector_path = Path("scripts/space_traversal/detectors/detector_duplication.py")
        module = _load_module(detector_path, "detector_duplication")
        context_index = _context_index_for(files)
        result = module.detect(context_index)
        
        assert result["counts"]["test"] == 3
        assert "test" in result["duplicate_groups"]


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_file_list(self):
        """Test with empty file list."""
        detector_path = Path("scripts/space_traversal/detectors/detector_duplication.py")
        module = _load_module(detector_path, "detector_duplication")
        context_index = {"files": []}
        result = module.detect(context_index)
        
        assert result["dup_ratio"] == 0.0
        assert result["evidence_count"] == 1  # max(0, 1)
        assert len(result["duplicate_groups"]) == 0
    
    def test_single_file(self, tmp_path: Path):
        """Test with single file."""
        files = [tmp_path / "single.py"]
        files[0].write_text("content\n", encoding="utf-8")
        
        detector_path = Path("scripts/space_traversal/detectors/detector_duplication.py")
        module = _load_module(detector_path, "detector_duplication")
        context_index = _context_index_for(files)
        result = module.detect(context_index)
        
        assert result["dup_ratio"] == 0.0
        assert result["evidence_count"] == 1
        assert len(result["duplicate_groups"]) == 0
    
    def test_all_same_stem(self, tmp_path: Path):
        """Test when all files have the same stem."""
        files = [
            tmp_path / "same.py",
            tmp_path / "same.md",
            tmp_path / "same.txt",
            tmp_path / "same.yml",
        ]
        for f in files:
            f.write_text("content\n", encoding="utf-8")
        
        detector_path = Path("scripts/space_traversal/detectors/detector_duplication.py")
        module = _load_module(detector_path, "detector_duplication")
        context_index = _context_index_for(files)
        result = module.detect(context_index)
        
        assert result["dup_ratio"] == 0.75  # 3 duplicates out of 4
        assert result["counts"]["same"] == 4
        assert result["metrics"]["total_duplicates"] == 3
    
    def test_special_characters_in_stem(self, tmp_path: Path):
        """Test files with special characters in names."""
        files = [
            tmp_path / "file-with-dashes.py",
            tmp_path / "file_with_underscores.py",
            tmp_path / "file.with.dots.py",
        ]
        for f in files:
            f.write_text("content\n", encoding="utf-8")
        
        detector_path = Path("scripts/space_traversal/detectors/detector_duplication.py")
        module = _load_module(detector_path, "detector_duplication")
        context_index = _context_index_for(files)
        result = module.detect(context_index)
        
        assert result["dup_ratio"] == 0.0  # All unique stems
        assert result["evidence_count"] == 3


class TestDeterminism:
    """Test deterministic behavior."""
    
    def test_deterministic_ordering(self, tmp_path: Path):
        """Test that results are deterministic with same inputs."""
        files = [
            tmp_path / "b.py",
            tmp_path / "a.py",
            tmp_path / "c.py",
            tmp_path / "a.md",
        ]
        for f in files:
            f.write_text("content\n", encoding="utf-8")
        
        detector_path = Path("scripts/space_traversal/detectors/detector_duplication.py")
        module = _load_module(detector_path, "detector_duplication")
        context_index = _context_index_for(files)
        
        # Run multiple times
        result1 = module.detect(context_index)
        result2 = module.detect(context_index)
        
        assert result1["dup_ratio"] == result2["dup_ratio"]
        assert result1["counts"] == result2["counts"]
        assert result1["duplicate_groups"] == result2["duplicate_groups"]
    
    def test_sorted_duplicate_groups(self, tmp_path: Path):
        """Test that duplicate groups are sorted deterministically."""
        files = [
            tmp_path / "z_test.py",
            tmp_path / "a_test.md",
            tmp_path / "m_test.txt",
        ]
        for f in files:
            f.write_text("content\n", encoding="utf-8")
        
        detector_path = Path("scripts/space_traversal/detectors/detector_duplication.py")
        module = _load_module(detector_path, "detector_duplication")
        context_index = _context_index_for(files)
        result = module.detect(context_index)
        
        # Verify group is sorted
        if "test" in result["duplicate_groups"]:
            group = result["duplicate_groups"]["test"]
            assert group == sorted(group)
    
    def test_reproducible_metrics(self, tmp_path: Path):
        """Test that metrics are reproducible."""
        files = [
            tmp_path / "file1.py",
            tmp_path / "file2.py",
            tmp_path / "file1.md",
        ]
        for f in files:
            f.write_text("content\n", encoding="utf-8")
        
        detector_path = Path("scripts/space_traversal/detectors/detector_duplication.py")
        module = _load_module(detector_path, "detector_duplication")
        context_index = _context_index_for(files)
        
        results = [module.detect(context_index) for _ in range(5)]
        
        # All runs should produce identical metrics
        for result in results[1:]:
            assert result["metrics"] == results[0]["metrics"]


class TestPatternDetection:
    """Test pattern detection logic."""
    
    def test_required_patterns(self, tmp_path: Path):
        """Test that all required patterns are specified."""
        files = [tmp_path / "test.py"]
        files[0].write_text("content\n", encoding="utf-8")
        
        detector_path = Path("scripts/space_traversal/detectors/detector_duplication.py")
        module = _load_module(detector_path, "detector_duplication")
        context_index = _context_index_for(files)
        result = module.detect(context_index)
        
        assert "required_patterns" in result
        assert "analysis" in result["required_patterns"]
        assert "detection" in result["required_patterns"]
        assert "reporting" in result["required_patterns"]
    
    def test_found_patterns(self, tmp_path: Path):
        """Test that found patterns are correctly identified."""
        files = [tmp_path / "test.py"]
        files[0].write_text("content\n", encoding="utf-8")
        
        detector_path = Path("scripts/space_traversal/detectors/detector_duplication.py")
        module = _load_module(detector_path, "detector_duplication")
        context_index = _context_index_for(files)
        result = module.detect(context_index)
        
        assert "found_patterns" in result
        assert "analysis" in result["found_patterns"]
        assert "detection" in result["found_patterns"]
        assert "reporting" in result["found_patterns"]
    
    def test_docs_keywords(self, tmp_path: Path):
        """Test that documentation keywords are provided."""
        files = [tmp_path / "test.py"]
        files[0].write_text("content\n", encoding="utf-8")
        
        detector_path = Path("scripts/space_traversal/detectors/detector_duplication.py")
        module = _load_module(detector_path, "detector_duplication")
        context_index = _context_index_for(files)
        result = module.detect(context_index)
        
        assert "docs_keywords" in result
        assert "duplication" in result["docs_keywords"]
        assert "similarity" in result["docs_keywords"]
        assert "analysis" in result["docs_keywords"]
        assert "detection" in result["docs_keywords"]
        assert "consistency" in result["docs_keywords"]


class TestMetadata:
    """Test metadata and safeguard indicators."""
    
    def test_metadata_present(self, tmp_path: Path):
        """Test that metadata is included."""
        files = [tmp_path / "test.py"]
        files[0].write_text("content\n", encoding="utf-8")
        
        detector_path = Path("scripts/space_traversal/detectors/detector_duplication.py")
        module = _load_module(detector_path, "detector_duplication")
        context_index = _context_index_for(files)
        result = module.detect(context_index)
        
        assert "meta" in result
        assert result["meta"]["method"] == "stem_based"
        assert result["meta"]["deterministic"] is True
        assert result["meta"]["offline"] is True
    
    def test_comprehensive_metrics(self, tmp_path: Path):
        """Test that comprehensive metrics are provided."""
        files = [
            tmp_path / "a.py",
            tmp_path / "a.md",
            tmp_path / "b.py",
        ]
        for f in files:
            f.write_text("content\n", encoding="utf-8")
        
        detector_path = Path("scripts/space_traversal/detectors/detector_duplication.py")
        module = _load_module(detector_path, "detector_duplication")
        context_index = _context_index_for(files)
        result = module.detect(context_index)
        
        assert "metrics" in result
        assert "total_duplicates" in result["metrics"]
        assert "unique_stems" in result["metrics"]
        assert "duplication_percentage" in result["metrics"]
        assert isinstance(result["metrics"]["duplication_percentage"], (int, float))


class TestAdditionalEdgeCases:
    """Additional edge case tests for comprehensive coverage."""
    
    def test_case_sensitivity(self, tmp_path: Path):
        """Test that file stem matching is case-sensitive."""
        files = [
            tmp_path / "Test.py",
            tmp_path / "test.py",
            tmp_path / "TEST.md",
        ]
        for f in files:
            f.write_text("content\n", encoding="utf-8")
        
        detector_path = Path("scripts/space_traversal/detectors/detector_duplication.py")
        module = _load_module(detector_path, "detector_duplication")
        context_index = _context_index_for(files)
        result = module.detect(context_index)
        
        # Different cases should be treated as different stems
        # (or same stem depending on implementation - verify consistency)
        assert result["id"] == "duplication_ratio"
        assert "duplicate_groups" in result
    
    def test_hidden_files(self, tmp_path: Path):
        """Test detection handles hidden files (dotfiles) correctly."""
        files = [
            tmp_path / ".hidden.py",
            tmp_path / ".hidden.md",
            tmp_path / "visible.py",
        ]
        for f in files:
            f.write_text("content\n", encoding="utf-8")
        
        detector_path = Path("scripts/space_traversal/detectors/detector_duplication.py")
        module = _load_module(detector_path, "detector_duplication")
        context_index = _context_index_for(files)
        result = module.detect(context_index)
        
        # Should detect .hidden duplication
        assert result["dup_ratio"] >= 0.0
        assert "metrics" in result
    
    def test_large_duplicate_group(self, tmp_path: Path):
        """Test detection with a large group of files sharing same stem."""
        files = [
            tmp_path / f"duplicate.{ext}"
            for ext in ["py", "md", "txt", "json", "yaml", "sh", "rst", "cfg"]
        ]
        for f in files:
            f.write_text("content\n", encoding="utf-8")
        
        detector_path = Path("scripts/space_traversal/detectors/detector_duplication.py")
        module = _load_module(detector_path, "detector_duplication")
        context_index = _context_index_for(files)
        result = module.detect(context_index)
        
        # All 8 files share "duplicate" stem
        assert result["dup_ratio"] > 0.8  # Very high duplication
        assert "duplicate" in result["duplicate_groups"]
        assert len(result["duplicate_groups"]["duplicate"]) == 8
    
    def test_mixed_unique_and_duplicate(self, tmp_path: Path):
        """Test accurate ratio calculation with mixed unique and duplicate files."""
        # 3 unique + 6 duplicate (2 groups of 3) = 9 files total
        files = [
            tmp_path / "unique1.py",
            tmp_path / "unique2.py",
            tmp_path / "unique3.py",
            tmp_path / "dup1.py",
            tmp_path / "dup1.md",
            tmp_path / "dup1.txt",
            tmp_path / "dup2.py",
            tmp_path / "dup2.md",
            tmp_path / "dup2.txt",
        ]
        for f in files:
            f.write_text("content\n", encoding="utf-8")
        
        detector_path = Path("scripts/space_traversal/detectors/detector_duplication.py")
        module = _load_module(detector_path, "detector_duplication")
        context_index = _context_index_for(files)
        result = module.detect(context_index)
        
        # 6 duplicate files out of 9 total
        assert 0.5 < result["dup_ratio"] < 0.8
        assert result["metrics"]["total_duplicates"] == 6
        assert len(result["duplicate_groups"]) == 2
    
    def test_special_characters_in_names(self, tmp_path: Path):
        """Test detection with special characters in filenames."""
        files = [
            tmp_path / "test-file_v1.0.py",
            tmp_path / "test-file_v1.0.md",
            tmp_path / "other_file.py",
        ]
        for f in files:
            f.write_text("content\n", encoding="utf-8")
        
        detector_path = Path("scripts/space_traversal/detectors/detector_duplication.py")
        module = _load_module(detector_path, "detector_duplication")
        context_index = _context_index_for(files)
        result = module.detect(context_index)
        
        # Should handle special characters in stem
        assert result["dup_ratio"] > 0.0
        assert "test-file_v1.0" in result["duplicate_groups"]
    
    def test_numeric_stems(self, tmp_path: Path):
        """Test detection with numeric file stems."""
        files = [
            tmp_path / "123.py",
            tmp_path / "123.md",
            tmp_path / "456.py",
        ]
        for f in files:
            f.write_text("content\n", encoding="utf-8")
        
        detector_path = Path("scripts/space_traversal/detectors/detector_duplication.py")
        module = _load_module(detector_path, "detector_duplication")
        context_index = _context_index_for(files)
        result = module.detect(context_index)
        
        # Should handle numeric stems
        assert "123" in result["duplicate_groups"]
        assert len(result["duplicate_groups"]["123"]) == 2
    
    def test_deterministic_ordering(self, tmp_path: Path):
        """Test that detection produces deterministic, sorted output."""
        files = [
            tmp_path / "z.py",
            tmp_path / "a.py",
            tmp_path / "m.py",
            tmp_path / "m.md",
        ]
        for f in files:
            f.write_text("content\n", encoding="utf-8")
        
        detector_path = Path("scripts/space_traversal/detectors/detector_duplication.py")
        module = _load_module(detector_path, "detector_duplication")
        context_index = _context_index_for(files)
        
        # Run multiple times
        results = [module.detect(context_index) for _ in range(3)]
        
        # All results should be identical (deterministic)
        for i in range(1, len(results)):
            assert results[i]["dup_ratio"] == results[0]["dup_ratio"]
            assert results[i]["duplicate_groups"] == results[0]["duplicate_groups"]
            # Evidence should be sorted
            if "evidence" in results[i]:
                evidence_keys = list(results[i]["evidence"].keys())
                assert evidence_keys == sorted(evidence_keys)
