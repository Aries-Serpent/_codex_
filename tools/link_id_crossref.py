#!/usr/bin/env python3
"""
Validate cross-references of CAP-/FIND-/PATCH-/REPRO- IDs inside a status report JSON.

Usage:
  python tools/link_id_crossref.py --report reports/daily/2025-11-02.json

Exit: 0 on success, 1 if missing IDs or dangling references
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def collect_ids(report: dict) -> dict[str, set[str]]:
    ids = {"CAP": set(), "FIND": set(), "PATCH": set(), "REPRO": set()}

    for cap in report.get("snapshot", {}).get("capabilities", []):
        if "id" in cap and isinstance(cap["id"], str):
            ids["CAP"].add(cap["id"])

    for f in report.get("snapshot", {}).get("findings", []):
        if "id" in f and isinstance(f["id"], str):
            ids["FIND"].add(f["id"])

    for p in report.get("patches", []):
        if "id" in p and isinstance(p["id"], str):
            ids["PATCH"].add(p["id"])

    for r in report.get("snapshot", {}).get("repro", {}).get("registry", []):
        if "id" in r and isinstance(r["id"], str):
            ids["REPRO"].add(r["id"])

    return ids


def validate_links(report: dict, ids: dict[str, set[str]]) -> dict[str, list]:
    errors = {"missing": [], "dangling": []}

    # Patches -> capability_ids, repro_ids, finding_ids
    for p in report.get("patches", []):
        for k, kind in (("capability_ids", "CAP"), ("repro_ids", "REPRO"), ("finding_ids", "FIND")):
            for ref in p.get(k, []) or []:
                if ref not in ids[kind]:
                    errors["dangling"].append({"patch": p.get("id"), "ref": ref, "kind": kind})

    # Findings -> capability_ids, patch_ids
    for f in report.get("snapshot", {}).get("findings", []):
        for ref in f.get("links", {}).get("capability_ids", []) or []:
            if ref not in ids["CAP"]:
                errors["dangling"].append({"finding": f.get("id"), "ref": ref, "kind": "CAP"})
        for ref in f.get("links", {}).get("patch_ids", []) or []:
            if ref not in ids["PATCH"]:
                errors["dangling"].append({"finding": f.get("id"), "ref": ref, "kind": "PATCH"})

    return errors


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", required=True)
    args = ap.parse_args(argv)

    data = json.loads(Path(args.report).read_text(encoding="utf-8"))
    ids = collect_ids(data)
    errors = validate_links(data, ids)

    if not errors["missing"] and not errors["dangling"]:
        print("[OK] Cross-references valid")
        return 0

    print("[FAIL] Cross-reference issues detected")
    if errors["missing"]:
        print("Missing IDs:", errors["missing"])
    if errors["dangling"]:
        print("Dangling refs:", errors["dangling"])
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
