#!/usr/bin/env python3
"""Standalone Markdown link audit for the repository."""

from __future__ import annotations

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "artifacts" / "docs_link_audit"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SKIP_PARTS = {
    ".git",
    ".nox",
    ".tox",
    "__pycache__",
    "artifacts",
    "build",
    "dist",
    "logs",
    "mlruns",
    "nox_sessions",
    "site-packages",
}
MARKDOWN_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def _should_skip(path: pathlib.Path) -> bool:
    return any(part in SKIP_PARTS for part in path.parts)


def main() -> None:
    results: list[dict[str, object]] = []
    for markdown in ROOT.rglob("*.md"):
        if _should_skip(markdown):
            continue
        try:
            text = markdown.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for match in MARKDOWN_LINK.finditer(text):
            target = match.group(2).strip()
            if target.startswith(("http://", "https://")):
                results.append(
                    {
                        "file": str(markdown),
                        "type": "external",
                        "target": target,
                        "exists": None,
                    }
                )
                continue
            resolved = (markdown.parent / target.split("#", 1)[0].split("?", 1)[0]).resolve()
            results.append(
                {
                    "file": str(markdown),
                    "type": "relative",
                    "target": target,
                    "exists": resolved.exists(),
                }
            )
    (OUTPUT_DIR / "links.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print("[links] DONE")


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
