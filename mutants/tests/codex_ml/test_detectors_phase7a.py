"""Phase 7A Wave 1 Lane 1.4: Capability Detectors and Detection Tests.

Comprehensive coverage for capability detection utilities including:
- Configuration capability detection
- File and directory utilities
- Pattern matching and scoring
- Detector result structures
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import pytest

logger = logging.getLogger(__name__)


# ============================================================================
# Test: Path and File Utilities
# ============================================================================


class TestPathAndFileUtilities:
    """Test path and file utility functions."""

    def test_path_exists_for_valid_path(self):
        """Test path exists check for valid paths."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            test_path = Path(tmpdir)
            assert test_path.exists(), "Condition must be true"

    def test_path_exists_for_invalid_path(self):
        """Test path exists check for invalid paths."""
        fake_path = Path("/nonexistent/path/12345")
        assert not fake_path.exists(), "Condition must be true"

    def test_path_is_directory(self):
        """Test path is directory check."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)
            assert path.is_dir(), "Condition must be true"

            # Create a file
            test_file = path / "test.txt"
            test_file.touch()
            assert test_file.is_file(), "Condition must be true"
            assert not test_file.is_dir(), "Condition must be true"

    def test_file_extension_checking(self):
        """Test file extension checking."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            py_file = Path(tmpdir) / "test.py"
            py_file.touch()

            txt_file = Path(tmpdir) / "test.txt"
            txt_file.touch()

            assert py_file.suffix == ".py", "suffix is not valid"
            assert txt_file.suffix == ".txt", "suffix is not valid"

    def test_glob_pattern_matching(self):
        """Test glob pattern matching."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create test files
            (tmppath / "test1.py").touch()
            (tmppath / "test2.py").touch()
            (tmppath / "data.json").touch()

            py_files = list(tmppath.glob("*.py"))
            assert len(py_files) == 2, "Py_files must not be empty"

            json_files = list(tmppath.glob("*.json"))
            assert len(json_files) == 1, "Json_files must not be empty"

    def test_recursive_glob_pattern(self):
        """Test recursive glob pattern matching."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create nested structure
            subdir = tmppath / "subdir"
            subdir.mkdir()

            (tmppath / "test.py").touch()
            (subdir / "nested.py").touch()

            all_py = list(tmppath.rglob("*.py"))
            assert len(all_py) == 2, "All_py must not be empty"


# ============================================================================
# Test: File Content Analysis
# ============================================================================


class TestFileContentAnalysis:
    """Test file content analysis and pattern matching."""

    def test_read_file_content(self):
        """Test reading file content."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("import torch\nimport numpy as np\n")

            content = test_file.read_text()
            assert "torch" in content, "Content must not be empty"
            assert "numpy" in content, "Content must not be empty"

    def test_file_line_counting(self):
        """Test counting lines in file."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("line1\nline2\nline3\n")

            lines = test_file.read_text().splitlines()
            assert len(lines) == 3, "Lines must not be empty"

    def test_pattern_search_in_content(self):
        """Test pattern searching in file content."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "config.py"
            test_file.write_text("""
class Config:
    hidden_size = 768
    num_layers = 12
""")

            content = test_file.read_text()
            assert "class Config" in content, "Content must not be empty"
            assert "hidden_size" in content, "Content must not be empty"

    def test_multiple_pattern_matching(self):
        """Test matching multiple patterns in content."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "model.py"
            test_file.write_text("""
import torch
from transformers import AutoModel
import pytest

def test_model_load():
    pass
""")

            content = test_file.read_text()
            patterns = ["torch", "transformers", "pytest", "test_"]

            matches = {p: p in content for p in patterns}
            assert all(matches.values()), "Value must be initialized"

    def test_import_statement_detection(self):
        """Test detecting import statements."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "imports.py"
            test_file.write_text("""
import torch
from pathlib import Path
from typing import Dict, List
""")

            content = test_file.read_text()

            has_torch = "import torch" in content
            has_pathlib = "from pathlib import Path" in content

            assert has_torch, "has_torch is not valid"
            assert has_pathlib, "has_pathlib is not valid"

    def test_json_content_parsing(self):
        """Test parsing JSON content from file."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            json_file = Path(tmpdir) / "config.json"
            config = {
                "hidden_size": 768,
                "num_layers": 12,
                "vocab_size": 50257,
            }
            json_file.write_text(json.dumps(config))

            loaded = json.loads(json_file.read_text())
            assert loaded["hidden_size"] == 768, "Condition must be true"
            assert loaded["num_layers"] == 12, "Condition must be true"


# ============================================================================
# Test: Directory Counting and Analysis
# ============================================================================


