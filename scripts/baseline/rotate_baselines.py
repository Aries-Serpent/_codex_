#!/usr/bin/env python3
import os, sys, shutil
from pathlib import Path

def main(retain: int = 5):
    base = Path("audit_artifacts/baselines")
    if not base.exists():
        print("[INFO] no baselines to rotate")
        return
    
    entries = sorted([p for p in base.iterdir() if p.is_dir()])
    if len(entries) <= retain:
        print("[INFO] within retain window")
        return
    
    to_delete = entries[:-retain]
    for d in to_delete:
        shutil.rmtree(d, ignore_errors=True)
        print(f"[INFO] removed baseline: {d}")

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    main(n)
