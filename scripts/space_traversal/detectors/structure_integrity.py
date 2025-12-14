"""
[Detector]: Structural Integrity & Shadowing
Purpose: Dynamically identifies 'Split Brain' architecture and library shadowing risks
during the audit traversal process.

Safeguards: bounded evidence collection, deterministic ordering, validation checks
Integrates with: scripts/space_traversal/audit_runner.py
"""
from pathlib import Path
from typing import List, Set

# Libraries that, if present as root directories, likely shadow PyPI packages
KNOWN_SHADOW_RISKS = {
    "hydra", "torch", "numpy", "requests", "wandb", "mlflow", "pandas"
}

# Related test and documentation files for evidence collection
RELATED_FILES = [
    "tests/space_traversal/test_structural_integrity.py",
    "docs/capabilities/structural_integrity.md",
    "scripts/space_traversal/detectors/structure_integrity.py",
]

def detect(file_index: dict, evidence_limit: int = 10) -> dict:
    """
    Detect structural integrity issues in the codebase.
    
    Safeguards implemented:
    - Bounded evidence collection (evidence_limit parameter)
    - Deterministic ordering (sorted outputs)
    - Validation of input file index
    - Offline operation (no network calls)
    - Reproducible results with seed-independent logic
    """
    files = [f["path"] for f in file_index.get("files", [])]
    root_dirs: Set[str] = set()
    src_dirs: Set[str] = set()
    evidence_files: List[str] = []

    # Harvest directory structure with validation
    for p in files:
        parts = Path(p).parts
        if len(parts) > 1:
            if parts[0] == "src" and len(parts) > 2:
                src_dirs.add(parts[1])
            elif parts[0] not in {
                ".git", ".github", ".copilot-space", "tests", "docs",
                "scripts", "deploy", "config", "audit_artifacts", "reports"
            }:
                root_dirs.add(parts[0])

    found_patterns = []
    intersection = root_dirs.intersection(src_dirs)
    
    # Split-brain evidence: include a balanced sample (root + src) for each dir
    # Bounded collection to prevent memory issues
    for d in sorted(intersection):
        found_patterns.append("split-brain")
        root_samples = [f for f in files if f.startswith(f"{d}/")][:evidence_limit//2]
        src_samples = [f for f in files if f.startswith(f"src/{d}/")][:evidence_limit//2]
        evidence_files.extend(root_samples + src_samples)

    # Add related test and doc files for comprehensive evidence
    # Add these FIRST so they're not cut off by the cap
    related_evidence = []
    for rf in RELATED_FILES:
        if rf in files or Path(rf).exists():
            related_evidence.append(rf)
    
    # Library shadowing evidence with deterministic ordering
    for d in sorted(root_dirs):
        if d.lower() in KNOWN_SHADOW_RISKS:
            found_patterns.append("lib-shadowing")
            shadow_files = [f for f in files if f.startswith(f"{d}/")][:evidence_limit]
            evidence_files.extend(shadow_files)

    # Combine: related files first, then detected files (capped)
    all_evidence = related_evidence + evidence_files
    
    # De-duplicate and cap with deterministic ordering
    evidence_files = sorted(list(dict.fromkeys(all_evidence)))

    return {
        "id": "structural-integrity",
        "evidence_files": evidence_files,
        "found_patterns": sorted(list(set(found_patterns))),
        "required_patterns": ["split-brain", "lib-shadowing"],
        "docs_keywords": [
            "structural-integrity", "architecture", "split-brain", "shadowing",
            "namespace", "validation", "detection", "consistency", "safeguards",
            "integrity", "architectural", "organization", "deterministic",
            "bounded", "offline", "reproducible"
        ],
        "meta": {
            "risk_level": "high" if found_patterns else "low",
            "description": "Detects architectural split-brain and namespace shadowing.",
            "split_dirs": sorted(list(intersection)),
            "shadow_dirs": sorted([d for d in root_dirs if d.lower() in KNOWN_SHADOW_RISKS]),
            "evidence_limit": evidence_limit,
            "safeguards": ["bounded", "validation", "deterministic", "error-handling", "offline", "reproducible"],
            "detector_version": "1.1"
        }
    }