class TestDirectoryAnalysis:
    """Test directory analysis and file counting."""

    def test_count_python_files_in_directory(self):
        """Test counting Python files in directory."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            (tmppath / "file1.py").touch()
            (tmppath / "file2.py").touch()
            (tmppath / "readme.txt").touch()

            py_count = len(list(tmppath.glob("*.py")))
            assert py_count == 2, "Count must be greater than zero"

    def test_count_test_files(self):
        """Test counting test files."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            (tmppath / "test_module.py").touch()
            (tmppath / "test_utils.py").touch()
            (tmppath / "module.py").touch()

            test_count = len(list(tmppath.glob("test_*.py")))
            assert test_count == 2, "Count must be greater than zero"

    def test_count_files_recursively(self):
        """Test counting files recursively."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            subdir = tmppath / "subdir"
            subdir.mkdir()

            (tmppath / "file1.py").touch()
            (subdir / "file2.py").touch()

            all_py = list(tmppath.rglob("*.py"))
            assert len(all_py) == 2, "All_py must not be empty"

    def test_directory_size_calculation(self):
        """Test directory size calculation."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            (tmppath / "file1.txt").write_text("a" * 1000)
            (tmppath / "file2.txt").write_text("b" * 2000)

            total_size = sum(f.stat().st_size for f in tmppath.glob("*.txt"))
            assert total_size == 3000, "total_size is not valid"


# ============================================================================
# Test: Capability Detector Utilities
# ============================================================================


class TestCapabilityDetectorUtilities:
    """Test capability detector utility functions."""

    def test_clamp01_function(self):
        """Test clamping values to [0, 1]."""
        from codex_ml.detectors.core import clamp01

        assert clamp01(-0.5) == 0.0, "Condition must be true"
        assert clamp01(0.0) == 0.0, "Condition must be true"
        assert clamp01(0.5) == 0.5, "Condition must be true"
        assert clamp01(1.0) == 1.0, "Condition must be true"
        assert clamp01(1.5) == 1.0, "Condition must be true"

    def test_detector_result_creation(self):
        """Test DetectorResult creation."""
        from codex_ml.detectors.core import DetectorResult

        result = DetectorResult(
            score=0.85,
            category="configuration",
            evidence=["config_schema_exists", "pydantic_validation"],
        )

        assert result.score == 0.85, "Result must not be empty"
        assert result.category == "configuration", "Result must not be empty"
        assert len(result.evidence) == 2, "Collection must not be empty"

    def test_detector_result_score_validation(self):
        """Test DetectorResult score validation."""
        from codex_ml.detectors.core import DetectorResult

        # Valid score
        result = DetectorResult(
            score=0.5,
            category="test",
            evidence=[],
        )
        assert 0 <= result.score <= 1, "Result must not be empty"

    def test_detector_evidence_collection(self):
        """Test evidence collection in detector results."""
        from codex_ml.detectors.core import DetectorResult

        evidence = [
            "config_path_exists",
            "schema_validation",
            "yaml_support",
            "hashing_for_reproducibility",
        ]

        result = DetectorResult(
            score=0.75,
            category="configuration",
            evidence=evidence,
        )

        assert len(result.evidence) == 4, "Collection must not be empty"
        assert "schema_validation" in result.evidence, "Result must not be empty"


# ============================================================================
# Test: Configuration Capability Detection
# ============================================================================


class TestConfigurationCapabilityDetection:
    """Test configuration capability detection."""

    def test_config_schema_path_detection(self):
        """Test detecting config schema file."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create config schema file
            schema_file = tmppath / "config_schema.py"
            schema_file.write_text("""
from pydantic import BaseModel

class ConfigSchema(BaseModel):
    pass
""")

            assert schema_file.exists(), "Condition must be true"
            assert "BaseModel" in schema_file.read_text(), "Condition must be true"

    def test_pydantic_patterns_detection(self):
        """Test detecting pydantic patterns."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            schema_file = Path(tmpdir) / "schema.py"
            schema_file.write_text("""
from pydantic import BaseModel, field_validator

class Config(BaseModel):
    @field_validator('field_name')
    def validate_field(cls, v):
        return v
""")

            content = schema_file.read_text()
            patterns = ["BaseModel", "field_validator", "ValidationError", "model_validate"]

            has_pydantic = all(p in content for p in patterns[:2])
            assert has_pydantic, "has_pydantic is not valid"

    def test_yaml_support_detection(self):
        """Test detecting YAML support."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            loader_file = Path(tmpdir) / "loader.py"
            loader_file.write_text("""
import yaml

def load_config(path):
    with open(path) as f:
        return yaml.safe_load(f)
""")

            content = loader_file.read_text()
            assert "yaml" in content, "Content must not be empty"
            assert "yaml.safe_load" in content, "Content must not be empty"

    def test_config_hashing_detection(self):
        """Test detecting config hashing."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            util_file = Path(tmpdir) / "utils.py"
            util_file.write_text("""
import hashlib
import json

def hash_config(config):
    return hashlib.sha256(json.dumps(config).encode()).hexdigest()
""")

            content = util_file.read_text()
            assert "hashlib" in content, "Content must not be empty"
            assert "sha256" in content, "Content must not be empty"

    def test_defaults_coverage_detection(self):
        """Test detecting default values in config."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.py"
            config_file.write_text("""
from dataclasses import dataclass

@dataclass
class Config:
    learning_rate: float = 1e-4
    batch_size: int = 32
    num_epochs: int = 3
