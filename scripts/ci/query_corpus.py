"""
scripts/ci/query_corpus.py
Phase 3 — Semantic query over unified agent memory corpus.

Combines FAISS semantic search + SQLite session log keyword match.
Also importable as a library: from scripts.ci.query_corpus import query

Usage (CLI):
  python scripts/ci/query_corpus.py "grounded enforcement policy violation"
  python scripts/ci/query_corpus.py --top-k 10 "agent handoff structured"

Usage (import):
  from scripts.ci.query_corpus import query
  results = query("agent capable of: CI test debugging", top_k=3)

Requires:
  pip install sentence-transformers faiss-cpu numpy
"""

from __future__ import annotations

import json
import pathlib
import sqlite3
import sys
from typing import Any

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
INDEX_PATH = REPO_ROOT / ".codex" / "embeddings" / "codex_index.faiss"
META_PATH = REPO_ROOT / ".codex" / "embeddings" / "codex_index_meta.json"
CHUNKS_PATH = REPO_ROOT / ".codex" / "embeddings" / "codex_index_chunks.json"
DB_PATH = REPO_ROOT / ".codex" / "codex_corpus.db"
MODEL_NAME = "all-MiniLM-L6-v2"


def _sqlite_keyword_search(query_text: str, top_k: int = 5) -> list[dict[str, Any]]:
    """Fallback: keyword search over SQLite session logs."""
    if not DB_PATH.exists():
        return []
    try:
        conn = sqlite3.connect(DB_PATH)
        keywords = [w for w in query_text.split() if len(w) > 3][
            :20
        ]  # cap at 20 to bound query size
        if not keywords:
            return []
        like_clauses = " OR ".join("summary LIKE ?" for _ in keywords)
        params = [f"%{kw}%" for kw in keywords]
        rows = conn.execute(
            f"SELECT session_id, agent_id, summary, start_time "  # noqa: S608
            f"FROM agent_sessions WHERE {like_clauses} "
            f"LIMIT ?",
            params + [top_k],
        ).fetchall()
        conn.close()
        return [
            {
                "rank": i + 1,
                "score": 0.5,  # placeholder for keyword match
                "source": f"sqlite://agent_sessions/{row[1]}",
                "text_preview": (row[2] or "")[:200],
            }
            for i, row in enumerate(rows)
        ]
    except Exception:  # noqa: BLE001
        return []


def query(query_text: str, top_k: int = 5) -> list[dict[str, Any]]:
    """
    Semantic search over the FAISS corpus.

    Falls back to SQLite keyword search when the FAISS index is absent
    (i.e., before Phase 3 build_embeddings.py has been run in CI).
    """
    if not INDEX_PATH.exists() or not META_PATH.exists():
        print(
            "⚠️  FAISS index not found — falling back to SQLite keyword search.\n"
            "   Run: python scripts/ci/build_embeddings.py  to build the index."
        )
        return _sqlite_keyword_search(query_text, top_k)

    try:
        import faiss
        import numpy as np
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        print(f"WARNING: Missing dependency — {exc}\nFalling back to SQLite keyword search.")
        return _sqlite_keyword_search(query_text, top_k)

    meta = json.loads(META_PATH.read_text(encoding="utf-8"))
    index = faiss.read_index(str(INDEX_PATH))

    # Load chunks from dedicated file (preferred) or fall back to legacy embedded chunks
    if CHUNKS_PATH.exists():
        chunks_data = json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))
        chunks = chunks_data.get("chunks", [])
    else:
        chunks = meta.get("chunks", [])

    # If no chunks are available, FAISS search cannot proceed; fall back to SQLite.
    if not chunks:
        print(
            "⚠️  FAISS index chunks not found or empty — falling back to SQLite keyword search.\n"
            "   Run: python scripts/ci/build_embeddings.py  to generate codex_index_chunks.json."
        )
        return _sqlite_keyword_search(query_text, top_k)

    model = SentenceTransformer(MODEL_NAME)
    q_vec = model.encode([query_text], convert_to_numpy=True).astype(np.float32)
    distances, indices = index.search(q_vec, min(top_k, len(chunks)))

    results = []
    for rank, (dist, idx) in enumerate(zip(distances[0], indices[0])):
        if idx < 0 or idx >= len(chunks):
            continue
        chunk = chunks[idx]
        results.append(
            {
                "rank": rank + 1,
                "score": float(1 / (1 + dist)),  # normalise L2 → 0–1
                "source": chunk["source_path"],
                "text_preview": chunk["text"][:200],
            }
        )
    return results


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Query the FAISS agent memory corpus")
    ap.add_argument("query", nargs="+", help="Search query text")
    ap.add_argument("--top-k", type=int, default=5, help="Number of results (default: 5)")
    args = ap.parse_args()

    q_text = " ".join(args.query)
    results = query(q_text, top_k=args.top_k)

    if not results:
        print("No results found.")
        sys.exit(0)

    print(f"\nResults for: '{q_text}'\n{'─' * 60}")
    for r in results:
        print(f"[{r['rank']}] score={r['score']:.3f} | {r['source']}")
        print(f"    {r['text_preview']}\n")
