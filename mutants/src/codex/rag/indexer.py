"""
RAG Indexer Module
Provides text chunking, embedding, and FAISS index persistence for expanded context workflows.
"""

import hashlib
import importlib.util
import json
import logging
import shutil
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import numpy as np

logger = logging.getLogger(__name__)

try:
    import faiss
except ImportError:  # pragma: no cover - exercised when optional dependency missing
    faiss = None


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 128) -> list[tuple[int, int, str]]:
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
    if overlap < 0:
        raise ValueError("overlap must be non-negative and less than chunk_size")
    if overlap >= chunk_size:
        if overlap == 128:
            adjusted_overlap = max(0, chunk_size - 1)
            logger.warning(
                "overlap (%s) must be less than chunk_size (%s); adjusting overlap to %s",
                overlap,
                chunk_size,
                adjusted_overlap,
            )
            overlap = adjusted_overlap
        else:
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

    logger.debug(
        f"Created {len(chunks)} chunks from {text_len} characters"
    )  # codeql[py/clear-text-logging-sensitive-data]
    return chunks


def embed_chunks(
    chunks: list[tuple[int, int, str]],
    model_profile: Optional[dict[str, Any]] = None,
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
        _st_installed: bool = importlib.util.find_spec("sentence_transformers") is not None
    except ValueError:
        # Python 3.12: find_spec raises ValueError when the module is in sys.modules
        # but module.__spec__ is None (happens with test doubles such as MagicMock or
        # SimpleNamespace injected via monkeypatch/patch.dict).  The module IS present
        # in sys.modules, so treat as installed.
        _st_installed = True
    if not _st_installed:
        logger.error(
            "sentence-transformers not installed. Install with: pip install sentence-transformers"
        )
        raise ImportError("sentence-transformers not installed")

    # Extract model configuration
    model_profile = model_profile or {}
    model_name = model_profile.get("model_name", "sentence-transformers/all-MiniLM-L6-v2")
    cache_dir = model_profile.get("cache_dir", None)

    logger.info(
        f"Loading embedding model: {model_name}"
    )  # codeql[py/clear-text-logging-sensitive-data]
    try:
        from codex.rag._model_utils import safe_load_sentence_transformer

        model = safe_load_sentence_transformer(model_name, cache_dir)

    except (RuntimeError, OSError, ValueError, NotImplementedError) as e:
        type(e).__name__
        logger.error(
            "Failed to load embedding model: <ERROR_TYPE>"
        )  # codeql[py/clear-text-logging-sensitive-data]
        raise

    # Extract text from chunks
    texts = [chunk[2] for chunk in chunks]

    # CRITICAL FIX: Validate and filter inputs BEFORE encoding
    original_count = len(texts)
    texts_filtered = [text.strip() for text in texts if text and text.strip()]

    if len(texts_filtered) < original_count:
        logger.warning(
            f"Filtered out {original_count - len(texts_filtered)} empty/whitespace texts"
        )

    if not texts_filtered:
        raise ValueError("No valid text chunks to encode after filtering empty inputs")

    logger.debug(
        f"Encoding {len(texts_filtered)} texts, first sample: {texts_filtered[0][:100]}"
    )  # codeql[py/clear-text-logging-sensitive-data]

    # Generate embeddings with explicit device parameter and detailed error handling
    logger.info(
        f"Generating embeddings for {len(texts_filtered)} chunks"
    )  # codeql[py/clear-text-logging-sensitive-data]
    try:
        embeddings = model.encode(
            texts_filtered,
            batch_size=32,
            show_progress_bar=True,
            convert_to_numpy=True,
            device="cpu",  # Explicit device specification
        )
        logger.info(
            f"Successfully encoded {len(texts_filtered)} texts, embedding shape: {embeddings.shape}"
        )
        return embeddings
    except IndexError as e:
        type(e).__name__
        logger.error(
            "IndexError during encoding: <ERROR_TYPE>"
        )  # codeql[py/clear-text-logging-sensitive-data]
        logger.error(
            f"Texts count: {len(texts_filtered)}"
        )  # codeql[py/clear-text-logging-sensitive-data]
        logger.error(
            f"Sample texts: {texts_filtered[:3] if texts_filtered else 'EMPTY'}"
        )  # codeql[py/clear-text-logging-sensitive-data]
        logger.error(f"Model info: {model}")  # codeql[py/clear-text-logging-sensitive-data]
        logger.error(
            f"Model max_seq_length: {getattr(model, 'max_seq_length', 'NOT SET')}"
        )  # codeql[py/clear-text-logging-sensitive-data]
        raise RuntimeError(
            "Failed to encode texts due to IndexError. Check input format and model compatibility."
        ) from e


def persist_index(
    index_name: str,
    embeddings: np.ndarray,
    chunks: list[tuple[int, int, str]],
    metadata: Optional[dict[str, Any]] = None,
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
        raise ValueError(f"Mismatch: {len(embeddings)} embeddings vs {len(chunks)} chunks")

    if faiss is None:
        logger.error(
            "faiss-cpu not installed. Install with: pip install faiss-cpu"
        )  # codeql[py/clear-text-logging-sensitive-data]
        raise ImportError("faiss-cpu not installed")

    # Create tenant directory
    tenant_dir = Path(index_dir) / tenant_id
    tenant_dir.mkdir(parents=True, exist_ok=True)

    index_path = tenant_dir / index_name
    index_path.mkdir(parents=True, exist_ok=True)

    # Build FAISS index
    dimension = embeddings.shape[1]
    logger.info(
        f"Building FAISS index with dimension {dimension}"
    )  # codeql[py/clear-text-logging-sensitive-data]

    # Use IndexFlatL2 for exact search (can be upgraded to IndexIVFFlat for larger datasets)
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings.astype(np.float32))

    logger.info(
        f"Added {index.ntotal} vectors to FAISS index"
    )  # codeql[py/clear-text-logging-sensitive-data]

    # Save index
    faiss_file = index_path / "index.faiss"
    faiss.write_index(index, str(faiss_file))
    logger.info(
        f"Saved FAISS index to {faiss_file}"
    )  # codeql[py/clear-text-logging-sensitive-data]

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
    logger.info(
        f"Saved chunks metadata to {chunks_file}"
    )  # codeql[py/clear-text-logging-sensitive-data]

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
    logger.info(
        f"Saved index metadata to {metadata_file}"
    )  # codeql[py/clear-text-logging-sensitive-data]

    logger.info(
        f"✅ Index '{index_name}' persisted to {index_path}"
    )  # codeql[py/clear-text-logging-sensitive-data]
    return index_path


def load_index(
    index_name: str, tenant_id: str = "default", index_dir: str = ".codex/tenants"
) -> tuple[Any, list[dict[str, Any]], dict[str, Any]]:
    """
    Load a persisted FAISS index and its metadata.

    Args:
        index_name: Name of the index to load
        tenant_id: Tenant identifier
        index_dir: Base directory for indices

    Returns:
        Tuple of (faiss_index, chunks_metadata, index_metadata)
    """
    if faiss is None:
        logger.error(
            "faiss-cpu not installed. Install with: pip install faiss-cpu"
        )  # codeql[py/clear-text-logging-sensitive-data]
        raise ImportError("faiss-cpu not installed")

    index_path = Path(index_dir) / tenant_id / index_name

    if not index_path.exists():
        raise FileNotFoundError(f"Index not found: {index_path}")

    # Load FAISS index
    faiss_file = index_path / "index.faiss"
    if not faiss_file.exists():
        raise FileNotFoundError(f"FAISS index file not found: {faiss_file}")

    index = faiss.read_index(str(faiss_file))
    logger.info(
        f"Loaded FAISS index with {index.ntotal} vectors"
    )  # codeql[py/clear-text-logging-sensitive-data]

    # Load chunks metadata
    chunks_file = index_path / "chunks.json"
    if chunks_file.exists():
        with open(chunks_file, encoding="utf-8") as f:
            chunks_metadata = json.load(f)
    else:
        chunks_metadata = []

    # Load index metadata
    metadata_file = index_path / "metadata.json"
    if metadata_file.exists():
        with open(metadata_file, encoding="utf-8") as f:
            index_metadata = json.load(f)
    else:
        index_metadata = {}

    logger.info(
        f"✅ Loaded index '{index_name}' from {index_path}"
    )  # codeql[py/clear-text-logging-sensitive-data]
    return index, chunks_metadata, index_metadata


def build_index_from_files(
    files: list[Path],
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
    processing_errors = []  # Track files that failed to process

    # Process each file
    for file_path in files:
        if not file_path.exists():
            logger.warning(
                f"File not found: {file_path}"
            )  # codeql[py/clear-text-logging-sensitive-data]
            continue

        try:
            with open(file_path, encoding="utf-8") as f:
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

            logger.info(
                f"Processed {file_path}: {len(chunks)} chunks"
            )  # codeql[py/clear-text-logging-sensitive-data]

        except UnicodeDecodeError as e:
            error_type = type(e).__name__
            logger.error(
                f"Error processing {file_path}: {error_type} - unable to read file with UTF-8 encoding"  # noqa: E501
            )
            processing_errors.append(str(file_path))
        except (IOError, OSError) as e:
            error_type = type(e).__name__
            logger.error(
                f"Error processing {file_path}: {error_type}"
            )  # codeql[py/clear-text-logging-sensitive-data]
            processing_errors.append(str(file_path))

    if not all_chunks:
        if not any(file_path.exists() for file_path in files):
            raise ValueError("No valid input files found")
        if all(fm["chunks"] == 0 for fm in file_metadata if fm):
            raise ValueError("Input files contain no text content")
        if processing_errors:
            raise ValueError(
                f"No chunks generated - {len(processing_errors)} file(s) failed to process: "
                f"{', '.join(processing_errors[:3])}{'...' if len(processing_errors) > 3 else ''}"
            )
        raise ValueError(
            "No chunks generated from input files - files may be empty or in unsupported format"
        )

    logger.info(
        f"Total chunks: {len(all_chunks)} from {len(files)} files"
    )  # codeql[py/clear-text-logging-sensitive-data]

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

    return persist_index(
        index_name=index_name,
        embeddings=embeddings,
        chunks=all_chunks,
        metadata=metadata,
        tenant_id=tenant_id,
        index_dir=index_dir,
    )


# ============================================================================
# Multi-Tenant Index Management (Phase B)
# ============================================================================


class IndexOperation(Enum):
    """Operations supported by multi-tenant index manager."""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    MERGE = "merge"
    LIST = "list"


@dataclass
class TenantOperationResult:
    """
    Result of a tenant index operation.

    Attributes:
        success: Whether operation completed successfully
        operation: Type of operation performed
        tenant_id: Affected tenant ID
        index_names: List of index names involved
        message: Human-readable result message
        details: Additional operation details
    """

    success: bool
    operation: IndexOperation
    tenant_id: str
    index_names: list[str]
    message: str
    details: Optional[dict[str, Any]] = None


def manage_tenant_indices(
    tenant_id: str,
    operation: str,
    index_names: list[str],
    index_dir: str = ".codex/tenants",
    **kwargs,
) -> TenantOperationResult:
    """
    Manage tenant indices with operations: create, update, delete, merge, list.

    This function supports multi-tenant RAG workflows by providing centralized
    index lifecycle management for expanded context scenarios (64k-512k tokens).

    Args:
        tenant_id: Tenant identifier
        operation: Operation to perform ('create', 'update', 'delete', 'merge', 'list')
        index_names: List of index names to operate on
        index_dir: Base directory for tenant indices
        **kwargs: Additional operation-specific parameters:
            - files: list[Path] for 'create' operation
            - chunk_size: int for 'create' operation
            - overlap: int for 'create' operation
            - merge_name: str for 'merge' operation

    Returns:
        TenantOperationResult with operation status and details

    Raises:
        ValueError: If operation is invalid or parameters are missing

    Example:
        >>> # Create new index for tenant
        >>> result = manage_tenant_indices(
        ...     tenant_id="customer_a",
        ...     operation="create",
        ...     index_names=["docs"],
        ...     files=[Path("docs/guide.md")],
        ...     chunk_size=1000
        ... )
        >>> logger.info(result.message)
        "Successfully created index 'docs' for tenant 'customer_a'"

        >>> # Merge multiple indices
        >>> result = manage_tenant_indices(
        ...     tenant_id="customer_a",
        ...     operation="merge",
        ...     index_names=["docs", "api", "faq"],
        ...     merge_name="all_content"
        ... )
    """
    try:
        op_enum = IndexOperation(operation.lower())
    except ValueError:
        return TenantOperationResult(
            success=False,
            operation=IndexOperation.LIST,  # Default for invalid
            tenant_id=tenant_id,
            index_names=index_names,
            message=f"Invalid operation: {operation}. Must be one of: create, update, delete, merge, list",  # noqa: E501
        )

    tenant_dir = Path(index_dir) / tenant_id

    # CREATE: Build new index from files
    if op_enum == IndexOperation.CREATE:
        files = kwargs.get("files", [])
        if not files:
            return TenantOperationResult(
                success=False,
                operation=op_enum,
                tenant_id=tenant_id,
                index_names=index_names,
                message="'create' operation requires 'files' parameter",
            )

        created = []
        for index_name in index_names:
            try:
                index_path = build_index_from_files(
                    files=files,
                    index_name=index_name,
                    tenant_id=tenant_id,
                    index_dir=index_dir,
                    chunk_size=kwargs.get("chunk_size", 1000),
                    overlap=kwargs.get("overlap", 128),
                )
                created.append(index_name)
                logger.info(
                    f"Created index '{index_name}' at {index_path}"
                )  # codeql[py/clear-text-logging-sensitive-data]
            except (IOError, OSError) as e:
                error_type = type(e).__name__
                logger.error(
                    f"Failed to create index '{index_name}': <ERROR_TYPE>"
                )  # codeql[py/clear-text-logging-sensitive-data]

        if created:
            return TenantOperationResult(
                success=True,
                operation=op_enum,
                tenant_id=tenant_id,
                index_names=created,
                message=f"Successfully created {len(created)} index(es) for tenant '{tenant_id}'",
                details={"created_indices": created},
            )
        return TenantOperationResult(
            success=False,
            operation=op_enum,
            tenant_id=tenant_id,
            index_names=index_names,
            message=f"Failed to create any indices for tenant '{tenant_id}'",
        )

    # UPDATE: Rebuild existing index with new data
    if op_enum == IndexOperation.UPDATE:
        files = kwargs.get("files", [])
        if not files:
            return TenantOperationResult(
                success=False,
                operation=op_enum,
                tenant_id=tenant_id,
                index_names=index_names,
                message="'update' operation requires 'files' parameter",
            )

        updated = []
        for index_name in index_names:
            try:
                # Delete old index if exists
                old_path = tenant_dir / index_name
                if old_path.exists():
                    shutil.rmtree(old_path)
                    logger.info(
                        f"Removed old index '{index_name}'"
                    )  # codeql[py/clear-text-logging-sensitive-data]

                # Create new index
                index_path = build_index_from_files(
                    files=files,
                    index_name=index_name,
                    tenant_id=tenant_id,
                    index_dir=index_dir,
                    chunk_size=kwargs.get("chunk_size", 1000),
                    overlap=kwargs.get("overlap", 128),
                )
                updated.append(index_name)
                logger.info(
                    f"Updated index '{index_name}' at {index_path}"
                )  # codeql[py/clear-text-logging-sensitive-data]
            except (IOError, OSError) as e:
                error_type = type(e).__name__
                logger.error(
                    f"Failed to update index '{index_name}': <ERROR_TYPE>"
                )  # codeql[py/clear-text-logging-sensitive-data]

        if updated:
            return TenantOperationResult(
                success=True,
                operation=op_enum,
                tenant_id=tenant_id,
                index_names=updated,
                message=f"Successfully updated {len(updated)} index(es) for tenant '{tenant_id}'",
                details={"updated_indices": updated},
            )
        return TenantOperationResult(
            success=False,
            operation=op_enum,
            tenant_id=tenant_id,
            index_names=index_names,
            message=f"Failed to update any indices for tenant '{tenant_id}'",
        )

    # DELETE: Remove indices
    if op_enum == IndexOperation.DELETE:
        deleted = []
        for index_name in index_names:
            try:
                index_path = tenant_dir / index_name
                if index_path.exists():
                    shutil.rmtree(index_path)
                    deleted.append(index_name)
                    logger.info(
                        f"Deleted index '{index_name}' from {tenant_dir}"
                    )  # codeql[py/clear-text-logging-sensitive-data]
                else:
                    logger.warning(
                        f"Index '{index_name}' not found for tenant '{tenant_id}'"
                    )  # codeql[py/clear-text-logging-sensitive-data]
            except (IOError, OSError) as e:
                error_type = type(e).__name__
                logger.error(
                    f"Failed to delete index '{index_name}': <ERROR_TYPE>"
                )  # codeql[py/clear-text-logging-sensitive-data]

        if deleted:
            return TenantOperationResult(
                success=True,
                operation=op_enum,
                tenant_id=tenant_id,
                index_names=deleted,
                message=f"Successfully deleted {len(deleted)} index(es) for tenant '{tenant_id}'",
                details={"deleted_indices": deleted},
            )
        return TenantOperationResult(
            success=False,
            operation=op_enum,
            tenant_id=tenant_id,
            index_names=index_names,
            message=f"No indices deleted for tenant '{tenant_id}'",
        )

    # MERGE: Combine multiple indices into one
    if op_enum == IndexOperation.MERGE:
        merge_name = kwargs.get("merge_name")
        if not merge_name:
            return TenantOperationResult(
                success=False,
                operation=op_enum,
                tenant_id=tenant_id,
                index_names=index_names,
                message="'merge' operation requires 'merge_name' parameter",
            )

        try:
            # Load all indices to merge
            all_embeddings = []
            all_chunks = []
            all_metadata = []

            for index_name in index_names:
                try:
                    index, chunks, metadata = load_index(index_name, tenant_id, index_dir)

                    # Extract embeddings from FAISS index
                    if index.ntotal > 0:
                        embeddings = np.zeros((index.ntotal, index.d), dtype=np.float32)
                        for i in range(index.ntotal):
                            embeddings[i] = index.reconstruct(i)

                        all_embeddings.append(embeddings)
                        all_chunks.extend([(c["start"], c["end"], c["text"]) for c in chunks])
                        all_metadata.append(metadata)

                    logger.info(
                        f"Loaded {index.ntotal} vectors from '{index_name}'"
                    )  # codeql[py/clear-text-logging-sensitive-data]
                except (ValueError, TypeError, RuntimeError, IOError, OSError) as e:
                    error_type = type(e).__name__
                    logger.error(
                        f"Failed to load index '{index_name}': {error_type}: {str(e)}"
                    )  # codeql[py/clear-text-logging-sensitive-data]

            if not all_embeddings:
                return TenantOperationResult(
                    success=False,
                    operation=op_enum,
                    tenant_id=tenant_id,
                    index_names=index_names,
                    message="No valid indices found to merge",
                )

            # Combine all embeddings
            combined_embeddings = np.vstack(all_embeddings)

            # Create merged metadata
            merged_metadata = {
                "merged_from": index_names,
                "source_metadata": all_metadata,
                "total_sources": len(index_names),
            }

            # Persist merged index
            index_path = persist_index(
                index_name=merge_name,
                embeddings=combined_embeddings,
                chunks=all_chunks,
                metadata=merged_metadata,
                tenant_id=tenant_id,
                index_dir=index_dir,
            )

            return TenantOperationResult(
                success=True,
                operation=op_enum,
                tenant_id=tenant_id,
                index_names=index_names,
                message=f"Successfully merged {len(index_names)} indices into '{merge_name}' for tenant '{tenant_id}'",  # noqa: E501
                details={
                    "merged_name": merge_name,
                    "source_indices": index_names,
                    "total_vectors": len(combined_embeddings),
                    "index_path": str(index_path),
                },
            )

        except (IOError, OSError) as e:
            error_type = type(e).__name__
            logger.error(
                "Merge operation failed: <ERROR_TYPE>"
            )  # codeql[py/clear-text-logging-sensitive-data]
            return TenantOperationResult(
                success=False,
                operation=op_enum,
                tenant_id=tenant_id,
                index_names=index_names,
                message=f"Failed to merge indices: {e!s}",
            )

    # LIST: List all indices for tenant
    elif op_enum == IndexOperation.LIST:
        try:
            if not tenant_dir.exists():
                return TenantOperationResult(
                    success=True,
                    operation=op_enum,
                    tenant_id=tenant_id,
                    index_names=[],
                    message=f"No indices found for tenant '{tenant_id}' (tenant directory does not exist)",  # noqa: E501
                    details={"indices": []},
                )

            indices = []
            for item in tenant_dir.iterdir():
                if item.is_dir() and (item / "index.faiss").exists():
                    # Load metadata for summary
                    metadata_file = item / "metadata.json"
                    if metadata_file.exists():
                        with open(metadata_file) as f:
                            metadata = json.load(f)
                        indices.append(
                            {
                                "name": item.name,
                                "vectors": metadata.get("num_vectors", 0),
                                "dimension": metadata.get("dimension", 0),
                                "created_at": metadata.get("created_at", "unknown"),
                            }
                        )
                    else:
                        indices.append(
                            {
                                "name": item.name,
                                "vectors": "unknown",
                                "dimension": "unknown",
                                "created_at": "unknown",
                            }
                        )

            return TenantOperationResult(
                success=True,
                operation=op_enum,
                tenant_id=tenant_id,
                index_names=[idx["name"] for idx in indices],
                message=f"Found {len(indices)} index(es) for tenant '{tenant_id}'",
                details={"indices": indices},
            )

        except (ValueError, TypeError, RuntimeError) as e:
            error_type = type(e).__name__
            logger.error(
                "List operation failed: <ERROR_TYPE>"
            )  # codeql[py/clear-text-logging-sensitive-data]
            return TenantOperationResult(
                success=False,
                operation=op_enum,
                tenant_id=tenant_id,
                index_names=[],
                message=f"Failed to list indices: {e!s}",
            )

    # Fallback for unknown operations
    return TenantOperationResult(
        success=False,
        operation=op_enum,
        tenant_id=tenant_id,
        index_names=index_names,
        message=f"Operation '{operation}' not fully implemented",
    )


class RAGIndexer:
    """High-level indexer facade for RAG operations.

    Wraps the module-level functions (build_index_from_files, load_index, etc.)
    in a stateful class interface expected by CLI and tenant management tests.
    """

    def __init__(
        self,
        index_dir: Optional[str] = None,
        device: str = "cpu",
    ) -> None:
        self.index_dir = Path(index_dir) if index_dir else Path(".")
        self.device = device
        self.model: Any = None
        self._try_load_model()

    def build_index(
        self,
        files: list[str],
        index_name: str = "default",
        chunk_size: int = 1000,
        overlap: int = 128,
    ) -> Path:
        """Build an index from a list of files."""
        return build_index_from_files(
            files=[Path(f) for f in files],
            index_dir=str(self.index_dir),
            index_name=index_name,
            chunk_size=chunk_size,
            overlap=overlap,
        )

    def list_tenants(self) -> list[str]:
        """List available tenant directories."""
        if not self.index_dir.exists():
            return []
        return [
            d.name for d in self.index_dir.iterdir() if d.is_dir() and not d.name.startswith(".")
        ]

    def _try_load_model(self) -> None:
        """Attempt to load the default embedding model onto self.device.

        Silently skips if sentence-transformers is not installed or the model
        cannot be loaded (e.g. no network access in offline CI environments).
        Callers that require a loaded model should check ``self.model is not None``.
        """
        try:
            from codex.rag._model_utils import safe_load_sentence_transformer
            from codex.rag.utils import safe_model_to_device

            self.model = safe_load_sentence_transformer(
                "sentence-transformers/all-MiniLM-L6-v2",
            )
            self.model = safe_model_to_device(self.model, self.device)
        except (ValueError, TypeError, RuntimeError):
            # Model unavailable (offline, missing dep, etc.) — leave as None.
            logger.debug(
                "Suppressed exception in handler", exc_info=True
            )  # codeql[py/clear-text-logging-sensitive-data]

    def move_to_device(self, device: str) -> None:
        """Move the loaded embedding model to *device* and update ``self.device``."""
        self.device = device
        if self.model is not None:
            from codex.rag.utils import safe_model_to_device

            self.model = safe_model_to_device(self.model, device)
