"""
FAISS Vector Store
Local CPU-based FAISS index for vector similarity search
"""

import logging
from pathlib import Path
from typing import Any, Optional

import numpy as np

logger = logging.getLogger(__name__)


class FAISSStore:
    """FAISS-based vector store for local operation"""
    
    def __init__(self, index_dir: Optional[str] = None, index_name: str = "default"):
        self.index_dir = Path(index_dir) if index_dir else Path(".codex/faiss")
        self.index_name = index_name
        self.index = None
        self.documents: list[dict[str, Any]] = []
        self.dimension: Optional[int] = None
        
        try:
            import faiss
            self.faiss = faiss
        except ImportError:
            logger.error("faiss-cpu not installed. Install with: pip install faiss-cpu")
            raise
    
    def create_index(self, embeddings: np.ndarray, documents: list[dict[str, Any]]):
        """Create a new FAISS index
        
        Args:
            embeddings: Embedding vectors (shape: [n_docs, dim])
            documents: List of document dictionaries
        """
        if len(embeddings) != len(documents):
            raise ValueError("Number of embeddings must match number of documents")
        
        self.dimension = embeddings.shape[1]
        self.documents = documents
        
        # Create index (L2 distance)
        logger.info(f"Creating FAISS index with dimension: {self.dimension}")
        self.index = self.faiss.IndexFlatL2(self.dimension)
        
        # Add vectors
        self.index.add(embeddings.astype(np.float32))
        
        logger.info(f"Added {self.index.ntotal} vectors to index")
    
    def save(self):
        """Save index and documents to disk"""
        if not self.index:
            raise RuntimeError("No index to save")
        
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        index_path = self.index_dir / f"{self.index_name}.index"
        self.faiss.write_index(self.index, str(index_path))
        logger.info(f"Saved FAISS index to {index_path}")
        
        # Save documents
        import json
        docs_path = self.index_dir / f"{self.index_name}.docs.jsonl"
        with open(docs_path, "w", encoding="utf-8") as f:
            for doc in self.documents:
                f.write(json.dumps(doc) + "\n")
        logger.info(f"Saved {len(self.documents)} documents to {docs_path}")
        
        # Save metadata
        metadata = {
            "index_name": self.index_name,
            "dimension": self.dimension,
            "num_vectors": self.index.ntotal if self.index else 0,
        }
        meta_path = self.index_dir / f"{self.index_name}.meta.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Saved metadata to {meta_path}")
    
    def load(self):
        """Load index and documents from disk"""
        index_path = self.index_dir / f"{self.index_name}.index"
        docs_path = self.index_dir / f"{self.index_name}.docs.jsonl"
        
        if not index_path.exists():
            raise FileNotFoundError(f"Index not found: {index_path}")
        
        # Load FAISS index
        self.index = self.faiss.read_index(str(index_path))
        self.dimension = self.index.d
        logger.info(f"Loaded FAISS index from {index_path}")
        
        # Load documents
        if docs_path.exists():
            import json
            self.documents = []
            with open(docs_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self.documents.append(json.loads(line))
            logger.info(f"Loaded {len(self.documents)} documents from {docs_path}")
        else:
            logger.warning(f"Documents file not found: {docs_path}")
            self.documents = []
    
    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Search for similar vectors
        
        Args:
            query_vector: Query embedding vector (shape: [dim] or [1, dim])
            top_k: Number of results to return
        
        Returns:
            List of results with document, score, and index
        """
        if not self.index:
            raise RuntimeError("Index not loaded")
        
        # Reshape query if needed
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)
        
        # Search
        distances, indices = self.index.search(
            query_vector.astype(np.float32),
            min(top_k, self.index.ntotal)
        )
        
        # Build results
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < 0 or idx >= len(self.documents):
                continue
            
            # Convert L2 distance to similarity score (inverse)
            # Normalize to [0, 1] range (approximate)
            score = 1.0 / (1.0 + float(dist))
            
            results.append({
                "document": self.documents[idx],
                "score": score,
                "index": int(idx),
                "distance": float(dist),
            })
        
        logger.debug(f"Found {len(results)} results for query")
        return results
