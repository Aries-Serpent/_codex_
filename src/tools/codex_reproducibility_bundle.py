#!/usr/bin/env python
"""Generate a reproducibility bundle manifest for `_codex_`.

The manifest is a JSON file that records the presence and paths of
key artifacts such as:

- Audit report
- Gap registry and reports
- Config validation report
- Dependency report
- Secret scan report
- Env snapshot
- Experiment index
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_FILES = [
    "_codex_status_update-2025-11-27.md",
    "codex_gap_registry.yaml",
    "codex_yaml_gap_report.md",
    "codex_gap_trends.md",
    "codex_config_validation_report.json",
    "codex_dependency_report.json",
    "codex_secret_scan_report.json",
    "codex_env_snapshot.json",
    "codex_experiment_index.json",
    "codex_experiment_index.md",
]


def _describe(path: Path) -> dict[str, Any]:
    return {
        "path": str(path),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else None,
    }


def build_manifest(repo_root: Path, audit: str) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    files: list[str] = list(DEFAULT_FILES)
    if audit not in files:
        files.insert(0, audit)

    entries = {}
    for name in files:
        entries[name] = _describe(repo_root / name)

    # convenience aliases expected by some tests
    entries["audit"] = entries.get(audit, _describe(repo_root / audit))
    entries["env_snapshot_json"] = entries.get("codex_env_snapshot.json", {})

    return {
        "repo_root": str(repo_root),
        "audit": audit,
        "artifacts": entries,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate reproducibility bundle manifest for _codex_."
    )
    parser.add_argument(
        "--repo-root",
        type=str,
        default=".",
        help="Repository root (default: current directory).",
    )
    parser.add_argument(
        "--audit",
        type=str,
        default="_codex_status_update-2025-11-27.md",
        help="Audit file name (default: _codex_status_update-2025-11-27.md).",
    )
    parser.add_argument(
        "--manifest-out",
        type=str,
        default="codex_reproducibility_manifest.json",
        help="Manifest output path (default: codex_reproducibility_manifest.json).",
    )
    args = parser.parse_args(argv)

    root = Path(args.repo_root).expanduser().resolve()
    manifest = build_manifest(root, args.audit)
    out_raw = Path(args.manifest_out)
    out = out_raw if out_raw.is_absolute() else root / out_raw
    out.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote reproducibility manifest to {out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
