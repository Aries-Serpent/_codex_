#!/usr/bin/env python3
"""
Extract per-module coverage from coverage.json.

Output:
  coverage_modules.json with module -> percent mapping

Usage:
  python tools/coverage_extract.py --coverage-json .coverage.json --out coverage_modules.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def extract_modules(cov: dict) -> dict:
    """Extract per-file coverage; group by top-level module."""
    files = cov.get("files", {})
    modules = {}
    for path, data in files.items():
        # Extract module name from path (e.g., src/security/core.py -> src/security)
        parts = Path(path).parts
        if len(parts) >= 2:
            mod = "/".join(parts[:2])
        else:
            mod = parts[0] if parts else "unknown"
        pct = data.get("summary", {}).get("percent_covered", 0.0)
        if mod not in modules:
            modules[mod] = []
        modules[mod].append(pct)

    # Average per module
    return {k: sum(v) / len(v) for k, v in modules.items()}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Extract per-module coverage")
    ap.add_argument("--coverage-json", required=True, help="Path to .coverage.json")
    ap.add_argument("--out", default="coverage_modules.json", help="Output JSON")
    args = ap.parse_args(argv)

    cov = json.loads(Path(args.coverage_json).read_text(encoding="utf-8"))
    modules = extract_modules(cov)
    out = Path(args.out)
    out.write_text(json.dumps(modules, indent=2), encoding="utf-8")
    print(f"[OK] Wrote {out} with {len(modules)} modules")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
