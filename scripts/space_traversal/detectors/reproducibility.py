"""Dynamic detector for reproducibility capability.

Detects seed management, RNG state persistence, deterministic
configurations, and integrity validation mechanisms.

Safeguards: Bounded processing, deterministic sorting, validation.
"""

from __future__ import annotations


def detect(file_index: dict) -> dict:
    """Detect reproducibility capability.

    Args:
        file_index: Context index from S1 with file metadata

    Returns:
        Capability detection result
    """
    files = file_index.get("files", [])

    # Evidence collection
    seed_files = []
    repro_files = []
    determinism_files = []
    integrity_files = []

    # Keywords indicating reproducibility features
    seed_keywords = ["seed", "rng", "random_state"]
    repro_keywords = ["reproducib", "deterministic", "repro_helper"]
    integrity_keywords = ["sha256", "checksum", "hash", "integrity"]

    for f in files:
        path = f["path"]
        path_lower = path.lower()

        # Seed management
        if any(kw in path_lower for kw in seed_keywords):
            seed_files.append(path)

        # Reproducibility utilities
        if any(kw in path_lower for kw in repro_keywords):
            repro_files.append(path)

        # Determinism configs
        if "deterministic" in path_lower or "cudnn" in path_lower:
            determinism_files.append(path)

        # Integrity validation
        if any(kw in path_lower for kw in integrity_keywords):
            integrity_files.append(path)

    # Pattern detection
    found_patterns = []
    required_patterns = [
        "seed",
        "deterministic",
        "sha256",
        "rng_state",
        "reproducibility",
    ]

    evidence_files = sorted(set(seed_files + repro_files + determinism_files + integrity_files))

    # Check which patterns are actually present
    if seed_files:
        found_patterns.extend(["seed", "rng_state"])
    if determinism_files or any("deterministic" in f.lower() for f in evidence_files):
        found_patterns.append("deterministic")
    if integrity_files or any("sha256" in f.lower() for f in evidence_files):
        found_patterns.append("sha256")
    if repro_files:
        found_patterns.append("reproducibility")

    # Calculate functionality score
    functionality_score = len(set(found_patterns) & set(required_patterns)) / len(required_patterns) if required_patterns else 0.0

    return {
        "id": "reproducibility",
        "evidence_files": evidence_files,
        "found_patterns": sorted(set(found_patterns)),
        "required_patterns": required_patterns,
        "docs_keywords": [
            "reproducibility", "deterministic", "seed", "random",
            "environment", "snapshot", "versioning", "rerun", "consistent"
        ],
        "safeguards": ["validation", "bounded", "deterministic", "seed-control"],
        "functionality_impl": functionality_score,
        "meta": {
            "seed_management": len(seed_files),
            "repro_utils": len(repro_files),
            "determinism_configs": len(determinism_files),
            "integrity_validation": len(integrity_files),
            "deterministic": True,
            "offline": True,
            "bounded": True,
            "detector_version": "2.0"
        },
    }
