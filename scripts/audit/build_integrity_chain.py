#!/usr/bin/env python3
"""
Build Audit Integrity Chain artifacts and a manifest with SHA256 hashes.

Artifacts (created or hashed if present):
 - audit_artifacts/context_index.json
 - audit_artifacts/facets.json
 - audit_artifacts/capabilities_raw.json
 - audit_artifacts/capabilities_scored.json
 - audit_artifacts/gaps.json
 - reports/capability_matrix_<ts>.md
 - audit_run_manifest.json
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = [
    "audit_artifacts/context_index.json",
    "audit_artifacts/facets.json",
    "audit_artifacts/capabilities_raw.json",
    "audit_artifacts/capabilities_scored.json",
    "audit_artifacts/gaps.json",
]
MANIFEST = REPO_ROOT / "audit_run_manifest.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_dirs():
    (REPO_ROOT / "audit_artifacts").mkdir(parents=True, exist_ok=True)
    (REPO_ROOT / "reports").mkdir(parents=True, exist_ok=True)


def main() -> int:
    ensure_dirs()
    entries: List[Dict] = []

    # Hash existing artifacts (create minimal placeholders if missing)
    for rel in ARTIFACTS:
        p = REPO_ROOT / rel
        if not p.exists():
            p.write_text("{}", encoding="utf-8")
        entries.append(
            {
                "path": rel,
                "sha256": sha256_file(p),
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "notes": "",
            }
        )

    # Hash capability matrix reports if any
    for md in sorted((REPO_ROOT / "reports").glob("capability_matrix_*.md")):
        entries.append(
            {
                "path": str(md.relative_to(REPO_ROOT)),
                "sha256": sha256_file(md),
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "notes": "Capability matrix snapshot",
            }
        )

    # Repo root SHA (if git available)
    try:
        import subprocess

        head = (
            subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(REPO_ROOT))
            .decode("utf-8")
            .strip()
        )
    except Exception:
        head = ""

    manifest = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root_sha": head,
        "artifacts": entries,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"[OK] Wrote manifest {MANIFEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
