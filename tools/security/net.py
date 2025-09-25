from __future__ import annotations

from typing import Mapping, MutableMapping, Optional, Tuple
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ALLOWED_SCHEMES = {"https"}


def _validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES or not parsed.netloc:
        raise ValueError(f"disallowed URL: {url!r}")


def safe_fetch(
    url: str,
    *,
    timeout: float = 20.0,
    headers: Optional[Mapping[str, str]] = None,
) -> bytes:
    _validate_url(url)
    request_headers: MutableMapping[str, str] = {"User-Agent": "codex-fetch/1.0"}
    if headers:
        request_headers.update(headers)
    req = Request(url, headers=request_headers)
    with urlopen(req, timeout=timeout) as resp:  # nosec B310 - scheme validated
        return resp.read()


def safe_request(
    url: str,
    *,
    timeout: float = 20.0,
    headers: Optional[Mapping[str, str]] = None,
    method: str = "GET",
    data: Optional[bytes] = None,
) -> Tuple[int, Mapping[str, str], bytes]:
    _validate_url(url)
    request_headers: MutableMapping[str, str] = {"User-Agent": "codex-fetch/1.0"}
    if headers:
        request_headers.update(headers)
    req = Request(url, data=data, headers=request_headers, method=method)
    with urlopen(req, timeout=timeout) as resp:  # nosec B310 - scheme validated
        status = getattr(resp, "status", 200)
        header_map = {k: v for k, v in resp.headers.items()}
        body = resp.read()
        return status, header_map, body


__all__ = ["safe_fetch", "safe_request", "ALLOWED_SCHEMES"]
