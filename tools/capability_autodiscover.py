#!/usr/bin/env python3
"""
Scan repository to suggest capability entries (CAP-XXX) with evidence and tags.

Writes audit_artifacts/capabilities_raw.json with a list of suggested capabilities.

Usage:
  python tools/capability_autodiscover.py
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "audit_artifacts" / "capabilities_raw.json"

HINTS = [
    ("Tokenization", ["tokenizer", "tokenization", "sentencepiece", "hf"], ["huggingface", "offline"]),
    ("Training", ["trainer", "training", "epoch", "optimizer"], ["gpu", "deterministic"]),
    ("Evaluation", ["eval", "metrics", "accuracy", "f1"], ["cli"]),
    ("Security", ["security", "sanitize", "detect-secrets", "bandit"], ["security"]),
    ("Configuration", ["hydra", "configs", "conf"], ["hydra"]),
    ("Tracking", ["mlflow", "tensorboard", "wandb"], ["mlflow"]),
    ("Testing", ["pytest", "tests", "nox"], ["pytest", "nox"]),
]


def discover() -> List[Dict]:
    results: List[Dict] = []
    for name, keywords, tags in HINTS:
        evidence: List[str] = []
        for kw in keywords:
            for p in REPO.rglob(f"*{kw}*"):
                if p.is_file() and len(evidence) < 25:
                    evidence.append(str(p.relative_to(REPO)))
        if evidence:
            results.append(
                {
                    "name": name,
                    "category": name if name in {"Tokenization", "Training", "Evaluation", "Security", "Configuration", "Testing", "Tracking"} else "Other",
                    "status": "Partially Implemented",
                    "artifacts": ", ".join(evidence[:10]),
                    "gaps": "",
                    "risks": "",
                    "severity": 3,
                    "confidence": 3,
                    "tags": tags,
                    "discovery_method": "code_scan",
                }
            )
    return results


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    data = {"generated": True, "suggested_capabilities": discover()}
    OUT.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"[OK] Wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
