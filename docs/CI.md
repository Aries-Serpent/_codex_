# CI notes: MCP mock-based testing

Purpose
- Ensure MCP protocol tests run reliably in CI without external provider secrets by default.

How it works
- The `mcp-ci.yml` workflow runs tests under `tests/mcp` and `tests/embeddings` using the in-repo mock backend.
- Live integration jobs (calling Pinecone / Supabase) are intentionally gated and require secrets — they will be added as separate workflows.

Local run
- Install dev deps:
  python -m venv .venv && source .venv/bin/activate
  pip install -r requirements-test.txt
- Run tests:
  pytest -q tests/mcp tests/embeddings --maxfail=1

CI considerations
- Keep tests deterministic (the mock backend uses deterministic cosine scoring).
- Avoid referencing provider environment variables in unit tests; the mock backend should be used unless an integration test is explicitly requested.
