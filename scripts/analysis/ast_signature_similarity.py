#!/usr/bin/env python
"""
AST Signature Similarity Analysis Tool (P6)

Computes AST-based uniqueness scores for each capability by analyzing
Python evidence files:
- Load capabilities_raw.json
- For each capability: parse Python files and extract AST signatures
- Compute pairwise structural similarity between files
- ast_uniqueness = 1 - avg_pairwise_similarity (higher is more unique)
- Output ast_similarity.json for scoring stage to consume

Environment Knobs (parsed via scripts/config/parse_knobs.py schema):
  AST_SIMILARITY_ENABLE=1       -> perform computation (required)
  AST_SIMILARITY_MAX_FILES=30   -> cap evidence set to reduce cost
  AST_SIMILARITY_MIN_NODES=10   -> skip files with fewer AST nodes
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

ART_DIR = Path("audit_artifacts")
RAW = ART_DIR / "capabilities_raw.json"
OUT = ART_DIR / "ast_similarity.json"


def extract_ast_signature(code: str) -> Optional[Dict]:
    """
    Extract AST signature from Python code.

    Returns dictionary with node type counts and structural hash,
    or None if parsing fails.
    """
    try:
        tree = ast.parse(code)
        counts: Dict[str, int] = defaultdict(int)
        for node in ast.walk(tree):
            counts[type(node).__name__] += 1
        # Create a normalized AST dump for structural hashing
        dump = ast.dump(tree, annotate_fields=False)
        struct_hash = hashlib.md5(dump.encode(, usedforsecurity=False)).hexdigest()
        return {"nodes": dict(counts), "hash": struct_hash}
    except SyntaxError:
        return None


def signature_similarity(sig1: Dict, sig2: Dict) -> float:
    """
    Calculate similarity between two AST signatures.

    Returns a value between 0.0 (completely different) and 1.0 (identical).
    """
    # Compare node type distributions
    nodes1 = sig1["nodes"]
    nodes2 = sig2["nodes"]
    all_nodes = set(nodes1.keys()) | set(nodes2.keys())

    if not all_nodes:
        return 1.0

    # Compute overlap ratio
    intersection = sum(min(nodes1.get(n, 0), nodes2.get(n, 0)) for n in all_nodes)
    total = max(sum(nodes1.values()), sum(nodes2.values()))

    node_sim = intersection / total if total > 0 else 1.0

    # Hash comparison for exact structural match
    hash_sim = 1.0 if sig1["hash"] == sig2["hash"] else 0.0

    # Weighted combination
    return 0.7 * node_sim + 0.3 * hash_sim


def compute_uniqueness(paths: List[Path], min_nodes: int = 10) -> float:
    """
    Compute AST uniqueness score for a set of Python files.

    Returns 1.0 for single/no files, otherwise 1 - avg_pairwise_similarity.

    Args:
        paths: List of Python file paths to analyze
        min_nodes: Minimum AST nodes required to include a file
    """
    signatures = []
    for p in paths:
        try:
            code = p.read_text(encoding="utf-8", errors="ignore")
            sig = extract_ast_signature(code)
            if sig and sum(sig["nodes"].values()) >= min_nodes:
                signatures.append(sig)
        except Exception:
            continue

    if len(signatures) < 2:
        return 1.0  # Single file or no valid files = trivially unique

    # Compute pairwise similarities
    sims = []
    for i in range(len(signatures)):
        for j in range(i + 1, len(signatures)):
            sims.append(signature_similarity(signatures[i], signatures[j]))

    if not sims:
        return 1.0

    avg_sim = sum(sims) / len(sims)
    return 1.0 - avg_sim  # Invert: high value = more unique


def main():
    enable = os.getenv("AST_SIMILARITY_ENABLE", "0") in {"1", "true", "TRUE"}
    if not enable:
        print("[INFO] AST similarity disabled (AST_SIMILARITY_ENABLE).")
        return 0

    # Read additional configuration knobs
    max_files = int(os.getenv("AST_SIMILARITY_MAX_FILES", "30"))
    min_nodes = int(os.getenv("AST_SIMILARITY_MIN_NODES", "10"))

    if not RAW.exists():
        print(f"[WARN] {RAW} missing; run earlier stages.", file=sys.stderr)
        return 2

    data = json.loads(RAW.read_text(encoding="utf-8"))
    results = []

    for cap in data["capabilities"]:
        evidence_files = cap.get("evidence_files", [])[:max_files]
        # Filter to Python files only, avoiding redundant Path construction
        py_paths = []
        for f in evidence_files:
            if f.endswith(".py"):
                p = Path(f)
                if p.exists():
                    py_paths.append(p)

        uniqueness = compute_uniqueness(py_paths, min_nodes)
        results.append({
            "id": cap["id"],
            "ast_uniqueness": round(uniqueness, 4),
            "python_files_analyzed": len(py_paths),
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"capabilities": results}, indent=2), encoding="utf-8")
    print(f"[INFO] AST similarity written: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
