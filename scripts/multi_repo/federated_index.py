#!/usr/bin/env python
"""
Federated Index Stub (P6)

Local multi-repo capability discovery stub.
Scans local repository directories for capability indicators.

Environment Knobs:
  FEDERATION_ENABLE=1           -> perform indexing
  FEDERATION_REPO_PATHS=csv     -> paths to scan (comma-separated)

Outputs:
  audit_artifacts/federated_index.json

Limitations:
- No remote fetch or network operations
- Skips files > 2MB for performance
- Does not yet feed scoring (future integration)

Structure:
{
  "repositories": [
    {
      "path": "/path/to/repo",
      "capabilities": ["training", "checkpoint"],
      "evidence_count": 42
    }
  ]
}
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict

ART_DIR = Path("audit_artifacts")
OUT = ART_DIR / "federated_index.json"

MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB

# Simple capability indicators
CAPABILITY_PATTERNS = {
    "training": re.compile(r"\b(train|epoch|fit|optimizer)\b", re.I),
    "checkpoint": re.compile(r"\b(checkpoint|save_checkpoint|restore)\b", re.I),
    "tokenization": re.compile(r"\b(tokeniz|encode|decode)\b", re.I),
    "evaluation": re.compile(r"\b(eval|metric|perplexity|accuracy)\b", re.I),
}

def scan_repo(repo_path: Path) -> Dict:
    """Scan a repository for capability indicators."""
    if not repo_path.exists() or not repo_path.is_dir():
        return {"path": str(repo_path), "error": "not_found"}
    
    capabilities_found = set()
    evidence_count = 0
    
    for file_path in repo_path.rglob("*.py"):
        if file_path.stat().st_size > MAX_FILE_SIZE:
            continue
        
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        
        for cap_name, pattern in CAPABILITY_PATTERNS.items():
            if pattern.search(content):
                capabilities_found.add(cap_name)
                evidence_count += 1
    
    return {
        "path": str(repo_path),
        "capabilities": sorted(capabilities_found),
        "evidence_count": evidence_count
    }

def main():
    enable = os.getenv("FEDERATION_ENABLE", "0") in {"1", "true", "TRUE"}
    if not enable:
        print("[INFO] Federation disabled (FEDERATION_ENABLE).")
        return 0
    
    repo_paths_str = os.getenv("FEDERATION_REPO_PATHS", "")
    if not repo_paths_str:
        print("[WARN] No FEDERATION_REPO_PATHS provided; nothing to scan.", file=sys.stderr)
        return 0
    
    repo_paths = [Path(p.strip()) for p in repo_paths_str.split(",") if p.strip()]
    
    repositories = []
    for repo_path in repo_paths:
        print(f"[INFO] Scanning {repo_path}...")
        result = scan_repo(repo_path)
        repositories.append(result)
    
    index = {
        "repositories": repositories,
        "total_scanned": len(repositories),
        "total_capabilities": sum(len(r.get("capabilities", [])) for r in repositories)
    }
    
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(index, indent=2), encoding="utf-8")
    print(f"[INFO] Federated index written: {OUT}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
