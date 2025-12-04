#!/usr/bin/env python
"""
Determinism Verifier
Runs the audit pipeline multiple times and compares artifacts ignoring timestamp fields.
Exits non-zero on mismatch.
"""
import json
import subprocess
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ["audit_artifacts/capabilities_scored.json", "audit_run_manifest.json"]

def normalized_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    # Recursively remove volatile fields
    def remove_volatile(obj):
        if isinstance(obj, dict):
            return {k: remove_volatile(v) for k, v in obj.items() 
                    if k not in ['generated', 'timestamp', 'generated_at', 'sha', 'size']}
        elif isinstance(obj, list):
            return [remove_volatile(item) for item in obj]
        return obj
    return remove_volatile(data)

def run_pipeline():
    result = subprocess.run(
        ["python", str(ROOT / "scripts" / "space_traversal" / "audit_runner.py"), "run"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"[ERROR] Pipeline failed with return code {result.returncode}")
        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")
        raise RuntimeError(f"Pipeline execution failed: {result.stderr[:500]}")
    return result

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
            assert p.exists(), f"Artifact missing: {rel}"
            snap[rel] = normalized_json(p)
        snapshots.append(snap)

    base = snapshots[0]
    for idx, snap in enumerate(snapshots[1:], start=2):
        for rel in ARTIFACTS:
            if base[rel] != snap[rel]:
                print(f"[FAIL] Mismatch in run {idx} for {rel}")
                print("Base vs Current diff (keys only):")
                print(set(base[rel].keys()) ^ set(snap[rel].keys()))
                raise SystemExit(1)

    print("\n[PASS] Determinism verified across runs.")

if __name__ == "__main__":
    main()
