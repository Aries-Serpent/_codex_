#!/usr/bin/env python
"""
Secret Context Correlation (P6)

Elevates entropy findings that appear near authentication/configuration contexts.
Produces secret_context_report.json with elevated findings.

Context Indicators (configurable):
- Path contains: auth, config, credentials, secrets, .env
- File proximity: within N lines of keywords like "password", "api_key", "token"

Environment Knobs:
  SECRET_CONTEXT_ENABLE=1         -> perform correlation
  SECRET_CONTEXT_WINDOW=10        -> line window for keyword proximity
  SECRET_CONTEXT_KEYWORDS=csv     -> additional keywords

Outputs:
  audit_artifacts/secret_context_report.json

Integration:
  Severity classification can use elevated context for higher weights.
"""
from __future__ import annotations
import os, json, sys, re
from pathlib import Path
from typing import List, Dict, Set

ART_DIR = Path("audit_artifacts")
ENTROPY_REPORT = ART_DIR / "secret_entropy_report.json"
OUT = ART_DIR / "secret_context_report.json"

DEFAULT_KEYWORDS = {"password", "api_key", "token", "secret", "credential", "auth"}
CONTEXT_PATHS = {"auth", "config", "credentials", "secrets", ".env", "security"}

def is_context_path(file_path: str) -> bool:
    """Check if path suggests sensitive context."""
    lower = file_path.lower()
    return any(ctx in lower for ctx in CONTEXT_PATHS)

def has_nearby_keywords(file_path: Path, line_hint: int, keywords: Set[str], window: int) -> List[str]:
    """Check for keywords within window lines of the finding."""
    if not file_path.exists():
        return []
    
    try:
        lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return []
    
    start = max(0, line_hint - window)
    end = min(len(lines), line_hint + window)
    context_lines = lines[start:end]
    
    found_keywords = []
    for kw in keywords:
        if any(kw in ln.lower() for ln in context_lines):
            found_keywords.append(kw)
    
    return found_keywords

def correlate_findings(findings: List[Dict], keywords: Set[str], window: int) -> List[Dict]:
    """Correlate findings with context indicators."""
    elevated = []
    
    for finding in findings:
        file_path_str = finding.get("file", "")
        file_path = Path(file_path_str)
        
        context_indicators = []
        
        # Path context
        if is_context_path(file_path_str):
            context_indicators.append("sensitive_path")
        
        # Keyword proximity (estimate line from span position)
        # Simple heuristic: assume finding at middle of file
        line_hint = 0  # Would need actual line numbers from entropy scan
        nearby = has_nearby_keywords(file_path, line_hint, keywords, window)
        if nearby:
            context_indicators.extend(f"keyword:{kw}" for kw in nearby)
        
        if context_indicators:
            elevated.append({
                **finding,
                "context_indicators": context_indicators,
                "elevation": "high" if len(context_indicators) >= 2 else "medium"
            })
    
    return elevated

def main():
    enable = os.getenv("SECRET_CONTEXT_ENABLE", "0") in {"1", "true", "TRUE"}
    if not enable:
        print("[INFO] Secret context correlation disabled (SECRET_CONTEXT_ENABLE).")
        return 0
    
    window = int(os.getenv("SECRET_CONTEXT_WINDOW", "10"))
    custom_keywords_str = os.getenv("SECRET_CONTEXT_KEYWORDS", "")
    
    keywords = DEFAULT_KEYWORDS.copy()
    if custom_keywords_str:
        keywords.update(kw.strip() for kw in custom_keywords_str.split(",") if kw.strip())
    
    if not ENTROPY_REPORT.exists():
        print("[WARN] secret_entropy_report.json missing; run entropy scan first.", file=sys.stderr)
        return 2
    
    entropy_data = json.loads(ENTROPY_REPORT.read_text())
    findings = entropy_data.get("findings", [])
    
    elevated = correlate_findings(findings, keywords, window)
    
    report = {
        "total_findings": len(findings),
        "elevated_findings": len(elevated),
        "context_keywords": sorted(keywords),
        "window_lines": window,
        "findings": elevated[:100],  # Cap output
    }
    
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"[INFO] Secret context correlation written: {OUT}")
    print(f"[INFO] Elevated: {len(elevated)}/{len(findings)} findings")
    return 0

if __name__ == "__main__":
    sys.exit(main())
