import json
import os
import sys
from pathlib import Path

import pytest

repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))

from mcp.config import MCPConfig, ToolDefinition, compute_checksum
from mcp.registry import MCPToolRegistry


def _write_config(tmp_path, tools):
    payload = {"name": "schema-test", "description": "", "tools": tools}
    path = tmp_path / "mcp.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_schema_validation_tool_definition_round_trip():
    payload = {"name": "alpha", "description": "Alpha tool", "endpoint": "/alpha"}
    tool = ToolDefinition.from_dict(payload)
    assert tool.name == "alpha"
    assert tool.description == "Alpha tool"
    assert tool.endpoint == "/alpha"


def test_schema_validation_tool_definition_missing_field():
    payload = {"name": "beta", "description": ""}
    with pytest.raises(KeyError):
        ToolDefinition.from_dict(payload)


def test_schema_validation_config_loads_tools(tmp_path, monkeypatch):
    tools = [{"name": "gamma", "description": "Gamma", "endpoint": "/gamma"}]
    config_path = _write_config(tmp_path, tools)
    monkeypatch.setenv("ITA_URL", "http://ita:9999")
    config = MCPConfig.load(config_path)
    assert config.get_tool("gamma").endpoint == "/gamma"


def test_schema_validation_config_checksum_changes(tmp_path):
    config_path = _write_config(tmp_path, [])
    cfg = MCPConfig.load(config_path)
    original = cfg.config_checksum
    config_path.write_text('{"name": "changed", "tools": []}', encoding="utf-8")
    cfg2 = MCPConfig.load(config_path)
    assert cfg2.config_checksum != original


def test_schema_validation_config_integrity_detects_changes(tmp_path):
    config_path = _write_config(tmp_path, [])
    cfg = MCPConfig.load(config_path)
    assert cfg.verify_integrity(config_path)
    config_path.write_text('{"tampered": true}', encoding="utf-8")
    assert not cfg.verify_integrity(config_path)


def test_schema_validation_config_respects_env_url(tmp_path, monkeypatch):
    config_path = _write_config(tmp_path, [])
    monkeypatch.setenv("ITA_URL", "http://custom-host:8080")
    cfg = MCPConfig.load(config_path)
    assert cfg.ita_url == "http://custom-host:8080"


def test_schema_validation_config_handles_no_tools(tmp_path):
    config_path = _write_config(tmp_path, [])
    cfg = MCPConfig.load(config_path)
    assert cfg.tools == []


def test_schema_validation_tool_definition_handles_extra_fields():
    payload = {"name": "delta", "description": "", "endpoint": "/delta", "extra": 1}
    tool = ToolDefinition.from_dict(payload)
    assert tool.name == "delta"


def test_schema_validation_tool_definition_schema_isolation():
    registry = MCPToolRegistry()
    registry.register_tool("epsilon", lambda **_: {}, schema={"type": "object"}, metadata={})
    tools = registry.list_tools()
    assert tools[0]["schema"]["type"] == "object"


def test_schema_validation_config_iterates_tools(tmp_path):
    config_path = _write_config(tmp_path, [
        {"name": "zeta", "description": "", "endpoint": "/zeta"},
        {"name": "eta", "description": "", "endpoint": "/eta"},
    ])
    cfg = MCPConfig.load(config_path)
    assert sorted(tool.name for tool in cfg.tools) == ["eta", "zeta"]


def test_schema_validation_compute_checksum_length():
    checksum = compute_checksum("payload")
    assert len(checksum) == 64


def test_schema_validation_compute_checksum_uniqueness():
    assert compute_checksum("a") != compute_checksum("b")


def test_schema_validation_config_returns_none_for_missing_tool(tmp_path):
    config_path = _write_config(tmp_path, [])
    cfg = MCPConfig.load(config_path)
    assert cfg.get_tool("missing") is None


def test_schema_validation_config_returns_tool(tmp_path):
    config_path = _write_config(tmp_path, [
        {"name": "theta", "description": "", "endpoint": "/theta"}
    ])
    cfg = MCPConfig.load(config_path)
    assert cfg.get_tool("theta").name == "theta"


def test_schema_validation_config_env_api_key(tmp_path, monkeypatch):
    config_path = _write_config(tmp_path, [])
    monkeypatch.setenv("ITA_API_KEY", "secret")
    cfg = MCPConfig.load(config_path)
    assert cfg.ita_api_key == "secret"


def test_schema_validation_config_default_url(tmp_path):
    config_path = _write_config(tmp_path, [])
    cfg = MCPConfig.load(config_path)
    assert cfg.ita_url.startswith("http://")


def test_schema_validation_tool_definition_hash_consistency():
    payload = {"name": "iota", "description": "", "endpoint": "/iota"}
    tool = ToolDefinition.from_dict(payload)
    assert tool.endpoint.endswith("iota")


def test_schema_validation_tool_schema_export(tmp_path):
    config_path = _write_config(tmp_path, [
        {"name": "kappa", "description": "", "endpoint": "/kappa"}
    ])
    cfg = MCPConfig.load(config_path)
    registry = MCPToolRegistry()
    for tool in cfg.tools:
        registry.register_tool(tool.name, lambda **_: {}, schema={"title": tool.name})
    metadata = registry.list_tools()
    assert metadata[0]["schema"]["title"] == "kappa"


def test_schema_validation_config_supports_multiple_tools(tmp_path):
    tools = [
        {"name": "lambda", "description": "", "endpoint": "/lambda"},
        {"name": "mu", "description": "", "endpoint": "/mu"},
    ]
    config_path = _write_config(tmp_path, tools)
    cfg = MCPConfig.load(config_path)
    assert len(cfg.tools) == 2


def test_schema_validation_config_description_default(tmp_path):
    config_path = _write_config(tmp_path, [])
    cfg = MCPConfig.load(config_path)
    assert cfg.description == ""
