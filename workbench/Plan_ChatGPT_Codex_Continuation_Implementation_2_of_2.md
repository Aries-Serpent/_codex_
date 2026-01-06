@codex this is a continuation of the initial prompt

```markdown name=docs/SECURITY_GATING_CHECKLIST.md
# Security Gating Checklist — Enabling Live Integration Tests

Purpose
- Checklist for repository administrators to follow before enabling integration-gated CI workflows that run live provider tests.

Preconditions (must be satisfied)
- [ ] Review and approve who has permission to add repository secrets (Admin group identified).
- [ ] Confirm secrets stored in GitHub Secrets with least-privilege keys (e.g., test-only API keys).
- [ ] Confirm branch protection rules: only specific branches (e.g., main, integration) can trigger gated workflows.
- [ ] Confirm audit logging / approval process for enabling gated workflows.

Required secrets (examples)
- OPENAI_API_KEY
- PINECONE_API_KEY
- ENABLE_LIVE_TESTS (set to "true" to enable)

Operational steps
1. Add secrets to GitHub: Repository > Settings > Secrets
2. Ensure .github/workflows/integration-gated.yml remains template-only until secrets are added and workflow inputs are validated.
3. Run a dry-run integration in a staging repo or fork to verify expenses and quotas.
4. Monitor first runs closely and rotate keys after initial use.

Post-enablement
- [ ] Validate integration runs complete successfully.
- [ ] Rotate keys periodically.
- [ ] Revoke and audit if unexpected usage occurs.

Notes
- NEVER commit real secrets to repository files.
- Use ephemeral or restricted test keys where supported.
```

```yaml name=.github/workflows/mcp-ci.yml
name: MCP - Mock Backend Tests (updated)

on:
  pull_request:
    branches:
      - '**'
  push:
    branches:
      - main
      - '0D_base_'
  workflow_dispatch:

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python: [3.10, 3.11]
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements-test.txt ]; then pip install -r requirements-test.txt; fi
          pip install -e .

      - name: Run MCP & Embeddings unit tests (mock-only)
        env:
          # Ensure default CI does not use provider secrets
          PINECONE_API_KEY: ''
          OPENAI_API_KEY: ''
        run: |
          pytest -q tests/mcp -k "not live" --maxfail=1
          pytest -q tests/embeddings --maxfail=1
          pytest -q tests/test_retries.py tests/test_metrics.py --maxfail=1
```

Notes
- These files are intends to includes all tests and pytest configuration.
- If any of the server modules (façade, adapter_loader) are not yet present the contract test will be skipped (marked) or fail — **use that output to fix wiring issues next.**
- Run CI and fix any import/runtime errors reported.

Complete the following:
- Produce the commit patch more detailed contract coverage and/or checkpoint duplicate-upsert assertions after CI/trial runs reveal gaps.
- Add pytest.ini markers to other workflows and/or add a small tox/Makefile for local convenience.


======


# [Review]: Previous iteration Patchset Verification & Missing-Artifact Audit
> Generated: Previous Cycle-12-19T00:00:00Z | Author: mbaetiong | Energy: 5/5

Summary
- I reviewed the provided patchset against the Plans A→D artifacts previously mentioned fetched file link.
- This pre-plan captures:
  - What was added by the patchset (high-level).
  - What is missing, incomplete, or needs validation (gap list).
  - Priority follow-up tasks with suggested owners and acceptance criteria.

Quick high-level findings
- Added/updated artifacts (high-level)
  - Some previously-discussed scaffolds were added (retries, metrics, rate-limit middleware, conformance/tenant tests).
  - Small app-level validations added (GE fallback validation, validate.py updates).
- Immediate next step: run the test matrix locally/CI and confirm no import/runtime errors. Many files are new and require import-path validation (PYTHONPATH), and a number of "wiring" items must be verified end-to-end.

