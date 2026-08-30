"""
Tests for structural integrity detector.

Tests split-brain detection, library shadowing detection, and architectural validation.
"""

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

    assert result["id"] == "structural-integrity", "Result must not be empty"
    assert result["found_patterns"] == [], "Result must not be empty"
    assert result["required_patterns"] == ["split-brain", "lib-shadowing"]
    assert result["meta"]["risk_level"] == "low", "Result must not be empty"
    assert result["meta"]["split_dirs"] == [], "Result must not be empty"
    assert result["meta"]["shadow_dirs"] == [], "Result must not be empty"


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

    assert result["id"] == "structural-integrity", "Result must not be empty"
    assert "split-brain" in result["found_patterns"], "Result must not be empty"
    assert result["meta"]["risk_level"] == "high", "Result must not be empty"
    assert "mymodule" in result["meta"]["split_dirs"], "Result must not be empty"
    assert len(result["evidence_files"]) > 0, "Collection must not be empty"
    # Should have both root and src samples
    assert any("mymodule/" in f for f in result["evidence_files"]), "Result must not be empty"
    assert any("src/mymodule/" in f for f in result["evidence_files"]), "Result must not be empty"


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

    assert result["id"] == "structural-integrity", "Result must not be empty"
    assert "lib-shadowing" in result["found_patterns"], "Result must not be empty"
    assert result["meta"]["risk_level"] == "high", "Result must not be empty"
    assert "torch" in result["meta"]["shadow_dirs"], "Result must not be empty"
    assert "numpy" in result["meta"]["shadow_dirs"], "Result must not be empty"
    assert len(result["evidence_files"]) > 0, "Collection must not be empty"


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

    assert result["id"] == "structural-integrity", "Result must not be empty"
    assert "split-brain" in result["found_patterns"], "Result must not be empty"
    assert "lib-shadowing" in result["found_patterns"], "Result must not be empty"
    assert result["meta"]["risk_level"] == "high", "Result must not be empty"
    assert "mymodule" in result["meta"]["split_dirs"], "Result must not be empty"
    assert "torch" in result["meta"]["shadow_dirs"], "Result must not be empty"


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

    assert len(result["evidence_files"]) <= evidence_limit, "Collection must not be empty"
    assert result["meta"]["evidence_limit"] == evidence_limit, "Result must not be empty"


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
    assert result["found_patterns"] == [], "Result must not be empty"
    assert result["meta"]["risk_level"] == "low", "Result must not be empty"
    assert result["meta"]["split_dirs"] == [], "Result must not be empty"
    assert result["meta"]["shadow_dirs"] == [], "Result must not be empty"


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

    assert "lib-shadowing" in result["found_patterns"], "Result must not be empty"
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

    assert "split-brain" in result["found_patterns"], "Result must not be empty"
    assert len(result["meta"]["split_dirs"]) == 3, "Collection must not be empty"
    assert "module_a" in result["meta"]["split_dirs"], "Result must not be empty"
    assert "module_b" in result["meta"]["split_dirs"], "Result must not be empty"
    assert "module_c" in result["meta"]["split_dirs"], "Result must not be empty"


def test_docs_keywords_present():
    """Test that required docs_keywords are present."""
    file_index = {"files": [{"path": "src/app/main.py"}]}

    result = structure_integrity.detect(file_index)

    assert "docs_keywords" in result, "Result must not be empty"
    expected_keywords = [
        "structural-integrity",
        "architecture",
        "split-brain",
        "shadowing",
        "namespace",
        "validation",
        "detection",
        "consistency",
        "safeguards",
    ]
    for keyword in expected_keywords:
        assert keyword in result["docs_keywords"], "Result must not be empty"


def test_safeguards_metadata():
    """Test that safeguards metadata is present."""
    file_index = {"files": [{"path": "src/app/main.py"}]}

    result = structure_integrity.detect(file_index)

    assert "safeguards" in result["meta"], "Result must not be empty"
    expected_safeguards = ["bounded", "validation", "deterministic", "error-handling"]
    for safeguard in expected_safeguards:
        assert safeguard in result["meta"]["safeguards"], "Result must not be empty"


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
        assert results[i]["found_patterns"] == results[0]["found_patterns"], "Result must not be empty"
        assert results[i]["evidence_files"] == results[0]["evidence_files"], "Result must not be empty"
        assert results[i]["meta"]["split_dirs"] == results[0]["meta"]["split_dirs"], "Result must not be empty"
        assert results[i]["meta"]["shadow_dirs"] == results[0]["meta"]["shadow_dirs"], "Result must not be empty"


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
    assert result["found_patterns"] == sorted(result["found_patterns"]), "Result must not be empty"
    # split_dirs should be sorted
    assert result["meta"]["split_dirs"] == sorted(result["meta"]["split_dirs"]), "Result must not be empty"
    # shadow_dirs should be sorted
    assert result["meta"]["shadow_dirs"] == sorted(result["meta"]["shadow_dirs"]), "Result must not be empty"
    # evidence_files should be sorted
    assert result["evidence_files"] == sorted(result["evidence_files"]), "Result must not be empty"


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
    assert len(result["evidence_files"]) == len(set(result["evidence_files"])), "Collection must not be empty"


