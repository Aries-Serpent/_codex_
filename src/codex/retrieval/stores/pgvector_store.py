"""
PostgreSQL pgvector Store with Scatter-Gather & Shard Support

This module implements a production-ready PGVector store with:
- Asynchronous scatter-gather query pattern
- Shard-aware operations
- Connection pooling
- Global re-ranking

Part of PS-06 Enhancement: Index Sharding - Priority 4
"""

import asyncio
import logging
from typing import Any, Optional, List, Dict
from dataclasses import dataclass

import numpy as np

logger = logging.getLogger(__name__)

# Check for optional dependencies
try:
    from psycopg_pool import AsyncConnectionPool
    HAS_PSYCOPG3 = True
except ImportError:
    HAS_PSYCOPG3 = False
    AsyncConnectionPool = None  # type: ignore
    logger.warning("psycopg3 not installed - PGVectorStore will be stub only")

# Optional dependency: scikit-learn for future centroid-based partitioning
# TODO(PS-06, semantic-sharding): Implement KMeans clustering for intelligent
# shard balancing based on document embeddings. This would enable semantic-aware
# sharding where similar documents are co-located on the same shard for improved
# query performance. Tracked as part of PS-06: Index Sharding (Priority 4). Current
# implementation: Uses hash-based consistent sharding only (see lines 307–316 for
# the current hash-based sharding logic in PGVectorStore).
try:
    from sklearn.cluster import KMeans  # noqa: F401
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    KMeans = None  # type: ignore
    logger.info("scikit-learn not installed - Centroid-based partitioning unavailable")


@dataclass
class SearchResult:
    """Result from vector search."""
    document_id: str
    content: str
    score: float
    metadata: Dict[str, Any]
    shard_id: int


