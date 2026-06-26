"""
Tests for MCP configuration management detector.

Tests detection of configuration files, environment handling, and mcp.json schema.
"""

from scripts.space_traversal.detectors import mcp_configuration


def test_detect_no_config():
    """Test detection with no configuration files."""
    file_index = {
        "files": [
            {"path": "src/app/main.py", "ext": "py", "size": 100, "sha": "abc123"},
            {"path": "src/app/utils.py", "ext": "py", "size": 50, "sha": "def456"},
        ]
    }

    result = mcp_configuration.detect(file_index)

    assert result["id"] == "mcp-configuration", "Result must not be empty"
    assert result["found_patterns"] == [], "Result must not be empty"
    assert "config" in result["required_patterns"], "Result must not be empty"
    assert "environment" in result["required_patterns"], "Result must not be empty"
    assert "mcp.json" in result["required_patterns"], "Result must not be empty"


def test_detect_mcp_json():
    """Test detection of mcp.json configuration file."""
    file_index = {
        "files": [
            {"path": "mcp.json", "ext": "json", "size": 200, "sha": "xyz"},
            {"path": "src/app/main.py", "ext": "py", "size": 100, "sha": "abc"},
        ]
    }

    result = mcp_configuration.detect(file_index)

    assert "mcp.json" in result["found_patterns"], "Result must not be empty"
    assert "mcp.json" in result["evidence_files"], "Result must not be empty"


def test_detect_env_file():
    """Test detection of .env environment file."""
    file_index = {
        "files": [
            {"path": ".env", "ext": "", "size": 150, "sha": "env123"},
            {"path": ".env.example", "ext": "example", "size": 100, "sha": "env456"},
        ]
    }

    result = mcp_configuration.detect(file_index)

    assert "environment" in result["found_patterns"], "Result must not be empty"
    assert ".env" in result["evidence_files"], "Result must not be empty"
    assert ".env.example" in result["evidence_files"], "Result must not be empty"


def test_detect_config_yaml():
    """Test detection of YAML configuration files."""
    file_index = {
        "files": [
            {"path": "config.yaml", "ext": "yaml", "size": 300, "sha": "yaml1"},
            {"path": "config/app.yml", "ext": "yml", "size": 200, "sha": "yaml2"},
        ]
    }

    result = mcp_configuration.detect(file_index)

    assert "config" in result["found_patterns"], "Result must not be empty"
    assert "config.yaml" in result["evidence_files"], "Result must not be empty"


def test_detect_settings_py():
    """Test detection of Python settings files."""
    file_index = {
        "files": [
            {"path": "settings.py", "ext": "py", "size": 400, "sha": "set1"},
            {"path": "configuration.py", "ext": "py", "size": 350, "sha": "set2"},
        ]
    }

    result = mcp_configuration.detect(file_index)

    assert "config" in result["found_patterns"], "Result must not be empty"
    assert "settings.py" in result["evidence_files"], "Result must not be empty"
    assert "configuration.py" in result["evidence_files"], "Result must not be empty"


def test_detect_all_patterns():
    """Test detection of all configuration patterns."""
    file_index = {
        "files": [
            {"path": "mcp.json", "ext": "json", "size": 200, "sha": "a"},
            {"path": ".env", "ext": "", "size": 150, "sha": "b"},
            {"path": "config.yaml", "ext": "yaml", "size": 300, "sha": "c"},
            {"path": "settings.py", "ext": "py", "size": 400, "sha": "d"},
        ]
    }

    result = mcp_configuration.detect(file_index)

    assert "mcp.json" in result["found_patterns"], "Result must not be empty"
    assert "environment" in result["found_patterns"], "Result must not be empty"
    assert "config" in result["found_patterns"], "Result must not be empty"
    assert len(result["evidence_files"]) == 4, "Collection must not be empty"


def test_detect_mcp_directory():
    """Test detection of config files in mcp/ directory."""
    file_index = {
        "files": [
            {"path": "mcp/config/settings.yaml", "ext": "yaml", "size": 200, "sha": "x"},
            {"path": "mcp/mcp_config.json", "ext": "json", "size": 150, "sha": "y"},
        ]
    }

    result = mcp_configuration.detect(file_index)

    assert "config" in result["found_patterns"], "Result must not be empty"
    assert "mcp.json" in result["found_patterns"], "Result must not be empty"
    assert len(result["evidence_files"]) > 0, "Collection must not be empty"


def test_detect_services_directory():
    """Test detection of config files in services/ directory."""
    file_index = {
        "files": [
            {"path": "services/mcp/configuration.py", "ext": "py", "size": 250, "sha": "s1"},
            {"path": "services/api/env_vars.py", "ext": "py", "size": 100, "sha": "s2"},
        ]
    }

    result = mcp_configuration.detect(file_index)

    assert len(result["found_patterns"]) > 0, "Collection must not be empty"
    assert len(result["evidence_files"]) > 0, "Collection must not be empty"


