import sys
from pathlib import Path

repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))

from mcp.errors import (
    ConfirmationRequired,
    DryRunRequired,
    MCPError,
    OfflineOnly,
    RateLimitExceeded,
    ToolNotFound,
    Unauthorized,
    ValidationError,
)


def test_error_serialization_contains_checksum():
    err = MCPError("boom")
    payload = err.to_dict()
    assert "checksum" in payload


def test_error_checksum_changes_with_message():
    e1 = MCPError("a").to_dict()["checksum"]
    e2 = MCPError("b").to_dict()["checksum"]
    assert e1 != e2


def test_tool_not_found_status_code():
    assert ToolNotFound().http_status == 404


def test_validation_error_status_code():
    assert ValidationError().http_status == 400


def test_rate_limit_error_status_code():
    assert RateLimitExceeded().http_status == 429


def test_unauthorized_status_code():
    assert Unauthorized().http_status == 401


def test_offline_only_sets_offline_hint():
    payload = OfflineOnly().to_dict()
    assert payload["offline"] is True


def test_confirmation_required_code():
    err = ConfirmationRequired()
    assert err.code < 0
    assert err.symbol == "CONFIRMATION_REQUIRED"


def test_dry_run_required_code():
    err = DryRunRequired()
    assert err.code < 0
    assert err.symbol == "DRY_RUN_REQUIRED"


def test_error_defaults_to_code_message():
    assert MCPError().message == "MCP_ERROR"


def test_error_context_is_serialized():
    err = MCPError("boom", context={"offline": True})
    assert err.to_dict()["context"]["offline"] is True


def test_confirmation_required_message_customization():
    err = ConfirmationRequired("Need confirm")
    assert err.message == "Need confirm"


def test_dry_run_required_message_customization():
    err = DryRunRequired("dry run missing")
    assert err.message == "dry run missing"


def test_offline_only_context_propagates():
    err = OfflineOnly("offline", context={"offline": True})
    assert err.to_dict()["context"]["offline"] is True


def test_tool_not_found_serialization_contains_code():
    err = ToolNotFound("missing")
    assert err.to_dict()["symbol"] == "TOOL_NOT_FOUND"


def test_validation_error_serialization_contains_message():
    err = ValidationError("invalid")
    data = err.to_dict()
    assert data["message"] == "invalid"
    assert data["symbol"] == "VALIDATION_ERROR"


def test_rate_limit_error_contains_checksum():
    err = RateLimitExceeded("too many")
    assert len(err.to_dict()["checksum"]) == 64


def test_unauthorized_error_contains_checksum():
    err = Unauthorized("forbidden")
    assert len(err.to_dict()["checksum"]) == 64


def test_confirmation_required_has_http_status():
    assert ConfirmationRequired().http_status == 412


def test_dry_run_required_has_http_status():
    assert DryRunRequired().http_status == 428
