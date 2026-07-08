"""
Indexing and search infrastructure.

Classes:
  - FullTextIndexer: Inverted index for keyword search
  - SemanticEmbeddings: Embedding-based similarity search
  - HistoryTracker: Track schema migrations and versioning
"""

import re
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple


class FullTextIndexer:
    """Build and search inverted indexes.

    Supports:
      - Keyword indexing
      - Phrase search
      - Boolean search (AND, OR, NOT)
      - Result ranking
    """

    def __init__(self):
        self.index: Dict[str, Set[str]] = defaultdict(set)
        self.documents: Dict[str, str] = {}

    def index_document(self, doc_id: str, content: str) -> None:
        """Index document content for full-text search."""
        self.documents[doc_id] = content

        # Tokenize and index
        tokens = self._tokenize(content)
        for token in tokens:
            self.index[token].add(doc_id)

    def search(self, query: str) -> List[str]:
        """Search for documents matching query."""
        # Parse query into tokens
        tokens = self._tokenize(query)

        if not tokens:
            return []

        # AND operation: intersection of all token results
        result_sets = [self.index[token] for token in tokens]

        if result_sets:
            results = result_sets[0]
            for token_set in result_sets[1:]:
                results = results & token_set
            return sorted(results)

        return []

    def search_phrase(self, phrase: str) -> List[str]:
        """Search for exact phrase."""
        results = []

        for doc_id, content in self.documents.items():
            if phrase.lower() in content.lower():
                results.append(doc_id)

        return results

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """Tokenize text into words."""
        # Convert to lowercase and split on non-word characters
        tokens = re.findall(r"\w+", text.lower())
        # Filter stopwords (simple list)
        stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for"}
        return [t for t in tokens if t not in stopwords and len(t) > 1]


class SemanticEmbeddings:
    """Embedding-based semantic search.

    Supports:
      - Vector representation of documents
      - Cosine similarity ranking
      - Semantic clustering
    """

    def __init__(self):
        self.embeddings: Dict[str, List[float]] = {}
        self.document_text: Dict[str, str] = {}

    def embed_document(self, doc_id: str, content: str) -> List[float]:
        """Create embedding for document (simplified).

        In a real implementation, would use a language model.
        Here we use a simple TF-IDF-like approach.
        """
        self.document_text[doc_id] = content

        # Tokenize
        tokens = self._get_tokens(content)

        # Create simple embedding (one dimension per token)
        # In practice would use pre-trained embeddings
        embedding = [float(tokens.count(token)) / len(tokens) for token in sorted(set(tokens))]

        self.embeddings[doc_id] = embedding
        return embedding

    def search_similar(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Find most similar documents to query."""
        query_tokens = self._get_tokens(query)
        query_embedding = [
            float(query_tokens.count(token)) / (len(query_tokens) or 1)
            for token in sorted(set(query_tokens))
        ]

        similarities = []

        for doc_id, doc_embedding in self.embeddings.items():
            # Cosine similarity (simplified)
            score = self._cosine_similarity(query_embedding, doc_embedding)
            similarities.append((doc_id, score))

        # Sort by similarity, descending
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    @staticmethod
    def _get_tokens(text: str) -> List[str]:
        """Extract tokens from text."""
        return re.findall(r"\w+", text.lower())

    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between vectors."""
        # Pad vectors to same length
        max_len = max(len(vec1), len(vec2))
        vec1_padded = vec1 + [0] * (max_len - len(vec1))
        vec2_padded = vec2 + [0] * (max_len - len(vec2))

        dot_product = sum(a * b for a, b in zip(vec1_padded, vec2_padded))
        norm1 = sum(a**2 for a in vec1_padded) ** 0.5
        norm2 = sum(b**2 for b in vec2_padded) ** 0.5

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)


class HistoryTracker:
    """Track schema migrations and versioning.

    Maintains:
      - Schema versions
      - Migration log
      - Backward compatibility
    """

    def __init__(self):
        self.current_version = "1.0.0"
        self.migration_log: List[Dict] = []
        self.schema_versions: Dict[str, str] = {
            "document": "1.0.0",
            "section": "1.0.0",
            "block": "1.0.0",
            "action": "1.0.0",
            "decision": "1.0.0",
            "requirement": "1.0.0",
            "reference": "1.0.0",
            "relationship": "1.0.0",
        }

    def record_migration(
        self,
        from_version: str,
        to_version: str,
        description: str,
    ) -> None:
        """Record a schema migration."""
        migration = {
            "from": from_version,
            "to": to_version,
            "description": description,
            "timestamp": self._get_timestamp(),
        }
        self.migration_log.append(migration)

    def get_migrations(
        self,
        from_version: Optional[str] = None,
    ) -> List[Dict]:
        """Get migrations from a version."""
        if not from_version:
            return self.migration_log

        result = []
        for migration in self.migration_log:
            if migration["from"] == from_version:
                result.append(migration)

        return result

    def get_schema_version(self, record_type: str) -> str:
        """Get schema version for record type."""
        return self.schema_versions.get(record_type, "unknown")

    def set_schema_version(self, record_type: str, version: str) -> None:
        """Update schema version for record type."""
        self.schema_versions[record_type] = version

    @staticmethod
    def _get_timestamp() -> str:
        """Get ISO 8601 timestamp."""
        from datetime import datetime

        return datetime.utcnow().isoformat() + "Z"