def test_empty_file_index():
    """Test detection with empty file index."""
    file_index = {"files": []}

    result = structure_integrity.detect(file_index)

    assert result["id"] == "structural-integrity", "Result must not be empty"
    assert result["found_patterns"] == [], "Result must not be empty"
    assert result["meta"]["risk_level"] == "low", "Result must not be empty"
    assert result["evidence_files"] == [], "Result must not be empty"


class TestStructuralIntegrityAdvanced:
    """Advanced structural integrity tests."""

    def test_nested_split_brain_detection(self):
        """Test detection of nested split-brain patterns."""
        file_index = {
            "files": [
                {"path": "myapp/core/engine.py"},
                {"path": "src/myapp/core/engine.py"},
                {"path": "lib/myapp/core/engine.py"},
            ]
        }

        result = structure_integrity.detect(file_index)

        assert "split-brain" in result["found_patterns"], "Result must not be empty"
        assert result["meta"]["risk_level"] == "high", "Result must not be empty"

    def test_shadowing_multiple_libraries(self):
        """Test detection of multiple library shadowing."""
        file_index = {
            "files": [
                {"path": "torch/nn.py"},
                {"path": "numpy/core.py"},
                {"path": "pandas/dataframe.py"},
                {"path": "src/myapp/main.py"},
            ]
        }

        result = structure_integrity.detect(file_index)

        assert "lib-shadowing" in result["found_patterns"], "Result must not be empty"
        # Should detect all three shadowed libraries
        shadow_dirs = result["meta"]["shadow_dirs"]
        assert len(shadow_dirs) >= 2, "Shadow_dirs must not be empty"

    def test_risk_level_calculation(self):
        """Test risk level is calculated correctly."""
        # Low risk - no issues
        result1 = structure_integrity.detect({"files": [{"path": "src/app.py"}]})
        assert result1["meta"]["risk_level"] == "low", "Result must not be empty"

        # High risk - split brain
        result2 = structure_integrity.detect(
            {
                "files": [
                    {"path": "mymodule/foo.py"},
                    {"path": "src/mymodule/foo.py"},
                ]
            }
        )
        assert result2["meta"]["risk_level"] == "high", "Result must not be empty"

    def test_edge_case_single_file_module(self):
        """Test detection with single-file modules."""
        file_index = {
            "files": [
                {"path": "utils.py"},
                {"path": "src/utils.py"},
            ]
        }

        result = structure_integrity.detect(file_index)

        # Single files might or might not trigger split-brain depending on implementation
        assert "id" in result, "Result must not be empty"
        assert "found_patterns" in result, "Result must not be empty"

    def test_case_sensitivity_handling(self):
        """Test case-sensitive path handling."""
        file_index = {
            "files": [
                {"path": "MyModule/Foo.py"},
                {"path": "src/mymodule/foo.py"},
            ]
        }

        result = structure_integrity.detect(file_index)

        # Should handle case differences appropriately
        assert "id" in result, "Result must not be empty"

    def test_unicode_path_handling(self):
        """Test handling of unicode characters in paths."""
        file_index = {
            "files": [
                {"path": "módulo/archivo.py"},
                {"path": "src/módulo/archivo.py"},
            ]
        }

        result = structure_integrity.detect(file_index)

        # Should handle unicode paths without errors
        assert result["id"] == "structural-integrity", "Result must not be empty"

    def test_deeply_nested_structures(self):
        """Test detection with deeply nested directory structures."""
        file_index = {
            "files": [
                {"path": "a/b/c/d/e/f/module.py"},
                {"path": "src/a/b/c/d/e/f/module.py"},
            ]
        }

        result = structure_integrity.detect(file_index)

        # Should detect split even in deep structures
        assert "split-brain" in result["found_patterns"], "Result must not be empty"

    def test_mixed_separators_handling(self):
        """Test handling of mixed path separators."""
        file_index = {
            "files": [
                {"path": "mymodule/submodule/file.py"},
                {"path": "src/mymodule/submodule/file.py"},
            ]
        }

        result = structure_integrity.detect(file_index)

        # Should normalize and detect properly
        assert "split-brain" in result["found_patterns"], "Result must not be empty"

    def test_symlink_awareness(self):
        """Test that detector can handle symlink scenarios."""
        # This is a structural test - actual symlink detection would require filesystem
        file_index = {
            "files": [
                {"path": "link_target/module.py"},
                {"path": "symlink/module.py"},  # Could be symlink to link_target
            ]
        }

        result = structure_integrity.detect(file_index)

        # Should produce valid result regardless
        assert result["id"] == "structural-integrity", "Result must not be empty"
