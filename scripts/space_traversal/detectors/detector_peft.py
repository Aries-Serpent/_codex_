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


def detect(repo_root: Path) -> Dict[str, Any]:
    """
    Find evidence of PEFT/LoRA wiring in the tree.

    Output schema:
    {
      "id": "peft_hooks",
      "evidence": { "<relpath>": ["token", ...], ... },
      "files_with_peft": <int>,
    }
    """
    repo_root = Path(repo_root).resolve()
    evidence: Dict[str, List[str]] = {}
    for p in repo_root.rglob('*.py'):
        try:
            text = p.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        tokens = sorted([t for t in PEFT_TOKENS if t in text])
        if tokens:
            evidence[str(p.relative_to(repo_root))] = tokens

    return {
        "id": "peft_hooks",
        "evidence": dict(sorted(evidence.items())),
        "files_with_peft": int(len(evidence)),
    }

