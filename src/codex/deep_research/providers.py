"""Callable provider boundary and network target checks for research retrieval."""

from __future__ import annotations

import hashlib
import http.client
import ipaddress
import re
import socket
import ssl
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol
from urllib.parse import (
    parse_qsl,
    quote,
    urlencode,
    urljoin,
    urlsplit,
    urlunsplit,
)


class ResearchProvider(Protocol):
    """Search and retrieve material using explicitly supplied runtime callables."""

    def search(self, query: str) -> list[dict[str, Any]]: ...

    def fetch(self, url: str) -> dict[str, Any]: ...


class RateLimitError(RuntimeError):
    """Raised by a provider when a retry-after delay was supplied."""

    def __init__(self, message: str, retry_after: float = 0.0) -> None:
        super().__init__(message)
        self.retry_after = max(0.0, retry_after)


class ProviderUnavailable(RuntimeError):
    """Signals that an expected provider callable was not supplied."""


@dataclass
class BrowserDiagnostics:
    """Optional adapters for inspecting a page after a browser-backed fetch."""

    console_messages: Callable[[], Any]
    network_requests: Callable[[], Any]
    handle_dialog: Callable[[bool], Any]
    dialog_pending: Callable[[], bool] | None = None


@dataclass
class HostToolProvider:
    """Bind host-provided search/fetch tools without assuming global tool access.

    The callbacks are the host's actual callable tools. This class deliberately
    does not select an endpoint or silently substitute a mocked provider.
    """

    search_call: Callable[[str], Any] | None
    fetch_call: Callable[[str], Any] | None = None
    resolver: Callable[[str], Sequence[str]] = field(default_factory=lambda: _resolve_addresses)
    sleep: Callable[[float], None] = time.sleep
    retries: int = 3
    browser_diagnostics: BrowserDiagnostics | None = None
    is_live: bool = False
    redirect_validation_verified: bool = False
    browser_backed: bool = False
    cost_per_search: float = 0.0

    def __post_init__(self) -> None:
        if self.retries < 0 or self.cost_per_search < 0:
            raise ValueError("retries and provider cost must be non-negative")
        if self.fetch_call is None:
            self.fetch_call = SafeHTTPSFetcher()
            self.redirect_validation_verified = True
        elif isinstance(self.fetch_call, SafeHTTPSFetcher):
            self.redirect_validation_verified = True

    @property
    def available(self) -> bool:
        return (
            self.search_call is not None
            and self.fetch_call is not None
            and self.redirect_validation_verified
        )

    def search(self, query: str) -> list[dict[str, Any]]:
        search_call = self.search_call
        if search_call is None:
            raise ProviderUnavailable("No callable host search tool was supplied")
        result = self._retry(lambda: search_call(query))
        return _normalize_search_results(result)

    def fetch(self, url: str) -> dict[str, Any]:
        fetch_call = self.fetch_call
        if fetch_call is None:
            raise ProviderUnavailable("No callable host fetch tool was supplied")
        if not self.redirect_validation_verified:
            raise ProviderUnavailable(
                "Fetch transport must validate every redirect and pin public DNS results"
            )
        validate_public_url(url, self.resolver)
        result = self._retry(lambda: fetch_call(url))
        normalized = _normalize_fetch_result(result, url)
        validate_public_url(normalized["final_url"], self.resolver)
        if self.browser_diagnostics is not None and self.browser_backed:
            normalized["browser_diagnostics"] = collect_browser_diagnostics(
                self.browser_diagnostics
            )
        return normalized

    def _retry(self, operation: Callable[[], Any]) -> Any:
        for attempt in range(self.retries + 1):
            try:
                return operation()
            except RateLimitError as exc:
                if attempt >= self.retries:
                    raise
                self.sleep(max(exc.retry_after, min(0.25 * (2**attempt), 2.0)))
            except (TimeoutError, ConnectionError):
                if attempt >= self.retries:
                    raise
                self.sleep(min(0.25 * (2**attempt), 2.0))
        raise AssertionError("unreachable")