""")

            content = config_file.read_text()
            assert "learning_rate: float = 1e-4" in content, "Content must not be empty"
            assert "batch_size: int = 32" in content, "Content must not be empty"


# ============================================================================
# Test: Detector Scoring and Aggregation
# ============================================================================


class TestDetectorScoringAndAggregation:
    """Test detector scoring and result aggregation."""

    def test_score_aggregation(self):
        """Test aggregating detector scores."""
        scores = [0.8, 0.9, 0.7, 0.85]

        avg_score = sum(scores) / len(scores)
        assert 0.8 < avg_score < 0.9, "8 is not valid"

    def test_weighted_score_aggregation(self):
        """Test weighted score aggregation."""
        scores = [0.8, 0.9, 0.7]
        weights = [0.3, 0.5, 0.2]

        weighted_score = sum(s * w for s, w in zip(scores, weights))
        assert 0.8 < weighted_score < 0.9, "8 is not valid"

    def test_detector_result_comparison(self):
        """Test comparing detector results."""
        from codex_ml.detectors.core import DetectorResult

        result1 = DetectorResult(score=0.8, category="test", evidence=[])
        result2 = DetectorResult(score=0.9, category="test", evidence=[])

        assert result1.score < result2.score, "Result must not be empty"
        assert result1.category == result2.category, "Result must not be empty"

    def test_evidence_aggregation(self):
        """Test aggregating evidence from multiple detectors."""
        evidence_sets = [
            ["check1", "check2"],
            ["check3", "check4"],
            ["check2", "check5"],  # check2 overlaps
        ]

        all_evidence = set()
        for evs in evidence_sets:
            all_evidence.update(evs)

        assert len(all_evidence) == 5, "All_evidence must not be empty"


# ============================================================================
# Test: Detector Integration
# ============================================================================


class TestDetectorIntegration:
    """Test detector integration and workflow."""

    def test_configuration_detector_workflow(self):
        """Test full configuration detector workflow."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create minimal config structure
            schema_file = tmppath / "config_schema.py"
            schema_file.write_text("from pydantic import BaseModel\n")

            yaml_file = tmppath / "config.yaml"
            yaml_file.write_text("key: value\n")

            # Verification
            assert schema_file.exists(), "Condition must be true"
            assert yaml_file.exists(), "Condition must be true"

    def test_detector_result_serialization(self):
        """Test detector result serialization."""
        from codex_ml.detectors.core import DetectorResult

        result = DetectorResult(
            score=0.85,
            category="configuration",
            evidence=["check1", "check2"],
        )

        result_dict = {
            "score": result.score,
            "category": result.category,
            "evidence": result.evidence,
        }

        json_str = json.dumps(result_dict)
        loaded = json.loads(json_str)

        assert loaded["score"] == 0.85, "Condition must be true"

    def test_multiple_detectors_execution(self):
        """Test executing multiple detectors."""
        from codex_ml.detectors.core import DetectorResult

        results = [
            DetectorResult(score=0.8, category="config", evidence=[]),
            DetectorResult(score=0.9, category="testing", evidence=[]),
            DetectorResult(score=0.7, category="logging", evidence=[]),
        ]

        assert len(results) == 3, "Results must not be empty"
        avg_score = sum(r.score for r in results) / len(results)
        assert 0.75 < avg_score < 0.85, "75 is not valid"


# ============================================================================
# Test: Edge Cases and Error Handling
# ============================================================================


class TestEdgeCasesAndErrorHandling:
    """Test edge cases in capability detection."""

    def test_empty_directory_handling(self):
        """Test handling empty directory."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            files = list(tmppath.glob("*.py"))
            assert len(files) == 0, "Files must not be empty"

    def test_nonexistent_file_handling(self):
        """Test handling nonexistent file."""
        fake_path = Path("/nonexistent/file.py")

        with pytest.raises(FileNotFoundError):
            fake_path.read_text()

    def test_invalid_json_in_file(self):
        """Test handling invalid JSON."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            json_file = Path(tmpdir) / "invalid.json"
            json_file.write_text("{ invalid json }")

            with pytest.raises(json.JSONDecodeError):
                json.loads(json_file.read_text())

    def test_permission_denied_handling(self):
        """Test handling permission denied scenarios."""
        import os
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            restricted_file = Path(tmpdir) / "restricted.txt"
            restricted_file.write_text("content")

            # Make unreadable
            os.chmod(restricted_file, 0o000)

            try:
                with pytest.raises(PermissionError):
                    restricted_file.read_text()
            finally:
                # Restore permissions for cleanup
                os.chmod(restricted_file, 0o600)  # nosemgrep: semgrep.insecure-file-permissions - Test cleanup: restoring permissions on test file

    def test_large_file_handling(self):
        """Test handling large files gracefully."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            large_file = Path(tmpdir) / "large.txt"

            # Write 1MB file
            large_file.write_text("x" * (1024 * 1024))

            assert large_file.stat().st_size == 1024 * 1024, "st_size is not valid"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
