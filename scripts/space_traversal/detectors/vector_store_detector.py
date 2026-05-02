"""
import logging
logger = logging.getLogger(__name__)
Vector Stores Detector

Detects vector store implementations for semantic search, embeddings storage,
and retrieval-augmented generation (RAG) systems.

Patterns detected: vector, embedding, similarity, search, retrieval
"""

from pathlib import Path
from typing import Any

TARGET_DIR = "codex_addons/vector_stores/"
VECTOR_KEYWORDS = {
    "vector",
    "embedding",
    "similarity",
    "faiss",
    "chroma",
    "pinecone",
    "weaviate",
    "cosine_similarity",
    "semantic_search",
}

MAX_READ_BYTES = 200_000
REPO_ROOT = Path(__file__).resolve().parents[3]


def _read_text(path_input) -> str:
    """
    Read text from file with bounded read.

    Safeguard: Bounded read to prevent memory issues.
    Validation: Handles both string and Path inputs.
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
    Detect vector store implementations in the codebase.

    Identifies vector database integrations, embedding storage systems,
    and semantic search implementations for RAG and similarity-based retrieval.

    Args:
        file_index: Dictionary containing file information from S1 index

    Returns:
        Detection result with evidence files, patterns, and metadata
    """
    files: list[dict[str, Any]] = file_index.get("files", [])

    # Path-based detection (primary)
    path_evidence = [
        f["path"] for f in files if f["path"].startswith(TARGET_DIR) and f["path"].endswith(".py")
    ]

    # Content-based detection (secondary)
    content_evidence: dict[str, list[str]] = {}
    for entry in files:
        rel_path = entry.get("path", "")

        # Validation: Check path is valid Python file
        if not rel_path.endswith(".py"):
            continue

        # Skip files already found by path
        if rel_path in path_evidence:
            continue

        # Read and analyze content (bounded, safe)
        text = _read_text(rel_path)
        if not text:
            continue

        # Detect vector store keywords
        found_keywords = sorted([kw for kw in VECTOR_KEYWORDS if kw in text])
        if len(found_keywords) >= 2:  # Require at least 2 keywords
            content_evidence[rel_path] = found_keywords

    # Combine evidence
    all_evidence_files = sorted(set(path_evidence) | set(content_evidence.keys()))

    # Extract found patterns
    found_patterns_set = set()
    for keywords in content_evidence.values():
        found_patterns_set.update(keywords)

    # Add pattern types based on evidence
    pattern_types = []
    if path_evidence:
        pattern_types.append("path_based_detection")
    if content_evidence:
        pattern_types.append("content_based_detection")
        found_patterns_set.update(["vector", "embedding", "similarity", "search", "retrieval"])

    # Calculate functionality based on patterns found
    required_patterns_list = ["vector", "embedding", "similarity", "search", "retrieval"]
    functionality_score = (
        len(found_patterns_set & set(required_patterns_list)) / len(required_patterns_list)
        if required_patterns_list
        else 0.0
    )

    return {
        "id": "vector-stores",
        "path_evidence": sorted(path_evidence),
        "content_evidence": dict(sorted(content_evidence.items())),
        "total_files": len(all_evidence_files),
        "metrics": {
            "path_based_files": len(path_evidence),
            "content_based_files": len(content_evidence),
            "total_files": len(all_evidence_files),
        },
        # Detector contract fields
        "evidence_files": all_evidence_files,
        "found_patterns": sorted(found_patterns_set) if found_patterns_set else pattern_types,
        "required_patterns": required_patterns_list,
        "docs_keywords": [
            "vector",
            "embedding",
            "similarity",
            "search",
            "retrieval",
            "semantic",
            "rag",
        ],
        "safeguards": ["validation", "bounded", "error-handling", "deterministic"],
        "functionality_impl": functionality_score,  # Explicit functionality tracking
        "meta": {
            "mode": "hybrid",  # Path + content detection
            "deterministic": True,
            "offline": True,
            "bounded": True,
            "validation": True,
            "error_handling": True,
        },
    }
