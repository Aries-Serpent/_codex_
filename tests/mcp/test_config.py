"""
Tests for MCP configuration management.
"""

import json
import tempfile
from pathlib import Path

# NOTE: Do not manually manipulate sys.path. The conftest.py already adds src/ to sys.path.
from mcp.config import MCPConfig, ToolDefinition, compute_checksum


def test_compute_checksum():
    """Test SHA-256 checksum computation."""
    data = "test data"
    checksum = compute_checksum(data)

    # SHA-256 produces 64 character hex string
    assert len(checksum) == 64, "Checksum must not be empty"
    assert all(c in "0123456789abcdef" for c in checksum), "Condition must be true"

    # Same data should produce same checksum
    assert compute_checksum(data) == checksum, "Data must not be empty"


def test_tool_definition_from_dict():
    """Test ToolDefinition creation from dictionary."""
    data = {
        "name": "test_tool",
        "description": "A test tool",
        "endpoint": "http://example.com/tool",
    }

    tool = ToolDefinition.from_dict(data)
    assert tool.name == "test_tool", "name is not valid"
    assert tool.description == "A test tool", "description is not valid"
    assert tool.endpoint == "http://example.com/tool", "endpoint is not valid"


def test_mcp_config_load():
    """Test loading MCPConfig from file with checksum verification."""
    config = MCPConfig.load()

    # Should have loaded successfully
    assert config.name is not None, "name must be initialized"
    assert isinstance(config.tools, list)
    assert config.ita_url is not None, "ita_url must be initialized"

    # Should have computed checksum
    assert config.config_checksum is not None, "config_checksum must be initialized"
    assert len(config.config_checksum) == 64, "Collection must not be empty"


def test_mcp_config_get_tool():
    """Test retrieving tool by name."""
    config = MCPConfig.load()

    if config.tools:
        # Get first tool
        tool_name = config.tools[0].name
        tool = config.get_tool(tool_name)
        assert tool is not None, "tool must be initialized"
        assert tool.name == tool_name, "name is not valid"


def test_mcp_config_get_nonexistent_tool():
    """Test that getting nonexistent tool returns None."""
    config = MCPConfig.load()
    tool = config.get_tool("nonexistent_tool_xyz")
    assert tool is None, "tool is not valid"


def test_mcp_config_verify_integrity():
    """Test configuration integrity verification using checksum."""
    # Create temporary config file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        config_data = {"name": "test-config", "description": "Test configuration", "tools": []}
        json.dump(config_data, f)
        temp_path = Path(f.name)

    try:
        # Load config
        config = MCPConfig.load(temp_path)

        # Verify integrity - should pass
        assert config.verify_integrity(temp_path), "Condition must be true"

        # Modify file
        temp_path.write_text('{"modified": true}')

        # Verify integrity - should fail
        assert not config.verify_integrity(temp_path), "Condition must be true"

    finally:
        temp_path.unlink()


def test_mcp_config_env_override():
    """Test that environment variables override config values."""
    import os

    # Set environment variables
    os.environ["ITA_URL"] = "http://custom-url:9999"
    os.environ["ITA_API_KEY"] = "custom_key_123"

    try:
        config = MCPConfig.load()

        assert config.ita_url == "http://custom-url:9999", "ita_url is not valid"
        assert config.ita_api_key == "custom_key_123", "ita_api_key is not valid"

    finally:
        # Clean up
        os.environ.pop("ITA_URL", None)
        os.environ.pop("ITA_API_KEY", None)
