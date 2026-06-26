"""
Tests for MCP schema validation detector.

Tests Pydantic BaseModel detection and OpenAPI specification detection.
"""

import tempfile
from pathlib import Path

from scripts.space_traversal.detectors import mcp_schema_validation


def test_detect_no_schemas():
    """Test detection with no schema validation."""
    file_index = {
        "files": [
            {"path": "src/app/main.py"},
            {"path": "src/app/utils.py"},
            {"path": "tests/test_app.py"},
        ]
    }

    result = mcp_schema_validation.detect(file_index)

    assert result["id"] == "mcp-schema-validation", "Result must not be empty"
    assert result["found_patterns"] == [], "Result must not be empty"
    assert result["required_patterns"] == ["BaseModel", "OpenAPI"]
    assert "docs_keywords" in result, "Result must not be empty"


def test_detect_base_model():
    """Test detection of BaseModel usage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create file with BaseModel
        py_file = Path(tmpdir) / "models.py"
        py_file.write_text("""
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
""")

        file_index = {
            "files": [
                {"path": str(py_file)},
            ]
        }

        result = mcp_schema_validation.detect(file_index)

        assert "BaseModel" in result["found_patterns"], "Result must not be empty"
        assert str(py_file) in result["evidence_files"], "Result must not be empty"


def test_detect_pydantic_import():
    """Test detection of pydantic import."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create file with pydantic import
        py_file = Path(tmpdir) / "schemas.py"
        py_file.write_text("""
import pydantic
from typing import Optional

# Using pydantic for validation
""")

        file_index = {
            "files": [
                {"path": str(py_file)},
            ]
        }

        result = mcp_schema_validation.detect(file_index)

        # Should find evidence even without BaseModel class
        assert str(py_file) in result["evidence_files"], "Result must not be empty"


def test_detect_openapi_yaml():
    """Test detection of OpenAPI specification."""
    file_index = {
        "files": [
            {"path": "docs/api/openapi.yaml"},
            {"path": "src/app/main.py"},
        ]
    }

    result = mcp_schema_validation.detect(file_index)

    assert "OpenAPI" in result["found_patterns"], "Result must not be empty"
    assert "docs/api/openapi.yaml" in result["evidence_files"], "Result must not be empty"


def test_detect_openapi_yml():
    """Test detection of OpenAPI .yml variant."""
    file_index = {
        "files": [
            {"path": "specs/openapi.yml"},
            {"path": "src/app/main.py"},
        ]
    }

    result = mcp_schema_validation.detect(file_index)

    assert "OpenAPI" in result["found_patterns"], "Result must not be empty"
    assert "specs/openapi.yml" in result["evidence_files"], "Result must not be empty"


def test_detect_both_patterns():
    """Test detection of both BaseModel and OpenAPI."""
    with tempfile.TemporaryDirectory() as tmpdir:
        py_file = Path(tmpdir) / "models.py"
        py_file.write_text("""
from pydantic import BaseModel

class APISchema(BaseModel):
    pass
""")

        file_index = {
            "files": [
                {"path": str(py_file)},
                {"path": "api/openapi.yaml"},
            ]
        }

        result = mcp_schema_validation.detect(file_index)

        assert "BaseModel" in result["found_patterns"], "Result must not be empty"
        assert "OpenAPI" in result["found_patterns"], "Result must not be empty"
        assert len(result["evidence_files"]) == 2, "Collection must not be empty"


def test_evidence_deduplication():
    """Test that evidence files are deduplicated."""
    with tempfile.TemporaryDirectory() as tmpdir:
        py_file = Path(tmpdir) / "models.py"
        py_file.write_text("""
from pydantic import BaseModel

class User(BaseModel):
    name: str

class Product(BaseModel):
    id: int
""")

        file_index = {
            "files": [
                {"path": str(py_file)},
            ]
        }

        result = mcp_schema_validation.detect(file_index)

        # File should appear only once even with multiple BaseModel occurrences
        assert len(result["evidence_files"]) == len(set(result["evidence_files"])), "Collection must not be empty"


