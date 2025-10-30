from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

PEFT_TOKENS = {
    "peft",
    "lora",
    "LoraConfig",
    "get_peft_model",
    "prepare_model_for_kbit_training",
}
MAX_READ_BYTES = 200_000
REPO_ROOT = Path(__file__).resolve().parents[3]


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:MAX_READ_BYTES]
    except Exception:
        return ""


def detect(file_index: Dict[str, Any]) -> Dict[str, Any]:
    """Find evidence of PEFT/LoRA wiring using the S1 context index."""

    files = file_index.get("files", [])
    evidence: Dict[str, List[str]] = {}
    for entry in files:
        rel_path = entry.get("path")
        if not rel_path or not rel_path.endswith(".py"):
            continue
        text = _read_text(REPO_ROOT / rel_path)
        tokens = sorted([t for t in PEFT_TOKENS if t in text])
        if tokens:
            evidence[rel_path] = tokens

    return {
        "id": "peft_hooks",
        "evidence": dict(sorted(evidence.items())),
        "files_with_peft": int(len(evidence)),
        "evidence_files": sorted(evidence.keys()),
        "found_patterns": sorted({token for tokens in evidence.values() for token in tokens}),
        "required_patterns": sorted(PEFT_TOKENS),
    }
