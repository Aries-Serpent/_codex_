# B2 RAG Index Health Report

## Verdict
- Build path: PASS (deterministic offline fallback)
- Structure validation: PASS
- Query validation: PASS
- Coverage gate (>=95%): FAIL
- Performance gate (p99 < 500ms): PASS

## B2.1 Build from scratch
- Builder located at `src/aries_serpent_core/rag/indexer.py`
- Validation mode: `deterministic_offline_validation`
- Index path: `.codex/lane2_b2_b5_workspace/indices/lane2/lane2-validation`
- Build time: 31.63 ms
- Multi-index lifecycle: create=True, list=True, delete=True

## B2.2 Structure validation
- Embedding provider: `TfidfEmbeddingProvider`
- Vector count: 200
- Chunk count: 200
- Dimension: 237
- Files indexed: 100
- Metadata integrity: files/chunks/index metadata all persisted and reloadable

## B2.3 Query test with 100 queries
- Queries executed: 100
- Successful queries: 100
- Top-1 topic accuracy: 100.00%
- Precision@5: 100.00%
- Recall@5: 100.00%

## B2.4 Coverage check
- `src/aries_serpent_core/rag/indexer.py`: 48.99%
- `src/aries_serpent_core/rag/retriever.py`: 58.90%
- Target: 95.00%
- Status: FAIL

## B2.5 Performance baseline
- p50: 0.399 ms
- p95: 0.451 ms
- p99: 0.573 ms
- Mean: 0.406 ms
- Status: PASS

## Summary
B2 functional validation passed, but promotion remains blocked by retrieval coverage far below the 95% gate.
