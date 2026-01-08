"""
RAG Retriever Module
Provides semantic search over FAISS indices with provenance tracking.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np

from .utils import safe_model_load

logger = logging.getLogger(__name__)


class Retriever:
    """
    Semantic retriever using FAISS indices with provenance tracking.

    Supports loading persisted indices and querying with configurable top-k results.
    Returns results with full provenance (file, line ranges, scores, timestamps).
    """

    def __init__(
        self,
        index_dir: str = ".codex/tenants",
        index_name: str = "default",
        tenant_id: str = "default",
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        cache_dir: Optional[str] = None,
    ):
        """
        Initialize retriever with index location and embedding model.

        Args:
            index_dir: Base directory containing tenant indices
            index_name: Name of the index to load
            tenant_id: Tenant identifier for multi-tenancy
            model_name: Embedding model name for query encoding
            cache_dir: Optional cache directory for model weights
        """
        self.index_dir = index_dir
        self.index_name = index_name
        self.tenant_id = tenant_id
        self.model_name = model_name
        self.cache_dir = cache_dir

        self.faiss_index = None
        self.chunks_metadata = []
        self.index_metadata = {}
        self.model = None

        self._load_index()
        self._load_model()

    def _load_index(self):
        """Load FAISS index and metadata from disk."""
        from codex.rag.indexer import load_index

        try:
            self.faiss_index, self.chunks_metadata, self.index_metadata = load_index(
                index_name=self.index_name,
                tenant_id=self.tenant_id,
                index_dir=self.index_dir,
            )
            logger.info(
                f"Loaded index '{self.index_name}' with {len(self.chunks_metadata)} chunks"
            )
        except FileNotFoundError as e:
            logger.warning(f"Index not found: {e}")
            logger.warning("Use indexer.py to build an index first")
            # Allow initialization without an index for testing
        except Exception as e:
            logger.error(f"Error loading index: {e}")
            raise

    def _load_model(self):
        """Load embedding model for query encoding."""
        try:
            from sentence_transformers import SentenceTransformer

            logger.info(f"Loading query embedding model: {self.model_name}")
            self.model = SentenceTransformer(
                self.model_name, cache_folder=self.cache_dir
            )
            # Apply safe model loading to handle meta device tensors
            self.model = safe_model_load(self.model, device="cpu")
            logger.info("Query embedding model loaded")
        except ImportError:
            logger.error(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )
            raise
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise

    def query(
        self, q: str, top_k: int = 5, min_score: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Query the index with a text query and return top-k results.

        Args:
            q: Query text
            top_k: Number of results to return
            min_score: Optional minimum similarity score threshold (lower L2 distance = better)

        Returns:
            List of result dictionaries with fields:
            - text: chunk text
            - file: source file path (if available)
            - start_line: start line number (estimated)
            - end_line: end line number (estimated)
            - score: L2 distance (lower is better)
            - generated_at: timestamp of result generation
        """
        if not self.faiss_index:
            logger.error("No index loaded. Cannot perform query.")
            return []

        if not q or not q.strip():
            logger.warning("Empty query provided")
            return []

        if top_k <= 0:
            logger.warning("top_k must be positive, using default of 5")
            top_k = 5

        # Encode query
        logger.debug(f"Encoding query: {q[:100]}...")
        query_embedding = self.model.encode(
            [q], convert_to_numpy=True, show_progress_bar=False
        )

        # Search index
        logger.debug(f"Searching index for top {top_k} results")
        distances, indices = self.faiss_index.search(
            query_embedding.astype(np.float32), top_k
        )

        # Build results with provenance
        results = []
        timestamp = datetime.utcnow().isoformat() + "Z"

        for i, (idx, distance) in enumerate(zip(indices[0], distances[0])):
            # Skip invalid indices
            if idx < 0 or idx >= len(self.chunks_metadata):
                continue

            # Apply score threshold if specified
            if min_score is not None and distance > min_score:
                continue

            chunk = self.chunks_metadata[idx]

            # Estimate line numbers from character positions
            # This is approximate - actual line numbers would require file re-reading
            start_line = self._estimate_line_number(chunk.get("start", 0))
            end_line = self._estimate_line_number(chunk.get("end", 0))

            result = {
                "text": chunk.get("text", ""),
                "file": self._extract_file_from_metadata(chunk),
                "start_line": start_line,
                "end_line": end_line,
                "score": float(distance),
                "generated_at": timestamp,
                "chunk_id": chunk.get("id", idx),
                "text_hash": chunk.get("text_hash", ""),
            }

            results.append(result)

        logger.info(f"Retrieved {len(results)} results for query")
        return results

    def _estimate_line_number(self, char_pos: int, chars_per_line: int = 80) -> int:
        """
        Estimate line number from character position.

        This is approximate. For exact line numbers, file would need to be re-read.
        Character positions should ideally be stored during chunking for accuracy.

        Args:
            char_pos: Character position in file
            chars_per_line: Estimated average characters per line (default 80)

        Returns:
            Estimated line number (1-indexed)
        
        Note:
            This uses a simple heuristic. For better accuracy:
            - Store actual line numbers during chunking
            - Calculate average line length from source files
            - Re-read files to map positions to lines
        """
        if char_pos <= 0:
            return 1
        return max(1, (char_pos // chars_per_line) + 1)

    def _extract_file_from_metadata(self, chunk: Dict[str, Any]) -> str:
        """
        Extract source file path from chunk or index metadata.

        Args:
            chunk: Chunk metadata dictionary

        Returns:
            File path or "unknown"
        """
        # Check if chunk has direct file reference
        if "file" in chunk:
            return chunk["file"]

        # Try to extract from index metadata
        if "files" in self.index_metadata:
            files = self.index_metadata["files"]
            if files and len(files) > 0:
                # This is a simplification - proper implementation would track
                # which file each chunk came from
                return files[0].get("file", "unknown")

        return "unknown"

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the loaded index.

        Returns:
            Dictionary with index statistics
        """
        return {
            "index_name": self.index_name,
            "tenant_id": self.tenant_id,
            "num_vectors": self.faiss_index.ntotal if self.faiss_index else 0,
            "num_chunks": len(self.chunks_metadata),
            "index_metadata": self.index_metadata,
        }

    def reload(self):
        """Reload the index from disk (useful if index was updated)."""
        logger.info("Reloading index from disk")
        self._load_index()


class MultiIndexRetriever:
    """
    Retriever that can query across multiple indices and merge results.

    Useful for querying across different document collections or tenants.
    """

    def __init__(
        self,
        indices: List[Dict[str, str]],
        index_dir: str = ".codex/tenants",
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        """
        Initialize multi-index retriever.

        Args:
            indices: List of dicts with 'index_name' and 'tenant_id' keys
            index_dir: Base directory for indices
            model_name: Embedding model name
        """
        self.retrievers = []

        for idx_config in indices:
            try:
                retriever = Retriever(
                    index_dir=index_dir,
                    index_name=idx_config["index_name"],
                    tenant_id=idx_config.get("tenant_id", "default"),
                    model_name=model_name,
                )
                self.retrievers.append(retriever)
            except Exception as e:
                logger.warning(
                    f"Failed to load index {idx_config.get('index_name')}: {e}"
                )

        logger.info(f"Initialized with {len(self.retrievers)} indices")

    def query(
        self, q: str, top_k: int = 5, min_score: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Query all indices and merge results by score.

        Args:
            q: Query text
            top_k: Total number of results to return across all indices
            min_score: Optional minimum similarity score threshold

        Returns:
            Merged and sorted list of results from all indices
        """
        all_results = []

        # Query each index
        for retriever in self.retrievers:
            try:
                results = retriever.query(q, top_k=top_k * 2, min_score=min_score)
                # Add index info to results
                for r in results:
                    r["index_name"] = retriever.index_name
                    r["tenant_id"] = retriever.tenant_id
                all_results.extend(results)
            except Exception as e:
                logger.warning(f"Error querying index {retriever.index_name}: {e}")

        # Sort by score (lower is better for L2 distance)
        all_results.sort(key=lambda x: x["score"])

        # Return top_k
        return all_results[:top_k]

    def get_stats(self) -> List[Dict[str, Any]]:
        """Get statistics for all loaded indices."""
        return [r.get_stats() for r in self.retrievers]
