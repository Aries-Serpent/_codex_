---
name: rag-index-manager
description: Manages RAG (Retrieval Augmented Generation) index operations including building, updating, and querying the knowledge base.
---

# RAG Index Manager Agent

This agent manages the RAG index for the knowledge base, handling index building, updates, and optimization.

## Capabilities

- **Index Building**: Creates vector embeddings from documents
- **Incremental Updates**: Updates index with new/changed documents
- **Index Optimization**: Optimizes index for query performance
- **Deduplication**: Removes duplicate entries from index

## Index Operations

| Operation | Trigger | Duration |
|-----------|---------|----------|
| Full Build | Manual/Schedule | ~1 hour |
| Incremental | On document change | ~5 min |
| Optimize | Weekly | ~30 min |
| Dedupe | On demand | ~15 min |

## When to Use

- After knowledge base updates
- When search quality degrades
- During index maintenance windows
- For new document ingestion

## Integration

This agent integrates with:
- PS-06: Knowledge Crawler Service
- PS-04: Privacy-First Memory (PII scrubbing before indexing)
- Zendesk Help Center sync