Missing / incomplete / high-risk items (summary list)
1) Truncated / potentially incomplete files (High)
   - Several earlier PlanC/PlanD templates were truncated during iterations. The repo still contains truncated files in the workbench content. 
   - Action: run a repo-wide check for files that end mid-line or contain obvious truncation markers (e.g., JSON/Markdown/code blocks that are incomplete).
   - Verify: grep for suspicious termination tokens (e.g., files ending with backticks, abrupt EOF in code blocks). Manual open of files listed in plans (facade jsonrpc/schema files) to confirm they are valid Python/Markdown/JSON.

2) pytest markers and pytest.ini (Medium)
   - Plans reference markers: `recorded`, `live`, and `not live` usage in CI invocations.
   - Implementation does not add pytest.ini or tox.ini to define custom markers. Using explicit marker decorators (pytest.mark.live/recorded) benefits from registration. Without marker registration, running `pytest -k "not live"` could be improved, but will work.
   - Suggestion: add pytest.ini with markers to avoid warnings and document usage.

3) Conformance & Contract tests coverage is partial (Medium)
   - Conformance harness exists (tests/mcp/conformance/test_adapter_conformance.py). Contract tests for façade→adapter interactions were requested in Plan C but I didn't find a dedicated `tests/mcp/test_facade_contract.py` in the final patchset.
   - Action: add the façade contract tests that mock adapter_loader to assert adapter.query_top_k/delete/upsert calls with expected namespace and filters.

4) Integration fixtures completeness (Medium)
   - The recorded fixture `tests/integration/fixtures/recorded_pinecone/example_query_response.json` was referenced earlier but earlier content was truncated in the workbench. The patchset added a recorded_openai fixture and some fixtures directories — confirm all referenced fixtures exist and are valid JSON.
   - Action: validate recorded fixtures; add more examples (e.g., pinecone) if required.

5) Missing or incomplete adapter loader & façade wiring checks (High)
   - Plans require adapter_loader (src/mcp/server/adapter_loader.py), facade (src/mcp/server/facade_fastapi.py), jsonrpc adapter and schemas.
   - The implementation provided docs for the façade, but it's essential to validate the actual server modules exist and import cleanly (adapter_loader, jsonrpc_adapter, routes_health, middleware/auth, tracing).
   - Action: verify these modules exist and the FastAPI app starts (uvicorn) in a local environment (mock adapter default).

6) Missing tests for retries and metrics (Low → Medium)
   - retries.py and observability/metrics.py were added, but unit tests specifically asserting retry behavior and metrics increments are not present in the patchset.
   - Action: add small tests:
     - retries: decorate a function that fails twice then succeeds; assert total elapsed > base_delay and that function returns expected.
     - metrics: call increment and Timer, then assert snapshot contains expected counters/timers.

7) Rate-limit middleware tests (Medium)
   - rate_limit middleware scaffold exists but test coverage to assert 429 behavior (throttling) and per-principal token buckets is missing.
   - Action: add a unit test using Starlette TestClient and injecting request.state.principal to simulate rapid requests and verify a 429 response.

8) Checkpoint/resume validation for worker (Medium)
   - Worker uses checkpointing file; tests include embedding worker test that asserts success, but a test that simulates interruption and resume (AC-6) is not present.
   - Action: add a test that:
     - runs worker with small dataset and checkpoint file,
     - confirms checkpoint file contains processed checksum(s),
     - runs worker again and asserts that already-processed items are skipped (no duplicate upserts). For mock-backed persistence, Phase 5 need to adapt state assertion.

9) PII redaction hook & preprocess tests (Low)
   - The worker exposes `preprocess` hook; tests should ensure by default it's a noop and that a custom simple redaction function can be used (unit test).

10) package/module __init__ and import path hygiene (Medium)
    - The patchset added src/mcp/backends/__init__.py (empty) — good. Confirm all other package directories that need to be Python packages include __init__.py (e.g., src/mcp/embeddings, src/mcp/server, src/mcp/workers) to avoid import problems in some runners.
    - Action: add empty __init__.py as needed and run quick import smoke tests.