def test_sorted_output():
    """Test that output lists are sorted."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file1 = Path(tmpdir) / "z_models.py"
        file1.write_text("from pydantic import BaseModel\nclass Z(BaseModel): pass")

        file2 = Path(tmpdir) / "a_schemas.py"
        file2.write_text("from pydantic import BaseModel\nclass A(BaseModel): pass")

        file_index = {
            "files": [
                {"path": str(file1)},
                {"path": str(file2)},
                {"path": "openapi.yaml"},
            ]
        }

        result = mcp_schema_validation.detect(file_index)

        # found_patterns should be sorted
        assert result["found_patterns"] == sorted(result["found_patterns"]), "Result must not be empty"
        # evidence_files should be sorted
        assert result["evidence_files"] == sorted(result["evidence_files"]), "Result must not be empty"


def test_docs_keywords_present():
    """Test that required docs_keywords are present."""
    file_index = {"files": []}

    result = mcp_schema_validation.detect(file_index)

    assert "docs_keywords" in result, "Result must not be empty"
    expected_keywords = [
        "mcp",
        "schema",
        "validation",
        "pydantic",
        "openapi",
        "basemodel",
        "type-safety",
    ]
    for keyword in expected_keywords:
        assert keyword in result["docs_keywords"], "Result must not be empty"


def test_safeguards_metadata():
    """Test that safeguards metadata is present."""
    file_index = {"files": []}

    result = mcp_schema_validation.detect(file_index)

    assert "meta" in result, "Result must not be empty"
    assert "safeguards" in result["meta"], "Result must not be empty"
    expected_safeguards = ["validation", "type-safety", "error-handling", "input-sanitization"]
    for safeguard in expected_safeguards:
        assert safeguard in result["meta"]["safeguards"], "Result must not be empty"


def test_detector_version():
    """Test that detector version is present."""
    file_index = {"files": []}

    result = mcp_schema_validation.detect(file_index)

    assert "detector_version" in result["meta"], "Result must not be empty"
    assert result["meta"]["detector_version"] == "1.2", "Result must not be empty"


def test_category_mcp():
    """Test that category is set to MCP."""
    file_index = {"files": []}

    result = mcp_schema_validation.detect(file_index)

    assert result["meta"]["category"] == "mcp", "Result must not be empty"


def test_non_python_files_ignored():
    """Test that non-Python files are skipped for BaseModel detection."""
    file_index = {
        "files": [
            {"path": "README.md"},
            {"path": "config.json"},
            {"path": "data.csv"},
        ]
    }

    result = mcp_schema_validation.detect(file_index)

    # Should not crash and should return empty results
    assert result["found_patterns"] == [], "Result must not be empty"
    assert result["evidence_files"] == [], "Result must not be empty"


def test_file_read_error_handling():
    """Test graceful handling of file read errors."""
    file_index = {
        "files": [
            {"path": "/nonexistent/file.py"},
        ]
    }

    # Should not crash on file read error
    result = mcp_schema_validation.detect(file_index)

    assert result["id"] == "mcp-schema-validation", "Result must not be empty"
    # File won't be in evidence since it couldn't be read
    assert len(result["evidence_files"]) == 0, "Collection must not be empty"


def test_empty_file_index():
    """Test detection with empty file index."""
    file_index = {"files": []}

    result = mcp_schema_validation.detect(file_index)

    assert result["id"] == "mcp-schema-validation", "Result must not be empty"
    assert result["found_patterns"] == [], "Result must not be empty"
    assert result["evidence_files"] == [], "Result must not be empty"


def test_deterministic_output():
    """Test that detector produces deterministic output."""
    with tempfile.TemporaryDirectory() as tmpdir:
        py_file = Path(tmpdir) / "models.py"
        py_file.write_text("from pydantic import BaseModel\nclass User(BaseModel): pass")

        file_index = {
            "files": [
                {"path": str(py_file)},
                {"path": "openapi.yaml"},
            ]
        }

        # Run detection multiple times
        results = [mcp_schema_validation.detect(file_index) for _ in range(3)]

        # All results should be identical
        for i in range(1, len(results)):
            assert results[i]["found_patterns"] == results[0]["found_patterns"], "Result must not be empty"
            assert results[i]["evidence_files"] == results[0]["evidence_files"], "Result must not be empty"