def canonicalize_url(url: str) -> str:
    """Normalize URL identity while preserving meaningful query parameters."""
    parts = urlsplit(url.strip())
    if parts.scheme.lower() not in {"http", "https"} or not parts.hostname:
        raise ValueError("Source URL must use HTTP(S) and include a hostname")
    hostname = parts.hostname.lower()
    if ":" in hostname and not hostname.startswith("["):
        hostname = f"[{hostname}]"
    port = parts.port
    netloc = (
        hostname
        if port is None
        or (parts.scheme.lower(), port)
        in {
            ("http", 80),
            ("https", 443),
        }
        else f"{hostname}:{port}"
    )
    ignored = {"fbclid", "gclid"}
    query = [
        (
            key,
            "[REDACTED]" if _sensitive_parameter(key) else value,
        )
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if key.lower().startswith("utm_") is False and key.lower() not in ignored
    ]
    return urlunsplit(
        (parts.scheme.lower(), netloc, parts.path or "/", urlencode(query, doseq=True), "")
    )


def validate_public_url(url: str, resolver: Callable[[str], Sequence[str]] | None = None) -> None:
    """Reject non-HTTPS and non-public DNS/IP targets before a fetch call."""
    _public_addresses(url, resolver or _resolve_addresses)


@dataclass
class SafeHTTPSFetcher:
    """Fetch HTTPS pages with public-IP pinning, bounded redirects, and byte limits."""

    resolver: Callable[[str], Sequence[str]] = field(default_factory=lambda: _resolve_addresses)
    timeout: float = 20.0
    max_bytes: int = 5_000_000
    max_redirects: int = 5
    connector: Callable[..., socket.socket] = socket.create_connection

    def __post_init__(self) -> None:
        if self.timeout <= 0 or self.max_bytes <= 0 or self.max_redirects < 0:
            raise ValueError("Fetch timeout/size must be positive and redirects non-negative")

    def __call__(self, url: str) -> dict[str, Any]:
        current_url = url
        for redirect_count in range(self.max_redirects + 1):
            parts = urlsplit(current_url)
            addresses = _public_addresses(current_url, self.resolver)
            hostname = parts.hostname or ""
            port = parts.port or 443
            address = str(addresses[0])
            host_header = _host_header(hostname, port)
            target = _request_target(parts.path, parts.query)
            request = (
                f"GET {target} HTTP/1.1\r\n"
                f"Host: {host_header}\r\n"
                "User-Agent: codex-deep-research/1\r\n"
                "Accept: text/html,application/json,text/plain,*/*\r\n"
                "Accept-Encoding: identity\r\n"
                "Connection: close\r\n\r\n"
            ).encode("ascii")
            raw_socket = self.connector((address, port), timeout=self.timeout)
            try:
                connection = ssl.create_default_context().wrap_socket(
                    raw_socket, server_hostname=hostname.encode("idna").decode("ascii")
                )
            except Exception:
                raw_socket.close()
                raise
            try:
                connection.sendall(request)
                response = http.client.HTTPResponse(connection)
                response.begin()
                if response.status in {301, 302, 303, 307, 308}:
                    location = response.getheader("Location")
                    response.close()
                    if not location:
                        raise ValueError("Redirect response has no Location header")
                    if redirect_count >= self.max_redirects:
                        raise ValueError("Maximum redirect count exceeded")
                    current_url = urljoin(current_url, location)
                    continue
                content_encoding = response.getheader("Content-Encoding", "identity")
                if content_encoding.lower() not in {"", "identity"}:
                    raise ValueError("Compressed response bodies are not supported")
                body = response.read(self.max_bytes + 1)
                content_type = response.getheader("Content-Type")
                if len(body) > self.max_bytes:
                    raise ValueError("Fetched response exceeds the configured byte limit")
                if response.status >= 400:
                    raise ConnectionError(f"Fetch returned HTTP status {response.status}")
                return {
                    "content": body.decode("utf-8", errors="replace"),
                    "final_url": current_url,
                    "content_type": content_type,
                    "content_sha256": hashlib.sha256(body).hexdigest(),
                }
            finally:
                connection.close()
        raise ValueError("Maximum redirect count exceeded")


