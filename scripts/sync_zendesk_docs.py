#!/usr/bin/env python3
"""Curate the local Zendesk API documentation index."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "zendesk_api_index.json"
OUT_MD = ROOT / "docs" / "zendesk_api_catalog_generated.md"


def main() -> int:
    payload = json.loads(INDEX.read_text(encoding="utf-8"))
    lines = ["# Zendesk API Catalog (Generated)", ""]
    for section, body in sorted(payload.items()):
        lines.append(f"## {section.replace('_', ' ').title()}")
        doc = body.get("doc")
        docs = body.get("docs", [])
        if doc:
            lines.append(f"- Doc: {doc}")
        for extra in docs:
            lines.append(f"- Doc: {extra}")
        for endpoint in body.get("endpoints", []):
            lines.append(f"- Endpoint: `{endpoint}`")
        lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
