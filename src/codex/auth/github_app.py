"""
GitHub App package for Codex platform.

Provides everything needed to operate as a GitHub App:

* :class:`GitHubAppConfig` — app credentials (App ID, private key PEM).
* :class:`GitHubApp` — JWT generation, installation-access-token exchange,
  and convenience wrappers for the GitHub REST API.
* :class:`WebhookVerifier` — validates ``X-Hub-Signature-256`` headers on
  incoming webhook payloads.
* :func:`build_app_manifest` — constructs a GitHub App manifest dict ready
  for the `POST /api/v3/app-manifests/{code}/conversions
  <https://docs.github.com/en/apps/sharing-github-apps/registering-a-github-app-from-a-manifest>`_
  endpoint.

Authentication flow (GitHub App)::

    ┌─────────────────────────────────────────────────┐
    │ 1. Sign a short-lived JWT with the app's RSA key │
    │    (valid ≤ 10 minutes, used only as bearer)     │
    └───────────────────┬─────────────────────────────┘
                        │
    ┌───────────────────▼─────────────────────────────┐
    │ 2. POST /app/installations/{id}/access_tokens    │
    │    → installation access token (1 hour)          │
    └───────────────────┬─────────────────────────────┘
                        │
    ┌───────────────────▼─────────────────────────────┐
    │ 3. Use installation token for repository calls   │
    └─────────────────────────────────────────────────┘

Webhook security::

    X-Hub-Signature-256: sha256=<HMAC-SHA256(secret, body)>

    verifier = WebhookVerifier(secret="webhook-secret")
    verifier.verify(request_body_bytes, signature_header)

Required dependency (already in pyproject.toml)::

    cryptography >= 42.0.0
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Optional

from .exceptions import AuthenticationError

logger = logging.getLogger(__name__)

# GitHub REST API base URL — override in tests or for GHES deployments.
_GITHUB_API_URL = "https://api.github.com"

# App JWT validity window (GitHub maximum is 10 minutes).
_JWT_MAX_EXPIRY_SECONDS = 600
_JWT_DEFAULT_EXPIRY_SECONDS = 540  # 9 minutes — safe margin


# ---------------------------------------------------------------------------
# Configuration dataclass
# ---------------------------------------------------------------------------


@dataclass
class GitHubAppConfig:
    """
    GitHub App credentials and identity.

    Args:
        app_id: Numeric GitHub App ID (visible on the App settings page).
        private_key_pem: PEM-encoded RSA private key (2048-bit minimum).
            Read from a file or an environment variable; never hard-code it.
        webhook_secret: Optional shared secret used to sign webhook payloads.
        api_base_url: Override for GitHub Enterprise Server installations.
    """

    app_id: int
    private_key_pem: str
    webhook_secret: Optional[str] = None
    api_base_url: str = _GITHUB_API_URL

    def __post_init__(self) -> None:
        if not self.app_id or self.app_id <= 0:
            raise ValueError("app_id must be a positive integer")
        if not self.private_key_pem or "PRIVATE KEY" not in self.private_key_pem:
            raise ValueError("private_key_pem must be a valid PEM-encoded RSA private key")
        # Validate api_base_url to prevent open-redirect / SSRF.
        # Accepted forms:
        #   - "https://api.github.com"               (GitHub.com)
        #   - "https://<hostname>/api/v3"             (GHES)
        _url = self.api_base_url.rstrip("/")
        if not _url.startswith("https://"):
            raise ValueError("api_base_url must use HTTPS (got: %r)" % self.api_base_url)
        # Reject obviously local / private addresses.
        from urllib.parse import urlparse as _urlparse

        _host = _urlparse(_url).hostname or ""
        if _host in ("", "localhost", "127.0.0.1", "::1"):
            raise ValueError("api_base_url must point to a remote GitHub endpoint, not %r" % _host)


# ---------------------------------------------------------------------------
# Installation token cache entry
# ---------------------------------------------------------------------------


@dataclass
class InstallationToken:
    """Cached installation access token."""

    token: str  # nosec B105 — not a hardcoded secret
    expires_at: float  # Unix timestamp
    installation_id: int
    permissions: dict[str, str] = field(default_factory=dict)
    repository_selection: str = "all"

    def is_expired(self, buffer_seconds: int = 60) -> bool:
        """Return ``True`` if the token has expired or expires within *buffer_seconds*."""
        return time.time() >= (self.expires_at - buffer_seconds)


# ---------------------------------------------------------------------------
# Core GitHub App client
# ---------------------------------------------------------------------------


class GitHubApp:
    """
    GitHub App client.

    Handles JWT generation (RS256), installation-access-token exchange, and
    basic GitHub REST API calls on behalf of an installation.

    All network calls use the Python standard-library :mod:`urllib.request`
    as the sanctioned fallback transport (no extra dependencies).

    Args:
        config: :class:`GitHubAppConfig` with the app's credentials.
    """

    def __init__(self, config: GitHubAppConfig) -> None:
        self._config = config
        self._token_cache: dict[int, InstallationToken] = {}

    # ------------------------------------------------------------------ #
    # JWT                                                                  #
    # ------------------------------------------------------------------ #

    def generate_jwt(self, expiry_seconds: int = _JWT_DEFAULT_EXPIRY_SECONDS) -> str:
        """
        Generate a signed RS256 JWT for authenticating as the GitHub App itself.

        The JWT is valid for *expiry_seconds* (capped at 10 minutes per GitHub's
        requirement).

        Args:
            expiry_seconds: Token lifetime.  Must be ≤ 600.

        Returns:
            Compact JWS string ``"<header_b64>.<payload_b64>.<sig_b64>"``.

        Raises:
            ValueError: If *expiry_seconds* exceeds the GitHub maximum.
            AuthenticationError: If the private key cannot be loaded or signing fails.
        """
        if expiry_seconds > _JWT_MAX_EXPIRY_SECONDS:
            raise ValueError(
                f"expiry_seconds must be ≤ {_JWT_MAX_EXPIRY_SECONDS} "
                f"(GitHub App JWT maximum); got {expiry_seconds}"
            )

        now = int(time.time())
        header = {"alg": "RS256", "typ": "JWT"}
        payload = {
            "iss": str(self._config.app_id),
            "iat": now - 60,  # slight back-date to avoid clock skew
            "exp": now + expiry_seconds,
        }

        try:
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import padding
            from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey

            private_key = serialization.load_pem_private_key(
                self._config.private_key_pem.encode("utf-8"),
                password=None,
            )

            if not isinstance(private_key, RSAPrivateKey):
                raise ValueError(
                    "GitHub App JWT signing requires an RSA private key; "
                    f"got {type(private_key).__name__}"
                )

            header_b64 = _b64url(json.dumps(header, separators=(",", ":")))
            payload_b64 = _b64url(json.dumps(payload, separators=(",", ":")))
            signing_input = f"{header_b64}.{payload_b64}".encode("ascii")

            signature = private_key.sign(signing_input, padding.PKCS1v15(), hashes.SHA256())
            sig_b64 = _b64url_bytes(signature)

            return f"{header_b64}.{payload_b64}.{sig_b64}"

        except (ImportError, Exception) as exc:
            raise AuthenticationError(f"Failed to generate GitHub App JWT: {exc}") from exc

    # ------------------------------------------------------------------ #
    # Installation access tokens                                           #
    # ------------------------------------------------------------------ #

    def get_installation_token(
        self,
        installation_id: int,
        permissions: Optional[dict[str, str]] = None,
        repositories: Optional[list[str]] = None,
        force_refresh: bool = False,
    ) -> InstallationToken:
        """
        Obtain an installation access token, using the in-process cache.

        Args:
            installation_id: GitHub App installation ID.
            permissions: Optional permissions subset (e.g. ``{"contents": "read"}``).
            repositories: Optional list of repository names to scope the token.
            force_refresh: Bypass the cache and always fetch a fresh token.

        Returns:
            :class:`InstallationToken`.

        Raises:
            AuthenticationError: If the GitHub API request fails.
        """
        cached = self._token_cache.get(installation_id)
        if not force_refresh and cached is not None and not cached.is_expired():
            return cached

        token = self._fetch_installation_token(installation_id, permissions, repositories)
        self._token_cache[installation_id] = token
        return token

    def _fetch_installation_token(
        self,
        installation_id: int,
        permissions: Optional[dict[str, str]],
        repositories: Optional[list[str]],
    ) -> InstallationToken:
        """Call the GitHub API to create an installation access token."""
        jwt = self.generate_jwt()
        url = f"{self._config.api_base_url}/app/installations/{installation_id}/access_tokens"

        body: dict[str, Any] = {}
        if permissions:
            body["permissions"] = permissions
        if repositories:
            body["repositories"] = repositories

        data = json.dumps(body).encode("utf-8") if body else b"{}"

        req = urllib.request.Request(
            url,
            data=data,
            method="POST",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {jwt}",
                "X-GitHub-Api-Version": "2022-11-28",
                "Content-Type": "application/json",
                "User-Agent": f"codex-github-app/{self._config.app_id}",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:  # nosec B310
                response_body = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise AuthenticationError(
                f"Failed to get installation token for installation "
                f"{installation_id}: HTTP {exc.code} — {error_body}"
            ) from exc
        except Exception as exc:
            raise AuthenticationError(f"Network error fetching installation token: {exc}") from exc

        # Parse ISO-8601 expiry → Unix timestamp
        expires_at = _parse_iso8601(response_body.get("expires_at", ""))

        return InstallationToken(
            token=response_body["token"],
            expires_at=expires_at,
            installation_id=installation_id,
            permissions=response_body.get("permissions", {}),
            repository_selection=response_body.get("repository_selection", "all"),
        )

    # ------------------------------------------------------------------ #
    # App metadata                                                         #
    # ------------------------------------------------------------------ #

    def get_app_info(self) -> dict[str, Any]:
        """
        Fetch the authenticated GitHub App's metadata (``GET /app``).

        Returns:
            Parsed JSON response from the GitHub API.

        Raises:
            AuthenticationError: On network or API errors.
        """
        jwt = self.generate_jwt()
        return self._api_get("/app", bearer=jwt)

    def list_installations(self) -> list[dict[str, Any]]:
        """
        List all installations of this GitHub App (``GET /app/installations``).

        Returns:
            List of installation objects.

        Raises:
            AuthenticationError: On network or API errors.
        """
        jwt = self.generate_jwt()
        return self._api_get("/app/installations", bearer=jwt)

    # ------------------------------------------------------------------ #
    # Internal HTTP helpers                                                #
    # ------------------------------------------------------------------ #

    def _api_get(self, path: str, bearer: str) -> Any:
        """Low-level GET using an explicit bearer token (e.g. App JWT)."""
        url = self._config.api_base_url + path
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {bearer}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": f"codex-github-app/{self._config.app_id}",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:  # nosec B310
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise AuthenticationError(
                f"GitHub API GET {path} failed: HTTP {exc.code} — {body}"
            ) from exc
        except Exception as exc:
            raise AuthenticationError(f"Network error on GET {path}: {exc}") from exc

    def pat_api_get(self, url: str) -> Any:
        """
        Perform an authenticated GET using environment-sourced PAT tokens.

        Token resolution order (mirrors the rest of the Codex platform):

        1. ``CODEX_MASTER_KEY``  — full-scope PAT (preferred)
        2. ``CODEX_BACKUP_KEY``  — fallback PAT (tried when master key absent
           *or* when the master key returns HTTP 401 / 403)
        3. ``AGENT_GITHUB_TOKEN`` / ``GITHUB_TOKEN`` — last-resort

        This method is intended for PAT-authenticated endpoints (e.g. listing
        repository variables) that do *not* accept a GitHub App JWT.

        Args:
            url: Absolute URL to fetch.

        Returns:
            Parsed JSON response.

        Raises:
            AuthenticationError: If all tokens fail or no token is available.
        """
        tokens = _resolve_github_token()
        last_exc: Optional[Exception] = None

        for token_value, token_name in tokens:
            if not token_value:
                continue
            req = urllib.request.Request(
                url,
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {token_value}",
                    "X-GitHub-Api-Version": "2022-11-28",
                    "User-Agent": f"codex-github-app/{self._config.app_id}",
                },
            )
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:  # nosec B310
                    logger.debug("pat_api_get succeeded with %s: %s", token_name, url)
                    return json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                if exc.code in (401, 403):
                    # Auth failure — try next token
                    logger.debug(
                        "pat_api_get: %s returned HTTP %d with %s — trying next token",
                        url,
                        exc.code,
                        token_name,
                    )
                    last_exc = exc
                    continue
                body = exc.read().decode("utf-8", errors="replace")
                raise AuthenticationError(
                    f"PAT API GET {url} failed: HTTP {exc.code} — {body}"
                ) from exc
            except Exception as exc:
                raise AuthenticationError(f"Network error on PAT GET {url}: {exc}") from exc

        raise AuthenticationError(
            f"All PAT tokens exhausted for GET {url}. "
            "Set CODEX_MASTER_KEY or CODEX_BACKUP_KEY environment variables."
        ) from last_exc


# ---------------------------------------------------------------------------
# Webhook signature verifier
# ---------------------------------------------------------------------------


class WebhookVerifier:
    """
    GitHub webhook payload verifier.

    Validates the ``X-Hub-Signature-256`` header that GitHub attaches to
    every webhook delivery when a webhook secret is configured.

    Args:
        secret: The shared webhook secret configured on the GitHub side.
    """

    _HEADER_PREFIX = "sha256="

    def __init__(self, secret: str) -> None:
        if not secret:
            raise ValueError("Webhook secret must not be empty")
        self._secret = secret.encode("utf-8")

    def compute_signature(self, payload: bytes) -> str:
        """
        Compute the expected ``X-Hub-Signature-256`` value for *payload*.

        Args:
            payload: Raw (undecoded) request body bytes.

        Returns:
            String of the form ``"sha256=<hex-digest>"``.
        """
        digest = hmac.new(self._secret, payload, hashlib.sha256).hexdigest()
        return f"{self._HEADER_PREFIX}{digest}"

    def verify(self, payload: bytes, signature_header: str) -> bool:
        """
        Verify *payload* against the ``X-Hub-Signature-256`` header.

        Uses :func:`hmac.compare_digest` to prevent timing side-channels.

        Args:
            payload: Raw request body bytes.
            signature_header: Value of the ``X-Hub-Signature-256`` header.

        Returns:
            ``True`` if the signature is valid.

        Raises:
            ValueError: If *signature_header* has an unexpected format.
        """
        if not signature_header.startswith(self._HEADER_PREFIX):
            raise ValueError(
                f"Unexpected signature format: expected header starting with "
                f"'{self._HEADER_PREFIX}', got '{signature_header[:20]}...'"
            )

        expected = self.compute_signature(payload)
        return hmac.compare_digest(expected, signature_header)


# ---------------------------------------------------------------------------
# App manifest helper
# ---------------------------------------------------------------------------


def build_app_manifest(
    name: str,
    url: str,
    webhook_url: str,
    description: str = "",
    callback_urls: Optional[list[str]] = None,
    request_oauth_on_install: bool = False,
    setup_url: Optional[str] = None,
    public: bool = False,
    default_events: Optional[list[str]] = None,
    default_permissions: Optional[dict[str, str]] = None,
) -> dict[str, Any]:
    """
    Build a GitHub App manifest dictionary.

    The returned dict can be embedded in an HTML form as the ``manifest``
    field (JSON-encoded) to trigger GitHub's
    `App-manifest flow
    <https://docs.github.com/en/apps/sharing-github-apps/registering-a-github-app-from-a-manifest>`_.

    Args:
        name: App name (must be unique on GitHub).
        url: Homepage URL of the app.
        webhook_url: URL that GitHub will deliver events to.
        description: Short app description (≤ 255 characters).
        callback_urls: OAuth callback URLs.
        request_oauth_on_install: Redirect to OAuth flow after installation.
        setup_url: Optional post-installation setup page URL.
        public: If ``True`` anyone can install the app; otherwise owner-only.
        default_events: Webhook events to subscribe to.  Defaults to a
            sensible set for CI-oriented apps.
        default_permissions: Permission map.  Defaults to read-only on
            contents, metadata, and pull-requests.

    Returns:
        Manifest dict ready to be ``json.dumps()``-ed into an HTML form.

    Example::

        manifest = build_app_manifest(
            name="codex-bot",
            url="https://aries-serpent.github.io/_codex_/",
            webhook_url="https://api.example.com/webhook/github",
        )
        json_manifest = json.dumps(manifest)
    """
    if default_events is None:
        default_events = [
            "push",
            "pull_request",
            "pull_request_review",
            "pull_request_review_comment",
            "issue_comment",
            "issues",
            "check_run",
            "check_suite",
            "workflow_run",
            "repository_dispatch",
        ]

    if default_permissions is None:
        default_permissions = {
            "contents": "read",
            "metadata": "read",
            "pull_requests": "write",
            "checks": "write",
            "statuses": "write",
            "issues": "write",
        }

    manifest: dict[str, Any] = {
        "name": name,
        "url": url,
        "hook_attributes": {
            "url": webhook_url,
            "active": True,
        },
        "redirect_url": callback_urls[0] if callback_urls else url,
        "callback_urls": callback_urls or [],
        "request_oauth_on_install": request_oauth_on_install,
        "public": public,
        "default_events": default_events,
        "default_permissions": default_permissions,
    }

    if description:
        manifest["description"] = description[:255]
    if setup_url:
        manifest["setup_url"] = setup_url

    return manifest


# ---------------------------------------------------------------------------
# Private utilities
# ---------------------------------------------------------------------------


def _resolve_github_token() -> list[tuple]:
    """
    Resolve GitHub PAT tokens from the environment in priority order.

    Returns a list of ``(token_value, token_name)`` pairs so callers can
    iterate and retry with the next token on a 401/403 response.

    Priority order (matches ``BrainClient._auth_header()`` and
    ``VariableManager._resolve_token()`` across the Codex platform):

    1. ``CODEX_MASTER_KEY``   — full-scope classic PAT (preferred)
    2. ``CODEX_BACKUP_KEY``   — fallback PAT (tried when master key absent
       or when it returns HTTP 401 / 403)
    3. ``AGENT_GITHUB_TOKEN`` — alias for ``GITHUB_TOKEN`` with a stable name
    4. ``GITHUB_TOKEN``       — last-resort installation token
    """
    import os as _os

    return [
        (_os.environ.get("CODEX_MASTER_KEY", ""), "CODEX_MASTER_KEY"),
        (_os.environ.get("CODEX_BACKUP_KEY", ""), "CODEX_BACKUP_KEY"),
        (_os.environ.get("AGENT_GITHUB_TOKEN", ""), "AGENT_GITHUB_TOKEN"),
        (_os.environ.get("GITHUB_TOKEN", ""), "GITHUB_TOKEN"),
    ]


def _b64url(text: str) -> str:
    """Base64url-encode a UTF-8 string (no padding)."""
    return base64.urlsafe_b64encode(text.encode("utf-8")).rstrip(b"=").decode("ascii")


def _b64url_bytes(data: bytes) -> str:
    """Base64url-encode raw bytes (no padding)."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _parse_iso8601(ts: str) -> float:
    """
    Parse an ISO-8601 timestamp string such as ``"2024-01-15T12:00:00Z"``
    into a Unix timestamp.  Returns ``time.time() + 3600`` as a safe fallback.
    """
    if not ts:
        return time.time() + 3600

    # Python 3.11+ fromisoformat handles Z, older versions need a replace.
    try:
        from datetime import datetime

        normalised = ts.replace("Z", "+00:00")
        dt = datetime.fromisoformat(normalised)
        return dt.timestamp()
    except Exception:
        # Unrecognised format — default to 1 hour from now.
        return time.time() + 3600
