#!/usr/bin/env python3
"""
Generate Context Manifest

Purpose:
    Generates context_manifest

Usage:
    python scripts/deepresearch/generate_context_manifest.py [options]
    
    Examples:
    $ python scripts/deepresearch/generate_context_manifest.py --help

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

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def discover_api_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in {".yaml", ".yml", ".json"}
    )


def build_manifest(apis_dir: Path) -> dict:
    api_files = discover_api_files(apis_dir)
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "generated_utc": generated,
        "apis_dir": str(apis_dir),
        "apis": [
            {
                "path": str(path.relative_to(apis_dir)),
                "name": path.stem,
            }
            for path in api_files
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the DeepResearch context manifest")
    parser.add_argument(
        "--apis-dir",
        default="docs/deepresearch/apis",
        help="Directory containing OpenAPI documents",
    )
    parser.add_argument(
        "--out",
        default="deepresearch/context_manifest.json",
        help="Manifest output path",
    )
    args = parser.parse_args(argv)

    apis_dir = Path(args.apis_dir)
    manifest = build_manifest(apis_dir)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"[OK] Wrote {out_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
