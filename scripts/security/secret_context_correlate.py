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
  SECRET_CONTEXT_ARTIFACT_DIR=dir -> override artifact directory (default ./audit_artifacts)
  SECRET_CONTEXT_WORKSPACE_DIR=dir -> base directory for file paths in entropy report

Outputs:
  audit_artifacts/secret_context_report.json

Integration:
  Severity classification can use elevated context for higher weights.
"""
from __future__ import annotations
import os, json, sys
from pathlib import Path
from bisect import bisect_right
from typing import Dict, List, Optional, Set, Tuple

ART_DIR = Path(os.getenv("SECRET_CONTEXT_ARTIFACT_DIR", "audit_artifacts"))
ENTROPY_REPORT = ART_DIR / "secret_entropy_report.json"
OUT = ART_DIR / "secret_context_report.json"

DEFAULT_KEYWORDS = {"password", "api_key", "token", "secret", "credential", "auth"}
CONTEXT_PATHS = {"auth", "config", "credentials", "secrets", ".env", "security"}

def is_context_path(file_path: str) -> bool:
    """Check if path suggests sensitive context."""
    lower = file_path.lower()
    return any(ctx in lower for ctx in CONTEXT_PATHS)

FileContent = Tuple[List[str], str, List[int]]


def has_nearby_keywords(lines: Optional[List[str]], line_hint: int, keywords: Set[str], window: int) -> List[str]:
    """Check for keywords within window lines of the finding."""
    if not lines:
        return []

    # Clamp to valid index range before slicing context lines.
    line_hint = max(0, min(line_hint, len(lines) - 1)) if lines else 0
    start = max(0, line_hint - window)
    end = min(len(lines), line_hint + window + 1)
    context_lines = lines[start:end]

    found_keywords = []
    for kw in keywords:
        if any(kw in ln.lower() for ln in context_lines):
            found_keywords.append(kw)

    return found_keywords


def load_file_content(file_path: Path) -> Optional[FileContent]:
    """Read a file once and cache its text, lines, and newline offsets."""
    if not file_path.exists():
        return None

    try:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None

    lines = text.splitlines()
    newline_positions = [idx for idx, ch in enumerate(text) if ch == "\n"]
    return lines, text, newline_positions


def compute_line_hints(span: str, text: str, newline_positions: List[int], total_lines: int) -> List[int]:
    """Return all candidate line indices where the span appears."""
    if not span:
        return []

    hints: List[int] = []
    step = max(1, len(span))
    start = 0
    while True:
        idx = text.find(span, start)
        if idx == -1:
            break
        line_no = bisect_right(newline_positions, idx)
        if 0 <= line_no < max(total_lines, 1):
            hints.append(line_no)
        start = idx + step
    return hints

def correlate_findings(
    findings: List[Dict],
    keywords: Set[str],
    window: int,
    workspace_root: Path,
) -> List[Dict]:
    """Correlate findings with context indicators."""
    elevated = []
    
    file_cache: Dict[Path, Optional[FileContent]] = {}

    for finding in findings:
        file_path_str = finding.get("file", "")
        raw_path = Path(file_path_str)
        file_path = raw_path if raw_path.is_absolute() else (workspace_root / raw_path)

        context_indicators = []

        # Path context
        if is_context_path(file_path_str):
            context_indicators.append("sensitive_path")

        # Keyword proximity based on actual span location if available
        if file_path not in file_cache:
            file_cache[file_path] = load_file_content(file_path)

        cached = file_cache[file_path]
        nearby: List[str] = []
        if cached:
            lines, text, newline_positions = cached
            total_lines = len(lines)
            hints = compute_line_hints(finding.get("span", ""), text, newline_positions, total_lines)
            if not hints:
                # Fall back to middle of file if span not located.
                fallback = total_lines // 2 if total_lines else 0
                hints = [fallback]

            found: Set[str] = set()
            for hint in hints:
                for kw in has_nearby_keywords(lines, hint, keywords, window):
                    found.add(kw)
            nearby = sorted(found)

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
    workspace_root = Path(os.getenv("SECRET_CONTEXT_WORKSPACE_DIR", ".")).resolve()
    
    keywords = DEFAULT_KEYWORDS.copy()
    if custom_keywords_str:
        keywords.update(kw.strip() for kw in custom_keywords_str.split(",") if kw.strip())
    
    if not ENTROPY_REPORT.exists():
        print("[WARN] secret_entropy_report.json missing; run entropy scan first.", file=sys.stderr)
        return 2
    
    entropy_data = json.loads(ENTROPY_REPORT.read_text())
    findings = entropy_data.get("findings", [])
    
    elevated = correlate_findings(findings, keywords, window, workspace_root)
    
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
