#!/usr/bin/env python
from __future__ import annotations
import argparse
import json
import os
import re
from pathlib import Path
from typing import Dict, List

SAFE_DATA_EXT = {".jsonl", ".json", ".csv", ".tsv", ".txt"}
MAX_FILE_BYTES = 5_000_000


def scan_data(root: Path, max_files: int = 500) -> List[Dict]:
    findings: List[Dict] = []
    count = 0
    for p in sorted(root.rglob("*")):
        if count >= max_files:
            break
        if p.is_dir() or p.suffix.lower() not in SAFE_DATA_EXT:
            continue
        if p.stat().st_size > MAX_FILE_BYTES:
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        # simple PII-like detectors
        rules = {
            "email": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            "phone": r"\+?\d[\d\-\s]{7,}\d",
        }
        for name, rx in rules.items():
            for m in re.finditer(rx, text):
                findings.append({"type": name, "path": p.as_posix(), "offset": m.start()})
        count += 1
    return findings


def main():
    ap = argparse.ArgumentParser(description="Dataset content scan (PII-like heuristics)")
    ap.add_argument("--root", default="data", help="Data directory")
    ap.add_argument("--out", default="artifacts/security/dataset_scan.json")
    ap.add_argument("--limit", type=int, default=500)
    args = ap.parse_args()

    root = Path(args.root)
    if not root.exists():
        print(f"Data root not found: {root}")
        return

    findings = scan_data(root, args.limit)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps({"root": str(root), "findings": findings}, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(f"Dataset scan complete. Findings: {len(findings)} -> {out}")


if __name__ == "__main__":
    main()
