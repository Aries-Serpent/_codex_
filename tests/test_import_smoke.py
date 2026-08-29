"""
Import smoke tests — P19 shadow-import regression guardrail (S679).

These tests verify that:
1. ``src.config.openai_client`` and ``src.services.github.client`` can be
   imported without hanging, raising unexpected errors, or making network calls.
2. When src/ is properly first on sys.path, ``services.github.client`` resolves
   to src/services/github/client.py, not to a root-level placeholder.
3. Import-time side effects are absent (no network I/O during import).

Run with: pytest -q tests/test_import_smoke.py
"""

from __future__ import annotations

import _socket
import importlib
import importlib.util
import os
import pathlib
import sys
import time
from unittest.mock import patch

import pytest

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
_SRC = str(_REPO_ROOT / "src")
_REPO_ROOT_STR = str(_REPO_ROOT)

# Ensure src/ is first on path so imports in this file work reliably.
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)
if _REPO_ROOT_STR not in sys.path:
    sys.path.append(_REPO_ROOT_STR)


def _evict_services_shadow() -> None:
    """Remove any root-level placeholder 'services.*' entries from sys.modules.

    The root-level services/github/__init__.py is a placeholder.  If it gets
    cached before src/services/ is on sys.path, subsequent imports of
    services.github.client fail with ModuleNotFoundError.  This helper evicts
    the wrong entries so re-imports resolve to src/services/.
    """
    for key in list(sys.modules.keys()):
        if key == "services" or key.startswith("services."):
            mod = sys.modules[key]
            origin = getattr(mod, "__file__", None) or ""
            if origin and not origin.startswith(_SRC):
                del sys.modules[key]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestImportSmoke:
    """Fast smoke-tests: imports complete quickly and resolve to src/."""

    def test_config_openai_client_importable(self) -> None:
        """src.config.openai_client imports without error."""
        t0 = time.monotonic()
        from config.openai_client import CodexOpenAIClient  # noqa: F401

        elapsed = time.monotonic() - t0
        assert elapsed < 5.0, (
            f"src.config.openai_client took {elapsed:.2f}s to import — "
            "possible blocking I/O at import time"
        )

    def test_services_github_client_importable(self) -> None:
        """src.services.github.client imports without error."""
        t0 = time.monotonic()
        from services.github.client import GitHubClient  # noqa: F401

        elapsed = time.monotonic() - t0
        assert elapsed < 5.0, (
            f"src.services.github.client took {elapsed:.2f}s to import — "
            "possible blocking I/O at import time"
        )

    def test_config_openai_client_resolves_to_src(self) -> None:
        """config.openai_client (if importable) resolves to src/, not a shadow."""
        spec = None
        try:
            spec = importlib.util.find_spec("config.openai_client")
        except (ModuleNotFoundError, ValueError):
            pytest.skip("config.openai_client not importable via 'config' namespace")
        if spec is None:
            pytest.skip("config.openai_client spec not found")
        origin = spec.origin or ""
        assert origin.startswith(_SRC), (
            f"config.openai_client resolved to {origin!r} — "
            f"expected a path inside {_SRC!r}.  "
            "Shadow-import detected: a non-src 'config' package is shadowing src/config/."
        )

    def test_services_github_client_resolves_to_src_when_path_correct(self) -> None:
        """services.github.client resolves to src/ when src/ is first on sys.path."""
        _evict_services_shadow()
        # Ensure src/ is first so the import is unambiguous.
        if sys.path[0] != _SRC:
            sys.path.insert(0, _SRC)

        spec = None
        try:
            spec = importlib.util.find_spec("services.github.client")
        except (ModuleNotFoundError, ValueError):
            pytest.skip("services.github.client not importable after path fix")
        if spec is None:
            pytest.skip("services.github.client spec not found after path fix")
        origin = spec.origin or ""
        assert origin.startswith(_SRC), (
            f"services.github.client resolved to {origin!r} — "
            f"expected a path inside {_SRC!r}.  "
            "Shadow-import detected: root-level services/github/ is shadowing src/services/github/."
        )

    def test_no_network_call_on_config_openai_client_import(self) -> None:
        """Importing src.config.openai_client must not trigger any network I/O."""
        # Evict cached module so the import actually executes.
        for key in ("config.openai_client", "src.config.openai_client"):
            sys.modules.pop(key, None)

        network_called: list[str] = []

        class _BlockingSocket:
            """Raises if any real socket connection is attempted."""

            def __init__(self, *a: object, **kw: object) -> None:
                network_called.append(f"socket({a}, {kw})")
                raise OSError("Network call during import of config.openai_client is forbidden")


        with patch.object(_socket, "socket", _BlockingSocket):
            importlib.import_module("src.config.openai_client")

        assert not network_called, f"Network I/O detected during import: {network_called}"

    def test_github_client_empty_token_no_auth_header(self) -> None:
        """GitHubClient(token='') must not include Authorization header.

        Regression test for P19: token='' was treated as falsy and fell back
        to GITHUB_TOKEN env var, leaking CI tokens into unit-test assertions.
        """
        from services.github.client import GitHubClient

        with patch.dict(os.environ, {"GITHUB_TOKEN": "env-token-should-not-be-used"}):
            client = GitHubClient(token="")
            headers = client._get_headers()

        assert "Authorization" not in headers, (
            "GitHubClient(token='') must not set Authorization header. "
            "Ensure __init__ uses 'token if token is not None else os.environ.get(...)'"
        )

    def test_github_client_none_token_uses_env(self) -> None:
        """GitHubClient(token=None) should fall back to GITHUB_TOKEN env var."""
        from services.github.client import GitHubClient

        with patch.dict(os.environ, {"GITHUB_TOKEN": "env-token-abc"}):
            client = GitHubClient(token=None)
            assert client.token == "env-token-abc", "token is not valid"

    def test_github_client_explicit_token_used(self) -> None:
        """GitHubClient(token='explicit') should use the provided token."""
        from services.github.client import GitHubClient

        with patch.dict(os.environ, {"GITHUB_TOKEN": "env-token-ignored"}):
            client = GitHubClient(token="explicit-token")
            assert client.token == "explicit-token", "token is not valid"
            headers = client._get_headers()
            assert headers.get("Authorization") == "Bearer explicit-token", "Condition must be true"
