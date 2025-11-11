#!/usr/bin/env python3
import json
import re
from pathlib import Path

PATTERNS = {
    "generic_api": re.compile(r"(api_?key|token|secret)\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}['\"]", re.IGNORECASE),
    "aws_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "gh_token": re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}"),
}

# Directories and files to exclude from scanning
EXCLUDE_DIRS = [".git", "artifacts", "audit_artifacts", "node_modules", "venv", "env"]

def mask(s: str) -> str:
    return s[:4] + "…" + s[-4:] if len(s) > 8 else "[REDACTED]"

def scan(root: Path):
    results = []
    for p in root.rglob("*"):
        if p.is_dir(): 
            continue
        if any(x in p.parts for x in EXCLUDE_DIRS):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for name, pat in PATTERNS.items():
            for m in pat.finditer(text):
                results.append({"path": str(p), "rule": name, "match": mask(m.group(0))})
    return results

def main():
    root = Path(".")
    rows = scan(root)
    outdir = Path("audit_artifacts"); outdir.mkdir(parents=True, exist_ok=True)
    (outdir/"secret_scan.json").write_text(json.dumps({"count": len(rows), "findings": rows}, indent=2))
    print("audit_artifacts/secret_scan.json")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
