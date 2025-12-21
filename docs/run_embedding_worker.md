# Running the Embedding Worker (Local & Docker)

Local (dev/mock)
- Ensure repo root is on PYTHONPATH:
  ```bash
  export PYTHONPATH="$(pwd):$PYTHONPATH"
  python -m venv .venv
  . .venv/bin/activate
  pip install -U pip
  pip install pytest
  python -m src.workers.embedding_worker --input samples/small_docs.json --batch-size 8
  ```

Docker (container)
- Build image:
  docker build -f Dockerfile.embedding -t mcp-embedding:local .
- Run via docker-compose:
  docker-compose -f docker-compose.embedding.yml up --build

Notes
- By default the worker uses the mock embedder and the in-repo mock backend; no provider secrets needed.
- To use a real provider, set EMBEDDER_CLASS to a provider adapter and add the required env vars. Only enable live-provider runs in controlled environments after reading docs/SECRETS_RUNBOOK.md.
