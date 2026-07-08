"""
Tests for MCP tooling registry detector.

Tests detection of tool registry, mcp.json, and plugin management.
"""

from scripts.space_traversal.detectors import mcp_tooling_registry


def test_detect_no_registry():
    """Test detection with no registry files."""
    file_index = {
        "files": [
            {"path": "src/app/main.py"},
            {"path": "src/app/utils.py"},
        ]
    }

    result = mcp_tooling_registry.detect(file_index)

    assert result["id"] == "mcp-tooling-registry", "Result must not be empty"
    assert result["found_patterns"] == [], "Result must not be empty"
    assert "registry" in result["required_patterns"], "Result must not be empty"
    assert "mcp.json" in result["required_patterns"], "Result must not be empty"


def test_detect_registry_file():
    """Test detection of registry.py file."""
    file_index = {
        "files": [
            {"path": "mcp/registry.py"},
            {"path": "src/app/main.py"},
        ]
    }

    result = mcp_tooling_registry.detect(file_index)

    assert "registry" in result["found_patterns"], "Result must not be empty"
    assert "mcp/registry.py" in result["evidence_files"], "Result must not be empty"


def test_detect_mcp_json():
    """Test detection of mcp.json config file."""
    file_index = {
        "files": [
            {"path": "mcp.json"},
            {"path": "src/app/main.py"},
        ]
    }

    result = mcp_tooling_registry.detect(file_index)

    assert "mcp.json" in result["found_patterns"], "Result must not be empty"
    assert "mcp.json" in result["evidence_files"], "Result must not be empty"


def test_detect_both_patterns():
    """Test detection of both registry and mcp.json."""
    file_index = {
        "files": [
            {"path": "mcp/tool_registry.py"},
            {"path": "mcp.json"},
        ]
    }

    result = mcp_tooling_registry.detect(file_index)

    assert "registry" in result["found_patterns"], "Result must not be empty"
    assert "mcp.json" in result["found_patterns"], "Result must not be empty"
    assert len(result["evidence_files"]) == 2, "Collection must not be empty"


def test_detect_tool_directory():
    """Test detection in tool directories."""
    file_index = {
        "files": [
            {"path": "tools/registry.py"},
            {"path": "tools/loader.py"},
        ]
    }

    result = mcp_tooling_registry.detect(file_index)

    assert "registry" in result["found_patterns"], "Result must not be empty"
    assert "tools/registry.py" in result["evidence_files"], "Result must not be empty"


def test_detect_mcp_directory_registry():
    """Test detection of registry in mcp/ directory."""
    file_index = {
        "files": [
            {"path": "mcp/tools/registry.py"},
            {"path": "mcp/services/api.py"},
        ]
    }

    result = mcp_tooling_registry.detect(file_index)

    assert "registry" in result["found_patterns"], "Result must not be empty"
    assert "mcp/tools/registry.py" in result["evidence_files"], "Result must not be empty"


def test_detect_nested_mcp_json():
    """Test detection of mcp.json in nested directories."""
    file_index = {
        "files": [
            {"path": "config/mcp.json"},
            {"path": "src/app/main.py"},
        ]
    }

    result = mcp_tooling_registry.detect(file_index)

    assert "mcp.json" in result["found_patterns"], "Result must not be empty"
    assert "config/mcp.json" in result["evidence_files"], "Result must not be empty"


def test_case_insensitive_matching():
    """Test that matching is case-insensitive."""
    file_index = {
        "files": [
            {"path": "MCP/Registry.py"},
            {"path": "MCP.json"},
        ]
    }

    result = mcp_tooling_registry.detect(file_index)

    # Should detect patterns regardless of case
    assert "registry" in result["found_patterns"], "Result must not be empty"
    assert "mcp.json" in result["found_patterns"], "Result must not be empty"


def test_tool_registry_variants():
    """Test detection of various registry file naming patterns."""
    file_index = {
        "files": [
            {"path": "mcp/tool_registry.py"},
            {"path": "mcp/plugin_registry.py"},
            {"path": "mcp/capability_registry.py"},
        ]
    }

    result = mcp_tooling_registry.detect(file_index)

    assert "registry" in result["found_patterns"], "Result must not be empty"
    # All should be detected as they contain "registry"
    assert len(result["evidence_files"]) == 3, "Collection must not be empty"


