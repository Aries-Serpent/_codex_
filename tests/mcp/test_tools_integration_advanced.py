import sys
from pathlib import Path

import pytest

repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))

from mcp.errors import ConfirmationRequired, DryRunRequired, ValidationError
from mcp.registry import MCPToolRegistry


def _registry():
    return MCPToolRegistry()


def test_tools_integration_registry_stores_checksum():
    registry = _registry()
    registry.register_tool("secure", lambda **_: None, metadata={"confirm": True})
    metadata = registry.get_metadata("secure")
    assert "checksum" in metadata


def test_tools_integration_registry_requires_confirmation():
    registry = _registry()
    registry.register_tool("danger", lambda **_: None, metadata={"confirm": True})
    with pytest.raises(ConfirmationRequired):
        registry.enforce_safeguards("danger", {"confirm": False})


def test_tools_integration_registry_allows_confirmation_flag():
    registry = _registry()
    registry.register_tool("safe", lambda **_: None, metadata={"confirm": True})
    registry.enforce_safeguards("safe", {"confirm": True})


def test_tools_integration_registry_denies_dry_run_when_disabled():
    registry = _registry()
    registry.register_tool("mutate", lambda **_: None, metadata={"dry_run": False})
    with pytest.raises(DryRunRequired):
        registry.enforce_safeguards("mutate", {"dry_run": True})


def test_tools_integration_registry_allows_dry_run_when_supported():
    registry = _registry()
    registry.register_tool("readonly", lambda **_: None, metadata={"dry_run": True})
    registry.enforce_safeguards("readonly", {"dry_run": True})


def test_tools_integration_registry_offline_flag():
    registry = _registry()
    registry.register_tool("offline", lambda **_: None)
    assert "offline" in registry.get_metadata("offline")["safeguards"]


def test_tools_integration_registry_metadata_signature():
    registry = _registry()
    registry.register_tool("sig", lambda **_: None)
    assert "signature" in registry.get_metadata("sig")


def test_tools_integration_registry_unknown_tool():
    registry = _registry()
    with pytest.raises(ValidationError):
        registry.get_metadata("missing")


def test_tools_integration_registry_list_tools_contains_metadata():
    registry = _registry()
    registry.register_tool("listed", lambda **_: None, metadata={"description": "x"})
    listed = registry.list_tools()[0]
    assert listed["metadata"]["description"] == "x"


def test_tools_integration_registry_enforce_safeguards_missing_confirm():
    registry = _registry()
    registry.register_tool("confirm", lambda **_: None, metadata={"confirm": True})
    with pytest.raises(ConfirmationRequired):
        registry.enforce_safeguards("confirm", {})


def test_tools_integration_registry_enforce_safeguards_allows_default():
    registry = _registry()
    registry.register_tool("default", lambda **_: None)
    registry.enforce_safeguards("default", {})


def test_tools_integration_registry_enforce_safeguards_for_dry_run_default():
    registry = _registry()
    registry.register_tool("dry", lambda **_: None, metadata={"dry_run": True})
    registry.enforce_safeguards("dry", {"dry_run": False})


def test_tools_integration_registry_enforce_safeguards_optional_confirm():
    registry = _registry()
    registry.register_tool("optional", lambda **_: None, metadata={"confirm": False})
    registry.enforce_safeguards("optional", {"confirm": False})


def test_tools_integration_registry_multiple_tools():
    registry = _registry()
    registry.register_tool("one", lambda **_: None)
    registry.register_tool("two", lambda **_: None)
    assert len(registry.list_tools()) == 2


def test_tools_integration_registry_metadata_checksum_unique():
    registry = _registry()
    registry.register_tool("unique", lambda **_: None)
    registry.register_tool("unique2", lambda **_: None)
    checksums = {
        registry.get_metadata("unique")["checksum"],
        registry.get_metadata("unique2")["checksum"],
    }
    assert len(checksums) == 2


def test_tools_integration_registry_schema_preserved():
    registry = _registry()
    registry.register_tool("schema", lambda **_: None, schema={"title": "schema"})
    assert registry.list_tools()[0]["schema"]["title"] == "schema"


def test_tools_integration_registry_offline_mode_exposed():
    registry = MCPToolRegistry(offline=True)
    assert registry.offline_mode() is True


def test_tools_integration_registry_metadata_signature_changes():
    registry = _registry()
    registry.register_tool("sig1", lambda **_: None)
    registry.register_tool("sig2", lambda **_: None, metadata={"description": "diff"})
    sigs = {
        registry.get_metadata("sig1")["signature"],
        registry.get_metadata("sig2")["signature"],
    }
    assert len(sigs) == 2


def test_tools_integration_registry_confirm_flag_default():
    registry = _registry()
    registry.register_tool("flag", lambda **_: None)
    assert registry.get_metadata("flag").get("confirm") is False


def test_tools_integration_registry_dry_run_default():
    registry = _registry()
    registry.register_tool("dryflag", lambda **_: None)
    assert registry.get_metadata("dryflag").get("dry_run") is False


def test_tools_integration_registry_enforce_multiple_calls():
    registry = _registry()
    registry.register_tool("multi", lambda **_: None, metadata={"confirm": True})
    with pytest.raises(ConfirmationRequired):
        registry.enforce_safeguards("multi", {})
    registry.enforce_safeguards("multi", {"confirm": True})


def test_tools_integration_registry_metadata_contains_endpoint():
    registry = _registry()
    registry.register_tool("endpoint", lambda **_: None, metadata={"endpoint": "/v1"})
    assert registry.get_metadata("endpoint")["endpoint"] == "/v1"


def test_tools_integration_registry_metadata_custom_fields():
    registry = _registry()
    registry.register_tool("custom", lambda **_: None, metadata={"tenant": "a"})
    assert registry.get_metadata("custom")["tenant"] == "a"


def test_tools_integration_registry_safeguard_structure():
    registry = _registry()
    registry.register_tool("structure", lambda **_: None)
    safeguards = registry.get_metadata("structure")["safeguards"]
    assert "requires_confirmation" in safeguards


def test_tools_integration_registry_metadata_copy_isolated():
    registry = _registry()
    original = {"description": "orig"}
    registry.register_tool("iso", lambda **_: None, metadata=original)
    original["description"] = "mutated"
    assert registry.get_metadata("iso")["description"] == "orig"


def test_tools_integration_registry_handles_empty_metadata():
    registry = _registry()
    registry.register_tool("empty", lambda **_: None)
    assert registry.get_metadata("empty")["safeguards"]
