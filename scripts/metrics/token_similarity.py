#!/usr/bin/env python
"""
import logging
logger = logging.getLogger(__name__)
Token Similarity Engine (P4)

Computes token-level similarity across evidence files for each capability
to refine consistency metric:
- Load capabilities_raw.json
- For each capability: tokenize contents of evidence files (simple word split)
- Build term frequency vectors & compute average pairwise cosine similarity
- similarity_index = 1 - avg_pairwise_similarity (higher is better uniqueness)
- Output token_similarity.json for scoring stage to consume

Environment Knobs (optional):
  TOKEN_SIMILARITY_ENABLE=1    -> perform computation
  TOKEN_SIMILARITY_MAX_FILES=50 -> cap evidence set to reduce cost
  TOKEN_SIMILARITY_MIN_LEN=5   -> skip tokens shorter than threshold
"""
from __future__ import annotations

import json
import math
import os
import re
import sys
from pathlib import Path

ART_DIR = Path("audit_artifacts")
RAW = ART_DIR / "capabilities_raw.json"
OUT = ART_DIR / "token_similarity.json"

WORD_RE = re.compile(r"[A-Za-z0-9_]+")


def tokenize(text: str, min_len: int) -> list[str]:
    return [w.lower() for w in WORD_RE.findall(text) if len(w) >= min_len]


def build_tf(tokens: list[str]) -> dict[str, int]:
    tf: dict[str, int] = {}
    for t in tokens:
        tf[t] = tf.get(t, 0) + 1
    return tf


def cosine(a: dict[str, int], b: dict[str, int]) -> float:
    if not a or not b:
        return 0.0
    keys = set(a) | set(b)
    dot = sum(a.get(k, 0) * b.get(k, 0) for k in keys)
    mag_a = math.sqrt(sum(v * v for v in a.values()))
    mag_b = math.sqrt(sum(v * v for v in b.values()))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def similarity_for_files(paths: list[Path], min_len: int) -> float:
    if len(paths) < 2:
        return 1.0  # single file uniqueness trivially high
    tfs = []
    for p in paths:
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            txt = ""
        tfs.append(build_tf(tokenize(txt, min_len)))
    sims = []
    for i in range(len(tfs)):
        for j in range(i + 1, len(tfs)):
            sims.append(cosine(tfs[i], tfs[j]))
    if not sims:
        return 1.0
    avg = sum(sims) / len(sims)
    return 1 - avg  # invert: high = more unique


def main():
    enable = os.getenv("TOKEN_SIMILARITY_ENABLE", "0") in {"1", "true", "TRUE"}
    if not enable:
        print("[INFO] Token similarity disabled (TOKEN_SIMILARITY_ENABLE).")
        return 0

    max_files = int(os.getenv("TOKEN_SIMILARITY_MAX_FILES", "50"))
    min_len = int(os.getenv("TOKEN_SIMILARITY_MIN_LEN", "5"))

    if not RAW.exists():
        print("[WARN] capabilities_raw.json missing; run earlier stages.", file=sys.stderr)
        return 2

    data = json.loads(RAW.read_text())
    results = []

    for cap in data["capabilities"]:
        ev = cap.get("evidence_files", [])[:max_files]
        paths = [Path(p) for p in ev if Path(p).exists()]
        score = similarity_for_files(paths, min_len)
        results.append(
            {"id": cap["id"], "similarity_index": round(score, 4), "files_considered": len(paths)}
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"capabilities": results}, indent=2), encoding="utf-8")
    print(f"[INFO] Token similarity written: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
