# META_TENSOR_VALIDATION_REPORT

Date: 2026-07-07
Source: lane2-metatensor (meta-tensor-validator)

## Executive Summary

- `src/cognitive_brain/**` has no direct heavy-model import dependency by default.
- Safe loading patterns exist in RAG model utilities.
- Non-RAG loaders still include medium-risk meta/materialization gaps.

## Findings

| Severity | Finding | Evidence |
|---|---|---|
| High | Recovery path can reinitialize params after empty materialization | `src/codex/rag/utils.py` |
| Medium | Some SentenceTransformer/CrossEncoder loads bypass safe wrapper behavior | `src/codex/docs_agent/semantic_indexer.py`, `src/codex/logging/session_embeddings.py`, `src/codex/retrieval/*` |
| Medium | Offline mode defaults can be weakened by online fallback defaults | `src/codex/rag/materialization_prevention.py` |
| Medium | Import-time heavy model load in one ingestion path | `cognitive/ingestion/Note_v2.py` |

## Recommended Remediations

1. Standardize all model loads through safe wrappers with explicit device/meta checks.
2. Remove import-time model initialization; switch to lazy load.
3. Keep offline flags fail-closed in isolated mode.
4. Validate meta-tensor recovery flow does not silently degrade pretrained behavior.
