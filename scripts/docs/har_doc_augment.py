#!/usr/bin/env python3
"""
har_doc_augment.py — Augment an HAR (HTTP Archive) file with documentation
content fetched from the local repository.

Reads an existing HAR file, finds entries whose URL matches the GitHub raw
content API pattern for Markdown files in this repository, and inserts/
replaces the response body with the current on-disk Markdown content.

This allows end-to-end tests and the HAR-replay Playwright fixture to serve
live, up-to-date documentation without hitting the network.

Usage:
    python scripts/docs/har_doc_augment.py --input HAR_FILE [--output HAR_OUT]
    python scripts/docs/har_doc_augment.py --input path/to/capture.har --dry-run
    python scripts/docs/har_doc_augment.py --create-stub --output path/to/new.har

Exit codes:
    0  — success
    1  — I/O or parse error
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Raw GitHub URL pattern for this repo
RAW_URL_PREFIX = "https://raw.githubusercontent.com/Aries-Serpent/_codex_/"


# ---------------------------------------------------------------------------
# HAR helpers
# ---------------------------------------------------------------------------

def _load_har(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _save_har(har: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(har, indent=2, ensure_ascii=False), encoding="utf-8")


def _make_stub_har() -> dict:
    """Return a minimal valid HAR 1.2 skeleton."""
    return {
        "log": {
            "version": "1.2",
            "creator": {"name": "har_doc_augment.py", "version": "1.0"},
            "entries": [],
        }
    }


def _url_to_repo_path(url: str) -> str | None:
    """
    Convert a raw.githubusercontent URL to a repo-relative path.

    e.g.:
      https://raw.githubusercontent.com/Aries-Serpent/_codex_/0D_base_/AGENTS.md
      → "AGENTS.md"
    """
    if not url.startswith(RAW_URL_PREFIX):
        return None
    remainder = url[len(RAW_URL_PREFIX):]
    # remainder: "<branch>/<path>"
    parts = remainder.split("/", 1)
    if len(parts) < 2:
        return None
    return parts[1]


def _build_har_entry(url: str, body: str) -> dict:
    body_bytes = body.encode("utf-8")
    return {
        "startedDateTime": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "time": 0,
        "request": {
            "method": "GET",
            "url": url,
            "httpVersion": "HTTP/1.1",
            "headers": [],
            "queryString": [],
            "cookies": [],
            "headersSize": -1,
            "bodySize": -1,
        },
        "response": {
            "status": 200,
            "statusText": "OK",
            "httpVersion": "HTTP/1.1",
            "headers": [
                {"name": "Content-Type", "value": "text/plain; charset=utf-8"},
                {"name": "Content-Length", "value": str(len(body_bytes))},
            ],
            "cookies": [],
            "content": {
                "size": len(body_bytes),
                "mimeType": "text/plain; charset=utf-8",
                "text": body,
                "encoding": "utf-8",
            },
            "redirectURL": "",
            "headersSize": -1,
            "bodySize": len(body_bytes),
        },
        "cache": {},
        "timings": {"send": 0, "wait": 0, "receive": 0},
        "_fromHarAugment": True,
    }


# ---------------------------------------------------------------------------
# Augmentation logic
# ---------------------------------------------------------------------------

def augment_har(har: dict, repo_root: Path, dry_run: bool = False) -> tuple[dict, int]:
    """
    Walk all HAR entries.  For entries whose URL maps to a local Markdown file,
    replace (or insert) the response body with on-disk content.

    Returns (augmented_har, count_augmented).
    """
    entries = har.get("log", {}).get("entries", [])
    augmented = 0

    for entry in entries:
        url = entry.get("request", {}).get("url", "")
        repo_path = _url_to_repo_path(url)
        if repo_path is None:
            continue
        local_file = repo_root / repo_path
        if not local_file.exists():
            continue
        if local_file.suffix.lower() not in (".md", ".txt", ".rst", ".json"):
            continue

        body = local_file.read_text(encoding="utf-8")
        if not dry_run:
            entry["response"]["content"]["text"] = body
            entry["response"]["content"]["size"] = len(body.encode("utf-8"))
            entry["response"]["content"]["encoding"] = "utf-8"
            entry["_fromHarAugment"] = True
        augmented += 1

    return har, augmented


def inject_catalog_stubs(har: dict, repo_root: Path, branch: str = "0D_base_") -> int:
    """
    For each entry in DOC_CATALOG that has a corresponding local file, add a
    stub HAR entry if one doesn't already exist for that URL.

    Returns count of entries injected.
    """
    # Lazily import to avoid hard dep on the doc catalog parsing
    sys.path.insert(0, str(Path(__file__).parent))
    try:
        from build_doc_search_index import DOC_DATA_TS, _extract_doc_catalog
        ts_source = DOC_DATA_TS.read_text(encoding="utf-8")
        catalog = _extract_doc_catalog(ts_source)
    except Exception:
        catalog = []
    finally:
        sys.path.pop(0)

    existing_urls = {
        e.get("request", {}).get("url", "")
        for e in har.get("log", {}).get("entries", [])
    }

    injected = 0
    for doc in catalog:
        path = doc.get("path", "")
        url = f"{RAW_URL_PREFIX}{branch}/{path}"
        if url in existing_urls:
            continue
        local_file = repo_root / path
        if not local_file.exists():
            continue
        body = local_file.read_text(encoding="utf-8")
        entry = _build_har_entry(url, body)
        har["log"]["entries"].append(entry)
        injected += 1

    return injected


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--input", type=Path, metavar="HAR_FILE",
                   help="Input HAR file to augment")
    p.add_argument("--output", type=Path, metavar="HAR_OUT",
                   help="Output HAR file (default: overwrite --input)")
    p.add_argument("--branch", default="0D_base_",
                   help="Repository branch used in raw URLs (default: 0D_base_)")
    p.add_argument("--dry-run", action="store_true",
                   help="Show what would be changed without writing")
    p.add_argument("--create-stub", action="store_true",
                   help="Create a new minimal HAR stub populated with catalog entries")
    p.add_argument("--inject-catalog", action="store_true",
                   help="Inject DOC_CATALOG stubs for local files missing from the HAR")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    if args.create_stub:
        if not args.output:
            print("ERROR: --output is required with --create-stub", file=sys.stderr)
            return 1
        har = _make_stub_har()
        n = inject_catalog_stubs(har, REPO_ROOT, args.branch)
        if not args.dry_run:
            _save_har(har, args.output)
        print(f"✓ Created stub HAR with {n} catalog entries → {args.output}")
        return 0

    if not args.input:
        print("ERROR: --input is required (or use --create-stub)", file=sys.stderr)
        return 1
    if not args.input.exists():
        print(f"ERROR: HAR file not found: {args.input}", file=sys.stderr)
        return 1

    try:
        har = _load_har(args.input)
    except Exception as exc:
        print(f"ERROR loading HAR: {exc}", file=sys.stderr)
        return 1

    har, n_aug = augment_har(har, REPO_ROOT, args.dry_run)

    n_inj = 0
    if args.inject_catalog:
        n_inj = inject_catalog_stubs(har, REPO_ROOT, args.branch)

    out = args.output or args.input
    if not args.dry_run:
        _save_har(har, out)

    mode = "DRY-RUN" if args.dry_run else "✓"
    print(f"{mode} augmented {n_aug} entries, injected {n_inj} stubs → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
