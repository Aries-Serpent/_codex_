"""
RAG Indexer Module
Provides text chunking, embedding, and FAISS index persistence for expanded context workflows.
"""

import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


def chunk_text(
    text: str, chunk_size: int = 1000, overlap: int = 128
) -> List[Tuple[int, int, str]]:
    """
    Split text into overlapping chunks for embedding.

    Args:
        text: Input text to chunk
        chunk_size: Maximum size of each chunk in characters
        overlap: Number of characters to overlap between chunks

    Returns:
        List of tuples (start_pos, end_pos, chunk_text)
    """
    if not text:
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be non-negative and less than chunk_size")

    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)

        # Try to break at sentence boundaries near the end
        if end < text_len:
            # Look for sentence endings in the last 20% of the chunk
            search_start = max(start, end - chunk_size // 5)
            for delimiter in [".\n", ". ", "!\n", "! ", "?\n", "? "]:
                last_pos = text.rfind(delimiter, search_start, end)
                if last_pos != -1:
                    end = last_pos + len(delimiter)
                    break

        chunk = text[start:end].strip()
        if chunk:  # Only add non-empty chunks
            chunks.append((start, end, chunk))

        # Move start position for next chunk, accounting for overlap
        start = end - overlap if end < text_len else text_len

    logger.debug(f"Created {len(chunks)} chunks from {text_len} characters")
    return chunks


def embed_chunks(
    chunks: List[Tuple[int, int, str]],
    model_profile: Optional[Dict[str, Any]] = None,
) -> np.ndarray:
    """
    Generate embeddings for text chunks using specified model.

    Args:
        chunks: List of (start, end, text) tuples from chunk_text()
        model_profile: Optional dict with 'model_name' and 'cache_dir' keys

    Returns:
        numpy array of embeddings (shape: [num_chunks, embedding_dim])
    """
    if not chunks:
        return np.array([])

    # Import here to avoid hard dependency
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        logger.error(
            "sentence-transformers not installed. "
            "Install with: pip install sentence-transformers"
        )
        raise

    # Extract model configuration
    model_profile = model_profile or {}
    model_name = model_profile.get(
        "model_name", "sentence-transformers/all-MiniLM-L6-v2"
    )
    cache_dir = model_profile.get("cache_dir", None)

    # Load model
    logger.info(f"Loading embedding model: {model_name}")
    model = SentenceTransformer(model_name, cache_folder=cache_dir)

    # Extract text from chunks
    texts = [chunk[2] for chunk in chunks]

    # Generate embeddings
    logger.info(f"Generating embeddings for {len(texts)} chunks")
    embeddings = model.encode(
        texts, batch_size=32, show_progress_bar=True, convert_to_numpy=True
    )

    logger.info(f"Generated embeddings with shape: {embeddings.shape}")
    return embeddings


def persist_index(
    index_name: str,
    embeddings: np.ndarray,
    chunks: List[Tuple[int, int, str]],
    metadata: Optional[Dict[str, Any]] = None,
    tenant_id: str = "default",
    index_dir: str = ".codex/tenants",
) -> Path:
    """
    Persist FAISS index and metadata to disk.

    Args:
        index_name: Name of the index (e.g., "repo_docs")
        embeddings: numpy array of embeddings
        chunks: List of (start, end, text) tuples
        metadata: Optional metadata dict (source files, timestamps, etc.)
        tenant_id: Tenant identifier for multi-tenancy support
        index_dir: Base directory for storing indices

    Returns:
        Path to the persisted index directory
    """
    if len(embeddings) == 0:
        raise ValueError("Cannot persist empty embeddings")

    if len(embeddings) != len(chunks):
        raise ValueError(
            f"Mismatch: {len(embeddings)} embeddings vs {len(chunks)} chunks"
        )

    # Import FAISS
    try:
        import faiss
    except ImportError:
        logger.error(
            "faiss-cpu not installed. Install with: pip install faiss-cpu"
        )
        raise

    # Create tenant directory
    tenant_dir = Path(index_dir) / tenant_id
    tenant_dir.mkdir(parents=True, exist_ok=True)

    index_path = tenant_dir / index_name
    index_path.mkdir(parents=True, exist_ok=True)

    # Build FAISS index
    dimension = embeddings.shape[1]
    logger.info(f"Building FAISS index with dimension {dimension}")

    # Use IndexFlatL2 for exact search (can be upgraded to IndexIVFFlat for larger datasets)
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings.astype(np.float32))

    logger.info(f"Added {index.ntotal} vectors to FAISS index")

    # Save index
    faiss_file = index_path / "index.faiss"
    faiss.write_index(index, str(faiss_file))
    logger.info(f"Saved FAISS index to {faiss_file}")

    # Save chunks metadata
    chunks_metadata = []
    for i, (start, end, text) in enumerate(chunks):
        chunks_metadata.append(
            {
                "id": i,
                "start": start,
                "end": end,
                "text": text,
                "text_hash": hashlib.sha256(text.encode()).hexdigest()[:16],
            }
        )

    chunks_file = index_path / "chunks.json"
    with open(chunks_file, "w", encoding="utf-8") as f:
        json.dump(chunks_metadata, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved chunks metadata to {chunks_file}")

    # Save index metadata
    index_metadata = {
        "index_name": index_name,
        "tenant_id": tenant_id,
        "dimension": dimension,
        "num_vectors": int(index.ntotal),
        "index_type": "IndexFlatL2",
        "created_at": str(Path(faiss_file).stat().st_mtime),
        **(metadata or {}),
    }

    metadata_file = index_path / "metadata.json"
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(index_metadata, f, indent=2)
    logger.info(f"Saved index metadata to {metadata_file}")

    logger.info(f"✅ Index '{index_name}' persisted to {index_path}")
    return index_path


def load_index(
    index_name: str, tenant_id: str = "default", index_dir: str = ".codex/tenants"
) -> Tuple[Any, List[Dict[str, Any]], Dict[str, Any]]:
    """
    Load a persisted FAISS index and its metadata.

    Args:
        index_name: Name of the index to load
        tenant_id: Tenant identifier
        index_dir: Base directory for indices

    Returns:
        Tuple of (faiss_index, chunks_metadata, index_metadata)
    """
    try:
        import faiss
    except ImportError:
        logger.error(
            "faiss-cpu not installed. Install with: pip install faiss-cpu"
        )
        raise

    index_path = Path(index_dir) / tenant_id / index_name

    if not index_path.exists():
        raise FileNotFoundError(f"Index not found: {index_path}")

    # Load FAISS index
    faiss_file = index_path / "index.faiss"
    if not faiss_file.exists():
        raise FileNotFoundError(f"FAISS index file not found: {faiss_file}")

    index = faiss.read_index(str(faiss_file))
    logger.info(f"Loaded FAISS index with {index.ntotal} vectors")

    # Load chunks metadata
    chunks_file = index_path / "chunks.json"
    if chunks_file.exists():
        with open(chunks_file, "r", encoding="utf-8") as f:
            chunks_metadata = json.load(f)
    else:
        chunks_metadata = []

    # Load index metadata
    metadata_file = index_path / "metadata.json"
    if metadata_file.exists():
        with open(metadata_file, "r", encoding="utf-8") as f:
            index_metadata = json.load(f)
    else:
        index_metadata = {}

    logger.info(f"✅ Loaded index '{index_name}' from {index_path}")
    return index, chunks_metadata, index_metadata


def build_index_from_files(
    files: List[Path],
    index_name: str,
    tenant_id: str = "default",
    index_dir: str = ".codex/tenants",
    chunk_size: int = 1000,
    overlap: int = 128,
) -> Path:
    """
    Build and persist a FAISS index from a list of text files.

    Args:
        files: List of file paths to index
        index_name: Name for the index
        tenant_id: Tenant identifier
        index_dir: Base directory for indices
        chunk_size: Chunk size for text splitting
        overlap: Overlap between chunks

    Returns:
        Path to the persisted index directory
    """
    all_chunks = []
    file_metadata = []

    # Process each file
    for file_path in files:
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

            chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
            all_chunks.extend(chunks)

            file_metadata.append(
                {
                    "file": str(file_path),
                    "size": len(text),
                    "chunks": len(chunks),
                }
            )

            logger.info(f"Processed {file_path}: {len(chunks)} chunks")

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")

    if not all_chunks:
        raise ValueError("No chunks generated from input files")

    logger.info(f"Total chunks: {len(all_chunks)} from {len(files)} files")

    # Generate embeddings
    embeddings = embed_chunks(all_chunks)

    # Persist index
    metadata = {
        "files": file_metadata,
        "total_files": len(files),
        "total_chunks": len(all_chunks),
        "chunk_size": chunk_size,
        "overlap": overlap,
    }

    index_path = persist_index(
        index_name=index_name,
        embeddings=embeddings,
        chunks=all_chunks,
        metadata=metadata,
        tenant_id=tenant_id,
        index_dir=index_dir,
    )

    return index_path
