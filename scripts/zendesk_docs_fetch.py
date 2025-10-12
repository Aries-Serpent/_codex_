#!/usr/bin/env python3
"""Fetch and snapshot Zendesk developer docs for local/offline training.

Constraints:
- No CI/GitHub Actions.
- Writes under docs/vendors/zendesk/YYYY-MM-DD/<section>/<page>.html.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "zendesk_docs_manifest.json"
OUTROOT = ROOT / "docs" / "vendors" / "zendesk"

SAFE_NAME = re.compile(r"[^a-z0-9]+")


def _slug(text: str) -> str:
    return SAFE_NAME.sub("-", text.lower()).strip("-")


def _fetch(url: str) -> bytes:
    with urllib.request.urlopen(url) as response:  # noqa: S310 - curated domains
        return response.read()


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
