"""Similarity utilities for consolidation heuristics."""

from __future__ import annotations

import ast
import hashlib
from dataclasses import dataclass
from pathlib import Path

_SPLIT = set(" \t\r\n,.;:()[]{}<>+-=*/\\|!@#$%^&~`'\"")


def _tokens(text: str) -> list[str]:
    tokens: list[str] = []
    current: list[str] = []
    for ch in text:
        if ch in _SPLIT:
            if current:
                tokens.append("".join(current))
                current.clear()
        else:
            current.append(ch)
    if current:
        tokens.append("".join(current))
    return tokens


def _shingles(tokens: list[str], k: int = 5) -> set[str]:
    if len(tokens) < k:
        return {" ".join(tokens)} if tokens else set()
    return {" ".join(tokens[i : i + k]) for i in range(len(tokens) - k + 1)}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    intersection = len(a & b)
    union = len(a | b)
    return intersection / union if union else 0.0


def py_ast_hash(text: str) -> str:
    try:
        tree = ast.parse(text)
        dump = ast.dump(tree, annotate_fields=True, include_attributes=False)
        return hashlib.sha1(dump.encode("utf-8")).hexdigest()
    except Exception:
        return ""


def simhash64(tokens: list[str]) -> int:
    vector = [0] * 64
    for token in tokens:
        hashed = int(hashlib.sha1(token.encode("utf-8")).hexdigest(), 16)
        for bit in range(64):
            if (hashed >> bit) & 1:
                vector[bit] += 1
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 1 << bit
    return value


def hamming64(a: int, b: int) -> int:
    return (a ^ b).bit_count()


@dataclass(slots=True)
class Similarity:
    jaccard: float
    py_ast_equal: bool
    doc_hd: int


def compute_similarity(path_a: Path, path_b: Path) -> Similarity:
    text_a = path_a.read_text(encoding="utf-8", errors="ignore")
    text_b = path_b.read_text(encoding="utf-8", errors="ignore")
    jaccard_score = jaccard(_shingles(_tokens(text_a)), _shingles(_tokens(text_b)))
    ast_equal = False
    if path_a.suffix == ".py" and path_b.suffix == ".py":
        hash_a = py_ast_hash(text_a)
        hash_b = py_ast_hash(text_b)
        ast_equal = bool(hash_a) and hash_a == hash_b
    doc_hd = 64
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        doc_hd = hamming64(simhash64(_tokens(text_a)), simhash64(_tokens(text_b)))
    return Similarity(jaccard=round(jaccard_score, 4), py_ast_equal=ast_equal, doc_hd=doc_hd)
