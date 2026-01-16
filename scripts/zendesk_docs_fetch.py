#!/usr/bin/env python3
"""
Zendesk Docs Fetch

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/zendesk_docs_fetch.py [options]
    
    Examples:
    $ python scripts/zendesk_docs_fetch.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""


"""Fetch and snapshot Zendesk developer docs for local/offline training.

Constraints:
- No CI/GitHub Actions.
- Writes under docs/vendors/zendesk/YYYY-MM-DD/<section>/<page>.html.
"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

import argparse
import datetime as dt
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "zendesk_docs_manifest.json"
OUTROOT = ROOT / "docs" / "vendors" / "zendesk"

SAFE_NAME = re.compile(r"[^a-z0-9]+")


def _slug(text: str) -> str:
    return SAFE_NAME.sub("-", text.lower()).strip("-")


def _fetch(url: str, retries: int = 3, backoff: float = 0.8) -> bytes:
    """Fetch URL with HTTPS-only validation and retry logic.
    
    Args:
        url: URL to fetch (must be HTTPS)
        retries: Number of retry attempts
        backoff: Backoff multiplier for retries
        
    Returns:
        Response body as bytes
        
    Raises:
        ValueError: If URL scheme is not HTTPS
        RuntimeError: If all retries fail
    """
    parsed = urllib.parse.urlparse(url)
    # Security: Only allow HTTPS to prevent file:// or other scheme attacks
    # RFC 3986: schemes are case-insensitive, so normalize to lowercase
    if parsed.scheme.lower() != "https":
        raise ValueError(
            f"Only HTTPS URLs are allowed, got scheme {parsed.scheme!r} in {url!r}"
        )
    # Additional validation: ensure hostname is present
    if not parsed.hostname:
        raise ValueError(f"URL must have a valid hostname: {url!r}")
    
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "codex-zendesk-docs/1.0 (+offline-snapshot)"},
        method="GET",
    )
    last_exc: Exception | None = None
    for attempt in range(retries):
        try:
            # Security: URL already validated to be HTTPS-only above
            with urllib.request.urlopen(req) as response:  # noqa: S310
                return response.read()
        except Exception as exc:  # pragma: no cover - network failures are non-deterministic
            last_exc = exc
            time.sleep(backoff * (2**attempt))
    raise RuntimeError(f"Failed to fetch {url!r}") from last_exc


def _write_html(base: Path, url: str, body: bytes) -> Path:
    base.mkdir(parents=True, exist_ok=True)
    name = _slug(url) + ".html"
    out = base / name
    out.write_bytes(body)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not download; only list targets.",
    )
    args = parser.parse_args()

    manifest: dict[str, Any] = json.loads(MANIFEST.read_text(encoding="utf-8"))
    stamp = dt.date.today().isoformat()
    outdir = OUTROOT / stamp

    planned: list[str] = []
    for section, buckets in manifest.items():
        for bucket, urls in (buckets or {}).items():
            for url in urls:
                planned.append(url)
                if args.dry_run:
                    print(f"[DRY] {section}/{bucket}: {url}")
                    continue
                body = _fetch(url)
                _write_html(outdir / section / bucket, url, body)

    if args.dry_run:
        print(f"[DRY] {len(planned)} pages planned")
    else:
        print(f"Wrote snapshot to {outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