def test_evidence_deduplication():
    """Test that evidence files are deduplicated."""
    file_index = {
        "files": [
            {"path": "mcp/registry.py"},
            {"path": "tools/registry.py"},
        ]
    }

    result = mcp_tooling_registry.detect(file_index)

    # Check no duplicates
    assert len(result["evidence_files"]) == len(set(result["evidence_files"])), "Collection must not be empty"


def test_sorted_output():
    """Test that output lists are sorted."""
    file_index = {
        "files": [
            {"path": "z_tools/registry.py"},
            {"path": "a_mcp/registry.py"},
            {"path": "mcp.json"},
        ]
    }

    result = mcp_tooling_registry.detect(file_index)

    # found_patterns should be sorted
    assert result["found_patterns"] == sorted(result["found_patterns"]), "Result must not be empty"
    # evidence_files should be sorted
    assert result["evidence_files"] == sorted(result["evidence_files"]), "Result must not be empty"


def test_docs_keywords_present():
    """Test that required docs_keywords are present."""
    file_index = {"files": []}

    result = mcp_tooling_registry.detect(file_index)

    assert "docs_keywords" in result, "Result must not be empty"
    expected_keywords = [
        "mcp",
        "tools",
        "registry",
        "tooling",
        "discovery",
        "invocation",
        "capabilities",
        "plugins",
        "extensions",
        "management",
    ]
    for keyword in expected_keywords:
        assert keyword in result["docs_keywords"], "Result must not be empty"


def test_safeguards_metadata():
    """Test that safeguards metadata is present."""
    file_index = {"files": []}

    result = mcp_tooling_registry.detect(file_index)

    assert "meta" in result, "Result must not be empty"
    assert "safeguards" in result["meta"], "Result must not be empty"
    expected_safeguards = [
        "validation",
        "timeout",
        "error-isolation",
        "resource-limits",
        "audit-trail",
    ]
    for safeguard in expected_safeguards:
        assert safeguard in result["meta"]["safeguards"], "Result must not be empty"


def test_detector_version():
    """Test that detector version is present."""
    file_index = {"files": []}

    result = mcp_tooling_registry.detect(file_index)

    assert "detector_version" in result["meta"], "Result must not be empty"
    assert result["meta"]["detector_version"] == "1.1", "Result must not be empty"


def test_category_mcp():
    """Test that category is set to MCP."""
    file_index = {"files": []}

    result = mcp_tooling_registry.detect(file_index)

    assert result["meta"]["category"] == "mcp", "Result must not be empty"


def test_empty_file_index():
    """Test detection with empty file index."""
    file_index = {"files": []}

    result = mcp_tooling_registry.detect(file_index)

    assert result["id"] == "mcp-tooling-registry", "Result must not be empty"
    assert result["found_patterns"] == [], "Result must not be empty"
    assert result["evidence_files"] == [], "Result must not be empty"


def test_missing_path_key():
    """Test handling of files without 'path' key."""
    file_index = {
        "files": [
            {"name": "registry.py"},  # Missing 'path' key
            {"path": "mcp.json"},
        ]
    }

    # Should handle gracefully
    result = mcp_tooling_registry.detect(file_index)

    assert result["id"] == "mcp-tooling-registry", "Result must not be empty"
    # Should still find mcp.json
    assert "mcp.json" in result["found_patterns"], "Result must not be empty"


def test_deterministic_output():
    """Test that detector produces deterministic output."""
    file_index = {
        "files": [
            {"path": "mcp/registry.py"},
            {"path": "tools/plugin_registry.py"},
            {"path": "mcp.json"},
        ]
    }

    # Run detection multiple times
    results = [mcp_tooling_registry.detect(file_index) for _ in range(3)]

    # All results should be identical
    for i in range(1, len(results)):
        assert results[i]["found_patterns"] == results[0]["found_patterns"], "Result must not be empty"
        assert results[i]["evidence_files"] == results[0]["evidence_files"], "Result must not be empty"


def test_mcp_and_tool_keywords():
    """Test that both mcp/ and tool keywords trigger detection."""
    file_index_mcp = {"files": [{"path": "mcp/service/registry.py"}]}

    file_index_tool = {"files": [{"path": "tools/registry.py"}]}

    result_mcp = mcp_tooling_registry.detect(file_index_mcp)
    result_tool = mcp_tooling_registry.detect(file_index_tool)

    # Both should detect registry
    assert "registry" in result_mcp["found_patterns"], "Result must not be empty"
    assert "registry" in result_tool["found_patterns"], "Result must not be empty"
