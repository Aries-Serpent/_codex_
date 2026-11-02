"""Offline transport boundaries for the proactive CI monitor."""

from __future__ import annotations

import importlib.util
import io
import json
import logging
import sys
import urllib.error
import urllib.request
import urllib.response
from email.message import Message
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/ci/proactive_ci_monitor.py"
spec = importlib.util.spec_from_file_location("monitor_transport_integrity", SCRIPT)
assert spec is not None and spec.loader is not None
monitor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(monitor)

TOKEN = "offline-caller-fixture"
ORIGINAL_BUILD_OPENER = urllib.request.build_opener
ORIGINAL_OPENER_OPEN = urllib.request.OpenerDirector.open


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def denied(*args, **kwargs):
        pytest.fail("Real network access is forbidden in transport fixtures")

    monkeypatch.setattr(urllib.request, "urlopen", denied)
    monkeypatch.setattr(urllib.request.OpenerDirector, "open", denied)
    monkeypatch.setattr(urllib.request.HTTPHandler, "http_open", denied)
    monkeypatch.setattr(urllib.request.HTTPSHandler, "https_open", denied)
    monkeypatch.setattr(monitor, "_CI_HEALTH_AVAILABLE", False)


@pytest.fixture
def transport(monkeypatch):
    class Response(io.BytesIO):
        def __init__(self):
            super().__init__(b'{"ok": true}')
            self.read_sizes = []

        def read(self, size=-1):
            self.read_sizes.append(size)
            assert size == monitor._MAX_RESPONSE_BYTES + 1
            return super().read(size)

    class Transport:
        def __init__(self):
            self.response = Response()
            self.error = None
            self.handlers = ()
            self.requests = []

        def build_opener(self, *handlers):
            self.handlers = handlers
            return self

        def open(self, request, timeout):
            self.requests.append((request, timeout))
            if self.error is not None:
                raise self.error
            return self.response

    fixture = Transport()
    monkeypatch.setattr(urllib.request, "build_opener", fixture.build_opener)
    return fixture


def test_explicit_token_fixed_origin_and_direct_bounded_transport(transport, monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "different-environment-fixture")
    monkeypatch.setenv("HTTPS_PROXY", "http://untrusted.fixture:8080")
    assert monitor._gh("/repos/fixture/repo/pulls?state=open", TOKEN) == {"ok": True}
    request, timeout = transport.requests[0]
    assert request.full_url == "https://api.github.com/repos/fixture/repo/pulls?state=open"
    assert request.get_header("Authorization") == "Bearer " + TOKEN
    assert request.get_method() == "GET"
    assert timeout == 30
    assert transport.response.read_sizes == [monitor._MAX_RESPONSE_BYTES + 1]
    assert transport.response.closed
    proxies, redirects = transport.handlers
    assert isinstance(proxies, urllib.request.ProxyHandler)
    assert proxies.proxies == {}
    assert isinstance(redirects, monitor._NoRedirect)


def test_post_transport_preserves_explicit_body_and_method(transport):
    monitor._gh("/repos/fixture/repo/issues/1/comments", TOKEN, "POST", {"body": "fixture"})
    request, _ = transport.requests[0]
    assert request.get_method() == "POST"
    assert json.loads(request.data) == {"body": "fixture"}
    assert request.get_header("Authorization") == "Bearer " + TOKEN


@pytest.mark.parametrize("status", [301, 302, 303, 307, 308])
def test_redirects_are_denied_without_second_request(transport, status, caplog):
    target = "https://untrusted.fixture/" + TOKEN
    transport.error = urllib.error.HTTPError(
        "https://api.github.com/repos/fixture/repo", status, target, {"Location": target}, None
    )
    with caplog.at_level(logging.WARNING), pytest.raises(urllib.error.HTTPError) as caught:
        monitor._gh("/repos/fixture/repo", TOKEN)
    assert caught.value.code == status
    assert len(transport.requests) == 1
    request, _ = transport.requests[0]
    redirect_handler = transport.handlers[1]
    assert redirect_handler.redirect_request(request, None, status, target, {}, target) is None
    assert target not in str(caught.value)
    assert TOKEN not in "\n".join(caplog.messages)


@pytest.mark.parametrize("status", [301, 302, 303, 307, 308])
def test_real_opener_does_not_follow_injected_redirect(monkeypatch, status):
    requests = []
    headers = Message()
    headers["Location"] = "https://untrusted.fixture/" + TOKEN

    class FixtureHTTPS(urllib.request.HTTPSHandler):
        def https_open(self, request):
            requests.append(request)
            response = urllib.response.addinfourl(
                io.BytesIO(b"denied-" + TOKEN.encode()), headers, request.full_url, status
            )
            response.msg = "Fixture redirect"
            return response

    def fixture_opener(*handlers):
        opener = ORIGINAL_BUILD_OPENER(*handlers, FixtureHTTPS())

        class DirectOpener:
            def open(self, request, timeout):
                return ORIGINAL_OPENER_OPEN(opener, request, timeout=timeout)

        return DirectOpener()

    monkeypatch.setattr(urllib.request, "build_opener", fixture_opener)
    monkeypatch.setenv("HTTPS_PROXY", "http://untrusted.fixture:8080")
    with pytest.raises(urllib.error.HTTPError) as caught:
        monitor._gh("/repos/fixture/repo", TOKEN)
    assert caught.value.code == status
    assert len(requests) == 1
    assert requests[0].host == "api.github.com"
    assert not requests[0].has_proxy()
    assert requests[0].get_header("Authorization") == "Bearer " + TOKEN