def _public_addresses(
    url: str, resolver: Callable[[str], Sequence[str]]
) -> list[ipaddress.IPv4Address | ipaddress.IPv6Address]:
    if any(ord(char) < 32 or ord(char) == 127 for char in url):
        raise ValueError("Control characters are not allowed in source URLs")
    parts = urlsplit(url)
    if parts.scheme.lower() != "https" or not parts.hostname:
        raise ValueError("Only absolute HTTPS source URLs are allowed")
    if parts.username or parts.password:
        raise ValueError("Credentials in source URLs are not allowed")
    hostname = parts.hostname.rstrip(".").lower()
    if hostname in {"localhost", "localhost.localdomain"} or hostname.endswith(".local"):
        raise ValueError("Local hostnames are not allowed")
    try:
        addresses = [ipaddress.ip_address(hostname)]
    except ValueError:
        resolved = resolver(hostname.encode("idna").decode("ascii"))
        if not resolved:
            raise ValueError("Source hostname did not resolve to a public address")
        try:
            addresses = [ipaddress.ip_address(address) for address in resolved]
        except ValueError as exc:
            raise ValueError("Source hostname resolved to an invalid address") from exc
    if any(not address.is_global for address in addresses):
        raise ValueError("Source hostname resolves to a non-public address")
    return addresses


def _host_header(hostname: str, port: int) -> str:
    normalized = hostname.encode("idna").decode("ascii")
    if ":" in normalized and not normalized.startswith("["):
        normalized = f"[{normalized}]"
    return normalized if port == 443 else f"{normalized}:{port}"


def _request_target(path: str, query: str) -> str:
    safe_path = quote(path or "/", safe="/%:@!$&'()*+,;=-._~")
    safe_query = quote(query, safe="=&?/:@!$'()*+,;%-._~")
    return f"{safe_path}?{safe_query}" if safe_query else safe_path


def collect_browser_diagnostics(diagnostics: BrowserDiagnostics) -> dict[str, Any]:
    """Capture browser console/network status and dismiss only an observed dialog."""
    dialog_handled = False
    failures = []
    try:
        if diagnostics.dialog_pending is not None and diagnostics.dialog_pending():
            diagnostics.handle_dialog(False)
            dialog_handled = True
    except Exception as exc:
        failures.append(f"dialog handling: {type(exc).__name__}")
    try:
        messages = _items(diagnostics.console_messages())
    except Exception as exc:
        messages = []
        failures.append(f"console inspection: {type(exc).__name__}")
    try:
        request_items = _items(diagnostics.network_requests())
    except Exception as exc:
        request_items = []
        failures.append(f"network inspection: {type(exc).__name__}")
    return {
        "inspected": True,
        "console_message_count": len(messages),
        "console_errors": [
            redact_sensitive_text(_message_text(item))
            for item in messages
            if _is_console_error(item)
        ],
        "network_request_count": len(request_items),
        "network_failures": [
            _safe_request_summary(item) for item in request_items if _is_network_failure(item)
        ],
        "dialog_present": dialog_handled,
        "dialog_action": "dismissed" if dialog_handled else "none_observed",
        "inspection_errors": failures,
    }


def _normalize_search_results(result: Any) -> list[dict[str, Any]]:
    if isinstance(result, Mapping):
        result = result.get("results", [])
    if not isinstance(result, Sequence) or isinstance(result, (str, bytes)):
        raise ValueError("Search callable must return a list or an object with results")
    normalized: list[dict[str, Any]] = []
    for hit in result:
        if not isinstance(hit, Mapping):
            continue
        url = hit.get("url") or hit.get("link")
        if not isinstance(url, str):
            continue
        role = hit.get("evidence_role")
        if not isinstance(role, str) or role not in {
            "current",
            "historical",
            "archive",
            "unknown",
        }:
            role = "unknown"
        normalized.append(
            {
                "url": url,
                "title": _optional_string(hit.get("title")),
                "author": _optional_string(hit.get("author")),
                "snippet": _optional_string(hit.get("snippet") or hit.get("description")),
                "publisher": _optional_string(hit.get("publisher")),
                "published_at": _optional_string(hit.get("published_at")),
                "license": _optional_string(hit.get("license")),
                "access_constraints": _optional_string(hit.get("access_constraints")),
                "evidence_role": role,
            }
        )
    return normalized


