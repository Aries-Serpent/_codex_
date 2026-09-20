from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from .utils import (
    classify_path,
    load_exceptions,
    load_policy,
    parse_common_args,
    requires_ingestion,
    utc_now,
    write_json,
)


def git_diff_name_status(repo_root: Path, base_ref: str, head_ref: str) -> list[tuple[str, str]]:
    cmd = ["git", "-C", str(repo_root), "diff", "--name-status", f"{base_ref}...{head_ref}"]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    rows: list[tuple[str, str]] = []
    for line in proc.stdout.splitlines():
        parts = line.strip().split("\t", 1)
        if len(parts) == 2:
            rows.append((parts[0], parts[1]))
    return rows


def run_changed_candidates(repo_root: Path, base_ref: str, head_ref: str = "HEAD") -> dict:
    policy = load_policy(repo_root)
    exceptions = load_exceptions(repo_root, policy)
    exts = set(policy.get("candidate_extensions", []))

    changed = []
    for status, path in git_diff_name_status(repo_root, base_ref, head_ref):
        suffix = Path(path).suffix.lower()
        if suffix not in exts:
            continue
        cls, confidence = classify_path(path, exceptions)
        changed.append(
            {
                "status": status,
                "path": path,
                "classification": cls,
                "confidence": confidence,
                "requires_ingestion": requires_ingestion(cls) and path not in exceptions,
            }
        )

    report = {
        "generated_at": utc_now(),
        "base_ref": base_ref,
        "head_ref": head_ref,
        "changed_candidates": changed,
        "new_unmanaged_candidates": [
            c["path"] for c in changed if c["status"].startswith("A") and c["requires_ingestion"]
        ],
    }
    out = repo_root / "docs-data" / "generated" / "changed-candidates.json"
    write_json(out, report)
    return {"ok": True, "changed": len(changed), "output": out.as_posix()}


def main() -> int:
    parser = parse_common_args(
        argparse.ArgumentParser(description="Detect changed candidate files")
    )
    parser.add_argument("--base-ref", default=None)
    parser.add_argument("--head-ref", default="HEAD")
    args = parser.parse_args()
    base_ref = args.base_ref or f"origin/{__import__('os').environ.get('GITHUB_BASE_REF', 'main')}"
    result = run_changed_candidates(Path(args.repo_root), base_ref, args.head_ref)
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print(f"changed candidates: {result['changed']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