@pytest.mark.parametrize(
    "path",
    [
        "",
        "repos/fixture/repo",
        "https://untrusted.fixture/repos/fixture",
        "//untrusted.fixture/repos/fixture",
        "/repos/fixture\\repo",
        "/repos/fixture\r\nInjected: value",
        "/repos/fixture\0repo",
        "/repos/fixture\trepo",
        "/repos/fixture repo",
        "/repos/fixturé/repo",
        "/repos/fixture#fragment",
        "/repos/%0arepo",
        "/repos/%00repo",
        "/repos/%5crepo",
        "/%2funtrusted.fixture",
        "/repos/../fixture",
        "/repos/%2e%2e/fixture",
        "/repos/.%2f./fixture",
        "/repos/%zz",
        "/repos/%",
        None,
    ],
)
def test_malformed_paths_fail_before_transport(transport, path):
    with pytest.raises(ValueError, match="invalid GitHub API path"):
        monitor._gh(path, TOKEN)
    assert not transport.requests
    assert not transport.handlers


@pytest.mark.parametrize("token", ["", "******", None, "bad\r\ntoken", " space", "bad\ttoken"])
def test_invalid_explicit_token_fails_closed_without_discovery(transport, monkeypatch, token):
    monkeypatch.setenv("GITHUB_TOKEN", TOKEN)
    with pytest.raises(ValueError, match="explicit GitHub API token required"):
        monitor._gh("/repos/fixture/repo", token)
    assert not transport.requests
    assert not transport.handlers


@pytest.mark.parametrize("oversize", [False, True])
def test_response_size_boundary(transport, oversize):
    limit = monitor._MAX_RESPONSE_BYTES
    transport.response = io.BytesIO(b" " * (limit - 2) + b"{}" + (b" " if oversize else b""))
    if oversize:
        with pytest.raises(ValueError, match="response exceeds size limit"):
            monitor._gh("/repos/fixture/repo", TOKEN)
    else:
        assert monitor._gh("/repos/fixture/repo", TOKEN) == {}
    assert transport.response.closed


@pytest.mark.parametrize("payload", [b"not-json-" + TOKEN.encode(), b"\xff" + TOKEN.encode()])
def test_malformed_response_errors_do_not_echo_body(transport, payload):
    transport.response = io.BytesIO(payload)
    with pytest.raises(ValueError, match="invalid JSON from GitHub API") as caught:
        monitor._gh("/repos/fixture/repo", TOKEN)
    assert TOKEN not in str(caught.value)
    assert transport.response.closed


def test_http_error_body_url_and_reason_never_logged_or_read(transport, caplog):
    class ForbiddenBody(io.BytesIO):
        def read(self, *args, **kwargs):
            pytest.fail("HTTP error bodies must not be read")

    body = ForbiddenBody(TOKEN.encode() * monitor._MAX_RESPONSE_BYTES)
    transport.error = urllib.error.HTTPError(
        "https://untrusted.fixture/" + TOKEN, 403, TOKEN + "\nforged log", {}, body
    )
    with caplog.at_level(logging.DEBUG), pytest.raises(urllib.error.HTTPError) as caught:
        monitor._gh("/repos/fixture/repo?fixture=" + TOKEN, TOKEN)
    assert body.closed
    assert caplog.messages == ["GitHub API request failed: HTTP 403"]
    assert str(caught.value) == "HTTP Error 403: GitHub API request failed"
    assert caught.value.url == "https://api.github.com"
    assert monitor._error_label(caught.value) == "HTTP 403"
    assert TOKEN not in "\n".join(record.getMessage() for record in caplog.records)


def test_transport_error_reason_is_safe(transport):
    transport.error = urllib.error.URLError("https://untrusted.fixture/" + TOKEN)
    with pytest.raises(urllib.error.URLError) as caught:
        monitor._gh("/repos/fixture/repo", TOKEN)
    assert TOKEN not in str(caught.value)
    assert str(caught.value.reason) == "GitHub API transport failed"


def test_cli_requires_existing_explicit_token_without_environment_fallback(monkeypatch, caplog):
    monkeypatch.setenv("GITHUB_TOKEN", TOKEN)
    monkeypatch.setattr(sys, "argv", ["proactive_ci_monitor.py", "--repo", "fixture/repo"])

    def forbidden(*args, **kwargs):
        pytest.fail("No explicit token must fail before scanning")

    monkeypatch.setattr(monitor, "scan", forbidden)
    assert monitor.main() == 1
    assert "--token is required" in caplog.messages


@pytest.mark.parametrize("posting", [False, True])
def test_callers_log_safe_http_error_labels(monkeypatch, caplog, posting):
    def denied(*args, **kwargs):
        raise urllib.error.HTTPError("https://untrusted.fixture/" + TOKEN, 403, TOKEN, {}, None)

    monkeypatch.setattr(monitor, "_gh", denied)
    with caplog.at_level(logging.DEBUG):
        if posting:
            assert not monitor._post_rescue_comment(
                "fixture/repo",
                1,
                "a" * 40,
                {"id": 2},
                {"id": "fixture", "category": "unknown", "fix": "inspect"},
                False,
                TOKEN,
            )
        else:
            report = monitor.scan("fixture/repo", TOKEN, True, 24, target_pr=1)
            assert not report["complete"]
            assert report["exit_code"] == 1
            assert report["errors"] == ["PR #1: HTTP 403"]
    assert TOKEN not in "\n".join(caplog.messages)
    assert "HTTP 403" in caplog.messages[-1]
