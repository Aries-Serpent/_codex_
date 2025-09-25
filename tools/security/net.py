"""Network helpers hardened against common security issues."""

from __future__ import annotations

from typing import Mapping, MutableMapping, Optional, Tuple
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ALLOWED_SCHEMES = {"https"}
_DEFAULT_HEADERS = {"User-Agent": "codex-fetch/1.0"}


def _merge_headers(user: Optional[Mapping[str, str]]) -> MutableMapping[str, str]:
    merged: MutableMapping[str, str] = dict(_DEFAULT_HEADERS)
    if user:
        merged.update(user)
    return merged


def safe_fetch(
    url: str,
    *,
    timeout: float = 20.0,
    headers: Optional[Mapping[str, str]] = None,
    data: Optional[bytes] = None,
    method: str = "GET",
    return_meta: bool = False,
) -> Tuple[int, bytes] | Tuple[int, bytes, dict[str, str]]:
    """Fetch a URL with an explicit scheme allow-list."""

    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise ValueError(f"disallowed scheme: {parsed.scheme}")

    req = Request(url, data=data, headers=_merge_headers(headers), method=method)
    with urlopen(req, timeout=timeout) as resp:  # nosec B310 - scheme validated above
        body = resp.read()
        code = resp.getcode() or 0
        if return_meta:
            meta = {
                "url": resp.geturl(),
                "headers": dict(resp.headers.items()),
            }
            return code, body, meta
        return code, body
