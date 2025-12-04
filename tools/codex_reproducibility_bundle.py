#!/usr/bin/env python
"""Create a small reproducibility bundle manifest for _codex_.

This tool does NOT create archives; instead it:
- Ensures an environment snapshot exists (creates one if needed).
- Collects paths to key artifacts (audit, gap registry, YAML reports, ML test summaries).
- Writes a JSON manifest with normalized, absolute paths and simple existence flags.

This keeps reproducibility metadata lightweight and local-only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Optional

import sys

_TOOLS_ROOT = Path(__file__).resolve().parent
if str(_TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(_TOOLS_ROOT))

import codex_env_snapshot as envsnap  # type: ignore[import]


def _hash_file(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _record_file(path: Path) -> Dict[str, Any]:
    return {
        "path": str(path),
        "exists": path.exists(),
        "sha256": _hash_file(path),
    }


def build_manifest(repo_root: Path, audit_name: str) -> Dict[str, Any]:
    audit_path = repo_root / audit_name

    artifacts = {
        "audit": _record_file(audit_path),
        "gap_registry": _record_file(repo_root / "codex_gap_registry.yaml"),
        "yaml_gap_report": _record_file(repo_root / "codex_yaml_gap_report.md"),
        "gap_trends": _record_file(repo_root / "codex_gap_trends.md"),
        "change_log": _record_file(repo_root / "codex_change_log.md"),
        "error_questions": _record_file(repo_root / "codex_error_questions.md"),
        "mltest_infra_summary": _record_file(
            repo_root / "codex_mltest_infra_summary.json"
        ),
        "env_snapshot_json": _record_file(repo_root / "codex_env_snapshot.json"),
        "env_snapshot_md": _record_file(repo_root / "codex_env_snapshot.md"),
        "dependency_report": _record_file(repo_root / "codex_dependency_report.json"),
        "secret_scan_report": _record_file(repo_root / "codex_secret_scan_report.json"),
    }

    manifest: Dict[str, Any] = {
        "repo_root": str(repo_root),
        "audit_name": audit_name,
        "artifacts": artifacts,
    }
    return manifest


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Create reproducibility bundle manifest.")
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
        help="Audit filename to reference (default: _codex_status_update-2025-11-27.md).",
    )
    parser.add_argument(
        "--manifest-out",
        type=str,
        default="codex_reproducibility_manifest.json",
        help="Path to manifest JSON output (default: codex_reproducibility_manifest.json).",
    )
    args = parser.parse_args(argv)

    root = Path(args.repo_root).expanduser().resolve()

    json_out = root / "codex_env_snapshot.json"
    md_out = root / "codex_env_snapshot.md"
    if not json_out.exists() or not md_out.exists():
        envsnap.main(
            [
                "--json-out",
                str(json_out),
                "--md-out",
                str(md_out),
            ]
        )

    manifest = build_manifest(root, args.audit)
    out_path = root / args.manifest_out
    out_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote reproducibility manifest to {out_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