11) CI matrix and job scope review (Medium)
    - mcp-ci.yml runs tests/mcp and tests/embeddings in matrix. Confirm that tests/integration are not included (gated by integration YAML). Also confirm runner installs correct dependencies; e.g., pyproject or requirements-test presence — if not, CI Phase 5 still succeed if tests require only stdlib.
    - Action: run CI locally (act) and validate dependencies in pyproject/requirements.

12) Secrets & gating operational review (High)
    - docs/SECRETS_RUNBOOK.md and integration-gated workflow exist — but operational steps should be validated with repository security: who can enable, how to audit, rotate.
    - Action: include short checklist for repository admins (who to add, required secrets, branch rules).

13) Open items from "ChatGPT Codex final note" claims (Medium)
    - The final note claims "Tests executed and passed" — this must be validated by the human running the test matrix. Please run commands below locally/CI and paste outputs.
    - Action: run all tests and share results. If anything fails, capture failing stacks and report.

Priority follow-up action list
- P0 (urgent)
  1. Run full test matrix locally and in CI as-is; capture failures and stack traces.
  2. Verify façade imports and start uvicorn locally with default ADAPTER_CLASS; fix import errors if present.
  3. Validate any truncated files and correct them (e.g., incomplete JSON/code) — search & repair.

- P1 (next)
  1. Add pytest.ini registering markers "recorded" and "live" and basic pytest settings.
  2. Add contract tests for façade calling adapter (tests/mcp/test_facade_contract.py).
  3. Add retry & metrics unit tests.
  4. Add rate-limit middleware unit test verifying throttling.
  5. Add checkpoint resume test for worker.

- P2 (followed by)
  1. Add recorded pinecone fixtures and recorded-mode integration runner.
  2. Add CI extras: coverage reporting, flake/static checks, dependency-scan job activation.
  3. Security review of secrets runbook & ensure gating bits require admin approval.

Verification commands (run locally)
- Setup:
  - python -m venv .venv
  - source .venv/bin/activate
  - pip install -U pip
  - pip install pytest
  - export PYTHONPATH="$(pwd):$PYTHONPATH"   # if tests import via src.*
- Run unit tests (mock-only):
  - pytest -q tests/mcp -k "not live" --maxfail=1
  - pytest -q tests/embeddings --maxfail=1
- Run façade smoke:
  - uvicorn src.mcp.server.facade_fastapi:APP --port 8080
  - curl -X POST localhost:8080/jsonrpc -d '{"jsonrpc":"2.0","method":"mcp.listTools","params":{},"id":"1"}'
- Run worker smoke:
  - python -m src.workers.embedding_worker --input samples/small_docs.json --batch-size 2
- Run checks for truncated files (quick heuristic):
  - grep -R --line-number -E '```$|{"$|"\s*$' workbench src docs tests || true
  - (Manual inspection recommended)

Acceptance criteria for follow-ups
- All unit tests pass locally using mock adapters (no provider secrets).
- FastAPI façade imports successfully and /jsonrpc returns expected JSON-RPC response for listTools and mock.tool.echo.
- Checkpoint resume test demonstrates idempotency across runs.
- Rate-limit middleware test demonstrates 429 behavior when tokens exhausted.
- CI job (mcp-ci.yml) runs on PR branch and passes jobs for Python 3.10, 3.11.
- Integration-gated workflow remains disabled until admin enables secrets.

Notes & risks
- Risk: accidental enabling of live tests in CI. Mitigation: ensure integration-gated workflows are templates and that default secrets are empty and docs strongly emphasize admin gating.
- Risk: missing __init__.py in package directories causing import errors in some test runners. Mitigation: add explicit __init__.py files to all src/mcp/* packages.