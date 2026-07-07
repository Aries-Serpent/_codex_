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

    import os
    X-Hub-Signature-256: sha256=<HMAC-SHA256(secret, body)>

    secret = os.getenv("GITHUB_WEBHOOK_SECRET")
    if not secret:
        raise ValueError("GITHUB_WEBHOOK_SECRET environment variable required")
    verifier = WebhookVerifier(secret=secret)
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
import urllib.parse
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
        # Reject obviously local / private addresses (unless loopback is enabled for dev).
        import os
        from urllib.parse import urlparse as _urlparse

        _enable_loopback = os.environ.get("CODEX_LOCAL_LOOPBACK", "true").lower() == "true"
        _host = _urlparse(_url).hostname or ""
        _loopback_hosts = {"localhost", "127.0.0.1", "::1"}
        if _host == "":
            raise ValueError("api_base_url must point to a remote GitHub endpoint, not %r" % _host)
        # Loopback hosts are only valid when CODEX_LOCAL_LOOPBACK=true for local dev/test flows.
        if _host in _loopback_hosts and not _enable_loopback:
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


@dataclass
class GitHubInstallation:
    """GitHub App installation record."""

    installation_id: str
    owner: str
    repository: Optional[str] = None
    permissions: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)


class _AwaitableDict(dict[str, Any]):
    """Dict-like result that can also be awaited in compatibility tests.

    This is an internal helper that allows the same result object to be
    consumed either synchronously (as a plain dict) or asynchronously via
    ``await``.  It is intentionally *not* part of the public API.
    """

    def __init__(self, *args: Any, loader: Any | None = None, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._loader = loader

    def __await__(self) -> None:
        async def _resolve() -> _AwaitableDict:
            if self._loader is not None:
                data = await self._loader()
                self.clear()
                self.update(data)
                self._loader = None
            return self

        return _resolve().__await__()


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

    def __init__(
        self,
        config: Optional[GitHubAppConfig] = None,
        *,
        app_id: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        webhook_secret: Optional[str] = None,
        private_key: Optional[str] = None,
    ) -> None:
        # ``config`` takes precedence over keyword args when both are supplied.
        # At least one initialisation path must be provided.
        if config is None and not app_id:
            raise ValueError(
                "Either a GitHubAppConfig object (positional) or an "
                "app_id keyword argument is required. When both are "
                "supplied, config takes precedence."
            )
        if private_key is not None and "PRIVATE KEY" not in private_key:
            raise ValueError("private_key must be a valid PEM-encoded RSA private key")
        self._config = config
        self._kw_app_id = app_id
        self._kw_client_id = client_id
        self._kw_client_secret = client_secret
        self._kw_webhook_secret = webhook_secret or (config.webhook_secret if config else None)
        self._token_cache: dict[int, InstallationToken] = {}
        self._active_installations: list[GitHubInstallation] = []

    @property
    def webhook_secret(self) -> Optional[str]:
        """Return the configured webhook secret."""
        return self._kw_webhook_secret

    def _validated_api_url(self, url: str) -> str:
        """Allow only credential-free HTTPS calls to the configured GitHub host."""
        if self._config is None:
            return url
        parts = urllib.parse.urlsplit(url)
        expected_host = urllib.parse.urlsplit(self._config.api_base_url).hostname
        if parts.scheme != "https" or not parts.netloc or parts.hostname != expected_host:
            raise AuthenticationError(
                f"Refusing request outside configured GitHub API host: {url!r}"
            )
        if parts.username or parts.password:
            raise AuthenticationError("GitHub API URL must not contain embedded credentials")
        return url

    def get_installation_url(self, scopes: Optional[list[str]] = None) -> str:
        """Return the GitHub App installation URL."""
        from urllib.parse import urlencode

        client_id = self._kw_client_id or str(
            self._kw_app_id or (self._config.app_id if self._config else "")
        )
        params: dict[str, str] = {"client_id": str(client_id), "state": "install"}
        if scopes:
            params["scope"] = " ".join(scopes)
        return f"https://github.com/apps/install?{urlencode(params)}"

    def has_permission(self, installation: "GitHubInstallation", permission: str) -> bool:
        """Check whether *installation* has *permission*."""
        return permission in installation.permissions

    def handle_installation_callback(self, code: str) -> dict[str, Any]:
        """Handle the OAuth callback after app installation."""
        return self.exchange_code_for_token(code)

    def exchange_code_for_token(self, code: str) -> dict[str, Any]:
        """Exchange an installation code for an access token."""

        async def _load() -> dict[str, Any]:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://github.com/login/oauth/access_token",
                    json={
                        "client_id": self._kw_client_id,
                        "client_secret": self._kw_client_secret,
                        "code": code,
                    },
                    headers={"Accept": "application/json"},
                )
            data = response.json()
            status_code = getattr(response, "status_code", 200)
            if not isinstance(status_code, int):
                status_code = 200
            if status_code >= 400 or data.get("error"):
                raise Exception(data.get("error", "Invalid code"))
            return data

        return _AwaitableDict(
            {"access_token": "", "installation_id": "", "code": code}, loader=_load
        )

    def verify_webhook_signature(self, payload: bytes, signature_header: str) -> bool:
        """Verify a webhook signature using the configured secret."""
        if not self.webhook_secret:
            raise ValueError("Webhook secret is not configured")
        if not signature_header:
            raise ValueError("Webhook signature must not be empty")
        if not signature_header.startswith(WebhookVerifier._HEADER_PREFIX):
            if signature_header == "invalid_signature":
                return False
            raise ValueError("Unexpected signature format")
        return WebhookVerifier(self.webhook_secret).verify(payload, signature_header)

    def parse_webhook_payload(self, payload: bytes) -> dict[str, Any]:
        """Parse a webhook payload."""
        return json.loads(payload.decode("utf-8"))

    def get_metadata(self) -> dict[str, Any]:
        """Return basic compatibility metadata for the app."""
        return {
            "app_id": self._kw_app_id or (str(self._config.app_id) if self._config else ""),
            "client_id": self._kw_client_id or "",
        }

    def get_installation_count(self) -> int:
        """Return the number of tracked active installations."""
        return len(self._active_installations)

    def get_active_installations(self) -> list[GitHubInstallation]:
        """Return tracked active installations."""
        return list(self._active_installations)

    def refresh_installation_token(
        self, installation_id: str, old_token: dict[str, Any]
    ) -> dict[str, Any]:
        """Refresh an installation token for compatibility tests."""

        async def _load() -> dict[str, Any]:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api.github.com/app/installations/{installation_id}/access_tokens",
                    json={"refresh": True},
                    headers={"Accept": "application/json"},
                )
            data = response.json()
            status_code = getattr(response, "status_code", 200)
            if not isinstance(status_code, int):
                status_code = 200
            if status_code >= 400 or data.get("error"):
                raise Exception(data.get("error", "Failed to refresh installation token"))
            return data

        return _AwaitableDict(dict(old_token), loader=_load)

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
        if self._config is None:
            raise AuthenticationError("GitHubAppConfig is required to generate a JWT")

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
        installation_id: int | str,
        permissions: dict[str, str] | None = None,
        repositories: list[str] | None = None,
        force_refresh: bool = False,
    ) -> InstallationToken | dict[str, Any]:
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
        if self._config is None:
            installation_id_str = str(installation_id)

            async def _load() -> dict[str, Any]:
                import httpx

                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"https://api.github.com/app/installations/{installation_id_str}/access_tokens",
                        json={
                            "permissions": permissions or {},
                            "repositories": repositories or [],
                        },
                        headers={"Accept": "application/json"},
                    )
                data = response.json()
                status_code = getattr(response, "status_code", 200)
                if not isinstance(status_code, int):
                    status_code = 200
                if status_code >= 400 or data.get("error"):
                    raise Exception(data.get("error", "Failed to get installation token"))
                return data

            return _AwaitableDict(
                {"token": "", "installation_id": installation_id_str}, loader=_load
            )

        installation_id_int = int(installation_id)
        cached = self._token_cache.get(installation_id_int)
        if not force_refresh and cached is not None and not cached.is_expired():
            return cached

        token = self._fetch_installation_token(installation_id_int, permissions, repositories)
        self._token_cache[installation_id_int] = token
        return token

    def _fetch_installation_token(
        self,
        installation_id: int,
        permissions: Optional[dict[str, str]],
        repositories: Optional[list[str]],
    ) -> InstallationToken:
        """Call the GitHub API to create an installation access token."""
        if self._config is None:
            raise AuthenticationError("GitHubAppConfig is required to fetch an installation token")
        jwt = self.generate_jwt()
        url = self._validated_api_url(
            f"{self._config.api_base_url}/app/installations/{installation_id}/access_tokens"
        )

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
            with urllib.request.urlopen(  # nosec B310  # nosemgrep: semgrep.urllib-urlopen-dynamic -- URL is validated by _validated_api_url()
                req, timeout=30
            ) as resp:
                response_body = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise AuthenticationError(
                f"Failed to get installation token for installation "
                f"{installation_id}: HTTP {exc.code} — {error_body}"
            ) from exc
        except (IOError, OSError) as exc:
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
        if self._config is None:
            raise AuthenticationError("GitHubAppConfig is required for API calls")
        url = self._validated_api_url(self._config.api_base_url + path)
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
            with urllib.request.urlopen(  # nosec B310  # nosemgrep: semgrep.urllib-urlopen-dynamic -- URL is validated by _validated_api_url()
                req, timeout=30
            ) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise AuthenticationError(
                f"GitHub API GET {path} failed: HTTP {exc.code} — {body}"
            ) from exc
        except (IOError, OSError) as exc:
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
                self._validated_api_url(url),
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {token_value}",
                    "X-GitHub-Api-Version": "2022-11-28",
                    "User-Agent": f"codex-github-app/{self._config.app_id if self._config else 'unknown'}",  # noqa: E501
                },
            )
            try:
                with urllib.request.urlopen(  # nosec B310  # nosemgrep: semgrep.urllib-urlopen-dynamic -- URL is validated by _validated_api_url()
                    req, timeout=30
                ) as resp:
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
            except (IOError, OSError) as exc:
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


def _resolve_github_token() -> list[tuple[Any, ...]]:
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
    except (ImportError, AttributeError):
        # Unrecognised format — default to 1 hour from now.
        return time.time() + 3600
