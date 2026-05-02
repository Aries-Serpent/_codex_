#!/usr/bin/env python
"""
Verify Determinism

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/space_traversal/verify_determinism.py [options]

    Examples:
    $ python scripts/space_traversal/verify_determinism.py --help

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


import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ["audit_artifacts/capabilities_scored.json", "audit_run_manifest.json"]


def normalized_json(path: Path) -> dict:
    """Normalize JSON for deterministic comparison."""
    data = json.loads(path.read_text(encoding="utf-8"))

    def round_floats(obj, decimals=6):
        """Round all float values to specified decimals."""
        if isinstance(obj, float):
            return round(obj, decimals)
        if isinstance(obj, dict):
            return {k: round_floats(v, decimals) for k, v in obj.items()}
        if isinstance(obj, list):
            return [round_floats(item, decimals) for item in obj]
        return obj

    def remove_volatile(obj):
        """Remove volatile fields and normalize structure."""
        if isinstance(obj, dict):
            # Remove volatile timestamp fields
            result = {
                k: remove_volatile(v)
                for k, v in obj.items()
                if k not in ["generated", "timestamp", "generated_at", "sha", "size"]
            }
            # Sort capabilities by id if present
            if "capabilities" in result and isinstance(result["capabilities"], list):
                result["capabilities"] = sorted(
                    result["capabilities"], key=lambda x: x.get("id", "")
                )
                # Normalize each capability
                for cap in result["capabilities"]:
                    if "evidence_files" in cap:
                        cap["evidence_files"] = sorted(cap["evidence_files"])
                    if "found_patterns" in cap:
                        cap["found_patterns"] = sorted(cap["found_patterns"])
            return result
        if isinstance(obj, list):
            return [remove_volatile(item) for item in obj]
        return obj

    # First remove volatile fields, then round floats
    normalized = remove_volatile(data)
    return round_floats(normalized)


def run_pipeline():
    import sys

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "space_traversal" / "audit_runner.py"), "run"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    if result.returncode != 0:
        print(f"[ERROR] Pipeline failed with return code {result.returncode}")
        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")
        raise RuntimeError(f"Pipeline execution failed: {result.stderr[:500]}")
    return result


def deep_diff(obj1, obj2, path=""):
    """Find deep differences between two objects."""
    if not isinstance(obj1, type(obj2)):
        return f"Type mismatch at {path}: {type(obj1).__name__} vs {type(obj2).__name__}"

    if isinstance(obj1, dict):
        keys1, keys2 = set(obj1.keys()), set(obj2.keys())
        if keys1 != keys2:
            return f"Key mismatch at {path}: {keys1 ^ keys2}"
        for key in keys1:
            diff = deep_diff(obj1[key], obj2[key], f"{path}.{key}")
            if diff:
                return diff
    elif isinstance(obj1, list):
        if len(obj1) != len(obj2):
            return f"Length mismatch at {path}: {len(obj1)} vs {len(obj2)}"
        for i, (item1, item2) in enumerate(zip(obj1, obj2)):
            diff = deep_diff(item1, item2, f"{path}[{i}]")
            if diff:
                return diff
    elif obj1 != obj2:
        return f"Value mismatch at {path}: {obj1} vs {obj2}"

    return None


def main():
    parser = argparse.ArgumentParser(description="Verify determinism of audit pipeline")
    parser.add_argument("--runs", type=int, default=2, help="Number of runs to compare")
    args = parser.parse_args()

    snapshots = []
    for i in range(args.runs):
        print(f"\n=== Run {i+1}/{args.runs} ===")
        run_pipeline()
        snap = {}
        for rel in ARTIFACTS:
            p = ROOT / rel
            artifact_exists = p.exists()
            assert artifact_exists, f"Artifact missing: {rel}"
            snap[rel] = normalized_json(p)
        snapshots.append(snap)

    base = snapshots[0]
    for idx, snap in enumerate(snapshots[1:], start=2):
        for rel in ARTIFACTS:
            if base[rel] != snap[rel]:
                print(f"[FAIL] Mismatch in run {idx} for {rel}")
                diff = deep_diff(base[rel], snap[rel], rel)
                if diff:
                    print(f"Difference: {diff}")
                else:
                    print("Structures differ but deep_diff couldn't pinpoint location")
                raise SystemExit(1)

    print("\n[PASS] Determinism verified across runs.")


if __name__ == "__main__":
    main()
