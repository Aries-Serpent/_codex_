"""Tests for enhanced coverage ingestion."""

from __future__ import annotations

import json
from pathlib import Path

import scripts.space_traversal.coverage_ingest as ci


def test_parse_coverage_xml_to_map_basic(tmp_path: Path):
    """Test basic coverage XML parsing."""

    # Create a minimal Cobertura-style coverage XML
    xml_content = """<?xml version="1.0"?>
<coverage version="1.0">
    <packages>
        <package name="src">
            <classes>
                <class filename="src/module.py" name="module">
                    <lines>
                        <line number="1" hits="1"/>
                        <line number="2" hits="1"/>
                        <line number="3" hits="0"/>
                        <line number="4" hits="1"/>
                    </lines>
                </class>
            </classes>
        </package>
    </packages>
</coverage>
"""

    xml_path = tmp_path / "coverage.xml"
    xml_path.write_text(xml_content)

    # Create a dummy source file
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    module_file = src_dir / "module.py"
    module_file.write_text("line1\nline2\nline3\nline4\nline5\n")

    # Parse
    cov_map = ci.parse_coverage_xml_to_map(xml_path, tmp_path)

    assert "src/module.py" in cov_map, "Condition must be true"
    data = cov_map["src/module.py"]
    assert "covered_lines" in data, "Data must not be empty"
    assert "percent" in data, "Data must not be empty"
    assert "total_lines" in data, "Data must not be empty"
    assert 1 in data["covered_lines"], "Data must not be empty"
    assert 2 in data["covered_lines"], "Data must not be empty"
    assert 4 in data["covered_lines"], "Data must not be empty"
    assert 3 not in data["covered_lines"], "Data must not be empty"
    assert data["total_lines"] == 5, "Data must not be empty"
    assert data["percent"] == 0.6, "Data must not be empty"


def test_parse_coverage_xml_to_map_empty():
    """Test parsing empty/invalid XML."""
    # Non-existent file - use tempfile for platform agnostic temp
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        nonexistent = Path(tmpdir) / "nonexistent.xml"
        cov_map = ci.parse_coverage_xml_to_map(nonexistent)
        assert cov_map == {}, "cov_map is not valid"


def test_parse_coverage_xml_to_map_missing_source(tmp_path: Path):
    """Test parsing when source file is missing."""
    xml_content = """<?xml version="1.0"?>
<coverage version="1.0">
    <packages>
        <package name="src">
            <classes>
                <class filename="src/missing.py" name="missing">
                    <lines>
                        <line number="1" hits="1"/>
                        <line number="5" hits="1"/>
                    </lines>
                </class>
            </classes>
        </package>
    </packages>
</coverage>
"""

    xml_path = tmp_path / "coverage.xml"
    xml_path.write_text(xml_content)

    # Don't create the source file
    cov_map = ci.parse_coverage_xml_to_map(xml_path, tmp_path)

    # Should still parse but estimate from covered lines
    assert "src/missing.py" in cov_map, "Condition must be true"
    data = cov_map["src/missing.py"]
    assert data["covered_lines"] == [1, 5]
    assert data["total_lines"] == 5, "Data must not be empty"


def test_discover_and_parse_coverage_disabled(tmp_path: Path):
    """Test that coverage discovery respects enabled flag."""
    cfg = {"scoring": {"coverage": {"enabled": False}}}

    result = ci.discover_and_parse_coverage(cfg, tmp_path)
    assert result is None, "Result must not be empty"


def test_discover_and_parse_coverage_default_patterns(tmp_path: Path):
    """Test coverage discovery with default patterns."""
    # Create coverage XML at root
    xml_content = """<?xml version="1.0"?>
<coverage version="1.0">
    <packages>
        <package name="test">
            <classes>
                <class filename="test.py" name="test">
                    <lines>
                        <line number="1" hits="1"/>
                    </lines>
                </class>
            </classes>
        </package>
    </packages>
</coverage>
"""

    coverage_xml = tmp_path / "coverage.xml"
    coverage_xml.write_text(xml_content)

    # Create source file
    test_file = tmp_path / "test.py"
    test_file.write_text("# test\n")

    cfg = {"scoring": {"coverage": {"enabled": True, "xml_patterns": ["coverage.xml"]}}}

    artifacts_dir = tmp_path / "audit_artifacts"
    artifacts_dir.mkdir()

    # Need to temporarily change ROOT for this test
    original_root = ci.ROOT
    try:
        ci.ROOT = tmp_path
        result = ci.discover_and_parse_coverage(cfg, artifacts_dir)
    finally:
        ci.ROOT = original_root

    assert result is not None, "result must be initialized"
    assert "test.py" in result, "Result must not be empty"

    # Check that coverage_map.json was written
    map_file = artifacts_dir / "coverage_map.json"
    assert map_file.exists(), "Condition must be true"

    data = json.loads(map_file.read_text())
    assert "test.py" in data, "Data must not be empty"


def test_discover_and_parse_coverage_custom_patterns(tmp_path: Path):
    """Test coverage discovery with custom patterns."""
    # Create coverage XML in subdirectory
    subdir = tmp_path / "build" / "reports"
    subdir.mkdir(parents=True)

    xml_content = """<?xml version="1.0"?>
<coverage version="1.0">
    <packages>
        <package name="app">
            <classes>
                <class filename="app.py" name="app">
                    <lines>
                        <line number="1" hits="1"/>
                        <line number="2" hits="1"/>
                    </lines>
                </class>
            </classes>
        </package>
    </packages>
</coverage>
"""

    coverage_xml = subdir / "coverage.xml"
    coverage_xml.write_text(xml_content)

    # Create source
    app_file = tmp_path / "app.py"
    app_file.write_text("line1\nline2\n")

    cfg = {
        "scoring": {"coverage": {"enabled": True, "xml_patterns": ["build/reports/coverage.xml"]}}
    }

    artifacts_dir = tmp_path / "audit_artifacts"
    artifacts_dir.mkdir()

    original_root = ci.ROOT
    try:
        ci.ROOT = tmp_path
        result = ci.discover_and_parse_coverage(cfg, artifacts_dir)
    finally:
        ci.ROOT = original_root

    assert result is not None, "result must be initialized"
    assert "app.py" in result, "Result must not be empty"


def test_parse_coverage_xml_backward_compat(tmp_path: Path):
    """Test backward compatibility of parse_coverage_xml function."""
    xml_content = """<?xml version="1.0"?>
<coverage version="1.0">
    <packages>
        <package name="src">
            <classes>
                <class filename="src/test.py" name="test">
                    <lines>
                        <line number="1" hits="1"/>
                    </lines>
                </class>
            </classes>
        </package>
    </packages>
</coverage>
"""

    xml_path = tmp_path / "coverage.xml"
    xml_path.write_text(xml_content)

    # Legacy function should still work
    result = ci.parse_coverage_xml(xml_path)
    assert isinstance(result, dict)
