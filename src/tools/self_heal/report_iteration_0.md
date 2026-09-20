# CI Failures Resolution - Iteration 0 Report

## Status
**Iteration:** 0  
**Outcome:** Applied P1 fixes; validation executed with best-effort coverage.

## Changes Applied
1. **Marker completeness**
   - Added `ml_comprehensive` marker to `pytest.ini`.
   - Synced development marker list in `configs/development/pytest.ini`.
2. **CI rate-limit stability**
   - Added permissive `RATE_LIMIT_RATE` and `RATE_LIMIT_BURST` env vars in `.github/workflows/mcp-ci.yml`.

## Rationale
- **Unknown marker failures** were caused by strict marker enforcement and missing `ml_comprehensive`.
- **MCP 429 responses** were caused by default, overly strict rate limits in CI.

## Verification Commands
Executed with best effort on this iteration:
- `pytest -q tests/mcp -k "not live" --maxfail=1`
- `pytest -q tests/embeddings -k "not live" --maxfail=1`
- `pytest -q tests/test_retries.py tests/test_metrics.py tests/test_server_smoke.py --maxfail=1`
- `pytest -q tests/callbacks/test_callbacks_comprehensive.py -m ml_comprehensive --maxfail=1`

## Residual Risks
- **Rate limiter init timing:** If configuration is read only at import, test-level overrides may not take effect without reload.
- **Dependency availability:** ML comprehensive tests may still require optional deps (torch, transformers).

## Next Iteration Notes
- If 429s persist, locate the rate limiter config and apply test-level monkeypatch + reload.
- Add a minimal rate-limiter regression test to keep coverage of strict limits.
