"""Offline link audit for Markdown documentation."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterator

DOCS_ROOT = Path("docs")
OUTPUT_PATH = Path("artifacts/docs/link_audit/report.json")
_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)#]+)(?:#[^)]+)?\)")


def _iter_markdown(root: Path) -> Iterator[Path]:
    for path in root.rglob("*.md"):
        if path.is_file():
            yield path


def _resolve(target: str, base: Path) -> Path:
    candidate = (base.parent / target).resolve()
    return candidate


def audit() -> dict[str, list[str]]:
    results: dict[str, list[str]] = {}
    for md in _iter_markdown(DOCS_ROOT):
        missing: list[str] = []
        text = md.read_text(encoding="utf-8")
        for match in _LINK_RE.finditer(text):
            link = match.group(1)
            if link.startswith("http"):
                continue
            candidate = _resolve(link, md)
            if not candidate.exists():
                missing.append(link)
        if missing:
            results[str(md)] = missing
    return results


def main() -> int:
    results = audit()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
