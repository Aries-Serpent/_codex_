"""The authenticated approval transport never follows redirects or ambient proxies."""

import urllib.error
import urllib.request

import pytest

from scripts.ci import approve_pending_runs as approval


def test_redirect_is_not_followed():
    request = urllib.request.Request("https://api.github.com/repos/o/r/actions/runs")
    assert (
        approval._NoRedirect().redirect_request(
            request, None, 302, "redirect", {}, "https://untrusted.invalid/"
        )
        is None
    )


@pytest.mark.parametrize("path", ["https://other.invalid", "//other.invalid", "/a\nb", "/a\\b"])
def test_bad_paths_reject_before_transport(monkeypatch, path):
    def unexpected(*args, **kwargs):
        pytest.fail("invalid path reached transport")

    monkeypatch.setattr(urllib.request, "build_opener", unexpected)
    with pytest.raises(ValueError, match="invalid GitHub API path"):
        approval._gh("GET", path, "fixture-not-a-credential")


def test_proxy_disabled_and_redirect_denied(monkeypatch):
    class Opener:
        def open(self, request, timeout):
            raise urllib.error.HTTPError(request.full_url, 302, "redirect", {}, None)

    def build(*handlers):
        assert handlers[0].proxies == {}
        assert isinstance(handlers[1], approval._NoRedirect)
        return Opener()

    monkeypatch.setattr(urllib.request, "build_opener", build)
    status, _ = approval._gh("GET", "/repos/o/r/actions/runs", "fixture-not-a-credential")
    assert status == 302


def test_oversized_inventory_is_error(monkeypatch):
    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self, size):
            return b"x" * size

    class Opener:
        def open(self, request, timeout):
            return Response()

    monkeypatch.setattr(urllib.request, "build_opener", lambda *args: Opener())
    status, body = approval._gh("GET", "/repos/o/r/actions/runs", "fixture-not-a-credential")
    assert status == 502
    assert "size limit" in body["error"]
