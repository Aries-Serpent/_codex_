#!/usr/bin/env python3
"""
Compare two JSON/YAML schemas and report additive/removal/breaking changes.

Usage:
  python tools/schema_diff.py --old path/to/old.schema.json --new path/to/new.schema.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

try:
    import yaml  # type: ignore
except Exception:
    yaml = None  # type: ignore


def load_any(p: Path) -> Any:
    text = p.read_text(encoding="utf-8")
    if p.suffix.lower() == ".json":
        return json.loads(text)
    if p.suffix.lower() in {".yaml", ".yml"} and yaml is not None:
        return yaml.safe_load(text)
    return json.loads(text)


def classify_changes(old: Dict, new: Dict) -> Dict[str, Any]:
    changes = {"added_keys": [], "removed_keys": [], "type_changes": []}

    def walk(o: Any, n: Any, path: str = ""):
        if isinstance(o, dict) and isinstance(n, dict):
            o_keys = set(o.keys())
            n_keys = set(n.keys())
            for k in sorted(n_keys - o_keys):
                changes["added_keys"].append(f"{path}.{k}".strip("."))
            for k in sorted(o_keys - n_keys):
                changes["removed_keys"].append(f"{path}.{k}".strip("."))
            for k in sorted(o_keys & n_keys):
                walk(o[k], n[k], f"{path}.{k}".strip("."))
        else:
            if type(o) is not type(n):
                changes["type_changes"].append(
                    {"path": path, "old": type(o).__name__, "new": type(n).__name__}
                )

    walk(old, new)
    return changes


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--old", required=True)
    ap.add_argument("--new", required=True)
    args = ap.parse_args(argv)

    old = load_any(Path(args.old))
    new = load_any(Path(args.new))
    diff = classify_changes(old, new)
    print(json.dumps(diff, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
