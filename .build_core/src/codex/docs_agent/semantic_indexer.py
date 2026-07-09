"""
Semantic Indexer Module for Docs Agent

Builds semantic search indexes using embeddings and FAISS for fast,
similarity-based document retrieval.

Authority: Lane 3 Unified Documentation Agent
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)

try:
    import faiss
except ImportError:
    logger.warning("FAISS not installed. Install with: pip install faiss-cpu or faiss-gpu")
    faiss = None

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    logger.warning(
        "sentence-transformers not installed. Install with: pip install sentence-transformers"
    )
    SentenceTransformer = None


@dataclass
class SearchResult:
    """Result from semantic search"""

    record_id: str
    record_type: str
    title: str
    content: str
    score: float
    metadata: Dict[str, Any]


class SemanticIndexer:
    """Builds and manages semantic search indexes"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize semantic indexer

        Args:
            model_name: HuggingFace model name for embeddings
        """
        self.model_name = model_name
        self.model = None
        self.embedding_dim = 384  # Default for all-MiniLM-L6-v2

        self.index = None
        self.records: dict[str, Any] = {}  # id -> record
        self.id_to_index: dict[str, Any] = {}  # record_id -> faiss_index
        self.embeddings = None  # numpy array of embeddings

        self._load_model()

    def _load_model(self):
        """Load embedding model"""
        if SentenceTransformer is None:
            logger.warning("sentence-transformers not available, using dummy embeddings")
            return

        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"Model loaded (embedding dimension: {self.embedding_dim})")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.model = None

    def add_record(self, record: Dict[str, Any]) -> bool:
        """Add a record to the index

        Args:
            record: Record dictionary

        Returns:
            True if added successfully
        """
        record_id = record.get("id")
        if not record_id:
            logger.warning("Record missing id field")
            return False

        self.records[record_id] = record
        return True

    def build_index(self, batch_size: int = 32) -> Dict[str, Any]:
        """Build FAISS index from records

        Args:
            batch_size: Batch size for embedding computation

        Returns:
            Dictionary with index statistics
        """
        if not self.records:
            logger.warning("No records to index")
            return {"record_count": 0, "indexed": 0}

        logger.info(f"Building index for {len(self.records)} records")

        # Extract indexable content
        records_list = []
        record_ids = []
        texts_to_embed = []

        for record_id, record in self.records.items():
            # Build searchable text from record
            content_parts = []

            if record.get("type") == "document":
                content_parts.append(record.get("title", ""))
                metadata = record.get("metadata", {})
                if isinstance(metadata, dict):
                    for v in metadata.values():
                        if isinstance(v, str):
                            content_parts.append(v)

            elif record.get("type") == "section":
                content_parts.append(record.get("title", ""))
                content_parts.append(record.get("content", "")[:500])  # First 500 chars

            elif record.get("type") == "block":
                content_parts.append(record.get("content_type", ""))
                content_parts.append(record.get("content", "")[:500])
                if record.get("language"):
                    content_parts.append(f"Language: {record['language']}")

            elif record.get("type") == "action":
                content_parts.append(record.get("description", ""))
                content_parts.append(f"Priority: {record.get('priority', '')}")

            elif record.get("type") == "requirement":
                content_parts.append(record.get("description", ""))
                content_parts.append(f"Category: {record.get('category', '')}")

            text = " ".join(str(p) for p in content_parts if p)
            if text:
                texts_to_embed.append(text)
                records_list.append(record)
                record_ids.append(record_id)

        if not texts_to_embed:
            logger.warning("No indexable content found")
            return {"record_count": 0, "indexed": 0}

        # Generate embeddings
        logger.info(f"Generating embeddings for {len(texts_to_embed)} records")
        embeddings = self._embed_texts(texts_to_embed, batch_size)

        if embeddings is None:
            logger.error("Failed to generate embeddings")
            return {"record_count": len(self.records), "indexed": 0}

        # Create FAISS index
        logger.info(f"Creating FAISS index (dimension: {embeddings.shape[1]})")
        self.index = faiss.IndexFlatL2(embeddings.shape[1]) if faiss else None

        if self.index:
            self.index.add(embeddings.astype(np.float32))
            self.embeddings = embeddings

            for i, record_id in enumerate(record_ids):
                self.id_to_index[record_id] = i

            indexed_count = len(record_ids)
            logger.info(f"Index created with {indexed_count} records")
            return {
                "record_count": len(self.records),
                "indexed": indexed_count,
                "embedding_dim": embeddings.shape[1],
            }

        return {"record_count": len(self.records), "indexed": 0}

    def _embed_texts(self, texts: List[str], batch_size: int = 32) -> Optional[np.ndarray]:
        """Generate embeddings for texts

        Args:
            texts: List of texts to embed
            batch_size: Batch size

        Returns:
            Numpy array of embeddings
        """
        if self.model is None:
            # Return dummy embeddings if model not available
            logger.debug("Using dummy embeddings (model not available)")
            return np.random.randn(len(texts), self.embedding_dim).astype(np.float32)

        try:
            embeddings = self.model.encode(
                texts, batch_size=batch_size, show_progress_bar=True, convert_to_numpy=True
            )
            return embeddings.astype(np.float32)
        except Exception as e:
            logger.error(f"Failed to embed texts: {e}")
            return None

    def search(self, query: str, k: int = 10, threshold: float = 0.0) -> List[SearchResult]:
        """Search for similar records

        Args:
            query: Search query text
            k: Number of results to return
            threshold: Minimum similarity score threshold

        Returns:
            List of search results
        """
        if self.index is None:
            logger.warning("Index not built yet")
            return []

        # Embed query
        query_embedding = self._embed_texts([query], batch_size=1)
        if query_embedding is None:
            return []

        # Search index
        distances, indices = self.index.search(query_embedding.astype(np.float32), k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:  # Invalid result
                continue

            # Find record with this index
            record_id = None
            for rid, ridx in self.id_to_index.items():
                if ridx == idx:
                    record_id = rid
                    break

            if record_id is None:
                continue

            record = self.records[record_id]

            # Convert distance to similarity (L2 distance)
            similarity = 1.0 / (1.0 + dist)

            if similarity < threshold:
                continue

            result = SearchResult(
                record_id=record_id,
                record_type=record.get("type", "unknown"),
                title=record.get("title", record.get("description", "")),
                content=record.get("content", "")[:200],
                score=float(similarity),
                metadata={
                    "distance": float(dist),
                    "created_at": record.get("created_at"),
                },
            )
            results.append(result)

        return results

    def save_index(self, output_path: Path):
        """Save index to disk

        Args:
            output_path: Path to save index
        """
        if self.index is None:
            logger.warning("No index to save")
            return

        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save FAISS index
        index_file = output_path.with_suffix(".index")
        if faiss:
            faiss.write_index(self.index, str(index_file))
            logger.info(f"Saved FAISS index to {index_file}")

        # Save metadata
        metadata = {
            "model_name": self.model_name,
            "embedding_dim": self.embedding_dim,
            "record_count": len(self.records),
            "indexed_count": len(self.id_to_index),
        }

        metadata_file = output_path.with_suffix(".json")
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Saved metadata to {metadata_file}")

    def load_index(self, input_path: Path) -> bool:
        """Load index from disk

        Args:
            input_path: Path to load index from

        Returns:
            True if loaded successfully
        """
        index_file = input_path.with_suffix(".index")
        metadata_file = input_path.with_suffix(".json")

        if not index_file.exists() or not metadata_file.exists():
            logger.error("Index files not found")
            return False

        try:
            # Load metadata
            with open(metadata_file, "r") as f:
                metadata = json.load(f)

            self.model_name = metadata["model_name"]
            self.embedding_dim = metadata["embedding_dim"]

            # Load FAISS index
            if faiss:
                self.index = faiss.read_index(str(index_file))
                logger.info(f"Loaded FAISS index from {index_file}")

            return True
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get indexing statistics

        Returns:
            Dictionary with statistics
        """
        return {
            "model_name": self.model_name,
            "embedding_dim": self.embedding_dim,
            "total_records": len(self.records),
            "indexed_records": len(self.id_to_index),
            "index_built": self.index is not None,
        }
