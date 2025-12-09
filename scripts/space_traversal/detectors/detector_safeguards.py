"""
Safeguard Keywords Detector

Scans codebase for defensive programming patterns and safeguard keywords.
Detects validation, sanitization, bounds checking, and other security/robustness patterns.

Patterns detected: validation, security, defensive, robust
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Set

# Expanded safeguard keyword list covering security, validation, and defensive programming
SAFEGUARD_KEYWORDS = {
    # Cryptographic & Security
    "sha256",
    "checksum",
    "validate",
    "validation",
    "sanitize",
    "sanitization",
    "authenticate",
    "authorization",
    # Determinism & Reproducibility
    "rng",
    "seed",
    "deterministic",
    "reproducible",
    "offline",
    # Rate Limiting & Bounds
    "rate_limit",
    "ratelimit",
    "bounds_check",
    "bounded",
    "timeout",
    "max_retries",
    # Error Handling & Safety
    "try_except",
    "error_handling",
    "rollback",
    "cleanup",
    "safeguard",
    "defensive",
    "robust",
    # Configuration
    "WANDB_MODE",
    "MAX_READ_BYTES",
}

# Defensive programming patterns (regex-based detection)
DEFENSIVE_PATTERNS = [
    (r'\btry\s*:', "try_except"),
    (r'\bif\s+.*\s+is\s+None\s*:', "null_check"),
    (r'\bassert\s+', "assertion"),
    (r'\braise\s+\w+Error', "explicit_error"),
    (r'\.strip\(\)', "input_sanitization"),
    (r'\.lower\(\)', "case_normalization"),
]

MAX_READ_BYTES = 200_000
REPO_ROOT = Path(__file__).resolve().parents[3]


def _read_text(path: Path) -> str:
    """
    Read text from file with bounded read and error handling.
    
    Safeguard: Bounded read to prevent memory issues.
    
    Args:
        path: Path to file (absolute or relative to REPO_ROOT)
        
    Returns:
        File content (up to MAX_READ_BYTES) or empty string on error
    """
    try:
        # Handle both absolute and relative paths
        if not path.is_absolute():
            path = REPO_ROOT / path
        
        # Validation: Check path exists
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")[:MAX_READ_BYTES]
    except (OSError, IOError, UnicodeDecodeError):
        # Defensive: Catch specific exceptions
        return ""


def _detect_context_aware_patterns(text: str) -> Set[str]:
    """
    Detect defensive programming patterns beyond simple keyword matching.
    
    Args:
        text: Source code text
        
    Returns:
        Set of detected pattern names
    """
    detected = set()
    
    for pattern, name in DEFENSIVE_PATTERNS:
        if re.search(pattern, text, re.MULTILINE):
            detected.add(name)
    
    return detected


def _calculate_safeguard_density(evidence: Dict[str, int], total_files: int) -> float:
    """
    Calculate safeguard density as ratio of files with safeguards.
    
    Safeguard: Bounded calculation, handles division by zero.
    
    Args:
        evidence: Dict of file paths to hit counts
        total_files: Total number of analyzed files
        
    Returns:
        Density ratio [0.0, 1.0]
    """
    if total_files == 0:
        return 0.0
    return min(1.0, len(evidence) / max(total_files, 1))


def detect(file_index: Dict[str, Any]) -> Dict[str, Any]:
    """
    Scan files for safeguard keywords and defensive programming patterns.
    
    This detector performs comprehensive analysis of security and robustness
    indicators across the codebase. It uses both keyword matching and pattern
    detection to identify validation, sanitization, error handling, and other
    defensive programming practices.
    
    Args:
        file_index: Context index from S1 with files list
        
    Returns:
        Detection result with evidence, metrics, and patterns
    """

    files = file_index.get("files", [])
    evidence: Dict[str, int] = {}
    text_cache: Dict[str, str] = {}
    pattern_detections: Dict[str, List[str]] = {}
    
    # Validation: Allowed file types for safeguard scanning
    allowed_suffixes = {".py", ".md", ".sh", ".txt", ".yml", ".yaml", ".json"}
    
    for entry in files:
        rel_path = entry.get("path")
        
        # Validation: Check path is valid
        if not rel_path:
            continue
        
        path_obj = Path(rel_path)
        
        # Skip non-text files
        if path_obj.suffix.lower() not in allowed_suffixes:
            continue
        
        # Read and analyze file (bounded read for safety)
        # Support both absolute paths (for tests) and relative paths (for repo files)
        if path_obj.is_absolute():
            text = _read_text(path_obj)
        else:
            text = _read_text(REPO_ROOT / rel_path)
        
        if not text:
            continue
        
        # Count keyword hits
        hits = sum(1 for w in SAFEGUARD_KEYWORDS if w in text)
        
        # Detect context-aware patterns
        context_patterns = _detect_context_aware_patterns(text)
        
        if hits or context_patterns:
            evidence[rel_path] = hits + len(context_patterns)
            text_cache[rel_path] = text
            if context_patterns:
                pattern_detections[rel_path] = sorted(context_patterns)

    total_hits = int(sum(evidence.values()))
    total_files = len(files)
    density = _calculate_safeguard_density(evidence, total_files)
    
    # Find which keywords and patterns were actually detected
    found_keywords = {
        w for w in SAFEGUARD_KEYWORDS 
        if any(w in text_cache[p] for p in evidence)
    }
    
    found_patterns = set()
    for patterns in pattern_detections.values():
        found_patterns.update(patterns)
    
    # Combine for comprehensive pattern list
    all_found_patterns = sorted(found_keywords | found_patterns)
    
    return {
        "id": "safeguards_keywords",
        "evidence": dict(sorted(evidence.items())),
        "total_hits": total_hits,
        "unique_files": int(len(evidence)),
        "safeguard_density": round(density, 4),
        "pattern_detections": pattern_detections,
        "metrics": {
            "files_with_safeguards": len(evidence),
            "total_analyzed_files": total_files,
            "average_safeguards_per_file": round(total_hits / max(len(evidence), 1), 2),
            "density_percentage": round(density * 100, 2),
        },
        # Detector contract fields
        "evidence_files": sorted(evidence.keys()),
        "found_patterns": all_found_patterns,
        "required_patterns": ["validation", "security", "defensive", "robust"],
        "docs_keywords": ["safeguard", "validation", "security", "defensive", "robust", "sanitize"],
        "meta": {
            "detection_method": "keyword_and_pattern",
            "context_aware": True,
            "deterministic": True,
            "offline": True,
        }
    }