def test_evidence_deduplication():
    """Test that evidence files are deduplicated."""
    file_index = {
        "files": [
            {"path": "config.yaml", "ext": "yaml", "size": 200, "sha": "a"},
            {"path": "config/settings.py", "ext": "py", "size": 150, "sha": "b"},
        ]
    }

    result = mcp_configuration.detect(file_index)

    # Check no duplicates
    assert len(result["evidence_files"]) == len(set(result["evidence_files"])), "Collection must not be empty"


def test_sorted_output():
    """Test that output lists are sorted."""
    file_index = {
        "files": [
            {"path": "z_config.yaml", "ext": "yaml", "size": 200, "sha": "z"},
            {"path": "a_settings.py", "ext": "py", "size": 150, "sha": "a"},
            {"path": ".env", "ext": "", "size": 100, "sha": "e"},
        ]
    }

    result = mcp_configuration.detect(file_index)

    # found_patterns should be sorted
    assert result["found_patterns"] == sorted(result["found_patterns"]), "Result must not be empty"
    # evidence_files should be sorted
    assert result["evidence_files"] == sorted(result["evidence_files"]), "Result must not be empty"


def test_docs_keywords_present():
    """Test that required docs_keywords are present."""
    file_index = {"files": []}

    result = mcp_configuration.detect(file_index)

    assert "docs_keywords" in result, "Result must not be empty"
    expected_keywords = [
        "mcp",
        "configuration",
        "settings",
        "environment",
        "mcp.json",
        "config",
        "management",
        "runtime",
        "validation",
    ]
    for keyword in expected_keywords:
        assert keyword in result["docs_keywords"], "Result must not be empty"


def test_safeguards_metadata():
    """Test that safeguards metadata is present."""
    file_index = {"files": []}

    result = mcp_configuration.detect(file_index)

    assert "meta" in result, "Result must not be empty"
    assert "safeguards" in result["meta"], "Result must not be empty"
    expected_safeguards = ["validation", "type-checking", "bounds-checking", "secret-management"]
    for safeguard in expected_safeguards:
        assert safeguard in result["meta"]["safeguards"], "Result must not be empty"


def test_detector_version():
    """Test that detector version is present."""
    file_index = {"files": []}

    result = mcp_configuration.detect(file_index)

    assert "detector_version" in result["meta"], "Result must not be empty"
    assert result["meta"]["detector_version"] == "1.1", "Result must not be empty"


def test_category_and_layer():
    """Test that category and layer are set correctly."""
    file_index = {"files": []}

    result = mcp_configuration.detect(file_index)

    assert result["meta"]["category"] == "mcp", "Result must not be empty"
    assert result["meta"]["layer"] == "infrastructure", "Result must not be empty"


def test_config_types_metadata():
    """Test that config types are documented."""
    file_index = {"files": []}

    result = mcp_configuration.detect(file_index)

    assert "config_types" in result["meta"], "Result must not be empty"
    expected_types = ["mcp.json", "environment", "yaml", "python"]
    for cfg_type in expected_types:
        assert cfg_type in result["meta"]["config_types"], "Result must not be empty"


def test_case_insensitive_matching():
    """Test that file matching is case-insensitive."""
    file_index = {
        "files": [
            {"path": "CONFIG.YAML", "ext": "yaml", "size": 200, "sha": "a"},
            {"path": "SETTINGS.PY", "ext": "py", "size": 150, "sha": "b"},
        ]
    }

    result = mcp_configuration.detect(file_index)

    # Should still detect config patterns
    assert "config" in result["found_patterns"], "Result must not be empty"
    assert len(result["evidence_files"]) > 0, "Collection must not be empty"


def test_empty_file_index():
    """Test detection with empty file index."""
    file_index = {"files": []}

    result = mcp_configuration.detect(file_index)

    assert result["id"] == "mcp-configuration", "Result must not be empty"
    assert result["found_patterns"] == [], "Result must not be empty"
    assert result["evidence_files"] == [], "Result must not be empty"


def test_deterministic_output():
    """Test that detector produces deterministic output."""
    file_index = {
        "files": [
            {"path": "mcp.json", "ext": "json", "size": 200, "sha": "a"},
            {"path": ".env", "ext": "", "size": 150, "sha": "b"},
            {"path": "config.yaml", "ext": "yaml", "size": 300, "sha": "c"},
        ]
    }

    # Run detection multiple times
    results = [mcp_configuration.detect(file_index) for _ in range(3)]

    # All results should be identical
    for i in range(1, len(results)):
        assert results[i]["found_patterns"] == results[0]["found_patterns"], "Result must not be empty"
        assert results[i]["evidence_files"] == results[0]["evidence_files"], "Result must not be empty"
