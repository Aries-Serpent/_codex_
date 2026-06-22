# ADR-20260302: FAISS Memory Corpus for Semantic Agent Routing
> Generated: 2026-06-22T07:00:00Z | Author: copilot-swe-agent[bot]
> Status: Accepted
> Related PRs: #3447

## 1. Context

The orchestrator routing system (`scripts/ci/orchestrator_routing.py`)
uses a 3-strategy approach to match tasks to specialized agents:

1. **FAISS semantic search** — embedding-based similarity matching.
2. **SQLite keyword search** — full-text search fallback.
3. **Static capability tags** — AGENT_REGISTRY.yaml `capability_tags` field.

Without a pre-built FAISS index, the orchestrator falls back to SQLite
keyword search, which lacks semantic understanding. For example, a query
like "fix flaky integration tests" would not match an agent described as
"stabilize intermittent CI failures" without exact keyword overlap.

## 2. Problem Statement

Select an embedding model and indexing strategy that enables offline
semantic search over the agent corpus (152 agents, ~500 capability
descriptions) while meeting these constraints:

- No external API calls (air-gapped CI environments).
- Apache 2.0 or equivalent permissive license.
- Index rebuild must complete within CI time limits (< 5 minutes).
- Retention policy to prevent unbounded index growth.

## 3. Decision

Use **all-MiniLM-L6-v2** (sentence-transformers, Apache 2.0) with the
following indexing parameters:

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Model | `all-MiniLM-L6-v2` | 384-dim, fast, offline, Apache 2.0 |
| Chunk size | 512 words | Balances context window vs granularity |
| Index type | FAISS `IndexFlatIP` | Exact inner-product; corpus is small enough |
| Rebuild trigger | Nightly at 02:00 UTC + on registry push to main |
| Retention | 90 days (enforced by `prune_corpus.py`) |
| Storage | `.codex/embeddings/` (gitignored, rebuilt in CI) |

Scripts created:
- `scripts/ci/build_embeddings.py` — builds the FAISS index from registry + agent docs.
- `scripts/ci/query_corpus.py` — queries the index with semantic + keyword fallback.
- `scripts/ci/prune_corpus.py` — enforces 90-day retention on stale corpus entries.

CI workflow: `embedding-index-rebuild.yml` (currently Tier-2 canary, nightly schedule).

## 4. Decision Drivers

| Driver | Notes |
|--------|-------|
| Offline requirement | CI runners may not have internet access |
| License compliance | Apache 2.0 required for open-source compatibility |
| Rebuild speed | Must complete within 5-minute CI budget |
| Semantic quality | Keyword search insufficient for synonym matching |
| Retention governance | Unbounded indices waste disk and slow queries |

## 5. Considered Alternatives

| Alternative | Rejected Because |
|-------------|------------------|
| OpenAI text-embedding-ada-002 | Requires API key; not offline-capable |
| Elasticsearch / Typesense | Heavyweight runtime dependency for small corpus |
| BM25 (rank-bm25 library) | Better than keyword but lacks true semantic understanding |
| Larger model (all-mpnet-base-v2) | 768-dim, 3x slower build; marginal quality gain for small corpus |
| ChromaDB | Additional dependency; FAISS is already used elsewhere in the codebase |

## 6. Consequences

### Positive
- Orchestrator routing gains semantic understanding (synonym matching, paraphrase detection).
- Index rebuilds in < 2 minutes for 152 agents.
- 90-day retention prevents unbounded growth.
- No external API dependencies.

### Negative
- FAISS index files are not committed to git (must be rebuilt in CI or locally).
- First CI run after a fresh clone requires an explicit build step.
- Model download (~80 MB) needed on first build (cached in CI thereafter).

### Risks & Mitigations
- **Risk**: Model download fails in air-gapped environments.
  **Mitigation**: `build_embeddings.py` supports `--model-path` for pre-downloaded models;
  CI caches the model in GitHub Actions cache.
- **Risk**: Index becomes stale between nightly rebuilds.
  **Mitigation**: `agent-registry-validation.yml` can trigger rebuild on push to main
  (TASK 1 in SESSION_RESTORE_GROUNDED_FOLLOWUP.md).
- **Risk**: Embedding quality degrades for domain-specific terms.
  **Mitigation**: Capability tags provide exact-match fallback (strategy 3).

## 7. Provenance & Compliance
- **Model**: `sentence-transformers/all-MiniLM-L6-v2` (Apache 2.0)
- **Index storage**: `.codex/embeddings/` (gitignored)
- **Retention**: 90 days, enforced by `scripts/ci/prune_corpus.py`
- **CI workflow**: `.github/workflows/embedding-index-rebuild.yml` (Tier-2 canary)
- **Change log**: PR #3447 merged to main
