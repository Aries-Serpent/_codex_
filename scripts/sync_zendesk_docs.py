#!/usr/bin/env python3
"""Curate and render the Zendesk API index for offline workflows."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "data" / "zendesk_api_index.json"
OUTPUT_MD = ROOT / "docs" / "zendesk_api_catalog_generated.md"


def _load_index(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):  # pragma: no cover - safety check
        raise ValueError("Zendesk API index must be a mapping")
    return payload


def _render_markdown(index: dict[str, Any]) -> str:
    lines: list[str] = ["# Zendesk API Catalog (Generated)", ""]
    for section, payload in sorted(index.items()):
        lines.append(f"## {section.replace('_', ' ').title()}")
        docs = payload.get("docs") or []
        doc = payload.get("doc")
        if doc:
            lines.append(f"- Doc: {doc}")
        for extra_doc in docs:
            lines.append(f"- Doc: {extra_doc}")
        for endpoint in payload.get("endpoints", []):
            lines.append(f"- Endpoint: `{endpoint}`")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def main() -> int:
    index = _load_index(INDEX_PATH)
    OUTPUT_MD.write_text(_render_markdown(index), encoding="utf-8")
    print(f"Wrote {OUTPUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
