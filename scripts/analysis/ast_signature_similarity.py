#!/usr/bin/env python
"""
AST Signature Similarity (P6)

Computes structural code duplication via AST node-type frequency vectors.
Produces ast_similarity.json with ast_uniqueness metric per capability.

Heuristic:
- Parse Python files in evidence sets (skip non-.py or parse failures)
- Extract AST node type counts (FunctionDef, ClassDef, Call, etc.)
- Build frequency vectors; compute pairwise cosine similarity
- ast_uniqueness = 1 - avg_similarity (higher = more diverse structure)

Environment Knobs:
  AST_SIMILARITY_ENABLE=1      -> perform computation
  AST_SIMILARITY_MAX_FILES=30  -> cap evidence set
  AST_SIMILARITY_MIN_NODES=10  -> skip trivial files

Outputs:
  audit_artifacts/ast_similarity.json

Integration:
  S4 scoring uses ast_uniqueness to refine consistency via blend modes.
"""
from __future__ import annotations
import os, json, sys, ast, math
from pathlib import Path
from typing import Dict, List
from collections import Counter

ART_DIR = Path("audit_artifacts")
RAW = ART_DIR / "capabilities_raw.json"
OUT = ART_DIR / "ast_similarity.json"

def extract_node_types(source: str) -> Counter:
    """Parse AST and count node types."""
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError):
        return Counter()
    
    counts = Counter()
    for node in ast.walk(tree):
        counts[type(node).__name__] += 1
    return counts

def cosine_similarity(a: Counter, b: Counter) -> float:
    """Cosine similarity between two count vectors."""
    if not a or not b:
        return 0.0
    
    keys = set(a) | set(b)
    dot = sum(a[k] * b[k] for k in keys)
    mag_a = math.sqrt(sum(v*v for v in a.values()))
    mag_b = math.sqrt(sum(v*v for v in b.values()))
    
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)

def ast_uniqueness_for_files(paths: List[Path], min_nodes: int) -> tuple[float, List[str]]:
    """Compute AST uniqueness across Python files."""
    warnings = []
    vectors = []
    
    for p in paths:
        if p.suffix.lower() != ".py":
            continue
        
        try:
            source = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            warnings.append(f"read_fail:{p.as_posix()}")
            continue
        
        vec = extract_node_types(source)
        if sum(vec.values()) < min_nodes:
            continue  # Skip trivial files
        
        vectors.append(vec)
    
    if len(vectors) < 2:
        return 1.0, warnings  # Single file = trivially unique
    
    # Pairwise similarities
    sims = []
    for i in range(len(vectors)):
        for j in range(i+1, len(vectors)):
            sims.append(cosine_similarity(vectors[i], vectors[j]))
    
    if not sims:
        return 1.0, warnings
    
    avg_sim = sum(sims) / len(sims)
    uniqueness = 1.0 - avg_sim
    return uniqueness, warnings

def main():
    enable = os.getenv("AST_SIMILARITY_ENABLE", "0") in {"1", "true", "TRUE"}
    if not enable:
        print("[INFO] AST similarity disabled (AST_SIMILARITY_ENABLE).")
        return 0
    
    max_files = int(os.getenv("AST_SIMILARITY_MAX_FILES", "30"))
    min_nodes = int(os.getenv("AST_SIMILARITY_MIN_NODES", "10"))
    
    if not RAW.exists():
        print("[WARN] capabilities_raw.json missing; run earlier stages.", file=sys.stderr)
        return 2
    
    data = json.loads(RAW.read_text())
    results = []
    global_warnings = []
    
    for cap in data["capabilities"]:
        ev = cap.get("evidence_files", [])[:max_files]
        paths = [Path(p) for p in ev if Path(p).exists()]
        
        uniqueness, warnings = ast_uniqueness_for_files(paths, min_nodes)
        global_warnings.extend(warnings)
        
        results.append({
            "id": cap["id"],
            "ast_uniqueness": round(uniqueness, 4),
            "python_files_analyzed": len([p for p in paths if p.suffix.lower() == ".py"]),
        })
    
    payload = {
        "capabilities": results,
        "warnings": global_warnings[:50],  # Cap warnings
    }
    
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"[INFO] AST similarity written: {OUT}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
