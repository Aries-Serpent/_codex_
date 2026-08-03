# CCA Hosted Runtime Boundary Notes
**Last Updated:** 2026-08-03
**Version:** v0.3.0

> **Purpose:** Clarify which Copilot Cloud Agent (CCA) failure modes are
> repo-controlled versus hosted-runtime-controlled, including the prior
> exit-134 (duplicate function-call ID) context.

## Boundary Matrix

| Concern | Repo-controlled mitigation | Hosted/runtime dependency | Verification method |
|---|---|---|---|
| Duplicate function-call IDs across turns | `.github/copilot-evolution/integrated_system.py` deduplication layer; `COPILOT_AGENT_DEDUPLICATION_ENABLED=true` | CAPI payload validation enforces unique IDs | Run multi-turn agentic integration tests; inspect payloads for duplicate `fc_call_*` IDs |
| Turn state leakage | `TurnState` / `PredictionTurnState` isolation; finalize turn after each agentic step; `COPILOT_AGENT_TURN_ISOLATION_ENABLED=true` | CCA runtime turn lifecycle | Unit tests assert no stale function-call IDs in turn N+1 payloads |
| CCA version drift | `COPILOT_AGENT_CCA_VERSION_LOCK=stable` in `.codex/agent_context.json` | GitHub-managed CCA release channel | CI validates env vars at boot; `kernel._assert_cca_stability()` logs warnings if misconfigured |
| Exit-134 / SIGABRT panic | `COGNITIVE_BRAIN_FAILSAFE_OFF` guard; `assert_loaded()` fail-fast before reasoning; deterministic shell policy | Hosted runtime process supervisor (OOM/crash handler) | Run `tests/cognitive_brain/test_failure_injection.py` kernel auto-load and shell bypass scenarios |
| Payload hash integrity | `PayloadDeduplicator` computes and verifies `payload_hash` | CAPI request/response transport | Regression guard validates orchestrator payload hashing |
| Hosted runner resource limits | Timeouts, concurrency groups, `ubuntu-latest-m` runner profile | GitHub Actions runner infrastructure | Workflow `timeout-minutes` and `concurrency` declarations |
| Network partitions / offline mode | `codex.network` isolation mocks; `COGNITIVE_BRAIN_ALLOW_SHELL` env gate | GitHub network, MCP server availability | `test_inject_with_brain_client.py` offline scenario tests |
| Token scope failures | Token hierarchy `CODEX_MASTER_KEY → CODEX_BACKUP_KEY → github.token` documented in WEC | GitHub token issuance / repo secrets | `test-variables-api.yml` and `agent-auth-delegation.yml` validation runs |

## Repo-Controlled vs Runtime-Controlled Responsibilities

### Repo-controlled
- Deduplication logic before payload submission.
- Turn-state finalization hooks in agentic loops.
- Env-var locks (`COPILOT_AGENT_*`) in `.codex/agent_context.json`.
- Kernel `assert_loaded()` entrypoint guards.
- Shell metacharacter and token-redaction policies.
- Forensics field preservation (`decision_id`, `turn_id`, `task_id`).

### Hosted/runtime-controlled
- CCA runtime version selection (we lock it; GitHub provides it).
- CAPI validation of duplicate function-call IDs.
- Process-level crash handling and exit-code translation (e.g., 134).
- GitHub Actions runner provisioning and network egress.
- MCP server availability for GitHub/Playwright toolsets.

## Verification in CI

The `.github/workflows/cognitive-brain-required-gate.yml` runs:
1. `python -m ruff check src/codex/cognitive_brain tests/cognitive_brain/test_boundary_regression_guards.py`
2. `python -m mypy src/codex/cognitive_brain`
3. Targeted pytest on core cognitive_brain tests + boundary guards.

These tests fail if future edits remove deduplication, turn isolation, or
forensics fields.

## References

- `.codex/AGENTIC_REPO_STATE.md` — CCA version lock and env variables.
- `src/codex/cognitive_brain/kernel.py` — `_assert_cca_stability()` and
  `assert_loaded()`.
- `src/codex/cognitive_brain/session_guard.py` — session/create boundary.
- `src/codex/cognitive_brain/telemetry.py` — forensics field preservation.
