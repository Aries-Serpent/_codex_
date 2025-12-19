# Plan for CI Failures Resolution

## 1. Exec Summary
**Core issues**
1. `ml_comprehensive` marker missing from `pytest.ini`, causing strict-marker failures.
2. MCP tests returning HTTP 429 due to strict rate limiting in CI, lacking permissive env overrides.

**Approach**
Apply minimal configuration fixes, then validate via focused test runs. Introduce a self-healing loop to detect and remediate similar failures, with iteration tracking and controlled automation.

## 2. Components
- **Test Config**
  - Files: `pytest.ini`, `configs/development/pytest.ini`
  - Concerns: marker completeness, strict-markers behavior, config drift between environments.
- **CI Workflows**
  - Files: `.github/workflows/mcp-ci.yml`, `optimized-ci.yml` (context)
  - Concerns: test env vars, rate-limit stability, secret clearing.
- **Rate Limiter / Middleware**
  - Files: locate via search (e.g., `RATE_LIMIT_RATE` / `RATE_LIMIT_BURST`)
  - Concerns: init-time env reads, global state across tests.
- **Tests**
  - Files: `tests/callbacks/test_callbacks_comprehensive.py`, `tests/mcp/test_facade.py`
  - Concerns: marker enforcement, CI rate-limit exposure, environment isolation.
- **Observability**
  - CI logs, pytest output, and iteration reports under `tools/self_heal/`.
- **Self-Healing**
  - Analyzer → Fixer → Verifier → Reporter → Orchestrator loop for CI failures.

## 3. Root Causes
- **Pytest marker gap:** `ml_comprehensive` is used in tests but absent from `pytest.ini`, causing `--strict-markers` failure.
- **MCP rate limiting:** CI uses default rate limits that are too strict; missing env overrides lead to 429 responses.
- **State persistence:** Rate limiter may read env at import time, limiting test-level overrides.

## 4. Fixes
### A. Add missing pytest marker
- File: `pytest.ini`
- Change: add `ml_comprehensive: Comprehensive ML tests for callback systems`.

### B. Sync development marker list
- File: `configs/development/pytest.ini`
- Change: add the same `ml_comprehensive` marker to prevent config drift.

### C. Add permissive CI rate limits
- File: `.github/workflows/mcp-ci.yml`
- Change: add `RATE_LIMIT_RATE=1000` and `RATE_LIMIT_BURST=1000` to test env.

### D. (Conditional) Test-level overrides
- File: `tests/mcp/test_facade.py` (if 429s persist)
- Change: monkeypatch env + reload rate limiter/app module to pick up test values.

## 5. Self-Healing Process
1. **Analyze** CI logs for known signatures (unknown markers, 429s).
2. **Propose** minimal diffs (config/env changes).
3. **Apply** patches in small, isolated commits.
4. **Verify** with targeted pytest commands.
5. **Report** iteration summary under `tools/self_heal/`.
6. **Repeat** until high/medium issues are resolved.

## 6. Iteration 0
**Findings**
1. Missing `ml_comprehensive` marker (high)
2. Missing CI env overrides (high)
3. Config drift between root and dev pytest.ini (medium)

**Actions**
- Apply fixes A–C.
- Record results in `tools/self_heal/report_iteration_0.md`.

## 7. Validation
**Acceptance criteria**
- Marker recognized; collection succeeds under strict markers.
- MCP tests return 200 without 429s under CI env.
- Dedicated rate-limit tests still catch strict limits (if present).

**Verification commands**
- `pytest -q tests/mcp -k "not live" --maxfail=1`
- `pytest -q tests/embeddings -k "not live" --maxfail=1`
- `pytest -q tests/test_retries.py tests/test_metrics.py tests/test_server_smoke.py --maxfail=1`
- `pytest -q tests/callbacks/test_callbacks_comprehensive.py -m ml_comprehensive --maxfail=1`

## 8. Loop & Safety
**Manual loop**
1. Analyze logs.
2. Apply minimal changes.
3. Verify targeted tests.
4. Report iteration.

**Safety controls**
- Limit auto-fixes to configuration-only changes.
- Require human review for code changes.

## 9. Self-Review
- Ensure changes are minimal and targeted.
- Verify no secrets or sensitive values in CI env.
- Confirm marker list consistency across configs.

## 10. Next Steps
1. Locate rate limiter config to confirm env read timing.
2. Add targeted test-level overrides if necessary.
3. Expand self-healing analyzer to flag marker gaps and 429s automatically.

## 11. Impl Directive
1. Patch marker lists in `pytest.ini` and `configs/development/pytest.ini`.
2. Add CI env overrides in `.github/workflows/mcp-ci.yml`.
3. Run validation commands.
4. Record iteration report in `tools/self_heal/report_iteration_0.md`.

## 12. Appendices
### A. Search command for rate limiter
```
rg -n "RATE_LIMIT_RATE|RATE_LIMIT_BURST|rate_limit|ratelimit|Limiter" src tests
```

### B. Example monkeypatch snippet
```python
import importlib
import pytest

import src.codex_ml.app as app_module

def test_call_tool_echo(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_RATE", "1000")
    monkeypatch.setenv("RATE_LIMIT_BURST", "1000")
    importlib.reload(app_module)
    client = app_module.create_test_client()
    response = client.post("/jsonrpc", json={
        "jsonrpc": "2.0",
        "method": "mcp.callTool",
        "params": {"tool_id": "mock.tool.echo", "input": {"text": "hello"}},
        "id": "t2",
    })
    assert response.status_code == 200
```
