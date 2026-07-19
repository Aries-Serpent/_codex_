# B3 Embedding Lifecycle Report

## Verdict
- Embedding regeneration: PASS
- Stale entry eviction: PASS
- TTL enforcement: PASS
- End-to-end lifecycle: PASS
- Coverage gate (>=85%): FAIL

## B3.1 Regenerate embeddings
- Provider used: `TfidfEmbeddingProvider`
- Test embedding shape: [3, 21]
- Cache reuse confirmed: True
- Cached provider hit rate: 50.00%

## B3.2 Stale entry eviction
- Freshness loop doc present: True
- Embedding evicted after TTL: True
- Query evicted after TTL: True
- Capacity eviction respected: embeddings=True, queries=True

## B3.3 TTL enforcement
- Embedding default TTL: 3600.0 s
- Query default TTL: 300.0 s
- Before expiry visibility: embedding=True, query=True

## B3.4 End-to-end lifecycle
- Flow validated: insert -> query -> stale mark (TTL expiry) -> evict
- Query cache stats: {'hits': 1, 'misses': 1, 'evictions': 1, 'expirations': 1, 'hit_rate': 0.5, 'size': 2, 'max_size': 2, 'total_requests': 2}
- Embedding cache stats: {'size': 2, 'max_size': 2, 'hits': 1, 'misses': 1, 'hit_rate': 0.5, 'memory_bytes': 168, 'memory_mb': 0.00016021728515625, 'dtype': 'float32'}

## B3.5 Coverage check
- `src/aries_serpent_core/rag/embeddings.py`: 38.75%
- `src/aries_serpent_core/rag/cache/embedding_cache.py`: 46.75%
- `src/aries_serpent_core/rag/cache/query_cache.py`: 59.91%
- Target: 85.00%
- Status: FAIL

## Summary
Lifecycle mechanics behave correctly, but embedding/lifecycle code coverage is materially below the required threshold.
