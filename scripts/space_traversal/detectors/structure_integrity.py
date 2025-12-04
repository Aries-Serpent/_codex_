"""
[Detector]: Structural Integrity & Shadowing
Purpose: Dynamically identifies 'Split Brain' architecture and library shadowing risks
during the audit traversal process.

Integrates with: scripts/space_traversal/audit_runner.py
"""
from pathlib import Path
from typing import List, Set

# Libraries that, if present as root directories, likely shadow PyPI packages
KNOWN_SHADOW_RISKS = {
    "hydra", "torch", "numpy", "requests", "wandb", "mlflow", "pandas"
}

EVIDENCE_LIMIT = 10  # configurable cap for evidence size

def detect(file_index: dict) -> dict:
    files = [f["path"] for f in file_index["files"]]
    root_dirs: Set[str] = set()
    src_dirs: Set[str] = set()
    evidence_files: List[str] = []

    # Harvest directory structure
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
    for d in sorted(intersection):
        found_patterns.append("split-brain")
        root_samples = [f for f in files if f.startswith(f"{d}/")][:EVIDENCE_LIMIT//2]
        src_samples = [f for f in files if f.startswith(f"src/{d}/")][:EVIDENCE_LIMIT//2]
        evidence_files.extend(root_samples + src_samples)

    # Library shadowing evidence
    for d in sorted(root_dirs):
        if d.lower() in KNOWN_SHADOW_RISKS:
            found_patterns.append("lib-shadowing")
            shadow_files = [f for f in files if f.startswith(f"{d}/")][:EVIDENCE_LIMIT]
            evidence_files.extend(shadow_files)

    # De-duplicate and cap
    evidence_files = sorted(list(dict.fromkeys(evidence_files)))[:EVIDENCE_LIMIT]

    return {
        "id": "structural-integrity",
        "evidence_files": evidence_files,
        "found_patterns": sorted(list(set(found_patterns))),
        "required_patterns": ["split-brain", "lib-shadowing"],
        "meta": {
            "risk_level": "high" if found_patterns else "low",
            "description": "Detects architectural split-brain and namespace shadowing.",
            "split_dirs": sorted(list(intersection)),
            "shadow_dirs": [d for d in root_dirs if d.lower() in KNOWN_SHADOW_RISKS],
            "evidence_limit": EVIDENCE_LIMIT
        }
    }
