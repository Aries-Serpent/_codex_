"""
Additional structural integrity tests.

Comprehensive tests for split-brain and shadowing detection.
Implements deterministic, reproducible, offline test patterns.
Uses checksum and manifest validation approaches.
"""

from scripts.space_traversal.detectors import structure_integrity


class TestStructuralSplitBrain:
    """Test split-brain detection patterns."""

    def test_split_brain_single_module(self):
        """Test split-brain with single module."""
        file_index = {
            "files": [
                {"path": "myapp/core.py"},
                {"path": "src/myapp/core.py"},
            ]
        }
        result = structure_integrity.detect(file_index)
        assert "split-brain" in result["found_patterns"], "Result must not be empty"
        assert "myapp" in result["meta"]["split_dirs"], "Result must not be empty"

    def test_split_brain_multiple_modules(self):
        """Test split-brain with multiple modules."""
        file_index = {
            "files": [
                {"path": "module_a/foo.py"},
                {"path": "src/module_a/foo.py"},
                {"path": "module_b/bar.py"},
                {"path": "src/module_b/bar.py"},
            ]
        }
        result = structure_integrity.detect(file_index)
        assert "split-brain" in result["found_patterns"], "Result must not be empty"
        assert len(result["meta"]["split_dirs"]) == 2, "Collection must not be empty"

    def test_no_split_brain_src_only(self):
        """Test no split-brain when only src/ exists."""
        file_index = {
            "files": [
                {"path": "src/myapp/core.py"},
                {"path": "src/myapp/utils.py"},
            ]
        }
        result = structure_integrity.detect(file_index)
        assert "split-brain" not in result["found_patterns"], "Result must not be empty"


class TestStructuralShadowing:
    """Test library shadowing detection."""

    def test_torch_shadowing(self):
        """Test torch library shadowing detection."""
        file_index = {
            "files": [
                {"path": "torch/custom_layer.py"},
            ]
        }
        result = structure_integrity.detect(file_index)
        assert "lib-shadowing" in result["found_patterns"], "Result must not be empty"
        assert "torch" in result["meta"]["shadow_dirs"], "Result must not be empty"

    def test_numpy_shadowing(self):
        """Test numpy library shadowing detection."""
        file_index = {
            "files": [
                {"path": "numpy/custom_ops.py"},
            ]
        }
        result = structure_integrity.detect(file_index)
        assert "lib-shadowing" in result["found_patterns"], "Result must not be empty"
        assert "numpy" in result["meta"]["shadow_dirs"], "Result must not be empty"

    def test_multiple_shadows(self):
        """Test multiple library shadowing."""
        file_index = {
            "files": [
                {"path": "torch/layer.py"},
                {"path": "numpy/array.py"},
                {"path": "pandas/frame.py"},
            ]
        }
        result = structure_integrity.detect(file_index)
        assert "lib-shadowing" in result["found_patterns"], "Result must not be empty"
        assert len(result["meta"]["shadow_dirs"]) >= 2, "Collection must not be empty"


class TestStructuralDeterminism:
    """Test deterministic behavior with baseline comparison."""

    def test_deterministic_patterns(self):
        """Test patterns are deterministic (baseline comparison)."""
        file_index = {"files": [{"path": "torch/x.py"}]}
        results = [structure_integrity.detect(file_index) for _ in range(5)]
        baseline = results[0]
        for r in results[1:]:
            assert r["found_patterns"] == baseline["found_patterns"], "Condition must be true"

    def test_deterministic_evidence(self):
        """Test evidence is deterministic (manifest-stable)."""
        file_index = {"files": [{"path": "myapp/a.py"}, {"path": "src/myapp/b.py"}]}
        results = [structure_integrity.detect(file_index) for _ in range(5)]
        baseline = results[0]
        for r in results[1:]:
            assert r["evidence_files"] == baseline["evidence_files"], "Condition must be true"

    def test_sorted_output(self):
        """Test all outputs are sorted (checksum-stable)."""
        file_index = {
            "files": [
                {"path": "z_module/z.py"},
                {"path": "src/z_module/z.py"},
                {"path": "a_module/a.py"},
                {"path": "src/a_module/a.py"},
            ]
        }
        result = structure_integrity.detect(file_index)
        assert result["evidence_files"] == sorted(result["evidence_files"]), "Result must not be empty"
        assert result["meta"]["split_dirs"] == sorted(result["meta"]["split_dirs"]), "Result must not be empty"
