#!/usr/bin/env python3
"""
Zendesk Docs Catalog

Purpose:
    Main execution script

Usage:
    python scripts/zendesk_docs_catalog.py [options]

    Examples:
    $ python scripts/zendesk_docs_catalog.py --help

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


from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "zendesk_docs_manifest.json"
OUT_MD = ROOT / "docs" / "zendesk_api_catalog_generated.md"


def main() -> int:
    payload: dict[str, Any] = json.loads(MANIFEST.read_text(encoding="utf-8"))
    lines: list[str] = ["# Zendesk API Catalog (Generated)", ""]

    # Known schema fields to skip (not Zendesk sections)
    schema_fields = {'name', 'version', 'splits', 'checksums', 'features'}

    # Only process Zendesk sections (which are dicts with URL arrays)
    for section, buckets in sorted(payload.items()):
        if section in schema_fields or not isinstance(buckets, dict):
            continue

        lines.append(f"## {section.title()}")
        for bucket, urls in (buckets or {}).items():
            if not isinstance(urls, list):
                continue
            lines.append(f"### {bucket.replace('_', ' ').title()}")
            for url in urls:
                lines.append(f"- {url}")
        lines.append("")
    content = "\n".join(lines).rstrip() + "\n"
    OUT_MD.write_text(content, encoding="utf-8")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
