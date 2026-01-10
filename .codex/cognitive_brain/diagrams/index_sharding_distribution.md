# Index Sharding Distribution Model

## Overview

This diagram illustrates the consistent hashing-based index sharding system for scaling the Knowledge Crawler to handle 100k+ documents.

## Sharding Architecture

```mermaid
graph TB
    subgraph "Document Ingestion"
        DOC[Document Stream] --> HASH[Hash Function<br/>MD5/xxhash]
        HASH --> RING[Consistent Hash Ring]
    end
    
    subgraph "Hash Ring (Virtual Nodes)"
        RING --> VN0[Virtual Node 0<br/>→ Shard 0]
        RING --> VN1[Virtual Node 1<br/>→ Shard 1]
        RING --> VN2[Virtual Node 2<br/>→ Shard 0]
        RING --> VN3[Virtual Node 3<br/>→ Shard 2]
        RING --> VN4[Virtual Node 4<br/>→ Shard 1]
        RING --> VN5[Virtual Node N<br/>→ Shard 3]
    end
    
    subgraph "Physical Shards"
        S0[(Shard 0<br/>vectors_shard_00)]
        S1[(Shard 1<br/>vectors_shard_01)]
        S2[(Shard 2<br/>vectors_shard_02)]
        S3[(Shard 3<br/>vectors_shard_03)]
    end
    
    VN0 --> S0
    VN2 --> S0
    VN1 --> S1
    VN4 --> S1
    VN3 --> S2
    VN5 --> S3
    
    subgraph "Query Processing"
        QUERY[Query Vector] --> SCATTER[Scatter Query<br/>to All Shards]
        SCATTER --> S0
        SCATTER --> S1
        SCATTER --> S2
        SCATTER --> S3
        
        S0 --> R0[Top K Results]
        S1 --> R1[Top K Results]
        S2 --> R2[Top K Results]
        S3 --> R3[Top K Results]
        
        R0 --> GATHER[Gather & Re-rank]
        R1 --> GATHER
        R2 --> GATHER
        R3 --> GATHER
        
        GATHER --> FINAL[Final Top K Results]
    end
    
    style RING fill:#9cf,stroke:#333,stroke-width:3px
    style S0 fill:#f96,stroke:#333,stroke-width:2px
    style S1 fill:#f96,stroke:#333,stroke-width:2px
    style S2 fill:#f96,stroke:#333,stroke-width:2px
    style S3 fill:#f96,stroke:#333,stroke-width:2px
    style GATHER fill:#9f9,stroke:#333,stroke-width:3px
```

## Consistent Hashing Algorithm

### Document to Shard Mapping

```python
def map_document_to_shard(document_id: str, num_shards: int) -> int:
    """Map document to shard using consistent hashing."""
    # Hash document ID
    hash_value = xxhash.xxh64(document_id.encode()).intdigest()
    
    # Find position in ring
    position = bisect.bisect_right(ring_positions, hash_value)
    virtual_node = ring[position % len(ring)]
    
    # Map virtual node to physical shard
    shard_id = virtual_node_to_shard[virtual_node]
    
    return shard_id
```

### Virtual Nodes Distribution

```mermaid
pie title "Virtual Nodes per Shard (4 shards, 150 vnodes each)"
    "Shard 0" : 150
    "Shard 1" : 150
    "Shard 2" : 150
    "Shard 3" : 150
```

## Scatter-Gather Query Pattern

### Query Flow

```mermaid
sequenceDiagram
    participant Client
    participant Store as PGVectorStore
    participant Pool as Connection Pool
    participant S0 as Shard 0
    participant S1 as Shard 1
    participant S2 as Shard 2
    participant S3 as Shard 3
    
    Client->>Store: search(query_vector, top_k=10)
    Store->>Pool: Get connections (4 parallel)
    
    par Scatter to all shards
        Store->>S0: SELECT TOP 20 FROM vectors_shard_00
        Store->>S1: SELECT TOP 20 FROM vectors_shard_01
        Store->>S2: SELECT TOP 20 FROM vectors_shard_02
        Store->>S3: SELECT TOP 20 FROM vectors_shard_03
    end
    
    S0-->>Store: Results (20)
    S1-->>Store: Results (20)
    S2-->>Store: Results (20)
    S3-->>Store: Results (20)
    
    Store->>Store: Gather all results (80 total)
    Store->>Store: Global re-rank by score
    Store->>Store: Take top 10
    
    Store-->>Client: Final results (10)
```

### Performance Characteristics

| Operation | Single Shard | 4 Shards (Scatter-Gather) |
|-----------|-------------|---------------------------|
| Query Latency | 50ms | 55ms (+10%) |
| Throughput | 100 QPS | 380 QPS (+280%) |
| Storage | 25GB limit | 100GB (4x25GB) |
| Index Size | 100K docs | 400K docs |

## Shard Balancing

### Load Distribution

```mermaid
graph LR
    subgraph "Balanced Distribution (Goal)"
        B0[Shard 0<br/>25,000 docs]
        B1[Shard 1<br/>25,100 docs]
        B2[Shard 2<br/>24,950 docs]
        B3[Shard 3<br/>24,950 docs]
    end
    
    subgraph "Imbalanced Distribution (Problem)"
        I0[Shard 0<br/>45,000 docs]
        I1[Shard 1<br/>15,000 docs]
        I2[Shard 2<br/>20,000 docs]
        I3[Shard 3<br/>20,000 docs]
    end
    
    I0 -.->|Rebalance| B0
    I1 -.->|Rebalance| B1
    I2 -.->|Rebalance| B2
    I3 -.->|Rebalance| B3
    
    style B0 fill:#9f9,stroke:#333,stroke-width:2px
    style B1 fill:#9f9,stroke:#333,stroke-width:2px
    style B2 fill:#9f9,stroke:#333,stroke-width:2px
    style B3 fill:#9f9,stroke:#333,stroke-width:2px
    
    style I0 fill:#f96,stroke:#333,stroke-width:2px
```

### Rebalancing Strategy

1. **Monitor** shard sizes every 24 hours
2. **Detect** imbalance: max/min ratio > 1.5
3. **Identify** overloaded shards
4. **Migrate** documents to underloaded shards
5. **Validate** new distribution

## Configuration

```yaml
# Sharding Configuration
sharding:
  num_shards: 4
  virtual_nodes_per_shard: 150
  hash_function: xxhash  # or md5
  
  # Rebalancing
  rebalance:
    enabled: true
    check_interval_hours: 24
    imbalance_threshold: 1.5
    max_migration_docs_per_cycle: 1000

# PGVector Store Configuration
pgvector:
  connection_string: "postgresql://user:pass@host/db"
  pool_size: 10
  shard_prefix: "vectors_shard_"
  
  # Index Settings
  index:
    type: hnsw
    m: 16  # HNSW parameter
    ef_construction: 64
```

## Monitoring Metrics

### Per-Shard Metrics

- **Document Count**: Number of documents in shard
- **Size (MB)**: Physical storage size
- **Query Latency (p50, p95, p99)**: Search performance
- **Insert Rate**: Documents per second
- **Load Factor**: Current load vs capacity

### System-Wide Metrics

- **Total Documents**: Sum across all shards
- **Imbalance Ratio**: max_shard_size / min_shard_size
- **Query Throughput**: Queries per second
- **Scatter-Gather Overhead**: Multi-shard latency penalty

## References

- **Implementation**: `src/codex/retrieval/sharding.py`
- **Store**: `src/codex/retrieval/stores/pgvector_store.py`
- **Tests**: `tests/retrieval/test_sharding.py`
