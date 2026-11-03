from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError

import pytest
import yaml

MODULE_PATH = Path(__file__).resolve().parents[2] / ".github" / "scripts" / "token_probe.py"
SPEC = importlib.util.spec_from_file_location("codex_token_probe", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
token_probe = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = token_probe
SPEC.loader.exec_module(token_probe)

NOW = datetime(2026, 11, 3, 6, 0, tzinfo=timezone.utc)
WORKFLOW_PATH = MODULE_PATH.parents[1] / "workflows" / "token-probe.yml"
OPTIMIZED_WORKFLOW_PATH = MODULE_PATH.parents[1] / "workflows" / "optimized-ci.yml"


class FakeResponse:
    def __init__(self, status: int, payload: bytes, headers: dict[str, str]) -> None:
        self.status = status
        self._payload = payload
        self.headers = headers
        self.closed = False

    def read(self) -> bytes:
        return self._payload

    def close(self) -> None:
        self.closed = True


def opener_for(response: FakeResponse):
    def open_url(request, *, timeout):
        assert request.full_url == "https://api.github.com/repos/Aries-Serpent/_codex_"
        assert request.get_header("Authorization") == "Bear" + "er " + "test-secret-value"
        assert timeout == 10
        return response

    return open_url


def test_missing_token_does_not_make_a_request() -> None:
    result = token_probe.probe_token(None, "Aries-Serpent/_codex_")

    assert result.status == "missing"
    assert result.usable_now is False
    assert result.token_type == "none"


def test_repository_read_access_preserves_colon_scopes_and_closes_response() -> None:
    response = FakeResponse(
        200,
        b'{"permissions":{"pull":true,"push":false}}',
        {
            "X-OAuth-Scopes": "repo, read:org, write:packages",
            "X-RateLimit-Remaining": "42",
            "GitHub-Authentication-Token-Expiration": "2026-11-10T00:00:00Z",
        },
    )
    result = token_probe.probe_token(
        "test-secret-value",
        "Aries-Serpent/_codex_",
        opener=opener_for(response),
        now=NOW,
    )

    assert result.status == "repository-readable"
    assert result.usable_now is True
    assert result.scopes == "repo, read:org, write:packages"
    assert result.repository_permissions == "pull"
    assert response.closed is True
    assert "test-secret-value" not in repr(result)


@pytest.mark.parametrize(
    ("status_code", "headers", "expected_status"),
    [
        (401, {}, "unauthorized"),
        (403, {"X-RateLimit-Remaining": "0"}, "rate-limited"),
        (403, {"X-RateLimit-Remaining": "10"}, "forbidden"),
        (404, {}, "not-found-or-inaccessible"),
        (429, {}, "rate-limited"),
        (503, {}, "service-unavailable"),
    ],
)
def test_http_failures_are_reported_without_claiming_access(
    status_code: int, headers: dict[str, str], expected_status: str
) -> None:
    response = FakeResponse(status_code, b"{}", headers)
    result = token_probe.probe_token(
        "test-secret-value",
        "Aries-Serpent/_codex_",
        opener=opener_for(response),
        now=NOW,
    )

    assert result.status == expected_status
    assert result.usable_now is False


def test_expired_and_expiring_tokens_are_distinguished() -> None:
    def run(expiration: str):
        response = FakeResponse(
            200,
            b'{"permissions":{"pull":true}}',
            {"GitHub-Authentication-Token-Expiration": expiration},
        )
        return token_probe.probe_token(
            "test-secret-value",
            "Aries-Serpent/_codex_",
            opener=opener_for(response),
            now=NOW,
        )

    expired = run("2026-11-03T05:59:59Z")
    expiring = run("2026-11-04T05:00:00Z")

    assert (expired.status, expired.usable_now) == ("expired", False)
    assert (expiring.status, expiring.usable_now) == ("expiring-soon", True)


def test_zero_rate_limit_blocks_current_usability() -> None:
    response = FakeResponse(
        200,
        b'{"permissions":{"pull":true}}',
        {"X-RateLimit-Remaining": "0"},
    )
    result = token_probe.probe_token(
        "test-secret-value",
        "Aries-Serpent/_codex_",
        opener=opener_for(response),
        now=NOW,
    )

    assert result.status == "rate-limited"
    assert result.usable_now is False


def test_unexpected_success_payload_is_not_treated_as_repository_access() -> None:
    response = FakeResponse(200, b"[]", {})
    result = token_probe.probe_token(
        "test-secret-value",
        "Aries-Serpent/_codex_",
        opener=opener_for(response),
        now=NOW,
    )

    assert result.status == "invalid-response"
    assert result.usable_now is False


def test_invalid_repository_slug_is_rejected_before_request() -> None:
    with pytest.raises(ValueError, match="owner/repository"):
        token_probe.probe_token("test-secret-value", "../repo")


def test_network_failure_is_not_misreported_as_invalid_token() -> None:
    def fail_open(request, *, timeout):
        raise URLError("unavailable")

    result = token_probe.probe_token("test-secret-value", "Aries-Serpent/_codex_", opener=fail_open)

    assert result.status == "probe-error"
    assert result.usable_now is False


def test_api_redirects_are_never_followed_with_credentials() -> None:
    handler = token_probe._RejectRedirectHandler()

    redirected = handler.redirect_request(
        request := token_probe.Request(
            "https://api.github.com/repos/Aries-Serpent/_codex_",
            headers={"Authorization": "Bear" + "er " + "test-secret-value"},
        ),
        object(),
        302,
        "Found",
        {},
        "https://attacker.example/collect",
    )

    assert request.get_header("Authorization") == "Bear" + "er " + "test-secret-value"
    assert redirected is None


def test_required_key_policy_and_markdown_cells() -> None:
    good = token_probe.ProbeResult(
        "repository-readable", True, "fine-grained-pat", "read:org|admin", "12", "unknown", "pull"
    )
    missing = token_probe.ProbeResult(
        "missing", False, "none", "not-reported", "unknown", "unknown", "unknown"
    )

    summary, passed = token_probe.render_summary(
        {"CODEX_MASTER_KEY": missing, "CODEX_BACKUP_KEY": good},
        require_both=False,
    )
    strict_summary, strict_passed = token_probe.render_summary(
        {"CODEX_MASTER_KEY": missing, "CODEX_BACKUP_KEY": good},
        require_both=True,
    )

    assert passed is True
    assert strict_passed is False
    assert "read:org\\|admin" in summary
    assert "**Result:** PASS" in summary
    assert "**Result:** FAIL" in strict_summary
    assert token_probe._markdown_cell("<script>|`") == "&lt;script&gt;\\|\\`"
    assert "[x](javascript:" not in token_probe._markdown_cell("[x](javascript:alert)")


def test_workflow_is_read_only_and_limited_to_trusted_branches() -> None:
    workflow = yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))
    job = workflow["jobs"]["probe-tokens"]
    checkout = job["steps"][0]

    assert set(workflow["on"]) == {"workflow_dispatch"}
    assert workflow["permissions"] == {"contents": "read"}
    assert job["if"] == ("github.ref == 'refs/heads/main' || github.ref == 'refs/heads/0D_base_'")
    assert checkout["with"]["ref"] == "${{ github.ref }}"
    assert checkout["with"]["persist-credentials"] is False


def test_optimized_cache_workflow_uses_shared_cache_paths_and_minor_python() -> None:
    workflow = yaml.safe_load(OPTIMIZED_WORKFLOW_PATH.read_text(encoding="utf-8"))
    setup = workflow["jobs"]["cache-dependencies"]["steps"][1]

    assert workflow["env"]["PIP_CACHE_DIR"] == "~/.cache/pip"
    assert workflow["env"]["UV_CACHE_DIR"] == "~/.cache/uv"
    assert setup["with"]["python-version"] == "3.12"
    assert "requirements/**" in workflow["on"]["push"]["paths"]
    assert ".github/actions/setup-python-cached/**" in workflow["on"]["push"]["paths"]
