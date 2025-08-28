#!/usr/bin/env python3
"""
Portable, offline fallback for `chatgpt-codex --prompt-file AUDIT_PROMPT.md`.

Reads a prompt file, builds a simple repository audit (inventory + quick checks),
and writes `audit_output/` artifacts for later review.

Usage:
  python tools/audit_builder.py --prompt-file AUDIT_PROMPT.md
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "audit_output"
OUT.mkdir(parents=True, exist_ok=True)


def ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256()
    h.update(b)
    return h.hexdigest()


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def build_inventory():
    items = []
    for root, dirs, files in os.walk(ROOT):
        if any(s in root for s in ("/.git", "/.venv", "/__pycache__")):
            continue
        for fn in files:
            p = Path(root) / fn
            try:
                sz = p.stat().st_size
            except Exception:
                sz = None
            items.append(
                {
                    "path": str(p.relative_to(ROOT)),
                    "size": sz,
                    "sha256": sha256_file(p) if sz is not None and sz <= 5_000_000 else None,
                }
            )
    return {"count": len(items), "items": items}


def summarize_readme():
    for candidate in ("README.md", "readme.md", "README.rst"):
        p = ROOT / candidate
        if p.exists():
            text = p.read_text(encoding="utf-8", errors="replace")
            return {
                "file": candidate,
                "sha256": sha256_bytes(text.encode("utf-8")),
                "preview": text[:2000],
            }
    return {"file": None, "note": "No README found"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt-file", required=True)
    args = ap.parse_args()

    prompt_path = ROOT / args.prompt_file
    if not prompt_path.exists():
        print(f"[audit_builder] prompt file not found: {prompt_path}", file=sys.stderr)
        sys.exit(2)

    prompt_text = prompt_path.read_text(encoding="utf-8", errors="replace")
    report = {
        "timestamp": ts(),
        "prompt_file": str(prompt_path),
        "prompt_sha256": sha256_bytes(prompt_text.encode("utf-8")),
        "readme": summarize_readme(),
        "inventory": build_inventory(),
    }

    (OUT / "audit.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (OUT / "prompt_copy.md").write_text(prompt_text, encoding="utf-8")

    md = [
        f"# Codex Audit ({report['timestamp']})",
        "",
        "## Prompt",
        f"- File: `{report['prompt_file']}`",
        f"- SHA-256: `{report['prompt_sha256']}`",
        "",
        "## README",
        f"- File: `{report['readme'].get('file')}`",
        f"- SHA-256: `{report['readme'].get('sha256')}`",
        "```",
        report["readme"].get("preview", ""),
        "```",
        "",
        "## Inventory",
        f"- Files: {report['inventory']['count']}",
        "",
        "<details><summary>Show inventory</summary>",
        "",
        "```json",
        json.dumps(report["inventory"]["items"][:500], indent=2),
        "```",
        "",
        "</details>",
        "",
    ]
    (OUT / "audit.md").write_text("\n".join(md), encoding="utf-8")
    print(f"[audit_builder] Wrote: {OUT/'audit.json'} and {OUT/'audit.md'}")


if __name__ == "__main__":
    main()
