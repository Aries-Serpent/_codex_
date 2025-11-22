"""Detector for training loop alias capability."""
from __future__ import annotations
from typing import Dict

def detect(file_index: Dict) -> Dict:
    files = [f.get("path") for f in file_index.get("files", []) if "train_loop" in f.get("path", "").lower()]
    evidence_files = sorted({p for p in files if p})
    return {
        "id": "train_loop",
        "evidence_files": evidence_files,
        "found_patterns": ["train_loop"] if evidence_files else [],
        "required_patterns": ["train_loop"],
        "meta": {"detector": "train_loop"},
    }
