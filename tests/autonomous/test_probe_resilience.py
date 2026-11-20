"""Resilience tests for redacted credential and maintainer probes."""

from __future__ import annotations

import io
import json
import socket
import urllib.error
from typing import Any

import pytest

from scripts.autonomous import credential_probe, maintainer_probe


class MalformedJsonResponse:
    status = 200
    headers: dict[str, str] = {}

    def __enter__(self) -> "MalformedJsonResponse":
        return self

    def __exit__(self, *args: Any) -> None:
        return None

    def read(self) -> bytes:
        return b"{not-json"


@pytest.mark.parametrize(
    ("failure", "error_type"),
    [
        (urllib.error.URLError("network unavailable"), "url_error"),
        (urllib.error.URLError(socket.gaierror("dns lookup failed")), "dns_error"),
        (socket.gaierror("dns lookup failed"), "dns_error"),
        (TimeoutError("timed out"), "timeout"),
        (OSError("connection reset"), "os_error"),
    ],
)
def test_credential_request_normalizes_network_failures(
    monkeypatch: pytest.MonkeyPatch,
    failure: BaseException,
    error_type: str,
) -> None:
    def fail(*args: Any, **kwargs: Any) -> None:
        raise failure

    monkeypatch.setattr(credential_probe.urllib.request, "urlopen", fail)

    result = credential_probe.request_json("/user", "redacted")

    assert result["status"] is None
    assert result["error_type"] == error_type
    assert "redacted" not in result["message"]


def test_credential_request_normalizes_malformed_json(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        credential_probe.urllib.request,
        "urlopen",
        lambda *args, **kwargs: MalformedJsonResponse(),
    )

    result = credential_probe.request_json("/user", "redacted")

    assert result["status"] is None
    assert result["error_type"] == "malformed_json"


def test_credential_github_url_has_a_fixed_origin() -> None:
    assert (
        credential_probe.github_api_url("/repos/Aries-Serpent/_codex_?per_page=1")
        == "https://api.github.com/repos/Aries-Serpent/_codex_?per_page=1"
    )
    with pytest.raises(ValueError):
        credential_probe.github_api_url("https://example.invalid/override")
    with pytest.raises(ValueError):
        credential_probe.github_api_url("//example.invalid/override")


