# Embeddings — Worker & Provider Configuration

Purpose
- Document how to configure and run the embedding worker safely.

Configuration variables
- EMBEDDER_CLASS: Python import path for embedder (default: src.mcp.embeddings.mock_embedder.MockEmbedder)
- OPENAI_API_KEY: OpenAI API key (do NOT commit)
- HF_API_TOKEN: Hugging Face token (do NOT commit)
- EMBEDDING_BATCH_SIZE: default batch size for worker (int)
- EMBEDDING_MAX_RETRIES: number of retry attempts for networked embed calls
- EMBEDDING_BACKOFF_BASE: base seconds for exponential backoff
- EMBEDDING_WORKER_NAMESPACE_DEFAULT: default namespace/tenant

Running worker locally
- Prepare a JSON file with a list of items:
  ```json
  [{"id":"1","content":"text","metadata":{}}, {"id":"2","content":"another","metadata":{}}]
  ```
- Run:
  ```bash
  python -m src.workers.embedding_worker --input path/to/sample.json --batch-size 32
  ```

Recorded / gated live runs
- For recorded-mode runs, use recorded fixtures under tests/integration/fixtures/recorded_openai/.
- Live-provider runs must be gated: set ENABLE_LIVE_TESTS=true and add provider secrets to GitHub Secrets or env (see docs/SECRETS_RUNBOOK.md).
