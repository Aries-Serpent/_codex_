"""
Semantic Clusterer

Embeddings-based clustering for semantic grouping of statements
using cosine similarity with configurable thresholds.
"""

import hashlib
import math
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


@dataclass
class ClusterMember:
    """A member of a semantic cluster."""

    text: str
    embedding: Optional[list[float]] = None
    similarity_to_centroid: float = 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""


@dataclass
class SemanticCluster:
    """A cluster of semantically similar statements."""

    cluster_id: str
    centroid_text: str
    centroid_embedding: Optional[list[float]] = None
    members: list[ClusterMember] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
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

    def xǁSemanticClustererǁ__init____mutmut_orig(
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

    def xǁSemanticClustererǁ__init____mutmut_1(
        self,
        similarity_threshold: float = DEFAULT_THRESHOLD,
        min_cluster_size: int = 3,
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

    def xǁSemanticClustererǁ__init____mutmut_2(
        self,
        similarity_threshold: float = DEFAULT_THRESHOLD,
        min_cluster_size: int = 2,
        max_clusters: int = 1001,
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

    def xǁSemanticClustererǁ__init____mutmut_3(
        self,
        similarity_threshold: float = DEFAULT_THRESHOLD,
        min_cluster_size: int = 2,
        max_clusters: int = 1000,
        use_embeddings: bool = True,
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

    def xǁSemanticClustererǁ__init____mutmut_4(
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
        self.similarity_threshold = None
        self.min_cluster_size = min_cluster_size
        self.max_clusters = max_clusters
        self.use_embeddings = use_embeddings

        self._clusters: dict[str, SemanticCluster] = {}
        self._text_to_cluster: dict[str, str] = {}  # text_hash -> cluster_id

    def xǁSemanticClustererǁ__init____mutmut_5(
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
        self.min_cluster_size = None
        self.max_clusters = max_clusters
        self.use_embeddings = use_embeddings

        self._clusters: dict[str, SemanticCluster] = {}
        self._text_to_cluster: dict[str, str] = {}  # text_hash -> cluster_id

    def xǁSemanticClustererǁ__init____mutmut_6(
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
        self.max_clusters = None
        self.use_embeddings = use_embeddings

        self._clusters: dict[str, SemanticCluster] = {}
        self._text_to_cluster: dict[str, str] = {}  # text_hash -> cluster_id

    def xǁSemanticClustererǁ__init____mutmut_7(
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
        self.use_embeddings = None

        self._clusters: dict[str, SemanticCluster] = {}
        self._text_to_cluster: dict[str, str] = {}  # text_hash -> cluster_id

    def xǁSemanticClustererǁ__init____mutmut_8(
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

        self._clusters: dict[str, SemanticCluster] = None
        self._text_to_cluster: dict[str, str] = {}  # text_hash -> cluster_id

    def xǁSemanticClustererǁ__init____mutmut_9(
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
        self._text_to_cluster: dict[str, str] = None  # text_hash -> cluster_id
    
    xǁSemanticClustererǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSemanticClustererǁ__init____mutmut_1': xǁSemanticClustererǁ__init____mutmut_1, 
        'xǁSemanticClustererǁ__init____mutmut_2': xǁSemanticClustererǁ__init____mutmut_2, 
        'xǁSemanticClustererǁ__init____mutmut_3': xǁSemanticClustererǁ__init____mutmut_3, 
        'xǁSemanticClustererǁ__init____mutmut_4': xǁSemanticClustererǁ__init____mutmut_4, 
        'xǁSemanticClustererǁ__init____mutmut_5': xǁSemanticClustererǁ__init____mutmut_5, 
        'xǁSemanticClustererǁ__init____mutmut_6': xǁSemanticClustererǁ__init____mutmut_6, 
        'xǁSemanticClustererǁ__init____mutmut_7': xǁSemanticClustererǁ__init____mutmut_7, 
        'xǁSemanticClustererǁ__init____mutmut_8': xǁSemanticClustererǁ__init____mutmut_8, 
        'xǁSemanticClustererǁ__init____mutmut_9': xǁSemanticClustererǁ__init____mutmut_9
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSemanticClustererǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁSemanticClustererǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁSemanticClustererǁ__init____mutmut_orig)
    xǁSemanticClustererǁ__init____mutmut_orig.__name__ = 'xǁSemanticClustererǁ__init__'

    def xǁSemanticClustererǁadd_statement__mutmut_orig(
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
        else:
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

    def xǁSemanticClustererǁadd_statement__mutmut_1(
        self, text: str, embedding: Optional[list[float]] = None, source: str = "XXXX"
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
        else:
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

    def xǁSemanticClustererǁadd_statement__mutmut_2(
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
        text_hash = None

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
        else:
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

    def xǁSemanticClustererǁadd_statement__mutmut_3(
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
        text_hash = self._hash_text(None)

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
        else:
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

    def xǁSemanticClustererǁadd_statement__mutmut_4(
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
        if text_hash not in self._text_to_cluster:
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
        else:
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

    def xǁSemanticClustererǁadd_statement__mutmut_5(
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
            return self._text_to_cluster[text_hash], True

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
        else:
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

    def xǁSemanticClustererǁadd_statement__mutmut_6(
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
        best_cluster_id = ""
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
        else:
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

    def xǁSemanticClustererǁadd_statement__mutmut_7(
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
        best_similarity = None

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
        else:
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

    def xǁSemanticClustererǁadd_statement__mutmut_8(
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
        best_similarity = 1.0

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
        else:
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

    def xǁSemanticClustererǁadd_statement__mutmut_9(
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
            similarity = None
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
        else:
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

    def xǁSemanticClustererǁadd_statement__mutmut_10(
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
                None, cluster.centroid_text, embedding, cluster.centroid_embedding
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
        else:
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

    def xǁSemanticClustererǁadd_statement__mutmut_11(
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
                text, None, embedding, cluster.centroid_embedding
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
        else:
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

    def xǁSemanticClustererǁadd_statement__mutmut_12(
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
                text, cluster.centroid_text, None, cluster.centroid_embedding
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
        else:
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

    def xǁSemanticClustererǁadd_statement__mutmut_13(
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
                text, cluster.centroid_text, embedding, None
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
        else:
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

    def xǁSemanticClustererǁadd_statement__mutmut_14(
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
                cluster.centroid_text, embedding, cluster.centroid_embedding
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
        else:
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

    def xǁSemanticClustererǁadd_statement__mutmut_15(
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
                text, embedding, cluster.centroid_embedding
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
        else:
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

    def xǁSemanticClustererǁadd_statement__mutmut_16(
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
                text, cluster.centroid_text, cluster.centroid_embedding
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
        else:
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

    def xǁSemanticClustererǁadd_statement__mutmut_17(
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
                text, cluster.centroid_text, embedding, )
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
        else:
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

    def xǁSemanticClustererǁadd_statement__mutmut_18(
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
            if similarity >= self.similarity_threshold or similarity > best_similarity:
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
        else:
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

    def xǁSemanticClustererǁadd_statement__mutmut_19(
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
            if similarity > self.similarity_threshold and similarity > best_similarity:
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
        else:
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

    def xǁSemanticClustererǁadd_statement__mutmut_20(
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
            if similarity >= self.similarity_threshold and similarity >= best_similarity:
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
        else:
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

    def xǁSemanticClustererǁadd_statement__mutmut_21(
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
                best_similarity = None
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
        else:
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

    def xǁSemanticClustererǁadd_statement__mutmut_22(
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
                best_cluster_id = None

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
        else:
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

    def xǁSemanticClustererǁadd_statement__mutmut_23(
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
            cluster = None
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
        else:
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

    def xǁSemanticClustererǁadd_statement__mutmut_24(
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
            member = None
            cluster.members.append(member)
            cluster.confidence_score = cluster.average_similarity
            self._text_to_cluster[text_hash] = best_cluster_id
            return best_cluster_id, False
        else:
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

    def xǁSemanticClustererǁadd_statement__mutmut_25(
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
                text=None,
                embedding=embedding,
                similarity_to_centroid=best_similarity,
                source=source,
            )
            cluster.members.append(member)
            cluster.confidence_score = cluster.average_similarity
            self._text_to_cluster[text_hash] = best_cluster_id
            return best_cluster_id, False
        else:
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

    def xǁSemanticClustererǁadd_statement__mutmut_26(
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
                embedding=None,
                similarity_to_centroid=best_similarity,
                source=source,
            )
            cluster.members.append(member)
            cluster.confidence_score = cluster.average_similarity
            self._text_to_cluster[text_hash] = best_cluster_id
            return best_cluster_id, False
        else:
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

    def xǁSemanticClustererǁadd_statement__mutmut_27(
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
                similarity_to_centroid=None,
                source=source,
            )
            cluster.members.append(member)
            cluster.confidence_score = cluster.average_similarity
            self._text_to_cluster[text_hash] = best_cluster_id
            return best_cluster_id, False
        else:
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

    def xǁSemanticClustererǁadd_statement__mutmut_28(
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
                source=None,
            )
            cluster.members.append(member)
            cluster.confidence_score = cluster.average_similarity
            self._text_to_cluster[text_hash] = best_cluster_id
            return best_cluster_id, False
        else:
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

    def xǁSemanticClustererǁadd_statement__mutmut_29(
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
                embedding=embedding,
                similarity_to_centroid=best_similarity,
                source=source,
            )
            cluster.members.append(member)
            cluster.confidence_score = cluster.average_similarity
            self._text_to_cluster[text_hash] = best_cluster_id
            return best_cluster_id, False
        else:
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

    def xǁSemanticClustererǁadd_statement__mutmut_30(
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
                similarity_to_centroid=best_similarity,
                source=source,
            )
            cluster.members.append(member)
            cluster.confidence_score = cluster.average_similarity
            self._text_to_cluster[text_hash] = best_cluster_id
            return best_cluster_id, False
        else:
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

    def xǁSemanticClustererǁadd_statement__mutmut_31(
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
                source=source,
            )
            cluster.members.append(member)
            cluster.confidence_score = cluster.average_similarity
            self._text_to_cluster[text_hash] = best_cluster_id
            return best_cluster_id, False
        else:
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

    def xǁSemanticClustererǁadd_statement__mutmut_32(
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
                )
            cluster.members.append(member)
            cluster.confidence_score = cluster.average_similarity
            self._text_to_cluster[text_hash] = best_cluster_id
            return best_cluster_id, False
        else:
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

    def xǁSemanticClustererǁadd_statement__mutmut_33(
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
            cluster.members.append(None)
            cluster.confidence_score = cluster.average_similarity
            self._text_to_cluster[text_hash] = best_cluster_id
            return best_cluster_id, False
        else:
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

    def xǁSemanticClustererǁadd_statement__mutmut_34(
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
            cluster.confidence_score = None
            self._text_to_cluster[text_hash] = best_cluster_id
            return best_cluster_id, False
        else:
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

    def xǁSemanticClustererǁadd_statement__mutmut_35(
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
            self._text_to_cluster[text_hash] = None
            return best_cluster_id, False
        else:
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

    def xǁSemanticClustererǁadd_statement__mutmut_36(
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
            return best_cluster_id, True
        else:
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

    def xǁSemanticClustererǁadd_statement__mutmut_37(
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
        else:
            # Create new cluster
            cluster_id = None
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

    def xǁSemanticClustererǁadd_statement__mutmut_38(
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
        else:
            # Create new cluster
            cluster_id = self._generate_cluster_id(None)
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

    def xǁSemanticClustererǁadd_statement__mutmut_39(
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
        else:
            # Create new cluster
            cluster_id = self._generate_cluster_id(text)
            member = None
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

    def xǁSemanticClustererǁadd_statement__mutmut_40(
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
        else:
            # Create new cluster
            cluster_id = self._generate_cluster_id(text)
            member = ClusterMember(text=None, embedding=embedding, source=source)
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

    def xǁSemanticClustererǁadd_statement__mutmut_41(
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
        else:
            # Create new cluster
            cluster_id = self._generate_cluster_id(text)
            member = ClusterMember(text=text, embedding=None, source=source)
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

    def xǁSemanticClustererǁadd_statement__mutmut_42(
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
        else:
            # Create new cluster
            cluster_id = self._generate_cluster_id(text)
            member = ClusterMember(text=text, embedding=embedding, source=None)
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

    def xǁSemanticClustererǁadd_statement__mutmut_43(
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
        else:
            # Create new cluster
            cluster_id = self._generate_cluster_id(text)
            member = ClusterMember(embedding=embedding, source=source)
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

    def xǁSemanticClustererǁadd_statement__mutmut_44(
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
        else:
            # Create new cluster
            cluster_id = self._generate_cluster_id(text)
            member = ClusterMember(text=text, source=source)
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

    def xǁSemanticClustererǁadd_statement__mutmut_45(
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
        else:
            # Create new cluster
            cluster_id = self._generate_cluster_id(text)
            member = ClusterMember(text=text, embedding=embedding, )
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

    def xǁSemanticClustererǁadd_statement__mutmut_46(
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
        else:
            # Create new cluster
            cluster_id = self._generate_cluster_id(text)
            member = ClusterMember(text=text, embedding=embedding, source=source)
            cluster = None
            self._clusters[cluster_id] = cluster
            self._text_to_cluster[text_hash] = cluster_id

            # Cleanup if over limit
            if len(self._clusters) > self.max_clusters:
                self._prune_smallest_clusters()

            return cluster_id, True

    def xǁSemanticClustererǁadd_statement__mutmut_47(
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
        else:
            # Create new cluster
            cluster_id = self._generate_cluster_id(text)
            member = ClusterMember(text=text, embedding=embedding, source=source)
            cluster = SemanticCluster(
                cluster_id=None,
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

    def xǁSemanticClustererǁadd_statement__mutmut_48(
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
        else:
            # Create new cluster
            cluster_id = self._generate_cluster_id(text)
            member = ClusterMember(text=text, embedding=embedding, source=source)
            cluster = SemanticCluster(
                cluster_id=cluster_id,
                centroid_text=None,
                centroid_embedding=embedding,
                members=[member],
            )
            self._clusters[cluster_id] = cluster
            self._text_to_cluster[text_hash] = cluster_id

            # Cleanup if over limit
            if len(self._clusters) > self.max_clusters:
                self._prune_smallest_clusters()

            return cluster_id, True

    def xǁSemanticClustererǁadd_statement__mutmut_49(
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
        else:
            # Create new cluster
            cluster_id = self._generate_cluster_id(text)
            member = ClusterMember(text=text, embedding=embedding, source=source)
            cluster = SemanticCluster(
                cluster_id=cluster_id,
                centroid_text=text,
                centroid_embedding=None,
                members=[member],
            )
            self._clusters[cluster_id] = cluster
            self._text_to_cluster[text_hash] = cluster_id

            # Cleanup if over limit
            if len(self._clusters) > self.max_clusters:
                self._prune_smallest_clusters()

            return cluster_id, True

    def xǁSemanticClustererǁadd_statement__mutmut_50(
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
        else:
            # Create new cluster
            cluster_id = self._generate_cluster_id(text)
            member = ClusterMember(text=text, embedding=embedding, source=source)
            cluster = SemanticCluster(
                cluster_id=cluster_id,
                centroid_text=text,
                centroid_embedding=embedding,
                members=None,
            )
            self._clusters[cluster_id] = cluster
            self._text_to_cluster[text_hash] = cluster_id

            # Cleanup if over limit
            if len(self._clusters) > self.max_clusters:
                self._prune_smallest_clusters()

            return cluster_id, True

    def xǁSemanticClustererǁadd_statement__mutmut_51(
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
        else:
            # Create new cluster
            cluster_id = self._generate_cluster_id(text)
            member = ClusterMember(text=text, embedding=embedding, source=source)
            cluster = SemanticCluster(
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

    def xǁSemanticClustererǁadd_statement__mutmut_52(
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
        else:
            # Create new cluster
            cluster_id = self._generate_cluster_id(text)
            member = ClusterMember(text=text, embedding=embedding, source=source)
            cluster = SemanticCluster(
                cluster_id=cluster_id,
                centroid_embedding=embedding,
                members=[member],
            )
            self._clusters[cluster_id] = cluster
            self._text_to_cluster[text_hash] = cluster_id

            # Cleanup if over limit
            if len(self._clusters) > self.max_clusters:
                self._prune_smallest_clusters()

            return cluster_id, True

    def xǁSemanticClustererǁadd_statement__mutmut_53(
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
        else:
            # Create new cluster
            cluster_id = self._generate_cluster_id(text)
            member = ClusterMember(text=text, embedding=embedding, source=source)
            cluster = SemanticCluster(
                cluster_id=cluster_id,
                centroid_text=text,
                members=[member],
            )
            self._clusters[cluster_id] = cluster
            self._text_to_cluster[text_hash] = cluster_id

            # Cleanup if over limit
            if len(self._clusters) > self.max_clusters:
                self._prune_smallest_clusters()

            return cluster_id, True

    def xǁSemanticClustererǁadd_statement__mutmut_54(
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
        else:
            # Create new cluster
            cluster_id = self._generate_cluster_id(text)
            member = ClusterMember(text=text, embedding=embedding, source=source)
            cluster = SemanticCluster(
                cluster_id=cluster_id,
                centroid_text=text,
                centroid_embedding=embedding,
                )
            self._clusters[cluster_id] = cluster
            self._text_to_cluster[text_hash] = cluster_id

            # Cleanup if over limit
            if len(self._clusters) > self.max_clusters:
                self._prune_smallest_clusters()

            return cluster_id, True

    def xǁSemanticClustererǁadd_statement__mutmut_55(
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
        else:
            # Create new cluster
            cluster_id = self._generate_cluster_id(text)
            member = ClusterMember(text=text, embedding=embedding, source=source)
            cluster = SemanticCluster(
                cluster_id=cluster_id,
                centroid_text=text,
                centroid_embedding=embedding,
                members=[member],
            )
            self._clusters[cluster_id] = None
            self._text_to_cluster[text_hash] = cluster_id

            # Cleanup if over limit
            if len(self._clusters) > self.max_clusters:
                self._prune_smallest_clusters()

            return cluster_id, True

    def xǁSemanticClustererǁadd_statement__mutmut_56(
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
        else:
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
            self._text_to_cluster[text_hash] = None

            # Cleanup if over limit
            if len(self._clusters) > self.max_clusters:
                self._prune_smallest_clusters()

            return cluster_id, True

    def xǁSemanticClustererǁadd_statement__mutmut_57(
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
        else:
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
            if len(self._clusters) >= self.max_clusters:
                self._prune_smallest_clusters()

            return cluster_id, True

    def xǁSemanticClustererǁadd_statement__mutmut_58(
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
        else:
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

            return cluster_id, False
    
    xǁSemanticClustererǁadd_statement__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSemanticClustererǁadd_statement__mutmut_1': xǁSemanticClustererǁadd_statement__mutmut_1, 
        'xǁSemanticClustererǁadd_statement__mutmut_2': xǁSemanticClustererǁadd_statement__mutmut_2, 
        'xǁSemanticClustererǁadd_statement__mutmut_3': xǁSemanticClustererǁadd_statement__mutmut_3, 
        'xǁSemanticClustererǁadd_statement__mutmut_4': xǁSemanticClustererǁadd_statement__mutmut_4, 
        'xǁSemanticClustererǁadd_statement__mutmut_5': xǁSemanticClustererǁadd_statement__mutmut_5, 
        'xǁSemanticClustererǁadd_statement__mutmut_6': xǁSemanticClustererǁadd_statement__mutmut_6, 
        'xǁSemanticClustererǁadd_statement__mutmut_7': xǁSemanticClustererǁadd_statement__mutmut_7, 
        'xǁSemanticClustererǁadd_statement__mutmut_8': xǁSemanticClustererǁadd_statement__mutmut_8, 
        'xǁSemanticClustererǁadd_statement__mutmut_9': xǁSemanticClustererǁadd_statement__mutmut_9, 
        'xǁSemanticClustererǁadd_statement__mutmut_10': xǁSemanticClustererǁadd_statement__mutmut_10, 
        'xǁSemanticClustererǁadd_statement__mutmut_11': xǁSemanticClustererǁadd_statement__mutmut_11, 
        'xǁSemanticClustererǁadd_statement__mutmut_12': xǁSemanticClustererǁadd_statement__mutmut_12, 
        'xǁSemanticClustererǁadd_statement__mutmut_13': xǁSemanticClustererǁadd_statement__mutmut_13, 
        'xǁSemanticClustererǁadd_statement__mutmut_14': xǁSemanticClustererǁadd_statement__mutmut_14, 
        'xǁSemanticClustererǁadd_statement__mutmut_15': xǁSemanticClustererǁadd_statement__mutmut_15, 
        'xǁSemanticClustererǁadd_statement__mutmut_16': xǁSemanticClustererǁadd_statement__mutmut_16, 
        'xǁSemanticClustererǁadd_statement__mutmut_17': xǁSemanticClustererǁadd_statement__mutmut_17, 
        'xǁSemanticClustererǁadd_statement__mutmut_18': xǁSemanticClustererǁadd_statement__mutmut_18, 
        'xǁSemanticClustererǁadd_statement__mutmut_19': xǁSemanticClustererǁadd_statement__mutmut_19, 
        'xǁSemanticClustererǁadd_statement__mutmut_20': xǁSemanticClustererǁadd_statement__mutmut_20, 
        'xǁSemanticClustererǁadd_statement__mutmut_21': xǁSemanticClustererǁadd_statement__mutmut_21, 
        'xǁSemanticClustererǁadd_statement__mutmut_22': xǁSemanticClustererǁadd_statement__mutmut_22, 
        'xǁSemanticClustererǁadd_statement__mutmut_23': xǁSemanticClustererǁadd_statement__mutmut_23, 
        'xǁSemanticClustererǁadd_statement__mutmut_24': xǁSemanticClustererǁadd_statement__mutmut_24, 
        'xǁSemanticClustererǁadd_statement__mutmut_25': xǁSemanticClustererǁadd_statement__mutmut_25, 
        'xǁSemanticClustererǁadd_statement__mutmut_26': xǁSemanticClustererǁadd_statement__mutmut_26, 
        'xǁSemanticClustererǁadd_statement__mutmut_27': xǁSemanticClustererǁadd_statement__mutmut_27, 
        'xǁSemanticClustererǁadd_statement__mutmut_28': xǁSemanticClustererǁadd_statement__mutmut_28, 
        'xǁSemanticClustererǁadd_statement__mutmut_29': xǁSemanticClustererǁadd_statement__mutmut_29, 
        'xǁSemanticClustererǁadd_statement__mutmut_30': xǁSemanticClustererǁadd_statement__mutmut_30, 
        'xǁSemanticClustererǁadd_statement__mutmut_31': xǁSemanticClustererǁadd_statement__mutmut_31, 
        'xǁSemanticClustererǁadd_statement__mutmut_32': xǁSemanticClustererǁadd_statement__mutmut_32, 
        'xǁSemanticClustererǁadd_statement__mutmut_33': xǁSemanticClustererǁadd_statement__mutmut_33, 
        'xǁSemanticClustererǁadd_statement__mutmut_34': xǁSemanticClustererǁadd_statement__mutmut_34, 
        'xǁSemanticClustererǁadd_statement__mutmut_35': xǁSemanticClustererǁadd_statement__mutmut_35, 
        'xǁSemanticClustererǁadd_statement__mutmut_36': xǁSemanticClustererǁadd_statement__mutmut_36, 
        'xǁSemanticClustererǁadd_statement__mutmut_37': xǁSemanticClustererǁadd_statement__mutmut_37, 
        'xǁSemanticClustererǁadd_statement__mutmut_38': xǁSemanticClustererǁadd_statement__mutmut_38, 
        'xǁSemanticClustererǁadd_statement__mutmut_39': xǁSemanticClustererǁadd_statement__mutmut_39, 
        'xǁSemanticClustererǁadd_statement__mutmut_40': xǁSemanticClustererǁadd_statement__mutmut_40, 
        'xǁSemanticClustererǁadd_statement__mutmut_41': xǁSemanticClustererǁadd_statement__mutmut_41, 
        'xǁSemanticClustererǁadd_statement__mutmut_42': xǁSemanticClustererǁadd_statement__mutmut_42, 
        'xǁSemanticClustererǁadd_statement__mutmut_43': xǁSemanticClustererǁadd_statement__mutmut_43, 
        'xǁSemanticClustererǁadd_statement__mutmut_44': xǁSemanticClustererǁadd_statement__mutmut_44, 
        'xǁSemanticClustererǁadd_statement__mutmut_45': xǁSemanticClustererǁadd_statement__mutmut_45, 
        'xǁSemanticClustererǁadd_statement__mutmut_46': xǁSemanticClustererǁadd_statement__mutmut_46, 
        'xǁSemanticClustererǁadd_statement__mutmut_47': xǁSemanticClustererǁadd_statement__mutmut_47, 
        'xǁSemanticClustererǁadd_statement__mutmut_48': xǁSemanticClustererǁadd_statement__mutmut_48, 
        'xǁSemanticClustererǁadd_statement__mutmut_49': xǁSemanticClustererǁadd_statement__mutmut_49, 
        'xǁSemanticClustererǁadd_statement__mutmut_50': xǁSemanticClustererǁadd_statement__mutmut_50, 
        'xǁSemanticClustererǁadd_statement__mutmut_51': xǁSemanticClustererǁadd_statement__mutmut_51, 
        'xǁSemanticClustererǁadd_statement__mutmut_52': xǁSemanticClustererǁadd_statement__mutmut_52, 
        'xǁSemanticClustererǁadd_statement__mutmut_53': xǁSemanticClustererǁadd_statement__mutmut_53, 
        'xǁSemanticClustererǁadd_statement__mutmut_54': xǁSemanticClustererǁadd_statement__mutmut_54, 
        'xǁSemanticClustererǁadd_statement__mutmut_55': xǁSemanticClustererǁadd_statement__mutmut_55, 
        'xǁSemanticClustererǁadd_statement__mutmut_56': xǁSemanticClustererǁadd_statement__mutmut_56, 
        'xǁSemanticClustererǁadd_statement__mutmut_57': xǁSemanticClustererǁadd_statement__mutmut_57, 
        'xǁSemanticClustererǁadd_statement__mutmut_58': xǁSemanticClustererǁadd_statement__mutmut_58
    }
    
    def add_statement(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSemanticClustererǁadd_statement__mutmut_orig"), object.__getattribute__(self, "xǁSemanticClustererǁadd_statement__mutmut_mutants"), args, kwargs, self)
        return result 
    
    add_statement.__signature__ = _mutmut_signature(xǁSemanticClustererǁadd_statement__mutmut_orig)
    xǁSemanticClustererǁadd_statement__mutmut_orig.__name__ = 'xǁSemanticClustererǁadd_statement'

    def xǁSemanticClustererǁget_cluster__mutmut_orig(self, cluster_id: str) -> Optional[SemanticCluster]:
        """Get cluster by ID."""
        return self._clusters.get(cluster_id)

    def xǁSemanticClustererǁget_cluster__mutmut_1(self, cluster_id: str) -> Optional[SemanticCluster]:
        """Get cluster by ID."""
        return self._clusters.get(None)
    
    xǁSemanticClustererǁget_cluster__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSemanticClustererǁget_cluster__mutmut_1': xǁSemanticClustererǁget_cluster__mutmut_1
    }
    
    def get_cluster(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSemanticClustererǁget_cluster__mutmut_orig"), object.__getattribute__(self, "xǁSemanticClustererǁget_cluster__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_cluster.__signature__ = _mutmut_signature(xǁSemanticClustererǁget_cluster__mutmut_orig)
    xǁSemanticClustererǁget_cluster__mutmut_orig.__name__ = 'xǁSemanticClustererǁget_cluster'

    def xǁSemanticClustererǁget_cluster_for_text__mutmut_orig(self, text: str) -> Optional[SemanticCluster]:
        """Get the cluster containing given text."""
        text_hash = self._hash_text(text)
        cluster_id = self._text_to_cluster.get(text_hash)
        if cluster_id:
            return self._clusters.get(cluster_id)
        return None

    def xǁSemanticClustererǁget_cluster_for_text__mutmut_1(self, text: str) -> Optional[SemanticCluster]:
        """Get the cluster containing given text."""
        text_hash = None
        cluster_id = self._text_to_cluster.get(text_hash)
        if cluster_id:
            return self._clusters.get(cluster_id)
        return None

    def xǁSemanticClustererǁget_cluster_for_text__mutmut_2(self, text: str) -> Optional[SemanticCluster]:
        """Get the cluster containing given text."""
        text_hash = self._hash_text(None)
        cluster_id = self._text_to_cluster.get(text_hash)
        if cluster_id:
            return self._clusters.get(cluster_id)
        return None

    def xǁSemanticClustererǁget_cluster_for_text__mutmut_3(self, text: str) -> Optional[SemanticCluster]:
        """Get the cluster containing given text."""
        text_hash = self._hash_text(text)
        cluster_id = None
        if cluster_id:
            return self._clusters.get(cluster_id)
        return None

    def xǁSemanticClustererǁget_cluster_for_text__mutmut_4(self, text: str) -> Optional[SemanticCluster]:
        """Get the cluster containing given text."""
        text_hash = self._hash_text(text)
        cluster_id = self._text_to_cluster.get(None)
        if cluster_id:
            return self._clusters.get(cluster_id)
        return None

    def xǁSemanticClustererǁget_cluster_for_text__mutmut_5(self, text: str) -> Optional[SemanticCluster]:
        """Get the cluster containing given text."""
        text_hash = self._hash_text(text)
        cluster_id = self._text_to_cluster.get(text_hash)
        if cluster_id:
            return self._clusters.get(None)
        return None
    
    xǁSemanticClustererǁget_cluster_for_text__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSemanticClustererǁget_cluster_for_text__mutmut_1': xǁSemanticClustererǁget_cluster_for_text__mutmut_1, 
        'xǁSemanticClustererǁget_cluster_for_text__mutmut_2': xǁSemanticClustererǁget_cluster_for_text__mutmut_2, 
        'xǁSemanticClustererǁget_cluster_for_text__mutmut_3': xǁSemanticClustererǁget_cluster_for_text__mutmut_3, 
        'xǁSemanticClustererǁget_cluster_for_text__mutmut_4': xǁSemanticClustererǁget_cluster_for_text__mutmut_4, 
        'xǁSemanticClustererǁget_cluster_for_text__mutmut_5': xǁSemanticClustererǁget_cluster_for_text__mutmut_5
    }
    
    def get_cluster_for_text(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSemanticClustererǁget_cluster_for_text__mutmut_orig"), object.__getattribute__(self, "xǁSemanticClustererǁget_cluster_for_text__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_cluster_for_text.__signature__ = _mutmut_signature(xǁSemanticClustererǁget_cluster_for_text__mutmut_orig)
    xǁSemanticClustererǁget_cluster_for_text__mutmut_orig.__name__ = 'xǁSemanticClustererǁget_cluster_for_text'

    def xǁSemanticClustererǁget_representative_statements__mutmut_orig(self, max_per_cluster: int = 1) -> list[str]:
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

    def xǁSemanticClustererǁget_representative_statements__mutmut_1(self, max_per_cluster: int = 2) -> list[str]:
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

    def xǁSemanticClustererǁget_representative_statements__mutmut_2(self, max_per_cluster: int = 1) -> list[str]:
        """
        Get representative statements from each cluster.

        Args:
            max_per_cluster: Maximum representatives per cluster

        Returns:
            list of representative statement texts
        """
        representatives = None
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

    def xǁSemanticClustererǁget_representative_statements__mutmut_3(self, max_per_cluster: int = 1) -> list[str]:
        """
        Get representative statements from each cluster.

        Args:
            max_per_cluster: Maximum representatives per cluster

        Returns:
            list of representative statement texts
        """
        representatives = []
        for cluster in self._clusters.values():
            if cluster.size <= self.min_cluster_size:
                continue
            # Get highest similarity members as representatives
            sorted_members = sorted(
                cluster.members, key=lambda m: m.similarity_to_centroid, reverse=True
            )
            for member in sorted_members[:max_per_cluster]:
                representatives.append(member.text)
        return representatives

    def xǁSemanticClustererǁget_representative_statements__mutmut_4(self, max_per_cluster: int = 1) -> list[str]:
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
                break
            # Get highest similarity members as representatives
            sorted_members = sorted(
                cluster.members, key=lambda m: m.similarity_to_centroid, reverse=True
            )
            for member in sorted_members[:max_per_cluster]:
                representatives.append(member.text)
        return representatives

    def xǁSemanticClustererǁget_representative_statements__mutmut_5(self, max_per_cluster: int = 1) -> list[str]:
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
            sorted_members = None
            for member in sorted_members[:max_per_cluster]:
                representatives.append(member.text)
        return representatives

    def xǁSemanticClustererǁget_representative_statements__mutmut_6(self, max_per_cluster: int = 1) -> list[str]:
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
                None, key=lambda m: m.similarity_to_centroid, reverse=True
            )
            for member in sorted_members[:max_per_cluster]:
                representatives.append(member.text)
        return representatives

    def xǁSemanticClustererǁget_representative_statements__mutmut_7(self, max_per_cluster: int = 1) -> list[str]:
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
                cluster.members, key=None, reverse=True
            )
            for member in sorted_members[:max_per_cluster]:
                representatives.append(member.text)
        return representatives

    def xǁSemanticClustererǁget_representative_statements__mutmut_8(self, max_per_cluster: int = 1) -> list[str]:
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
                cluster.members, key=lambda m: m.similarity_to_centroid, reverse=None
            )
            for member in sorted_members[:max_per_cluster]:
                representatives.append(member.text)
        return representatives

    def xǁSemanticClustererǁget_representative_statements__mutmut_9(self, max_per_cluster: int = 1) -> list[str]:
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
                key=lambda m: m.similarity_to_centroid, reverse=True
            )
            for member in sorted_members[:max_per_cluster]:
                representatives.append(member.text)
        return representatives

    def xǁSemanticClustererǁget_representative_statements__mutmut_10(self, max_per_cluster: int = 1) -> list[str]:
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
                cluster.members, reverse=True
            )
            for member in sorted_members[:max_per_cluster]:
                representatives.append(member.text)
        return representatives

    def xǁSemanticClustererǁget_representative_statements__mutmut_11(self, max_per_cluster: int = 1) -> list[str]:
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
                cluster.members, key=lambda m: m.similarity_to_centroid, )
            for member in sorted_members[:max_per_cluster]:
                representatives.append(member.text)
        return representatives

    def xǁSemanticClustererǁget_representative_statements__mutmut_12(self, max_per_cluster: int = 1) -> list[str]:
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
                cluster.members, key=lambda m: None, reverse=True
            )
            for member in sorted_members[:max_per_cluster]:
                representatives.append(member.text)
        return representatives

    def xǁSemanticClustererǁget_representative_statements__mutmut_13(self, max_per_cluster: int = 1) -> list[str]:
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
                cluster.members, key=lambda m: m.similarity_to_centroid, reverse=False
            )
            for member in sorted_members[:max_per_cluster]:
                representatives.append(member.text)
        return representatives

    def xǁSemanticClustererǁget_representative_statements__mutmut_14(self, max_per_cluster: int = 1) -> list[str]:
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
                representatives.append(None)
        return representatives
    
    xǁSemanticClustererǁget_representative_statements__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSemanticClustererǁget_representative_statements__mutmut_1': xǁSemanticClustererǁget_representative_statements__mutmut_1, 
        'xǁSemanticClustererǁget_representative_statements__mutmut_2': xǁSemanticClustererǁget_representative_statements__mutmut_2, 
        'xǁSemanticClustererǁget_representative_statements__mutmut_3': xǁSemanticClustererǁget_representative_statements__mutmut_3, 
        'xǁSemanticClustererǁget_representative_statements__mutmut_4': xǁSemanticClustererǁget_representative_statements__mutmut_4, 
        'xǁSemanticClustererǁget_representative_statements__mutmut_5': xǁSemanticClustererǁget_representative_statements__mutmut_5, 
        'xǁSemanticClustererǁget_representative_statements__mutmut_6': xǁSemanticClustererǁget_representative_statements__mutmut_6, 
        'xǁSemanticClustererǁget_representative_statements__mutmut_7': xǁSemanticClustererǁget_representative_statements__mutmut_7, 
        'xǁSemanticClustererǁget_representative_statements__mutmut_8': xǁSemanticClustererǁget_representative_statements__mutmut_8, 
        'xǁSemanticClustererǁget_representative_statements__mutmut_9': xǁSemanticClustererǁget_representative_statements__mutmut_9, 
        'xǁSemanticClustererǁget_representative_statements__mutmut_10': xǁSemanticClustererǁget_representative_statements__mutmut_10, 
        'xǁSemanticClustererǁget_representative_statements__mutmut_11': xǁSemanticClustererǁget_representative_statements__mutmut_11, 
        'xǁSemanticClustererǁget_representative_statements__mutmut_12': xǁSemanticClustererǁget_representative_statements__mutmut_12, 
        'xǁSemanticClustererǁget_representative_statements__mutmut_13': xǁSemanticClustererǁget_representative_statements__mutmut_13, 
        'xǁSemanticClustererǁget_representative_statements__mutmut_14': xǁSemanticClustererǁget_representative_statements__mutmut_14
    }
    
    def get_representative_statements(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSemanticClustererǁget_representative_statements__mutmut_orig"), object.__getattribute__(self, "xǁSemanticClustererǁget_representative_statements__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_representative_statements.__signature__ = _mutmut_signature(xǁSemanticClustererǁget_representative_statements__mutmut_orig)
    xǁSemanticClustererǁget_representative_statements__mutmut_orig.__name__ = 'xǁSemanticClustererǁget_representative_statements'

    def xǁSemanticClustererǁcluster_statements__mutmut_orig(self, statements: list[str]) -> dict[str, list[str]]:
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

    def xǁSemanticClustererǁcluster_statements__mutmut_1(self, statements: list[str]) -> dict[str, list[str]]:
        """
        Cluster a list of statements.

        Args:
            statements: list of statement texts

        Returns:
            dict mapping cluster_id to list of statement texts
        """
        for stmt in statements:
            self.add_statement(None)

        result = {}
        for cluster_id, cluster in self._clusters.items():
            result[cluster_id] = [m.text for m in cluster.members]
        return result

    def xǁSemanticClustererǁcluster_statements__mutmut_2(self, statements: list[str]) -> dict[str, list[str]]:
        """
        Cluster a list of statements.

        Args:
            statements: list of statement texts

        Returns:
            dict mapping cluster_id to list of statement texts
        """
        for stmt in statements:
            self.add_statement(stmt)

        result = None
        for cluster_id, cluster in self._clusters.items():
            result[cluster_id] = [m.text for m in cluster.members]
        return result

    def xǁSemanticClustererǁcluster_statements__mutmut_3(self, statements: list[str]) -> dict[str, list[str]]:
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
            result[cluster_id] = None
        return result
    
    xǁSemanticClustererǁcluster_statements__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSemanticClustererǁcluster_statements__mutmut_1': xǁSemanticClustererǁcluster_statements__mutmut_1, 
        'xǁSemanticClustererǁcluster_statements__mutmut_2': xǁSemanticClustererǁcluster_statements__mutmut_2, 
        'xǁSemanticClustererǁcluster_statements__mutmut_3': xǁSemanticClustererǁcluster_statements__mutmut_3
    }
    
    def cluster_statements(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSemanticClustererǁcluster_statements__mutmut_orig"), object.__getattribute__(self, "xǁSemanticClustererǁcluster_statements__mutmut_mutants"), args, kwargs, self)
        return result 
    
    cluster_statements.__signature__ = _mutmut_signature(xǁSemanticClustererǁcluster_statements__mutmut_orig)
    xǁSemanticClustererǁcluster_statements__mutmut_orig.__name__ = 'xǁSemanticClustererǁcluster_statements'

    def xǁSemanticClustererǁget_cluster_summary__mutmut_orig(self) -> dict:
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

    def xǁSemanticClustererǁget_cluster_summary__mutmut_1(self) -> dict:
        """Get summary statistics of all clusters."""
        return {
            "XXtotal_clustersXX": len(self._clusters),
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

    def xǁSemanticClustererǁget_cluster_summary__mutmut_2(self) -> dict:
        """Get summary statistics of all clusters."""
        return {
            "TOTAL_CLUSTERS": len(self._clusters),
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

    def xǁSemanticClustererǁget_cluster_summary__mutmut_3(self) -> dict:
        """Get summary statistics of all clusters."""
        return {
            "total_clusters": len(self._clusters),
            "XXtotal_statementsXX": sum(c.size for c in self._clusters.values()),
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

    def xǁSemanticClustererǁget_cluster_summary__mutmut_4(self) -> dict:
        """Get summary statistics of all clusters."""
        return {
            "total_clusters": len(self._clusters),
            "TOTAL_STATEMENTS": sum(c.size for c in self._clusters.values()),
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

    def xǁSemanticClustererǁget_cluster_summary__mutmut_5(self) -> dict:
        """Get summary statistics of all clusters."""
        return {
            "total_clusters": len(self._clusters),
            "total_statements": sum(None),
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

    def xǁSemanticClustererǁget_cluster_summary__mutmut_6(self) -> dict:
        """Get summary statistics of all clusters."""
        return {
            "total_clusters": len(self._clusters),
            "total_statements": sum(c.size for c in self._clusters.values()),
            "XXaverage_cluster_sizeXX": (
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

    def xǁSemanticClustererǁget_cluster_summary__mutmut_7(self) -> dict:
        """Get summary statistics of all clusters."""
        return {
            "total_clusters": len(self._clusters),
            "total_statements": sum(c.size for c in self._clusters.values()),
            "AVERAGE_CLUSTER_SIZE": (
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

    def xǁSemanticClustererǁget_cluster_summary__mutmut_8(self) -> dict:
        """Get summary statistics of all clusters."""
        return {
            "total_clusters": len(self._clusters),
            "total_statements": sum(c.size for c in self._clusters.values()),
            "average_cluster_size": (
                sum(c.size for c in self._clusters.values()) * len(self._clusters)
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

    def xǁSemanticClustererǁget_cluster_summary__mutmut_9(self) -> dict:
        """Get summary statistics of all clusters."""
        return {
            "total_clusters": len(self._clusters),
            "total_statements": sum(c.size for c in self._clusters.values()),
            "average_cluster_size": (
                sum(None) / len(self._clusters)
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

    def xǁSemanticClustererǁget_cluster_summary__mutmut_10(self) -> dict:
        """Get summary statistics of all clusters."""
        return {
            "total_clusters": len(self._clusters),
            "total_statements": sum(c.size for c in self._clusters.values()),
            "average_cluster_size": (
                sum(c.size for c in self._clusters.values()) / len(self._clusters)
                if self._clusters
                else 1
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

    def xǁSemanticClustererǁget_cluster_summary__mutmut_11(self) -> dict:
        """Get summary statistics of all clusters."""
        return {
            "total_clusters": len(self._clusters),
            "total_statements": sum(c.size for c in self._clusters.values()),
            "average_cluster_size": (
                sum(c.size for c in self._clusters.values()) / len(self._clusters)
                if self._clusters
                else 0
            ),
            "XXaverage_confidenceXX": (
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

    def xǁSemanticClustererǁget_cluster_summary__mutmut_12(self) -> dict:
        """Get summary statistics of all clusters."""
        return {
            "total_clusters": len(self._clusters),
            "total_statements": sum(c.size for c in self._clusters.values()),
            "average_cluster_size": (
                sum(c.size for c in self._clusters.values()) / len(self._clusters)
                if self._clusters
                else 0
            ),
            "AVERAGE_CONFIDENCE": (
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

    def xǁSemanticClustererǁget_cluster_summary__mutmut_13(self) -> dict:
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
                sum(c.confidence_score for c in self._clusters.values()) * len(self._clusters)
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

    def xǁSemanticClustererǁget_cluster_summary__mutmut_14(self) -> dict:
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
                sum(None) / len(self._clusters)
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

    def xǁSemanticClustererǁget_cluster_summary__mutmut_15(self) -> dict:
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
                else 1
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

    def xǁSemanticClustererǁget_cluster_summary__mutmut_16(self) -> dict:
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
            "XXclustersXX": [
                {
                    "id": c.cluster_id,
                    "size": c.size,
                    "confidence": c.confidence_score,
                    "centroid_preview": c.centroid_text[:100],
                }
                for c in self._clusters.values()
            ],
        }

    def xǁSemanticClustererǁget_cluster_summary__mutmut_17(self) -> dict:
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
            "CLUSTERS": [
                {
                    "id": c.cluster_id,
                    "size": c.size,
                    "confidence": c.confidence_score,
                    "centroid_preview": c.centroid_text[:100],
                }
                for c in self._clusters.values()
            ],
        }

    def xǁSemanticClustererǁget_cluster_summary__mutmut_18(self) -> dict:
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
                    "XXidXX": c.cluster_id,
                    "size": c.size,
                    "confidence": c.confidence_score,
                    "centroid_preview": c.centroid_text[:100],
                }
                for c in self._clusters.values()
            ],
        }

    def xǁSemanticClustererǁget_cluster_summary__mutmut_19(self) -> dict:
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
                    "ID": c.cluster_id,
                    "size": c.size,
                    "confidence": c.confidence_score,
                    "centroid_preview": c.centroid_text[:100],
                }
                for c in self._clusters.values()
            ],
        }

    def xǁSemanticClustererǁget_cluster_summary__mutmut_20(self) -> dict:
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
                    "XXsizeXX": c.size,
                    "confidence": c.confidence_score,
                    "centroid_preview": c.centroid_text[:100],
                }
                for c in self._clusters.values()
            ],
        }

    def xǁSemanticClustererǁget_cluster_summary__mutmut_21(self) -> dict:
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
                    "SIZE": c.size,
                    "confidence": c.confidence_score,
                    "centroid_preview": c.centroid_text[:100],
                }
                for c in self._clusters.values()
            ],
        }

    def xǁSemanticClustererǁget_cluster_summary__mutmut_22(self) -> dict:
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
                    "XXconfidenceXX": c.confidence_score,
                    "centroid_preview": c.centroid_text[:100],
                }
                for c in self._clusters.values()
            ],
        }

    def xǁSemanticClustererǁget_cluster_summary__mutmut_23(self) -> dict:
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
                    "CONFIDENCE": c.confidence_score,
                    "centroid_preview": c.centroid_text[:100],
                }
                for c in self._clusters.values()
            ],
        }

    def xǁSemanticClustererǁget_cluster_summary__mutmut_24(self) -> dict:
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
                    "XXcentroid_previewXX": c.centroid_text[:100],
                }
                for c in self._clusters.values()
            ],
        }

    def xǁSemanticClustererǁget_cluster_summary__mutmut_25(self) -> dict:
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
                    "CENTROID_PREVIEW": c.centroid_text[:100],
                }
                for c in self._clusters.values()
            ],
        }

    def xǁSemanticClustererǁget_cluster_summary__mutmut_26(self) -> dict:
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
                    "centroid_preview": c.centroid_text[:101],
                }
                for c in self._clusters.values()
            ],
        }
    
    xǁSemanticClustererǁget_cluster_summary__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSemanticClustererǁget_cluster_summary__mutmut_1': xǁSemanticClustererǁget_cluster_summary__mutmut_1, 
        'xǁSemanticClustererǁget_cluster_summary__mutmut_2': xǁSemanticClustererǁget_cluster_summary__mutmut_2, 
        'xǁSemanticClustererǁget_cluster_summary__mutmut_3': xǁSemanticClustererǁget_cluster_summary__mutmut_3, 
        'xǁSemanticClustererǁget_cluster_summary__mutmut_4': xǁSemanticClustererǁget_cluster_summary__mutmut_4, 
        'xǁSemanticClustererǁget_cluster_summary__mutmut_5': xǁSemanticClustererǁget_cluster_summary__mutmut_5, 
        'xǁSemanticClustererǁget_cluster_summary__mutmut_6': xǁSemanticClustererǁget_cluster_summary__mutmut_6, 
        'xǁSemanticClustererǁget_cluster_summary__mutmut_7': xǁSemanticClustererǁget_cluster_summary__mutmut_7, 
        'xǁSemanticClustererǁget_cluster_summary__mutmut_8': xǁSemanticClustererǁget_cluster_summary__mutmut_8, 
        'xǁSemanticClustererǁget_cluster_summary__mutmut_9': xǁSemanticClustererǁget_cluster_summary__mutmut_9, 
        'xǁSemanticClustererǁget_cluster_summary__mutmut_10': xǁSemanticClustererǁget_cluster_summary__mutmut_10, 
        'xǁSemanticClustererǁget_cluster_summary__mutmut_11': xǁSemanticClustererǁget_cluster_summary__mutmut_11, 
        'xǁSemanticClustererǁget_cluster_summary__mutmut_12': xǁSemanticClustererǁget_cluster_summary__mutmut_12, 
        'xǁSemanticClustererǁget_cluster_summary__mutmut_13': xǁSemanticClustererǁget_cluster_summary__mutmut_13, 
        'xǁSemanticClustererǁget_cluster_summary__mutmut_14': xǁSemanticClustererǁget_cluster_summary__mutmut_14, 
        'xǁSemanticClustererǁget_cluster_summary__mutmut_15': xǁSemanticClustererǁget_cluster_summary__mutmut_15, 
        'xǁSemanticClustererǁget_cluster_summary__mutmut_16': xǁSemanticClustererǁget_cluster_summary__mutmut_16, 
        'xǁSemanticClustererǁget_cluster_summary__mutmut_17': xǁSemanticClustererǁget_cluster_summary__mutmut_17, 
        'xǁSemanticClustererǁget_cluster_summary__mutmut_18': xǁSemanticClustererǁget_cluster_summary__mutmut_18, 
        'xǁSemanticClustererǁget_cluster_summary__mutmut_19': xǁSemanticClustererǁget_cluster_summary__mutmut_19, 
        'xǁSemanticClustererǁget_cluster_summary__mutmut_20': xǁSemanticClustererǁget_cluster_summary__mutmut_20, 
        'xǁSemanticClustererǁget_cluster_summary__mutmut_21': xǁSemanticClustererǁget_cluster_summary__mutmut_21, 
        'xǁSemanticClustererǁget_cluster_summary__mutmut_22': xǁSemanticClustererǁget_cluster_summary__mutmut_22, 
        'xǁSemanticClustererǁget_cluster_summary__mutmut_23': xǁSemanticClustererǁget_cluster_summary__mutmut_23, 
        'xǁSemanticClustererǁget_cluster_summary__mutmut_24': xǁSemanticClustererǁget_cluster_summary__mutmut_24, 
        'xǁSemanticClustererǁget_cluster_summary__mutmut_25': xǁSemanticClustererǁget_cluster_summary__mutmut_25, 
        'xǁSemanticClustererǁget_cluster_summary__mutmut_26': xǁSemanticClustererǁget_cluster_summary__mutmut_26
    }
    
    def get_cluster_summary(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSemanticClustererǁget_cluster_summary__mutmut_orig"), object.__getattribute__(self, "xǁSemanticClustererǁget_cluster_summary__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_cluster_summary.__signature__ = _mutmut_signature(xǁSemanticClustererǁget_cluster_summary__mutmut_orig)
    xǁSemanticClustererǁget_cluster_summary__mutmut_orig.__name__ = 'xǁSemanticClustererǁget_cluster_summary'

    def clear(self):
        """Clear all clusters."""
        self._clusters.clear()
        self._text_to_cluster.clear()

    def xǁSemanticClustererǁ_compute_similarity__mutmut_orig(
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
        else:
            return self._token_similarity(text1, text2)

    def xǁSemanticClustererǁ_compute_similarity__mutmut_1(
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
        if embedding1 or embedding2:
            return self._cosine_similarity(embedding1, embedding2)
        else:
            return self._token_similarity(text1, text2)

    def xǁSemanticClustererǁ_compute_similarity__mutmut_2(
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
            return self._cosine_similarity(None, embedding2)
        else:
            return self._token_similarity(text1, text2)

    def xǁSemanticClustererǁ_compute_similarity__mutmut_3(
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
            return self._cosine_similarity(embedding1, None)
        else:
            return self._token_similarity(text1, text2)

    def xǁSemanticClustererǁ_compute_similarity__mutmut_4(
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
            return self._cosine_similarity(embedding2)
        else:
            return self._token_similarity(text1, text2)

    def xǁSemanticClustererǁ_compute_similarity__mutmut_5(
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
            return self._cosine_similarity(embedding1, )
        else:
            return self._token_similarity(text1, text2)

    def xǁSemanticClustererǁ_compute_similarity__mutmut_6(
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
        else:
            return self._token_similarity(None, text2)

    def xǁSemanticClustererǁ_compute_similarity__mutmut_7(
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
        else:
            return self._token_similarity(text1, None)

    def xǁSemanticClustererǁ_compute_similarity__mutmut_8(
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
        else:
            return self._token_similarity(text2)

    def xǁSemanticClustererǁ_compute_similarity__mutmut_9(
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
        else:
            return self._token_similarity(text1, )
    
    xǁSemanticClustererǁ_compute_similarity__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSemanticClustererǁ_compute_similarity__mutmut_1': xǁSemanticClustererǁ_compute_similarity__mutmut_1, 
        'xǁSemanticClustererǁ_compute_similarity__mutmut_2': xǁSemanticClustererǁ_compute_similarity__mutmut_2, 
        'xǁSemanticClustererǁ_compute_similarity__mutmut_3': xǁSemanticClustererǁ_compute_similarity__mutmut_3, 
        'xǁSemanticClustererǁ_compute_similarity__mutmut_4': xǁSemanticClustererǁ_compute_similarity__mutmut_4, 
        'xǁSemanticClustererǁ_compute_similarity__mutmut_5': xǁSemanticClustererǁ_compute_similarity__mutmut_5, 
        'xǁSemanticClustererǁ_compute_similarity__mutmut_6': xǁSemanticClustererǁ_compute_similarity__mutmut_6, 
        'xǁSemanticClustererǁ_compute_similarity__mutmut_7': xǁSemanticClustererǁ_compute_similarity__mutmut_7, 
        'xǁSemanticClustererǁ_compute_similarity__mutmut_8': xǁSemanticClustererǁ_compute_similarity__mutmut_8, 
        'xǁSemanticClustererǁ_compute_similarity__mutmut_9': xǁSemanticClustererǁ_compute_similarity__mutmut_9
    }
    
    def _compute_similarity(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSemanticClustererǁ_compute_similarity__mutmut_orig"), object.__getattribute__(self, "xǁSemanticClustererǁ_compute_similarity__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _compute_similarity.__signature__ = _mutmut_signature(xǁSemanticClustererǁ_compute_similarity__mutmut_orig)
    xǁSemanticClustererǁ_compute_similarity__mutmut_orig.__name__ = 'xǁSemanticClustererǁ_compute_similarity'

    def xǁSemanticClustererǁ_cosine_similarity__mutmut_orig(self, vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def xǁSemanticClustererǁ_cosine_similarity__mutmut_1(self, vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(vec1) == len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def xǁSemanticClustererǁ_cosine_similarity__mutmut_2(self, vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 1.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def xǁSemanticClustererǁ_cosine_similarity__mutmut_3(self, vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = None
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def xǁSemanticClustererǁ_cosine_similarity__mutmut_4(self, vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(None)
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def xǁSemanticClustererǁ_cosine_similarity__mutmut_5(self, vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a / b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def xǁSemanticClustererǁ_cosine_similarity__mutmut_6(self, vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(None, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def xǁSemanticClustererǁ_cosine_similarity__mutmut_7(self, vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, None))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def xǁSemanticClustererǁ_cosine_similarity__mutmut_8(self, vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def xǁSemanticClustererǁ_cosine_similarity__mutmut_9(self, vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, ))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def xǁSemanticClustererǁ_cosine_similarity__mutmut_10(self, vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = None
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def xǁSemanticClustererǁ_cosine_similarity__mutmut_11(self, vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(None)
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def xǁSemanticClustererǁ_cosine_similarity__mutmut_12(self, vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(None))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def xǁSemanticClustererǁ_cosine_similarity__mutmut_13(self, vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a / a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def xǁSemanticClustererǁ_cosine_similarity__mutmut_14(self, vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = None

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def xǁSemanticClustererǁ_cosine_similarity__mutmut_15(self, vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(None)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def xǁSemanticClustererǁ_cosine_similarity__mutmut_16(self, vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(None))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def xǁSemanticClustererǁ_cosine_similarity__mutmut_17(self, vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b / b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def xǁSemanticClustererǁ_cosine_similarity__mutmut_18(self, vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 and norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def xǁSemanticClustererǁ_cosine_similarity__mutmut_19(self, vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 != 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def xǁSemanticClustererǁ_cosine_similarity__mutmut_20(self, vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 1 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def xǁSemanticClustererǁ_cosine_similarity__mutmut_21(self, vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 != 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def xǁSemanticClustererǁ_cosine_similarity__mutmut_22(self, vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 1:
            return 0.0

        return dot_product / (norm1 * norm2)

    def xǁSemanticClustererǁ_cosine_similarity__mutmut_23(self, vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 1.0

        return dot_product / (norm1 * norm2)

    def xǁSemanticClustererǁ_cosine_similarity__mutmut_24(self, vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product * (norm1 * norm2)

    def xǁSemanticClustererǁ_cosine_similarity__mutmut_25(self, vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 / norm2)
    
    xǁSemanticClustererǁ_cosine_similarity__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSemanticClustererǁ_cosine_similarity__mutmut_1': xǁSemanticClustererǁ_cosine_similarity__mutmut_1, 
        'xǁSemanticClustererǁ_cosine_similarity__mutmut_2': xǁSemanticClustererǁ_cosine_similarity__mutmut_2, 
        'xǁSemanticClustererǁ_cosine_similarity__mutmut_3': xǁSemanticClustererǁ_cosine_similarity__mutmut_3, 
        'xǁSemanticClustererǁ_cosine_similarity__mutmut_4': xǁSemanticClustererǁ_cosine_similarity__mutmut_4, 
        'xǁSemanticClustererǁ_cosine_similarity__mutmut_5': xǁSemanticClustererǁ_cosine_similarity__mutmut_5, 
        'xǁSemanticClustererǁ_cosine_similarity__mutmut_6': xǁSemanticClustererǁ_cosine_similarity__mutmut_6, 
        'xǁSemanticClustererǁ_cosine_similarity__mutmut_7': xǁSemanticClustererǁ_cosine_similarity__mutmut_7, 
        'xǁSemanticClustererǁ_cosine_similarity__mutmut_8': xǁSemanticClustererǁ_cosine_similarity__mutmut_8, 
        'xǁSemanticClustererǁ_cosine_similarity__mutmut_9': xǁSemanticClustererǁ_cosine_similarity__mutmut_9, 
        'xǁSemanticClustererǁ_cosine_similarity__mutmut_10': xǁSemanticClustererǁ_cosine_similarity__mutmut_10, 
        'xǁSemanticClustererǁ_cosine_similarity__mutmut_11': xǁSemanticClustererǁ_cosine_similarity__mutmut_11, 
        'xǁSemanticClustererǁ_cosine_similarity__mutmut_12': xǁSemanticClustererǁ_cosine_similarity__mutmut_12, 
        'xǁSemanticClustererǁ_cosine_similarity__mutmut_13': xǁSemanticClustererǁ_cosine_similarity__mutmut_13, 
        'xǁSemanticClustererǁ_cosine_similarity__mutmut_14': xǁSemanticClustererǁ_cosine_similarity__mutmut_14, 
        'xǁSemanticClustererǁ_cosine_similarity__mutmut_15': xǁSemanticClustererǁ_cosine_similarity__mutmut_15, 
        'xǁSemanticClustererǁ_cosine_similarity__mutmut_16': xǁSemanticClustererǁ_cosine_similarity__mutmut_16, 
        'xǁSemanticClustererǁ_cosine_similarity__mutmut_17': xǁSemanticClustererǁ_cosine_similarity__mutmut_17, 
        'xǁSemanticClustererǁ_cosine_similarity__mutmut_18': xǁSemanticClustererǁ_cosine_similarity__mutmut_18, 
        'xǁSemanticClustererǁ_cosine_similarity__mutmut_19': xǁSemanticClustererǁ_cosine_similarity__mutmut_19, 
        'xǁSemanticClustererǁ_cosine_similarity__mutmut_20': xǁSemanticClustererǁ_cosine_similarity__mutmut_20, 
        'xǁSemanticClustererǁ_cosine_similarity__mutmut_21': xǁSemanticClustererǁ_cosine_similarity__mutmut_21, 
        'xǁSemanticClustererǁ_cosine_similarity__mutmut_22': xǁSemanticClustererǁ_cosine_similarity__mutmut_22, 
        'xǁSemanticClustererǁ_cosine_similarity__mutmut_23': xǁSemanticClustererǁ_cosine_similarity__mutmut_23, 
        'xǁSemanticClustererǁ_cosine_similarity__mutmut_24': xǁSemanticClustererǁ_cosine_similarity__mutmut_24, 
        'xǁSemanticClustererǁ_cosine_similarity__mutmut_25': xǁSemanticClustererǁ_cosine_similarity__mutmut_25
    }
    
    def _cosine_similarity(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSemanticClustererǁ_cosine_similarity__mutmut_orig"), object.__getattribute__(self, "xǁSemanticClustererǁ_cosine_similarity__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _cosine_similarity.__signature__ = _mutmut_signature(xǁSemanticClustererǁ_cosine_similarity__mutmut_orig)
    xǁSemanticClustererǁ_cosine_similarity__mutmut_orig.__name__ = 'xǁSemanticClustererǁ_cosine_similarity'

    def xǁSemanticClustererǁ_token_similarity__mutmut_orig(self, text1: str, text2: str) -> float:
        """Compute token-based Jaccard similarity."""
        tokens1 = set(text1.lower().split())
        tokens2 = set(text2.lower().split())

        if not tokens1 or not tokens2:
            return 0.0

        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)

        return intersection / union if union > 0 else 0.0

    def xǁSemanticClustererǁ_token_similarity__mutmut_1(self, text1: str, text2: str) -> float:
        """Compute token-based Jaccard similarity."""
        tokens1 = None
        tokens2 = set(text2.lower().split())

        if not tokens1 or not tokens2:
            return 0.0

        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)

        return intersection / union if union > 0 else 0.0

    def xǁSemanticClustererǁ_token_similarity__mutmut_2(self, text1: str, text2: str) -> float:
        """Compute token-based Jaccard similarity."""
        tokens1 = set(None)
        tokens2 = set(text2.lower().split())

        if not tokens1 or not tokens2:
            return 0.0

        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)

        return intersection / union if union > 0 else 0.0

    def xǁSemanticClustererǁ_token_similarity__mutmut_3(self, text1: str, text2: str) -> float:
        """Compute token-based Jaccard similarity."""
        tokens1 = set(text1.upper().split())
        tokens2 = set(text2.lower().split())

        if not tokens1 or not tokens2:
            return 0.0

        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)

        return intersection / union if union > 0 else 0.0

    def xǁSemanticClustererǁ_token_similarity__mutmut_4(self, text1: str, text2: str) -> float:
        """Compute token-based Jaccard similarity."""
        tokens1 = set(text1.lower().split())
        tokens2 = None

        if not tokens1 or not tokens2:
            return 0.0

        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)

        return intersection / union if union > 0 else 0.0

    def xǁSemanticClustererǁ_token_similarity__mutmut_5(self, text1: str, text2: str) -> float:
        """Compute token-based Jaccard similarity."""
        tokens1 = set(text1.lower().split())
        tokens2 = set(None)

        if not tokens1 or not tokens2:
            return 0.0

        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)

        return intersection / union if union > 0 else 0.0

    def xǁSemanticClustererǁ_token_similarity__mutmut_6(self, text1: str, text2: str) -> float:
        """Compute token-based Jaccard similarity."""
        tokens1 = set(text1.lower().split())
        tokens2 = set(text2.upper().split())

        if not tokens1 or not tokens2:
            return 0.0

        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)

        return intersection / union if union > 0 else 0.0

    def xǁSemanticClustererǁ_token_similarity__mutmut_7(self, text1: str, text2: str) -> float:
        """Compute token-based Jaccard similarity."""
        tokens1 = set(text1.lower().split())
        tokens2 = set(text2.lower().split())

        if not tokens1 and not tokens2:
            return 0.0

        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)

        return intersection / union if union > 0 else 0.0

    def xǁSemanticClustererǁ_token_similarity__mutmut_8(self, text1: str, text2: str) -> float:
        """Compute token-based Jaccard similarity."""
        tokens1 = set(text1.lower().split())
        tokens2 = set(text2.lower().split())

        if tokens1 or not tokens2:
            return 0.0

        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)

        return intersection / union if union > 0 else 0.0

    def xǁSemanticClustererǁ_token_similarity__mutmut_9(self, text1: str, text2: str) -> float:
        """Compute token-based Jaccard similarity."""
        tokens1 = set(text1.lower().split())
        tokens2 = set(text2.lower().split())

        if not tokens1 or tokens2:
            return 0.0

        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)

        return intersection / union if union > 0 else 0.0

    def xǁSemanticClustererǁ_token_similarity__mutmut_10(self, text1: str, text2: str) -> float:
        """Compute token-based Jaccard similarity."""
        tokens1 = set(text1.lower().split())
        tokens2 = set(text2.lower().split())

        if not tokens1 or not tokens2:
            return 1.0

        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)

        return intersection / union if union > 0 else 0.0

    def xǁSemanticClustererǁ_token_similarity__mutmut_11(self, text1: str, text2: str) -> float:
        """Compute token-based Jaccard similarity."""
        tokens1 = set(text1.lower().split())
        tokens2 = set(text2.lower().split())

        if not tokens1 or not tokens2:
            return 0.0

        intersection = None
        union = len(tokens1 | tokens2)

        return intersection / union if union > 0 else 0.0

    def xǁSemanticClustererǁ_token_similarity__mutmut_12(self, text1: str, text2: str) -> float:
        """Compute token-based Jaccard similarity."""
        tokens1 = set(text1.lower().split())
        tokens2 = set(text2.lower().split())

        if not tokens1 or not tokens2:
            return 0.0

        intersection = len(tokens1 & tokens2)
        union = None

        return intersection / union if union > 0 else 0.0

    def xǁSemanticClustererǁ_token_similarity__mutmut_13(self, text1: str, text2: str) -> float:
        """Compute token-based Jaccard similarity."""
        tokens1 = set(text1.lower().split())
        tokens2 = set(text2.lower().split())

        if not tokens1 or not tokens2:
            return 0.0

        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)

        return intersection * union if union > 0 else 0.0

    def xǁSemanticClustererǁ_token_similarity__mutmut_14(self, text1: str, text2: str) -> float:
        """Compute token-based Jaccard similarity."""
        tokens1 = set(text1.lower().split())
        tokens2 = set(text2.lower().split())

        if not tokens1 or not tokens2:
            return 0.0

        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)

        return intersection / union if union >= 0 else 0.0

    def xǁSemanticClustererǁ_token_similarity__mutmut_15(self, text1: str, text2: str) -> float:
        """Compute token-based Jaccard similarity."""
        tokens1 = set(text1.lower().split())
        tokens2 = set(text2.lower().split())

        if not tokens1 or not tokens2:
            return 0.0

        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)

        return intersection / union if union > 1 else 0.0

    def xǁSemanticClustererǁ_token_similarity__mutmut_16(self, text1: str, text2: str) -> float:
        """Compute token-based Jaccard similarity."""
        tokens1 = set(text1.lower().split())
        tokens2 = set(text2.lower().split())

        if not tokens1 or not tokens2:
            return 0.0

        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)

        return intersection / union if union > 0 else 1.0
    
    xǁSemanticClustererǁ_token_similarity__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSemanticClustererǁ_token_similarity__mutmut_1': xǁSemanticClustererǁ_token_similarity__mutmut_1, 
        'xǁSemanticClustererǁ_token_similarity__mutmut_2': xǁSemanticClustererǁ_token_similarity__mutmut_2, 
        'xǁSemanticClustererǁ_token_similarity__mutmut_3': xǁSemanticClustererǁ_token_similarity__mutmut_3, 
        'xǁSemanticClustererǁ_token_similarity__mutmut_4': xǁSemanticClustererǁ_token_similarity__mutmut_4, 
        'xǁSemanticClustererǁ_token_similarity__mutmut_5': xǁSemanticClustererǁ_token_similarity__mutmut_5, 
        'xǁSemanticClustererǁ_token_similarity__mutmut_6': xǁSemanticClustererǁ_token_similarity__mutmut_6, 
        'xǁSemanticClustererǁ_token_similarity__mutmut_7': xǁSemanticClustererǁ_token_similarity__mutmut_7, 
        'xǁSemanticClustererǁ_token_similarity__mutmut_8': xǁSemanticClustererǁ_token_similarity__mutmut_8, 
        'xǁSemanticClustererǁ_token_similarity__mutmut_9': xǁSemanticClustererǁ_token_similarity__mutmut_9, 
        'xǁSemanticClustererǁ_token_similarity__mutmut_10': xǁSemanticClustererǁ_token_similarity__mutmut_10, 
        'xǁSemanticClustererǁ_token_similarity__mutmut_11': xǁSemanticClustererǁ_token_similarity__mutmut_11, 
        'xǁSemanticClustererǁ_token_similarity__mutmut_12': xǁSemanticClustererǁ_token_similarity__mutmut_12, 
        'xǁSemanticClustererǁ_token_similarity__mutmut_13': xǁSemanticClustererǁ_token_similarity__mutmut_13, 
        'xǁSemanticClustererǁ_token_similarity__mutmut_14': xǁSemanticClustererǁ_token_similarity__mutmut_14, 
        'xǁSemanticClustererǁ_token_similarity__mutmut_15': xǁSemanticClustererǁ_token_similarity__mutmut_15, 
        'xǁSemanticClustererǁ_token_similarity__mutmut_16': xǁSemanticClustererǁ_token_similarity__mutmut_16
    }
    
    def _token_similarity(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSemanticClustererǁ_token_similarity__mutmut_orig"), object.__getattribute__(self, "xǁSemanticClustererǁ_token_similarity__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _token_similarity.__signature__ = _mutmut_signature(xǁSemanticClustererǁ_token_similarity__mutmut_orig)
    xǁSemanticClustererǁ_token_similarity__mutmut_orig.__name__ = 'xǁSemanticClustererǁ_token_similarity'

    def xǁSemanticClustererǁ_hash_text__mutmut_orig(self, text: str) -> str:
        """Generate hash for text."""
        return hashlib.sha256(text.encode()).hexdigest()[:16]

    def xǁSemanticClustererǁ_hash_text__mutmut_1(self, text: str) -> str:
        """Generate hash for text."""
        return hashlib.sha256(None).hexdigest()[:16]

    def xǁSemanticClustererǁ_hash_text__mutmut_2(self, text: str) -> str:
        """Generate hash for text."""
        return hashlib.sha256(text.encode()).hexdigest()[:17]
    
    xǁSemanticClustererǁ_hash_text__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSemanticClustererǁ_hash_text__mutmut_1': xǁSemanticClustererǁ_hash_text__mutmut_1, 
        'xǁSemanticClustererǁ_hash_text__mutmut_2': xǁSemanticClustererǁ_hash_text__mutmut_2
    }
    
    def _hash_text(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSemanticClustererǁ_hash_text__mutmut_orig"), object.__getattribute__(self, "xǁSemanticClustererǁ_hash_text__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _hash_text.__signature__ = _mutmut_signature(xǁSemanticClustererǁ_hash_text__mutmut_orig)
    xǁSemanticClustererǁ_hash_text__mutmut_orig.__name__ = 'xǁSemanticClustererǁ_hash_text'

    def xǁSemanticClustererǁ_generate_cluster_id__mutmut_orig(self, text: str) -> str:
        """Generate unique cluster ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        text_hash = self._hash_text(text)[:8]
        return f"cluster_{timestamp}_{text_hash}"

    def xǁSemanticClustererǁ_generate_cluster_id__mutmut_1(self, text: str) -> str:
        """Generate unique cluster ID."""
        timestamp = None
        text_hash = self._hash_text(text)[:8]
        return f"cluster_{timestamp}_{text_hash}"

    def xǁSemanticClustererǁ_generate_cluster_id__mutmut_2(self, text: str) -> str:
        """Generate unique cluster ID."""
        timestamp = datetime.now().strftime(None)
        text_hash = self._hash_text(text)[:8]
        return f"cluster_{timestamp}_{text_hash}"

    def xǁSemanticClustererǁ_generate_cluster_id__mutmut_3(self, text: str) -> str:
        """Generate unique cluster ID."""
        timestamp = datetime.now().strftime("XX%Y%m%d%H%M%S%fXX")
        text_hash = self._hash_text(text)[:8]
        return f"cluster_{timestamp}_{text_hash}"

    def xǁSemanticClustererǁ_generate_cluster_id__mutmut_4(self, text: str) -> str:
        """Generate unique cluster ID."""
        timestamp = datetime.now().strftime("%y%m%d%h%m%s%f")
        text_hash = self._hash_text(text)[:8]
        return f"cluster_{timestamp}_{text_hash}"

    def xǁSemanticClustererǁ_generate_cluster_id__mutmut_5(self, text: str) -> str:
        """Generate unique cluster ID."""
        timestamp = datetime.now().strftime("%Y%M%D%H%M%S%F")
        text_hash = self._hash_text(text)[:8]
        return f"cluster_{timestamp}_{text_hash}"

    def xǁSemanticClustererǁ_generate_cluster_id__mutmut_6(self, text: str) -> str:
        """Generate unique cluster ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        text_hash = None
        return f"cluster_{timestamp}_{text_hash}"

    def xǁSemanticClustererǁ_generate_cluster_id__mutmut_7(self, text: str) -> str:
        """Generate unique cluster ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        text_hash = self._hash_text(None)[:8]
        return f"cluster_{timestamp}_{text_hash}"

    def xǁSemanticClustererǁ_generate_cluster_id__mutmut_8(self, text: str) -> str:
        """Generate unique cluster ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        text_hash = self._hash_text(text)[:9]
        return f"cluster_{timestamp}_{text_hash}"
    
    xǁSemanticClustererǁ_generate_cluster_id__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSemanticClustererǁ_generate_cluster_id__mutmut_1': xǁSemanticClustererǁ_generate_cluster_id__mutmut_1, 
        'xǁSemanticClustererǁ_generate_cluster_id__mutmut_2': xǁSemanticClustererǁ_generate_cluster_id__mutmut_2, 
        'xǁSemanticClustererǁ_generate_cluster_id__mutmut_3': xǁSemanticClustererǁ_generate_cluster_id__mutmut_3, 
        'xǁSemanticClustererǁ_generate_cluster_id__mutmut_4': xǁSemanticClustererǁ_generate_cluster_id__mutmut_4, 
        'xǁSemanticClustererǁ_generate_cluster_id__mutmut_5': xǁSemanticClustererǁ_generate_cluster_id__mutmut_5, 
        'xǁSemanticClustererǁ_generate_cluster_id__mutmut_6': xǁSemanticClustererǁ_generate_cluster_id__mutmut_6, 
        'xǁSemanticClustererǁ_generate_cluster_id__mutmut_7': xǁSemanticClustererǁ_generate_cluster_id__mutmut_7, 
        'xǁSemanticClustererǁ_generate_cluster_id__mutmut_8': xǁSemanticClustererǁ_generate_cluster_id__mutmut_8
    }
    
    def _generate_cluster_id(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSemanticClustererǁ_generate_cluster_id__mutmut_orig"), object.__getattribute__(self, "xǁSemanticClustererǁ_generate_cluster_id__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _generate_cluster_id.__signature__ = _mutmut_signature(xǁSemanticClustererǁ_generate_cluster_id__mutmut_orig)
    xǁSemanticClustererǁ_generate_cluster_id__mutmut_orig.__name__ = 'xǁSemanticClustererǁ_generate_cluster_id'

    def xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_orig(self):
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

    def xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_1(self):
        """Remove smallest clusters when over limit."""
        if len(self._clusters) < self.max_clusters:
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

    def xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_2(self):
        """Remove smallest clusters when over limit."""
        if len(self._clusters) <= self.max_clusters:
            return

        # Sort by size (ascending) then confidence (ascending)
        sorted_clusters = None

        # Remove bottom 10%
        remove_count = max(1, len(sorted_clusters) // 10)
        for cluster_id, cluster in sorted_clusters[:remove_count]:
            # Remove text mappings
            for member in cluster.members:
                text_hash = self._hash_text(member.text)
                self._text_to_cluster.pop(text_hash, None)
            # Remove cluster
            del self._clusters[cluster_id]

    def xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_3(self):
        """Remove smallest clusters when over limit."""
        if len(self._clusters) <= self.max_clusters:
            return

        # Sort by size (ascending) then confidence (ascending)
        sorted_clusters = sorted(
            None, key=lambda x: (x[1].size, x[1].confidence_score)
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

    def xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_4(self):
        """Remove smallest clusters when over limit."""
        if len(self._clusters) <= self.max_clusters:
            return

        # Sort by size (ascending) then confidence (ascending)
        sorted_clusters = sorted(
            self._clusters.items(), key=None
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

    def xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_5(self):
        """Remove smallest clusters when over limit."""
        if len(self._clusters) <= self.max_clusters:
            return

        # Sort by size (ascending) then confidence (ascending)
        sorted_clusters = sorted(
            key=lambda x: (x[1].size, x[1].confidence_score)
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

    def xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_6(self):
        """Remove smallest clusters when over limit."""
        if len(self._clusters) <= self.max_clusters:
            return

        # Sort by size (ascending) then confidence (ascending)
        sorted_clusters = sorted(
            self._clusters.items(), )

        # Remove bottom 10%
        remove_count = max(1, len(sorted_clusters) // 10)
        for cluster_id, cluster in sorted_clusters[:remove_count]:
            # Remove text mappings
            for member in cluster.members:
                text_hash = self._hash_text(member.text)
                self._text_to_cluster.pop(text_hash, None)
            # Remove cluster
            del self._clusters[cluster_id]

    def xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_7(self):
        """Remove smallest clusters when over limit."""
        if len(self._clusters) <= self.max_clusters:
            return

        # Sort by size (ascending) then confidence (ascending)
        sorted_clusters = sorted(
            self._clusters.items(), key=lambda x: None
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

    def xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_8(self):
        """Remove smallest clusters when over limit."""
        if len(self._clusters) <= self.max_clusters:
            return

        # Sort by size (ascending) then confidence (ascending)
        sorted_clusters = sorted(
            self._clusters.items(), key=lambda x: (x[2].size, x[1].confidence_score)
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

    def xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_9(self):
        """Remove smallest clusters when over limit."""
        if len(self._clusters) <= self.max_clusters:
            return

        # Sort by size (ascending) then confidence (ascending)
        sorted_clusters = sorted(
            self._clusters.items(), key=lambda x: (x[1].size, x[2].confidence_score)
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

    def xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_10(self):
        """Remove smallest clusters when over limit."""
        if len(self._clusters) <= self.max_clusters:
            return

        # Sort by size (ascending) then confidence (ascending)
        sorted_clusters = sorted(
            self._clusters.items(), key=lambda x: (x[1].size, x[1].confidence_score)
        )

        # Remove bottom 10%
        remove_count = None
        for cluster_id, cluster in sorted_clusters[:remove_count]:
            # Remove text mappings
            for member in cluster.members:
                text_hash = self._hash_text(member.text)
                self._text_to_cluster.pop(text_hash, None)
            # Remove cluster
            del self._clusters[cluster_id]

    def xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_11(self):
        """Remove smallest clusters when over limit."""
        if len(self._clusters) <= self.max_clusters:
            return

        # Sort by size (ascending) then confidence (ascending)
        sorted_clusters = sorted(
            self._clusters.items(), key=lambda x: (x[1].size, x[1].confidence_score)
        )

        # Remove bottom 10%
        remove_count = max(None, len(sorted_clusters) // 10)
        for cluster_id, cluster in sorted_clusters[:remove_count]:
            # Remove text mappings
            for member in cluster.members:
                text_hash = self._hash_text(member.text)
                self._text_to_cluster.pop(text_hash, None)
            # Remove cluster
            del self._clusters[cluster_id]

    def xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_12(self):
        """Remove smallest clusters when over limit."""
        if len(self._clusters) <= self.max_clusters:
            return

        # Sort by size (ascending) then confidence (ascending)
        sorted_clusters = sorted(
            self._clusters.items(), key=lambda x: (x[1].size, x[1].confidence_score)
        )

        # Remove bottom 10%
        remove_count = max(1, None)
        for cluster_id, cluster in sorted_clusters[:remove_count]:
            # Remove text mappings
            for member in cluster.members:
                text_hash = self._hash_text(member.text)
                self._text_to_cluster.pop(text_hash, None)
            # Remove cluster
            del self._clusters[cluster_id]

    def xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_13(self):
        """Remove smallest clusters when over limit."""
        if len(self._clusters) <= self.max_clusters:
            return

        # Sort by size (ascending) then confidence (ascending)
        sorted_clusters = sorted(
            self._clusters.items(), key=lambda x: (x[1].size, x[1].confidence_score)
        )

        # Remove bottom 10%
        remove_count = max(len(sorted_clusters) // 10)
        for cluster_id, cluster in sorted_clusters[:remove_count]:
            # Remove text mappings
            for member in cluster.members:
                text_hash = self._hash_text(member.text)
                self._text_to_cluster.pop(text_hash, None)
            # Remove cluster
            del self._clusters[cluster_id]

    def xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_14(self):
        """Remove smallest clusters when over limit."""
        if len(self._clusters) <= self.max_clusters:
            return

        # Sort by size (ascending) then confidence (ascending)
        sorted_clusters = sorted(
            self._clusters.items(), key=lambda x: (x[1].size, x[1].confidence_score)
        )

        # Remove bottom 10%
        remove_count = max(1, )
        for cluster_id, cluster in sorted_clusters[:remove_count]:
            # Remove text mappings
            for member in cluster.members:
                text_hash = self._hash_text(member.text)
                self._text_to_cluster.pop(text_hash, None)
            # Remove cluster
            del self._clusters[cluster_id]

    def xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_15(self):
        """Remove smallest clusters when over limit."""
        if len(self._clusters) <= self.max_clusters:
            return

        # Sort by size (ascending) then confidence (ascending)
        sorted_clusters = sorted(
            self._clusters.items(), key=lambda x: (x[1].size, x[1].confidence_score)
        )

        # Remove bottom 10%
        remove_count = max(2, len(sorted_clusters) // 10)
        for cluster_id, cluster in sorted_clusters[:remove_count]:
            # Remove text mappings
            for member in cluster.members:
                text_hash = self._hash_text(member.text)
                self._text_to_cluster.pop(text_hash, None)
            # Remove cluster
            del self._clusters[cluster_id]

    def xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_16(self):
        """Remove smallest clusters when over limit."""
        if len(self._clusters) <= self.max_clusters:
            return

        # Sort by size (ascending) then confidence (ascending)
        sorted_clusters = sorted(
            self._clusters.items(), key=lambda x: (x[1].size, x[1].confidence_score)
        )

        # Remove bottom 10%
        remove_count = max(1, len(sorted_clusters) / 10)
        for cluster_id, cluster in sorted_clusters[:remove_count]:
            # Remove text mappings
            for member in cluster.members:
                text_hash = self._hash_text(member.text)
                self._text_to_cluster.pop(text_hash, None)
            # Remove cluster
            del self._clusters[cluster_id]

    def xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_17(self):
        """Remove smallest clusters when over limit."""
        if len(self._clusters) <= self.max_clusters:
            return

        # Sort by size (ascending) then confidence (ascending)
        sorted_clusters = sorted(
            self._clusters.items(), key=lambda x: (x[1].size, x[1].confidence_score)
        )

        # Remove bottom 10%
        remove_count = max(1, len(sorted_clusters) // 11)
        for cluster_id, cluster in sorted_clusters[:remove_count]:
            # Remove text mappings
            for member in cluster.members:
                text_hash = self._hash_text(member.text)
                self._text_to_cluster.pop(text_hash, None)
            # Remove cluster
            del self._clusters[cluster_id]

    def xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_18(self):
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
                text_hash = None
                self._text_to_cluster.pop(text_hash, None)
            # Remove cluster
            del self._clusters[cluster_id]

    def xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_19(self):
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
                text_hash = self._hash_text(None)
                self._text_to_cluster.pop(text_hash, None)
            # Remove cluster
            del self._clusters[cluster_id]

    def xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_20(self):
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
                self._text_to_cluster.pop(None, None)
            # Remove cluster
            del self._clusters[cluster_id]

    def xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_21(self):
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
                self._text_to_cluster.pop(None)
            # Remove cluster
            del self._clusters[cluster_id]

    def xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_22(self):
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
                self._text_to_cluster.pop(text_hash, )
            # Remove cluster
            del self._clusters[cluster_id]
    
    xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_1': xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_1, 
        'xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_2': xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_2, 
        'xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_3': xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_3, 
        'xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_4': xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_4, 
        'xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_5': xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_5, 
        'xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_6': xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_6, 
        'xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_7': xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_7, 
        'xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_8': xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_8, 
        'xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_9': xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_9, 
        'xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_10': xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_10, 
        'xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_11': xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_11, 
        'xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_12': xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_12, 
        'xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_13': xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_13, 
        'xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_14': xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_14, 
        'xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_15': xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_15, 
        'xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_16': xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_16, 
        'xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_17': xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_17, 
        'xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_18': xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_18, 
        'xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_19': xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_19, 
        'xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_20': xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_20, 
        'xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_21': xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_21, 
        'xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_22': xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_22
    }
    
    def _prune_smallest_clusters(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_orig"), object.__getattribute__(self, "xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _prune_smallest_clusters.__signature__ = _mutmut_signature(xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_orig)
    xǁSemanticClustererǁ_prune_smallest_clusters__mutmut_orig.__name__ = 'xǁSemanticClustererǁ_prune_smallest_clusters'
