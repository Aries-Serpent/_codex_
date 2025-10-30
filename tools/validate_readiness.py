#!/usr/bin/env python
"""
Validate readiness.json artifacts against docs/status_updates/readiness.schema.json.
Usage:
  python tools/validate_readiness.py <path/to/readiness.json> [...] --schema docs/status_updates/readiness.schema.json
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys


def _as_float(v):
    try:
        return float(v)
    except Exception:
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("artifacts", nargs="+", help="Path(s) to readiness.json")
    ap.add_argument("--schema", required=True, help="Path to readiness.schema.json")
    args = ap.parse_args()

    schema = pathlib.Path(args.schema)
    if not schema.exists():
        print(f"ERROR: Schema not found: {schema}", file=sys.stderr)
        return 2

    json.loads(schema.read_text(encoding="utf-8"))

    status = 0
    for artifact_path in args.artifacts:
        artifact = pathlib.Path(artifact_path)
        if not artifact.exists():
            print(f"ERROR: Artifact not found: {artifact}", file=sys.stderr)
            status = max(status, 2)
            continue

        data = json.loads(artifact.read_text(encoding="utf-8"))

        # Minimal structural checks (no external libs)
        missing = [key for key in ("readiness", "scores", "weights") if key not in data]
        if missing:
            print(f"ERROR: Missing key(s): {', '.join(missing)}", file=sys.stderr)
            status = max(status, 3)
            continue

        scores = data["scores"]
        if not isinstance(scores, dict):
            print("ERROR: scores must be an object", file=sys.stderr)
            status = max(status, 3)
            continue

        missing_scores = [k for k in ("E", "T", "D") if k not in scores]
        if missing_scores:
            for k in missing_scores:
                print(f"ERROR: scores.{k} missing", file=sys.stderr)
            status = max(status, 3)
            continue

        weights = data["weights"]
        if not isinstance(weights, dict):
            print("ERROR: weights must be an object", file=sys.stderr)
            status = max(status, 3)
            continue

        missing_weights = [k for k in ("alpha", "beta", "gamma") if k not in weights]
        if missing_weights:
            for k in missing_weights:
                print(f"ERROR: weights.{k} missing", file=sys.stderr)
            status = max(status, 3)
            continue

        R = _as_float(data["readiness"])
        E = _as_float(scores["E"])
        T = _as_float(scores["T"])
        D = _as_float(scores["D"])
        a = _as_float(weights["alpha"])
        b = _as_float(weights["beta"])
        g = _as_float(weights["gamma"])

        if None in (R, E, T, D, a, b, g):
            print("ERROR: Non-numeric values where numbers expected", file=sys.stderr)
            status = max(status, 3)
            continue

        if abs((a + b + g) - 1.0) > 1e-6:
            print(f"ERROR: Weights must sum to 1.0 (got {a + b + g:.6f})", file=sys.stderr)
            status = max(status, 4)
            continue

        R_calc = a * E + b * T + g * D
        if abs(R_calc - R) > 0.01:
            print(
                f"WARNING: Readiness mismatch (reported {R:.4f} vs calc {R_calc:.4f})",
                file=sys.stderr,
            )

        print(f"OK: {artifact} validated")

    return status


if __name__ == "__main__":
    raise SystemExit(main())
