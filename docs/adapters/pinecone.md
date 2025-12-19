# Pinecone Adapter (Plan B) — Quick Guide

Env vars (document in .env.example):
- PINECONE_API_KEY
- PINECONE_ENV
- PINECONE_INDEX_NAME (optional; defaults to 'mcp-index')
- PINECONE_MAX_RETRIES (optional; default in adapter)

Safety & gating
- Live-provider operations (upsert/query/delete) are guarded by ENABLE_LIVE_TESTS.
- To enable live tests (only in controlled environments), set:
  - ENABLE_LIVE_TESTS=true
  - Add provider secrets in GitHub Secrets (PINECONE_API_KEY, PINECONE_ENV)
- DO NOT commit real credentials to the repository.

Recorded fixtures
- Sample recorded responses live under tests/integration/fixtures/recorded_pinecone/.

Backup/restore
- See tools/backup/pinecone_export.sh for the placeholder export scaffolding.
