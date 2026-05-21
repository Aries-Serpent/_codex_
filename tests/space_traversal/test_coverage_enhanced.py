"""Tests for enhanced coverage ingestion."""

from __future__ import annotations

import json
from pathlib import Path


def test_parse_coverage_xml_to_map_basic(tmp_path: Path):
    """Test basic coverage XML parsing."""
    from scripts.space_traversal.coverage_ingest import parse_coverage_xml_to_map

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
    cov_map = parse_coverage_xml_to_map(xml_path, tmp_path)

    assert "src/module.py" in cov_map
    data = cov_map["src/module.py"]
    assert "covered_lines" in data
    assert "percent" in data
    assert "total_lines" in data
    assert 1 in data["covered_lines"]
    assert 2 in data["covered_lines"]
    assert 4 in data["covered_lines"]
    assert 3 not in data["covered_lines"]
    assert data["total_lines"] == 5
    assert data["percent"] == 0.6  # 3/5


def test_parse_coverage_xml_to_map_empty():
    """Test parsing empty/invalid XML."""
    from scripts.space_traversal.coverage_ingest import parse_coverage_xml_to_map

    # Non-existent file
    cov_map = parse_coverage_xml_to_map(Path("/nonexistent.xml"))
    assert cov_map == {}


def test_parse_coverage_xml_to_map_missing_source(tmp_path: Path):
    """Test parsing when source file is missing."""
    from scripts.space_traversal.coverage_ingest import parse_coverage_xml_to_map

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
    cov_map = parse_coverage_xml_to_map(xml_path, tmp_path)

    # Should still parse but estimate from covered lines
    assert "src/missing.py" in cov_map
    data = cov_map["src/missing.py"]
    assert data["covered_lines"] == [1, 5]
    assert data["total_lines"] == 5  # Estimated from max line number


def test_discover_and_parse_coverage_disabled(tmp_path: Path):
    """Test that coverage discovery respects enabled flag."""
    from scripts.space_traversal.coverage_ingest import discover_and_parse_coverage

    cfg = {"scoring": {"coverage": {"enabled": False}}}

    result = discover_and_parse_coverage(cfg, tmp_path)
    assert result is None


def test_discover_and_parse_coverage_default_patterns(tmp_path: Path):
    """Test coverage discovery with default patterns."""
    from scripts.space_traversal.coverage_ingest import discover_and_parse_coverage

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
    import scripts.space_traversal.coverage_ingest as ci

    original_root = ci.ROOT
    try:
        ci.ROOT = tmp_path
        result = discover_and_parse_coverage(cfg, artifacts_dir)
    finally:
        ci.ROOT = original_root

    assert result is not None
    assert "test.py" in result

    # Check that coverage_map.json was written
    map_file = artifacts_dir / "coverage_map.json"
    assert map_file.exists()

    data = json.loads(map_file.read_text())
    assert "test.py" in data


def test_discover_and_parse_coverage_custom_patterns(tmp_path: Path):
    """Test coverage discovery with custom patterns."""
    from scripts.space_traversal.coverage_ingest import discover_and_parse_coverage

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

    import scripts.space_traversal.coverage_ingest as ci
    from scripts.space_traversal.coverage_ingest import discover_and_parse_coverage

    original_root = ci.ROOT
    try:
        ci.ROOT = tmp_path
        result = discover_and_parse_coverage(cfg, artifacts_dir)
    finally:
        ci.ROOT = original_root

    assert result is not None
    assert "app.py" in result


def test_parse_coverage_xml_backward_compat(tmp_path: Path):
    """Test backward compatibility of parse_coverage_xml function."""
    from scripts.space_traversal.coverage_ingest import parse_coverage_xml

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
    result = parse_coverage_xml(xml_path)
    assert isinstance(result, dict)
