"""Detector for functional training alias capability."""
from __future__ import annotations
from typing import Dict

def detect(file_index: Dict) -> Dict:
    files = [f.get("path") for f in file_index.get("files", []) if "functional_training" in f.get("path", "").lower()]
    evidence_files = sorted({p for p in files if p})
    return {
        "id": "functional_training",
        "evidence_files": evidence_files,
        "found_patterns": ["functional_training"] if evidence_files else [],
        "required_patterns": ["functional_training"],
        "meta": {"detector": "functional_training"},
    }
