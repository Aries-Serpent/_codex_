# MCP Testing Guide

## Mock-only test runs (default)

```bash
pytest -q tests/mcp -k "not live" --maxfail=1
pytest -q tests/embeddings -k "not live" --maxfail=1
pytest -q tests/test_retries.py tests/test_metrics.py tests/test_server_smoke.py --maxfail=1
```

## Local server (mock adapter)

```bash
python3 -m src.mcp.server.run --host 0.0.0.0 --port 8080
```

## Smoke checks

```bash
scripts/run_local_server.sh
scripts/smoke_test_local.sh
```

## Live tests

Live provider tests must be gated via `ENABLE_LIVE_TESTS=true` and repository secrets.
