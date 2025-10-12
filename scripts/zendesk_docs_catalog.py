#!/usr/bin/env python3
"""Render a Markdown catalog from captured Zendesk docs."""
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
    for section, buckets in sorted(payload.items()):
        lines.append(f"## {section.title()}")
        for bucket, urls in (buckets or {}).items():
            lines.append(f"### {bucket.replace('_', ' ').title()}")
            for url in urls:
                lines.append(f"- {url}")
        lines.append("")
    OUT_MD.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