def test_credential_http_error_does_not_read_or_report_body(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret = "token-body-must-not-escape"
    body = io.BytesIO(secret.encode())
    failure = urllib.error.HTTPError(
        "https://api.github.com/user",
        403,
        "Forbidden",
        {},
        body,
    )

    def fail(*args: Any, **kwargs: Any) -> None:
        raise failure

    monkeypatch.setattr(credential_probe.urllib.request, "urlopen", fail)

    result = credential_probe.request_json("/user", "redacted-token")

    assert result["status"] == 403
    assert result["message"] == "http_error"
    assert secret not in json.dumps(result)
    assert body.tell() == 0


def test_credential_unexpected_exception_is_sanitized_and_continues(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    def request(path: str, token: str, **kwargs: Any) -> dict[str, Any]:
        calls.append(path)
        if path == "/user":
            raise ValueError(f"request leaked token={token} body=exception-body-sentinel")
        return {"status": 200, "payload": {}}

    monkeypatch.setattr(credential_probe, "request_json", request)

    result = credential_probe.probe_source("GITHUB_TOKEN", "secret-token")

    assert len(calls) == len(credential_probe.READ_PROBES) + 1
    assert result["identity_error_type"] == "probe_exception"
    assert "secret-token" not in json.dumps(result)
    assert "exception-body-sentinel" not in json.dumps(result)


def test_credential_source_continues_after_a_failed_read(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def request(path: str, token: str, **kwargs: Any) -> dict[str, Any]:
        calls.append(path)
        if path == "/user":
            return {"status": None, "error_type": "url_error", "message": "offline"}
        return {"status": 200, "payload": {}}

    monkeypatch.setattr(credential_probe, "request_json", request)

    result = credential_probe.probe_source("GITHUB_TOKEN", "redacted")

    assert len(result["reads"]) == len(credential_probe.READ_PROBES)
    assert len(calls) == len(credential_probe.READ_PROBES) + 1
    assert result["identity_status"] is None
    assert result["identity_error_type"] == "url_error"
    assert all(probe["error_type"] is None for probe in result["reads"].values())


@pytest.mark.parametrize(
    ("probe", "expected_type"),
    [
        (maintainer_probe.github_identity_probe, "url_error"),
        (maintainer_probe.public_repo_probe, "url_error"),
    ],
)
def test_maintainer_http_probes_normalize_url_errors(
    monkeypatch: pytest.MonkeyPatch,
    probe: Any,
    expected_type: str,
) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "redacted")

    def fail(*args: Any, **kwargs: Any) -> None:
        raise urllib.error.URLError("dns lookup failed")

    monkeypatch.setattr(maintainer_probe.urllib.request, "urlopen", fail)

    result = probe()

    assert result["error_type"] == expected_type
    assert "redacted" not in result["message"]


def test_maintainer_identity_normalizes_malformed_json(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "redacted")
    monkeypatch.setattr(
        maintainer_probe.urllib.request,
        "urlopen",
        lambda *args, **kwargs: MalformedJsonResponse(),
    )

    result = maintainer_probe.github_identity_probe()

    assert result["error_type"] == "malformed_json"
    assert result["http_status"] is None


def test_maintainer_http_error_does_not_report_body(monkeypatch: pytest.MonkeyPatch) -> None:
    secret = "private-http-body-and-token"
    body = io.BytesIO(secret.encode())
    failure = urllib.error.HTTPError(
        "https://api.github.com/user",
        401,
        "Unauthorized",
        {},
        body,
    )

    def fail(*args: Any, **kwargs: Any) -> None:
        raise failure

    monkeypatch.setenv("GITHUB_TOKEN", "redacted-token")
    monkeypatch.setattr(maintainer_probe.urllib.request, "urlopen", fail)

    result = maintainer_probe.github_identity_probe()

    assert result["error_type"] == "http_error"
    assert result["message"] == "http_error"
    assert secret not in json.dumps(result)
    assert body.tell() == 0


def test_maintainer_report_removes_exception_text() -> None:
    secret = "exception-token-and-body"

    def fail() -> dict[str, Any]:
        raise OSError(secret)

    result = maintainer_probe.report_probe(fail)

    assert result == {
        "attempted": True,
        "error_type": "probe_exception",
        "message": "probe_exception",
    }
    assert secret not in json.dumps(result)


def test_cli_probe_report_redacts_url_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "CODEX_CLI_API_URL",
        "http://build-user:secret-token@127.0.0.1:8765/?token=private",
    )

    result = maintainer_probe.cli_api_probe()

    assert result["blocked_reason"] == "origin_not_approved"
    assert "secret-token" not in json.dumps(result)
    assert "token=private" not in json.dumps(result)
    assert maintainer_probe.approved_api_origin("http://localhost:8765") is True
    assert maintainer_probe.approved_api_origin("http://localhost:8765/private") is False
    assert maintainer_probe.approved_api_origin("http://localhost:8765?private=true") is False


def test_maintainer_main_continues_after_probe_exception(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fail_git() -> dict[str, Any]:
        raise OSError("git unavailable")

    monkeypatch.setattr(maintainer_probe, "git_state", fail_git)
    monkeypatch.setattr(maintainer_probe, "github_identity_probe", lambda: {"attempted": False})
    monkeypatch.setattr(maintainer_probe, "gh_probe", lambda: {"installed": False})
    monkeypatch.setattr(maintainer_probe, "public_repo_probe", lambda: {"http_status": 200})
    monkeypatch.setattr(maintainer_probe, "cli_api_probe", lambda: {"reachable": False})
    monkeypatch.setattr(maintainer_probe, "mcp_probe", lambda: {"probe_available": True})
    monkeypatch.setattr(
        maintainer_probe, "vscode_extension_probe", lambda: {"code_cli_available": False}
    )

    assert maintainer_probe.main() == 0

    report = json.loads(capsys.readouterr().out)
    assert report["git"]["error_type"] == "probe_exception"
    assert report["github_identity"] == {"attempted": False}
    assert report["public_repository"] == {"http_status": 200}
    assert "workspace_files" in report