def _normalize_fetch_result(result: Any, requested_url: str) -> dict[str, Any]:
    if isinstance(result, bytes):
        content = result.decode("utf-8", errors="replace")
        content_sha256 = hashlib.sha256(result).hexdigest()
        final_url = requested_url
        title = None
        content_type = None
    elif isinstance(result, str):
        content = result
        content_sha256 = hashlib.sha256(result.encode("utf-8")).hexdigest()
        final_url = requested_url
        title = None
        content_type = None
    elif isinstance(result, Mapping):
        raw_content = result.get("content", result.get("text", ""))
        if isinstance(raw_content, bytes):
            content = raw_content.decode("utf-8", errors="replace")
            content_sha256 = hashlib.sha256(raw_content).hexdigest()
        elif isinstance(raw_content, str):
            content = raw_content
            content_sha256 = hashlib.sha256(raw_content.encode("utf-8")).hexdigest()
        else:
            raise ValueError("Fetch callable content must be text or bytes")
        final_url = result.get("final_url", result.get("url", requested_url))
        if not isinstance(final_url, str):
            raise ValueError("Fetch callable final_url must be a string")
        title = _optional_string(result.get("title"))
        content_type = _optional_string(result.get("content_type"))
        supplied_hash = result.get("content_sha256")
        if supplied_hash is not None and supplied_hash != content_sha256:
            raise ValueError("Fetch callable content_sha256 does not match content")
    else:
        raise ValueError("Fetch callable must return text, bytes, or a result object")
    return {
        "content": content,
        "final_url": final_url,
        "title": title,
        "content_type": content_type,
        "content_sha256": content_sha256,
    }


def _resolve_addresses(hostname: str) -> Sequence[str]:
    return tuple(
        {str(item[4][0]) for item in socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)}
    )


def _items(value: Any) -> list[Any]:
    if isinstance(value, Mapping):
        nested = value.get("messages", value.get("requests", value.get("items", [])))
        return (
            list(nested)
            if isinstance(nested, Sequence) and not isinstance(nested, (str, bytes))
            else []
        )
    return (
        list(value) if isinstance(value, Sequence) and not isinstance(value, (str, bytes)) else []
    )


def _message_text(value: Any) -> str:
    if isinstance(value, Mapping):
        return str(value.get("text", value.get("message", "")))
    return str(value)


def _is_console_error(value: Any) -> bool:
    if isinstance(value, Mapping):
        return str(value.get("type", value.get("level", ""))).lower() in {
            "error",
            "assert",
            "critical",
        }
    return "error" in str(value).lower()


def _is_network_failure(value: Any) -> bool:
    if not isinstance(value, Mapping):
        return False
    if value.get("failed") is True or value.get("failure"):
        return True
    status = value.get("status")
    return isinstance(status, int) and status >= 400


def _safe_request_summary(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        return {"detail": redact_sensitive_text(str(value))}
    url = value.get("url")
    safe_url = None
    if isinstance(url, str):
        parts = urlsplit(url)
        try:
            host = parts.hostname or ""
            if ":" in host and not host.startswith("["):
                host = f"[{host}]"
            port = parts.port
            netloc = host if port is None else f"{host}:{port}"
            safe_url = urlunsplit((parts.scheme, netloc, parts.path, "", ""))
        except ValueError:
            safe_url = None
    return {
        "url": safe_url,
        "method": value.get("method"),
        "status": value.get("status"),
        "failure": redact_sensitive_text(str(value.get("failure", ""))) or None,
    }


def redact_sensitive_text(text: str) -> str:
    patterns = (
        r"(?i)(authorization|token|secret|api[_-]?key|password)(\s*[:=]\s*|\s+)[^\s,;]+",
        r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+",
        r"\bAKIA[0-9A-Z]{16}\b",
        r"\bsk-[A-Za-z0-9_-]{16,}\b",
    )
    for pattern in patterns:
        text = re.sub(
            pattern,
            r"\1 [REDACTED]" if pattern.startswith("(?i)(authorization") else "[REDACTED]",
            text,
        )
    return text[:500]


def contains_sensitive_material(text: str) -> bool:
    patterns = (
        r"(?i)(authorization|token|secret|api[_-]?key|password)\s*[:=]\s*\S+",
        r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+",
        r"\bAKIA[0-9A-Z]{16}\b",
        r"\bsk-[A-Za-z0-9_-]{16,}\b",
    )
    return any(re.search(pattern, text) for pattern in patterns)


def _sensitive_parameter(name: str) -> bool:
    lowered = name.casefold().replace("-", "_")
    return any(
        marker in lowered
        for marker in (
            "token",
            "secret",
            "password",
            "api_key",
            "apikey",
            "signature",
            "credential",
        )
    ) or lowered in {"key", "auth", "authorization", "sig"}


def _optional_string(value: Any) -> str | None:
    return (
        redact_sensitive_text(value.strip()) if isinstance(value, str) and value.strip() else None
    )
