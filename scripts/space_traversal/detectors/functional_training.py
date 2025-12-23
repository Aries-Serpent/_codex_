"""Detector for functional training capability.

import logging
logger = logging.getLogger(__name__)
Detects functional, composable training patterns including
training loops, steps, epochs, and pipeline composition.

Safeguards: Bounded processing, deterministic sorting, validation.
"""

from __future__ import annotations
from typing import Dict
from pathlib import Path

MAX_READ_BYTES = 200_000
REPO_ROOT = Path(__file__).resolve().parents[3]


def _read_text(path_input) -> str:
    """
    Read text from file with bounded read.

    Safeguard: Bounded read to prevent memory issues.
    Validation: Handles both string and Path inputs.
    """
    try:
        if isinstance(path_input, str):
            path = Path(path_input)
        else:
            path = path_input

        if not path.is_absolute():
            path = REPO_ROOT / path

        if not path.exists():
            return ""

        return path.read_text(encoding="utf-8", errors="ignore")[:MAX_READ_BYTES]
    except (OSError, IOError, UnicodeDecodeError):
        return ""


def detect(file_index: Dict) -> Dict:
    """Detect functional training capability.

    Args:
        file_index: Context index from S1 with file metadata

    Returns:
        Capability detection result with comprehensive metadata
    """
    files = file_index.get("files", [])
    evidence = []
    found_patterns = set()

    required_patterns = ["training_step", "train_epoch", "optimizer", "batch", "loss", "backward"]

    # Training patterns to detect
    training_patterns = {
        "training_step": ["training_step", "train_step", "step("],
        "train_epoch": ["train_epoch", "epoch", "for epoch in"],
        "optimizer": ["optimizer", "Adam", "SGD", "optim."],
        "batch": ["batch", "dataloader", "DataLoader"],
        "loss": ["loss", "criterion", "CrossEntropy", "MSE"],
        "backward": ["backward", ".backward()", "grad"],
        "functional": ["functional", "compose", "pipeline"],
        "callback": ["callback", "on_epoch", "on_batch"],
    }

    for meta in files:
        p = meta["path"]
        lower = p.lower()

        # Path-based detection
        if "train" in lower or "training" in lower:
            evidence.append(p)
            found_patterns.add("training_step")

        # Content-based detection for Python files
        ext = meta.get("ext", ".")
        if ext == ".py" and ("train" in lower or "codex_ml" in lower):
            text = _read_text(p)
            if text:
                for pattern_name, keywords in training_patterns.items():
                    if any(kw in text for kw in keywords):
                        if p not in evidence:
                            evidence.append(p)
                        found_patterns.add(pattern_name)

    # Calculate functionality score
    matched = len(found_patterns & set(required_patterns))
    functionality_score = matched / len(required_patterns) if required_patterns else 0.0

    return {
        "id": "functional_training",
        "evidence_files": sorted(set(evidence)),
        "found_patterns": sorted(found_patterns),
        "required_patterns": required_patterns,
        "docs_keywords": [
            "training",
            "functional",
            "pipeline",
            "composable",
            "train-loop",
            "step",
            "epoch",
            "batch",
            "optimizer",
        ],
        "safeguards": ["validation", "bounded", "deterministic", "gradient-clipping"],
        "functionality_impl": functionality_score,
        "meta": {
            "category": "training",
            "patterns_found": len(found_patterns),
            "deterministic": True,
            "offline": True,
            "bounded": True,
            "detector_version": "2.0",
        },
    }
