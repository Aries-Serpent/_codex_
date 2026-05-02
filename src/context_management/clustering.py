"""
Semantic Clusterer

Embeddings-based clustering for semantic grouping of statements
using cosine similarity with configurable thresholds.
"""

import hashlib
import math
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Optional


@dataclass
class ClusterMember:
    """A member of a semantic cluster."""

    text: str
    embedding: Optional[list[float]] = None
    similarity_to_centroid: float = 1.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    source: str = ""


@dataclass
class SemanticCluster:
    """A cluster of semantically similar statements."""

    cluster_id: str
    centroid_text: str
    centroid_embedding: Optional[list[float]] = None
    members: list[ClusterMember] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    confidence_score: float = 1.0

    @property
    def size(self) -> int:
        """Number of members in cluster."""
        return len(self.members)

    @property
    def average_similarity(self) -> float:
        """Average similarity of members to centroid."""
        if not self.members:
            return 0.0
        return sum(m.similarity_to_centroid for m in self.members) / len(self.members)


class SemanticClusterer:
    """
    Cluster statements based on semantic similarity.

    Uses embeddings when available, falls back to token-based
    similarity for lightweight operation.
    """

    DEFAULT_THRESHOLD = 0.85

    def __init__(
        self,
        similarity_threshold: float = DEFAULT_THRESHOLD,
        min_cluster_size: int = 2,
        max_clusters: int = 1000,
        use_embeddings: bool = False,
    ):
        """
        Initialize clusterer.

        Args:
            similarity_threshold: Minimum cosine similarity (0.0-1.0) to cluster together
            min_cluster_size: Minimum members for a valid cluster
            max_clusters: Maximum clusters to maintain
            use_embeddings: Whether to use ML embeddings (requires external model)
        """
        self.similarity_threshold = similarity_threshold
        self.min_cluster_size = min_cluster_size
        self.max_clusters = max_clusters
        self.use_embeddings = use_embeddings

        self._clusters: dict[str, SemanticCluster] = {}
        self._text_to_cluster: dict[str, str] = {}  # text_hash -> cluster_id

    def add_statement(
        self, text: str, embedding: Optional[list[float]] = None, source: str = ""
    ) -> tuple[str, bool]:
        """
        Add statement to appropriate cluster or create new cluster.

        Args:
            text: Statement text
            embedding: Pre-computed embedding vector (optional)
            source: Source identifier

        Returns:
            tuple of (cluster_id, is_new_cluster)
        """
        text_hash = self._hash_text(text)

        # Check if already clustered
        if text_hash in self._text_to_cluster:
            return self._text_to_cluster[text_hash], False

        # Find best matching cluster
        best_cluster_id = None
        best_similarity = 0.0

        for cluster_id, cluster in self._clusters.items():
            similarity = self._compute_similarity(
                text, cluster.centroid_text, embedding, cluster.centroid_embedding
            )
            if similarity >= self.similarity_threshold and similarity > best_similarity:
                best_similarity = similarity
                best_cluster_id = cluster_id

        if best_cluster_id:
            # Add to existing cluster
            cluster = self._clusters[best_cluster_id]
            member = ClusterMember(
                text=text,
                embedding=embedding,
                similarity_to_centroid=best_similarity,
                source=source,
            )
            cluster.members.append(member)
            cluster.confidence_score = cluster.average_similarity
            self._text_to_cluster[text_hash] = best_cluster_id
            return best_cluster_id, False
        # Create new cluster
        cluster_id = self._generate_cluster_id(text)
        member = ClusterMember(text=text, embedding=embedding, source=source)
        cluster = SemanticCluster(
            cluster_id=cluster_id,
            centroid_text=text,
            centroid_embedding=embedding,
            members=[member],
        )
        self._clusters[cluster_id] = cluster
        self._text_to_cluster[text_hash] = cluster_id

        # Cleanup if over limit
        if len(self._clusters) > self.max_clusters:
            self._prune_smallest_clusters()

        return cluster_id, True

    def get_cluster(self, cluster_id: str) -> Optional[SemanticCluster]:
        """Get cluster by ID."""
        return self._clusters.get(cluster_id)

    def get_cluster_for_text(self, text: str) -> Optional[SemanticCluster]:
        """Get the cluster containing given text."""
        text_hash = self._hash_text(text)
        cluster_id = self._text_to_cluster.get(text_hash)
        if cluster_id:
            return self._clusters.get(cluster_id)
        return None

    def get_representative_statements(self, max_per_cluster: int = 1) -> list[str]:
        """
        Get representative statements from each cluster.

        Args:
            max_per_cluster: Maximum representatives per cluster

        Returns:
            list of representative statement texts
        """
        representatives = []
        for cluster in self._clusters.values():
            if cluster.size < self.min_cluster_size:
                continue
            # Get highest similarity members as representatives
            sorted_members = sorted(
                cluster.members, key=lambda m: m.similarity_to_centroid, reverse=True
            )
            for member in sorted_members[:max_per_cluster]:
                representatives.append(member.text)
        return representatives

    def cluster_statements(self, statements: list[str]) -> dict[str, list[str]]:
        """
        Cluster a list of statements.

        Args:
            statements: list of statement texts

        Returns:
            dict mapping cluster_id to list of statement texts
        """
        for stmt in statements:
            self.add_statement(stmt)

        result = {}
        for cluster_id, cluster in self._clusters.items():
            result[cluster_id] = [m.text for m in cluster.members]
        return result

    def get_cluster_summary(self) -> dict:
        """Get summary statistics of all clusters."""
        return {
            "total_clusters": len(self._clusters),
            "total_statements": sum(c.size for c in self._clusters.values()),
            "average_cluster_size": (
                sum(c.size for c in self._clusters.values()) / len(self._clusters)
                if self._clusters
                else 0
            ),
            "average_confidence": (
                sum(c.confidence_score for c in self._clusters.values()) / len(self._clusters)
                if self._clusters
                else 0
            ),
            "clusters": [
                {
                    "id": c.cluster_id,
                    "size": c.size,
                    "confidence": c.confidence_score,
                    "centroid_preview": c.centroid_text[:100],
                }
                for c in self._clusters.values()
            ],
        }

    def clear(self):
        """Clear all clusters."""
        self._clusters.clear()
        self._text_to_cluster.clear()

    def _compute_similarity(
        self,
        text1: str,
        text2: str,
        embedding1: Optional[list[float]] = None,
        embedding2: Optional[list[float]] = None,
    ) -> float:
        """
        Compute similarity between two texts.

        Uses embeddings if available, otherwise falls back to token overlap.
        """
        if embedding1 and embedding2:
            return self._cosine_similarity(embedding1, embedding2)
        return self._token_similarity(text1, text2)

    def _cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2, strict=False))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def _token_similarity(self, text1: str, text2: str) -> float:
        """Compute token-based Jaccard similarity."""
        tokens1 = set(text1.lower().split())
        tokens2 = set(text2.lower().split())

        if not tokens1 or not tokens2:
            return 0.0

        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)

        return intersection / union if union > 0 else 0.0

    def _hash_text(self, text: str) -> str:
        """Generate hash for text."""
        return hashlib.sha256(text.encode()).hexdigest()[:16]

    def _generate_cluster_id(self, text: str) -> str:
        """Generate unique cluster ID."""
        timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S%f")
        text_hash = self._hash_text(text)[:8]
        return f"cluster_{timestamp}_{text_hash}"

    def _prune_smallest_clusters(self):
        """Remove smallest clusters when over limit."""
        if len(self._clusters) <= self.max_clusters:
            return

        # Sort by size (ascending) then confidence (ascending)
        sorted_clusters = sorted(
            self._clusters.items(), key=lambda x: (x[1].size, x[1].confidence_score)
        )

        # Remove bottom 10%
        remove_count = max(1, len(sorted_clusters) // 10)
        for cluster_id, cluster in sorted_clusters[:remove_count]:
            # Remove text mappings
            for member in cluster.members:
                text_hash = self._hash_text(member.text)
                self._text_to_cluster.pop(text_hash, None)
            # Remove cluster
            del self._clusters[cluster_id]
