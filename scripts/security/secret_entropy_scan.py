#!/usr/bin/env python
"""
Secret Entropy Scan (P4)

Scans text artifacts for high-entropy substrings resembling credentials.

Heuristic:
- Sliding window (length 16–48) compute Shannon entropy; threshold > 3.5 considered candidate.
- Optionally exclude known benign tokens (ALLOWLIST_SECRET_PREFIXES env CSV).
- Writes secret_entropy_report.json with findings; does NOT mutate originals (non-destructive).
"""
from __future__ import annotations
import os, json, math, sys
from pathlib import Path
from typing import List, Dict

ART_DIR = Path("audit_artifacts")
REPORT = ART_DIR / "secret_entropy_report.json"
TEXT_EXT = {".py",".md",".txt",".json",".yaml",".yml",".toml",".cfg",".ini"}


def shannon(s: str) -> float:
    if not s:
        return 0.0
    freq = {}
    for c in s:
        freq[c] = freq.get(c,0)+1
    return sum((f/len(s))*math.log2(len(s)/f) for f in freq.values())


def windows(content: str, min_len=16, max_len=48):
    for L in range(min_len, max_len+1, 8):
        for i in range(0, len(content)-L+1):
            yield content[i:i+L]


def scan_file(path: Path, entropy_threshold: float, allow_prefixes: List[str]) -> List[Dict]:
    try:
        txt = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []
    
    findings = []
    for w in windows(txt):
        if any(w.startswith(p) for p in allow_prefixes):
            continue
        e = shannon(w)
        if e >= entropy_threshold:
            findings.append({"span": w, "entropy": round(e,3), "file": path.as_posix()})
    return findings


def main():
    ent_raw = os.getenv("SECRET_ENTROPY_THRESHOLD","3.5")
    try:
        threshold = float(ent_raw)
    except ValueError:
        threshold = 3.5
    
    allow = [p.strip() for p in os.getenv("ALLOWLIST_SECRET_PREFIXES","").split(",") if p.strip()]
    
    root = Path(".")
    all_files = []
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix.lower() in TEXT_EXT and len(p.name) < 128:
            all_files.append(p)
    
    aggregated = []
    for f in all_files:
        aggregated.extend(scan_file(f, threshold, allow))
    
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({"findings": aggregated, "count": len(aggregated), "threshold": threshold}, indent=2), encoding="utf-8")
    print(f"[INFO] Secret entropy report written: {REPORT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
