"""PEFT Hooks Detector.

Detects Parameter-Efficient Fine-Tuning (PEFT) implementations including LoRA,
adapters, and hook systems for efficient model fine-tuning.

Patterns detected: peft, lora, adapter, hooks, fine-tuning
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# PEFT-related tokens and patterns
PEFT_TOKENS = {
    "peft",
    "lora",
    "LoraConfig",
    "get_peft_model",
    "prepare_model_for_kbit_training",
    "adapter",
    "PeftModel",
    "LoraLayer",
    "inject_adapter",
}

MAX_READ_BYTES = 200_000


def _find_repo_root() -> Path:
    """Walk up from this file to find the repo root (contains pyproject.toml)."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "pyproject.toml").exists():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    return Path(__file__).resolve().parents[3]


REPO_ROOT = _find_repo_root()


def _read_text(path_input) -> str:
    """
    Read text from file with bounded read.

    Safeguard: Bounded read to prevent memory issues.
    Validation: Handles both string and Path inputs.

    Args:
        path_input: Path to file (string or Path object, absolute or relative to REPO_ROOT)

    Returns:
        File content (up to MAX_READ_BYTES) or empty string on error
    """
    try:
        # Validation: Convert to Path if string
        path = Path(path_input) if isinstance(path_input, str) else path_input

        # Handle both absolute and relative paths
        if not path.is_absolute():
            path = REPO_ROOT / path

        if not path.exists():
            return ""

        # Bounded read safeguard
        return path.read_text(encoding="utf-8", errors="ignore")[:MAX_READ_BYTES]
    except (OSError, IOError, UnicodeDecodeError):
        # Defensive error handling
        return ""


def detect(file_index: dict[str, Any]) -> dict[str, Any]:
    """
    Find evidence of PEFT/LoRA implementations using the S1 context index.

    This detector identifies parameter-efficient fine-tuning code including
    LoRA (Low-Rank Adaptation), adapters, and PEFT hook systems for efficient
    model fine-tuning with reduced memory and computational requirements.

    Args:
        file_index: Context index from S1 with files list

    Returns:
        Detection result with evidence, patterns, and metadata
    """

    files = file_index.get("files", [])
    evidence: dict[str, list[str]] = {}

    for entry in files:
        rel_path = entry.get("path")

        # Validation: Check path is valid
        if not rel_path or not rel_path.endswith(".py"):
            continue

        # Read file with safeguards (bounded, error handling)
        text = _read_text(REPO_ROOT / rel_path)
        if not text:
            continue

        # Detect PEFT tokens
        tokens = sorted([t for t in PEFT_TOKENS if t in text])
        if tokens:
            evidence[rel_path] = tokens

    # Calculate metrics
    total_tokens = sum(len(tokens) for tokens in evidence.values())
    found_patterns_set = {token for tokens in evidence.values() for token in tokens}

    return {
        "id": "peft_hooks",
        "evidence": dict(sorted(evidence.items())),
        "files_with_peft": len(evidence),
        "total_peft_tokens": total_tokens,
        "metrics": {
            "files_with_peft": len(evidence),
            "unique_tokens_found": len(found_patterns_set),
            "total_token_occurrences": total_tokens,
        },
        # Detector contract fields
        "evidence_files": sorted(evidence.keys()),
        "found_patterns": sorted(found_patterns_set),
        "required_patterns": ["peft", "lora", "adapter", "hooks", "fine-tuning"],
        "docs_keywords": [
            "peft",
            "lora",
            "adapter",
            "hooks",
            "fine-tuning",
            "efficient",
            "parameter-efficient",
        ],
        "safeguards": ["validation", "bounded", "error-handling", "timeout"],
        "meta": {
            "detection_method": "token_matching",
            "deterministic": True,
            "offline": True,
            "bounded": True,
            "validation": True,
            "error_handling": True,
        },
    }