class PGVectorStore:
    """PostgreSQL pgvector store with scatter-gather shard support.
    
    Features:
    - Async scatter-gather queries across shards
    - Connection pooling for concurrent queries
    - Centroid-based partitioning (optional)
    - Global re-ranking across shards
    - Batch write optimization
    
    Example:
        >>> store = PGVectorStore(
        ...     connection_string="postgresql://...",
        ...     num_shards=4
        ... )
        >>> await store.initialize()
        >>> results = await store.search(query_vector, top_k=10)
    """

    def __init__(
        self,
        connection_string: Optional[str] = None,
        num_shards: int = 4,
        pool_size: int = 10,
        shard_id: Optional[int] = None,
    ):
        """Initialize PGVector store.
        
        Args:
            connection_string: PostgreSQL connection string
            num_shards: Total number of shards
            pool_size: Connection pool size
            shard_id: If provided, operate on single shard only
        """
        self.connection_string = connection_string
        self.num_shards = num_shards
        self.pool_size = pool_size
        self.shard_id = shard_id  # None = operate on all shards
        self.pool: Optional[AsyncConnectionPool] = None
        
        if not HAS_PSYCOPG3:
            logger.warning(
                "PGVectorStore is disabled: psycopg3 not installed. "
                "Use FAISSStore for local vector search."
            )
        
        if not connection_string:
            logger.warning(
                "PGVectorStore initialized without connection string. "
                "Call initialize() with connection_string to enable."
            )
    
    async def initialize(self, connection_string: Optional[str] = None) -> None:
        """Initialize connection pool and create tables.
        
        Args:
            connection_string: Override connection string
        """
        if not HAS_PSYCOPG3:
            raise RuntimeError(
                "PGVectorStore requires psycopg3. "
                "Install: pip install psycopg[binary,pool]"
            )
        
        conn_str = connection_string or self.connection_string
        if not conn_str:
            raise ValueError("connection_string required")
        
        self.connection_string = conn_str
        
        # Create async connection pool
        self.pool = AsyncConnectionPool(
            conn_str,
            min_size=2,
            max_size=self.pool_size,
        )
        
        # Create shard tables
        await self._create_shard_tables()
        
        logger.info(
            f"PGVectorStore initialized: {self.num_shards} shards, "
            f"pool size {self.pool_size}"
        )
    
    async def _create_shard_tables(self) -> None:
        """Create shard tables with pgvector extension."""
        if not self.pool:
            raise RuntimeError("Pool not initialized")
        
        target_shards = (
            [self.shard_id] if self.shard_id is not None
            else range(self.num_shards)
        )
        
        async with self.pool.connection() as conn:
            # Enable pgvector extension
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            
            for shard_id in target_shards:
                table_name = f"vectors_shard_{shard_id:02d}"
                
                # Create shard table with HNSW index
                await conn.execute(f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        id TEXT PRIMARY KEY,
                        embedding vector(1536),
                        content TEXT,
                        metadata JSONB,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                
                # Create HNSW index for fast similarity search
                await conn.execute(f"""
                    CREATE INDEX IF NOT EXISTS {table_name}_embedding_idx
                    ON {table_name}
                    USING hnsw (embedding vector_cosine_ops)
                """)
                
            await conn.commit()
            logger.info(f"Created {len(target_shards)} shard tables")
    
    async def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 5,
        target_shards: Optional[List[int]] = None,
    ) -> List[SearchResult]:
        """Scatter-gather search across shards.
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            target_shards: Optional list of shards to query (default: all)
            
        Returns:
            List of search results, globally re-ranked
        """
        if not HAS_PSYCOPG3:
            raise RuntimeError(
                "PGVectorStore not available in offline mode. Use FAISSStore."
            )
        
        if not self.pool:
            raise RuntimeError("Call initialize() first")
        
        # Determine target shards
        if self.shard_id is not None:
            shards_to_query = [self.shard_id]
        elif target_shards:
            shards_to_query = target_shards
        else:
            shards_to_query = list(range(self.num_shards))
        
        # Scatter: Query all shards in parallel
        tasks = [
            self._query_single_shard(shard_id, query_vector, top_k * 2)
            for shard_id in shards_to_query
        ]
        shard_results = await asyncio.gather(*tasks)
        
        # Gather: Combine results from all shards
        all_results = []
        for shard_id, results in zip(shards_to_query, shard_results):
            all_results.extend(results)
        
        # Global re-ranking by score
        all_results.sort(key=lambda r: r.score, reverse=True)
        
        return all_results[:top_k]
    
    async def _query_single_shard(
        self,
        shard_id: int,
        query_vector: np.ndarray,
        limit: int,
    ) -> List[SearchResult]:
        """Query a single shard.
        
        Args:
            shard_id: Shard ID to query
            query_vector: Query embedding
            limit: Max results from this shard
            
        Returns:
            List of search results from this shard
        """
        if not self.pool:
            return []
        
        table_name = f"vectors_shard_{shard_id:02d}"
        
        async with self.pool.connection() as conn:
            # Execute local HNSW search on shard
            cursor = await conn.execute(
                f"""
                SELECT id, content, metadata, 
                       1 - (embedding <=> %s::vector) as score
                FROM {table_name}
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (query_vector.tolist(), query_vector.tolist(), limit)
            )
            
            rows = await cursor.fetchall()
            
            return [
                SearchResult(
                    document_id=row[0],
                    content=row[1],
                    metadata=row[2],
                    score=float(row[3]),
                    shard_id=shard_id,
                )
                for row in rows
            ]
    
    async def insert_batch(
        self,
        documents: List[Dict[str, Any]],
        embeddings: np.ndarray,
        shard_mapper: Optional[callable] = None,
    ) -> None:
        """Batch insert documents with pipeline optimization.
        
        Args:
            documents: List of documents with 'id', 'content', 'metadata'
            embeddings: Embedding vectors (one per document)
            shard_mapper: Optional function to map document to shard
        """
        if not HAS_PSYCOPG3:
            raise RuntimeError("PGVectorStore not available")
        
        if not self.pool:
            raise RuntimeError("Call initialize() first")
        
        # Group documents by shard
        shard_groups: Dict[int, List[tuple]] = {
            i: [] for i in range(self.num_shards)
        }
        
        for doc, emb in zip(documents, embeddings):
            if shard_mapper:
                shard_id = shard_mapper(doc['id'])
            else:
                # Simple hash-based sharding using xxhash (faster than MD5)
                # For production with multi-process sharding, xxhash is required
                # for deterministic routing. The MD5 fallback ensures determinism
                # across Python sessions/processes.
                try:
                    import xxhash
                    hash_val = xxhash.xxh64(doc['id'].encode()).intdigest()
                except ImportError:
                    # Fallback to MD5 for deterministic sharding when xxhash unavailable
                    import hashlib
                    hash_val = int.from_bytes(
                        hashlib.md5(doc['id'].encode()).digest()[:8], 
                        'big'
                    )
                shard_id = hash_val % self.num_shards
            
            shard_groups[shard_id].append((
                doc['id'],
                emb.tolist(),
                doc.get('content', ''),
                doc.get('metadata', {}),
            ))
        
        # Insert to each shard using pipeline
        tasks = [
            self._insert_to_shard(shard_id, docs)
            for shard_id, docs in shard_groups.items()
            if docs
        ]
        await asyncio.gather(*tasks)
        
        logger.info(f"Inserted {len(documents)} documents across {len(tasks)} shards")
    
    async def _insert_to_shard(
        self,
        shard_id: int,
        documents: List[tuple],
    ) -> None:
        """Insert documents to a single shard using pipeline."""
        if not self.pool:
            return
        
        table_name = f"vectors_shard_{shard_id:02d}"
        
        async with self.pool.connection() as conn:
            async with conn.pipeline():
                for doc_id, embedding, content, metadata in documents:
                    await conn.execute(
                        f"""
                        INSERT INTO {table_name} (id, embedding, content, metadata)
                        VALUES (%s, %s::vector, %s, %s)
                        ON CONFLICT (id) DO UPDATE
                        SET embedding = EXCLUDED.embedding,
                            content = EXCLUDED.content,
                            metadata = EXCLUDED.metadata
                        """,
                        (doc_id, embedding, content, metadata)
                    )
            await conn.commit()
    
    async def close(self) -> None:
        """Close connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("PGVectorStore connection pool closed")
    
    # Stub methods for backward compatibility
    def create_index(self, embeddings: np.ndarray, documents: list[dict[str, Any]]):
        """Stub: Use async insert_batch() instead."""
        raise RuntimeError(
            "Use async methods: await store.initialize() then "
            "await store.insert_batch(documents, embeddings)"
        )

    def save(self):
        """Stub: Data is persisted automatically in PostgreSQL."""
        raise RuntimeError("Data is automatically persisted in PostgreSQL")

    def load(self):
        """Stub: Data is loaded automatically from PostgreSQL."""
        raise RuntimeError("Data is automatically loaded from PostgreSQL")
