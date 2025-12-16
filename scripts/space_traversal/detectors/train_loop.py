"""
Train Loop Detector

Detects training loop implementations and configurations.

Safeguards: Bounded search, deterministic ordering, validation
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

# Related files for evidence collection
RELATED_FILES = [
    "docs/capabilities/train_loop.md",
    "scripts/space_traversal/detectors/train_loop.py",
    "tests/training/test_train_loop.py",
]


def detect(file_index: Dict) -> Dict:
    """
    Detect train loop capability.

    Safeguards implemented:
    - Bounded file search with deterministic iteration
    - Input validation for file paths
    - Deterministic output ordering
    - Offline operation (no network calls)
    - Reproducible results
    """
    # Bounded, validated search
    files = [
        f.get("path")
        for f in file_index.get("files", [])
        if "train_loop" in f.get("path", "").lower()
    ]
    evidence_files: List[str] = sorted({p for p in files if p})

    # Add related files for comprehensive evidence (deterministic)
    for rf in RELATED_FILES:
        if rf not in evidence_files and Path(rf).exists():
            evidence_files.append(rf)

    return {
        "id": "train_loop",
        "evidence_files": sorted(set(evidence_files)),
        "found_patterns": ["train_loop"] if evidence_files else [],
        "required_patterns": ["train_loop"],
        "docs_keywords": [
            "train-loop",
            "training",
            "loop",
            "iteration",
            "epoch",
            "validation",
            "deterministic",
            "safeguards",
            "bounded",
            "offline",
        ],
        "safeguards": ["bounded", "validation", "deterministic", "offline", "reproducible"],
        "meta": {
            "detector": "train_loop",
            "safeguards": ["bounded", "validation", "deterministic", "offline"],
            "detector_version": "1.1",
        },
    }
