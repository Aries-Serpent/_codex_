from __future__ import annotations

import argparse
import json
from pathlib import Path

from .inventory import run_inventory
from .utils import (
    CANONICAL_JSONL_FILES,
    load_policy,
    parse_common_args,
    read_jsonl,
    utc_now,
    write_json,
)


def _source_trace_paths(repo_root: Path) -> set[str]:
    covered: set[str] = set()
    for file in CANONICAL_JSONL_FILES.values():
        for row in read_jsonl(file):
            trace = row.get("source_trace", {})
            src = trace.get("source_path")
            if src:
                covered.add(src)
    return covered


def run_coverage(repo_root: Path, strict: bool = True) -> dict:
    generated_dir = repo_root / "docs-data" / "generated"
    inv_path = generated_dir / "candidate-inventory.json"
    if not inv_path.exists():
        run_inventory(repo_root)
    inventory = json.loads(inv_path.read_text(encoding="utf-8")).get("candidates", [])

    policy = load_policy(repo_root)
    covered_paths = _source_trace_paths(repo_root)

    covered = []
    unmanaged = []
    exempted = []
    generated = []
    ignored = []
    requires_ingestion = []
    review = []

    for entry in inventory:
        path = entry["path"]
        cls = entry["classification"]
        if cls == "generated_machine_readable_artifact":
            generated.append(path)
            continue
        if cls == "exception_candidate":
            exempted.append(path)
            continue
        if cls in {
            "workflow_file",
            "configuration",
            "schema",
            "canonical_machine_readable_record",
            "ignored_dependency_or_build_file",
        }:
            covered.append(path)
            continue
        if path in covered_paths:
            covered.append(path)
            continue
        if entry.get("requires_ingestion"):
            requires_ingestion.append(path)
            unmanaged.append(path)
        else:
            review.append(path)

    report = {
        "generated_at": utc_now(),
        "covered_files": sorted(covered),
        "unmanaged_files": sorted(unmanaged),
        "exempted_files": sorted(exempted),
        "generated_files": sorted(generated),
        "ignored_files": sorted(ignored),
        "files_requiring_ingestion": sorted(requires_ingestion),
        "files_requiring_review": sorted(review),
        "strict_mode": policy.get("enforcement", {}).get("default_mode", "strict") == "strict",
        "ci_failure_reason": "" if not unmanaged else "Unmanaged candidate files detected",
    }

    out = generated_dir / "machine-readable-coverage-report.json"
    write_json(out, report)
    fail = (
        strict
        and bool(unmanaged)
        and policy.get("enforcement", {}).get("fail_on_unmanaged_candidates", True)
    )
    return {"ok": not fail, "unmanaged": len(unmanaged), "output": out.as_posix(), "report": report}


def main() -> int:
    parser = parse_common_args(
        argparse.ArgumentParser(description="Coverage verification for machine-readable docs")
    )
    parser.add_argument("--no-strict", action="store_true")
    args = parser.parse_args()
    result = run_coverage(Path(args.repo_root), strict=not args.no_strict)
    if args.json:
        print(json.dumps({k: v for k, v in result.items() if k != "report"}, sort_keys=True))
    else:
        print(f"coverage ok={result['ok']} unmanaged={result['unmanaged']}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
