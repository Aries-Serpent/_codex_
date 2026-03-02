"""
scripts/ci/build_embeddings.py
Phase 3 — Unified Agent Memory Corpus: embedding index builder.

Sources: .codex/docs/, .github/agents/, src/codex/cognitive/, AGENT_REGISTRY.yaml
Model:   all-MiniLM-L6-v2 (offline, Apache 2.0, ~80 MB)
Output:  .codex/embeddings/codex_index.faiss   (git-ignored)
         .codex/embeddings/codex_index_meta.json (git-tracked metadata only)

Usage:
  pip install sentence-transformers faiss-cpu numpy
  python scripts/ci/build_embeddings.py

Exit codes:
  0  — success
  1  — dependency missing (run pip install above)
  2  — no chunks collected (empty source directories)
"""

from __future__ import annotations

import json
import pathlib
import sys
import time
from dataclasses import asdict, dataclass

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
EMBED_DIR = REPO_ROOT / ".codex" / "embeddings"
INDEX_PATH = EMBED_DIR / "codex_index.faiss"
META_PATH = EMBED_DIR / "codex_index_meta.json"
MODEL_NAME = "all-MiniLM-L6-v2"

SOURCES = [
    REPO_ROOT / ".codex" / "docs",
    REPO_ROOT / ".github" / "agents",
    REPO_ROOT / "src" / "codex" / "cognitive",
    REPO_ROOT / ".github" / "agents" / "AGENT_REGISTRY.yaml",
]

# Chunk size in words; 64-word overlap for context continuity
CHUNK_SIZE = 512
CHUNK_OVERLAP = 64


@dataclass
class Chunk:
    source_path: str
    chunk_index: int
    text: str


def chunk_file(path: pathlib.Path, chunk_size: int = CHUNK_SIZE) -> list[Chunk]:
    """Split file text into overlapping word-boundary chunks."""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []
    words = text.split()
    if not words:
        return []
    chunks: list[Chunk] = []
    step = chunk_size - CHUNK_OVERLAP
    for i in range(0, len(words), step):
        chunk_text = " ".join(words[i : i + chunk_size])
        chunks.append(
            Chunk(
                source_path=str(path.relative_to(REPO_ROOT)),
                chunk_index=len(chunks),
                text=chunk_text,
            )
        )
    return chunks


def collect_chunks() -> list[Chunk]:
    """Collect text chunks from all configured source directories and files."""
    all_chunks: list[Chunk] = []
    for source in SOURCES:
        if source.is_file():
            all_chunks.extend(chunk_file(source))
        elif source.is_dir():
            for ext in ("*.md", "*.yaml", "*.yml", "*.py"):
                for f in sorted(source.rglob(ext)):
                    # Skip very large files (>500KB) to avoid CI timeout
                    if f.stat().st_size > 500_000:
                        continue
                    all_chunks.extend(chunk_file(f))
    return all_chunks


def build_index(chunks: list[Chunk]) -> None:
    """Encode chunks with sentence-transformers and write FAISS index + metadata."""
    try:
        import faiss
        import numpy as np
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        print(
            f"ERROR: Missing dependency — {exc}\n"
            "Install with: pip install sentence-transformers faiss-cpu numpy"
        )
        sys.exit(1)

    EMBED_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Loading model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    texts = [c.text for c in chunks]
    print(f"Encoding {len(texts)} chunks…")
    t0 = time.time()
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
    elapsed = time.time() - t0
    print(f"Encoded in {elapsed:.1f}s")

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings.astype(np.float32))
    faiss.write_index(index, str(INDEX_PATH))

    meta = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model": MODEL_NAME,
        "dim": dim,
        "chunk_count": len(chunks),
        "build_time_seconds": round(elapsed, 1),
        # Only metadata (not vectors) is committed to git
        "chunks": [asdict(c) for c in chunks],
    }
    META_PATH.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(
        f"Index written: {INDEX_PATH} ({len(chunks)} chunks, dim={dim})\n"
        f"Metadata written: {META_PATH}"
    )


if __name__ == "__main__":
    chunks = collect_chunks()
    if not chunks:
        print("ERROR: No chunks collected — check that source directories are populated")
        sys.exit(2)
    print(f"Collected {len(chunks)} chunks from {len(SOURCES)} sources")
    build_index(chunks)
