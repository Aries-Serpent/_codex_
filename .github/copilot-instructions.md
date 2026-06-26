# AGENTS

Guidelines for contributors and Codex automation. Keep this file updated as conventions change.

---

## 🤖 MANDATORY SESSION PRE-LOAD — First action of EVERY session, no exceptions

**Before reading anything else, before any tool call, before any file change:**

1. **READ** `.codex/AGENTIC_REPO_STATE.md` — confirms auth is permanently active, no approval needed
2. **READ** `.codex/CODEBASE_AGENCY_POLICY.md` — mandatory rules governing all agent actions
3. **READ** `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` — last session state and patterns
4. **READ** last 5 lines of `.codex/aftermath/pda_iterations.jsonl` — PDA loop state
5. **READ** `.codex/agent_context.json` — repo variable snapshot (COPILOT_AGENT_AUTH_ENABLED etc.)
6. **LOAD** all stored session memories (store_memory tool)

This is not optional. This is not only triggered by deferral language.
**Every session starts here.** The copilot-setup-steps.yml workflow automates this
at environment boot — the output appears in the "🧠 Session Context Pre-load" step.

### What these files tell you every time

| File | Key fact |
|------|----------|
| `AGENTIC_REPO_STATE.md` | `COPILOT_AGENT_AUTH_ENABLED=true` is permanent. No checkbox. No human gate. |
| `CODEBASE_AGENCY_POLICY.md` | Fix ALL issues found. No deferral. No "pre-existing". |
| `AGENT_ACCOUNTABILITY_REPORT.md` | What the last session did, patterns resolved, what's open. |
| `pda_iterations.jsonl` | PDA loop iteration history — what patterns are implemented. |
| `agent_context.json` | Live repo variable values at last sync. |

---

## 🔒 COPILOT CLOUD AGENT (CCA) VERSION LOCK — CRITICAL CONFIGURATION

**Effective from Session 1293 onwards**

### Why This Lock Exists

The Copilot Cloud Agent runtime was experiencing **duplicate function call ID errors** across multi-turn agentic sessions:

`CAPIError: 400 — Duplicate item found with id fc_call_FemHt2ijHDFdgdakM7sqwQJF`

**Root Cause**: Payload deduplication layer was missing in CCA runtime. Function calls from Turn N were leaking into Turn N+1 payloads, causing CAPI validation to reject duplicates.

**Fix Implemented** (Session 1293):
- Deduplication layer in `.github/copilot-evolution/integrated_system.py`
- Turn-state isolation with unique turn IDs (`TurnState` class)
- Pre-flight validation for function call IDs (`PayloadDeduplicator` class)
- Payload hash integrity checks (`payload_hash` field)
- ML turn-state isolation via `PredictionTurnState` + `TurnAwareMLSelector` in `ml_strategy_selector.py`

### Configuration

**MANDATORY ENVIRONMENT VARIABLES**:

```yaml
COPILOT_AGENT_CCA_VERSION_LOCK: "stable"
COPILOT_AGENT_DEDUPLICATION_ENABLED: "true"
COPILOT_AGENT_TURN_ISOLATION_ENABLED: "true"
```

**What This Means**:

| Variable | Value | Enforcement |
|----------|-------|-------------|
| `COPILOT_AGENT_CCA_VERSION_LOCK` | `stable` | **Do NOT auto-upgrade CCA**. Pin to last stable release. |
| `COPILOT_AGENT_DEDUPLICATION_ENABLED` | `true` | **Always clean payloads** before submission to CAPI. |
| `COPILOT_AGENT_TURN_ISOLATION_ENABLED` | `true` | **Finalize turn state** after each agentic turn completes. |

### When Using Copilot Cloud Agent

**BEFORE** initiating any multi-turn agentic loop:

1. ✅ **Verify** `COPILOT_AGENT_CCA_VERSION_LOCK=stable` is set
2. ✅ **Verify** `COPILOT_AGENT_DEDUPLICATION_ENABLED=true` is set
3. ✅ **Verify** `COPILOT_AGENT_TURN_ISOLATION_ENABLED=true` is set
4. ✅ **Call** `IntegratedEvolutionSystem.deduplicate_agentic_payload()` before payload submission
5. ✅ **Finalize** turn state with `system.deduplicator.finalize_turn()` after each turn
6. ✅ **Pass** `turn_id` to `MLStrategySelector.predict_strategy()` for per-turn score isolation
7. ✅ **Call** `turn_state.end_turn(turn_id)` after ML predictions complete

**FORBIDDEN**:

```
❌ DO NOT upgrade CCA version without explicit session review
❌ DO NOT skip deduplication step in payload preparation
❌ DO NOT reuse function call IDs across turns
❌ DO NOT submit payloads without turn-state isolation
❌ DO NOT call predict_strategy() without a turn_id in multi-turn loops
```

---

## 🚨 HARD STOP — DEFERRAL LANGUAGE TRIGGER PROTOCOL

**This rule fires BEFORE any other instruction.**

If you are about to write — or have just written — ANY of the following, you MUST STOP and re-run the mandatory pre-load above:

1. 🔃 **LOAD** `.codex/CODEBASE_AGENCY_POLICY.md` (read it fully)
2. 🔃 **LOAD** `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` (read it fully)
3. 🔃 **LOAD** all stored session memories
4. **FIX** the issue NOW

**Trigger phrases (any variation triggers the protocol):**

```
"This was from a different branch/agent/PR/session"
"Not from our current feature/branch/PR"
"Pre-existing issue / pre-existing code / pre-existing and safe"
"Not introduced by this PR/change/commit"
"Out of scope / outside the scope / not related to this PR"
"Not my responsibility / not my problem / not my concern"
"Will address in a future PR/task/session/iteration"
"Future PR / follow-up PR / follow-up task"
"Address incrementally / address separately / address later"
"Can be addressed later / will fix later / will resolve later"
"Another session/agent should handle this"
"Not actionable in this PR"
"Can be deferred / should be deferred"
```

**Why:** These phrases have recurred across Sessions 20–25 of this repository.
Automated enforcement via `.github/workflows/deferral-language-gate.yml` runs
`scripts/ci/check_deferral_language.py` on every PR. CI will fail.

**The only acceptable response to finding an issue is to fix it.**
Origin (branch / PR / agent / session) is irrelevant per Codebase Agency Policy §2 and §3a.

---

## Environment Variables

- `CODEX_ENV_PYTHON_VERSION`, `CODEX_ENV_NODE_VERSION`, `CODEX_ENV_RUST_VERSION`, `CODEX_ENV_GO_VERSION`, `CODEX_ENV_SWIFT_VERSION` – select language versions during environment setup.
- `CODEX_SESSION_ID` – identifier for a logical session; group log events.
- `CODEX_SESSION_LOG_DIR` – directory for session log files (default: `.codex/sessions`).
- `CODEX_LOG_DB_PATH` / `CODEX_DB_PATH` – path to the SQLite database used by logging tools.
- `CODEX_SQLITE_POOL` – set to `1` to enable per-session SQLite connection pooling.
- `COPILOT_AGENT_CCA_VERSION_LOCK` – **lock CCA to stable release** (set to `stable`)
- `COPILOT_AGENT_DEDUPLICATION_ENABLED` – **enable payload deduplication** (set to `true`)
- `COPILOT_AGENT_TURN_ISOLATION_ENABLED` – **enable turn-state isolation** (set to `true`)

## Logging Roles

Use one of the following roles when recording conversation or session events: `system`, `user`, `assistant`, `tool`.

## Tooling & Testing

- Format with **Black**, lint with **Ruff**, sort imports with **isort**.
- Run type checks with **mypy** if changing Python modules.
- Before committing, run:

```bash
pre-commit run --files <changed_files>
nox -s tests
```

- Ensure optional test dependencies (e.g., `hydra-core`, `mlflow`) are installed or appropriately mocked.

## Useful Commands

- `python -m codex.logging.session_logger` – record session events.
- `python -m codex.logging.viewer` – view session logs.
- `python -m codex.logging.query_logs` – search conversation transcripts.

## GitHub API & MCP Knowledge — MUST LOAD

> Every agent session MUST be aware of these references before making any GitHub API call.

| Document | Path | When to Use |
|----------|------|-------------|
| **Variables & Secrets Reference** | `docs/reference/GITHUB_VARIABLES_SECRETS_REFERENCE.md` | Any operation on variables, secrets, Dependabot, Codespaces secrets | <!-- pragma: allowlist secret -->
| **Copilot Agent API Reference** | `docs/ci/GITHUB_API_COPILOT_AGENT_REFERENCE.md` | Token hierarchy, repo variables, PR body WEC protocol, workflow ops | <!-- pragma: allowlist secret -->
| **MCP Tool Reference** | `.codex/docs/COPILOT_MCP_TOOL_REFERENCE.md` | Tool inventory: 21 Playwright + 28 GitHub MCP tools |
| **CB API Knowledge Entry** | `.codex/docs/GITHUB_API_AND_MCP_REFERENCE.md` | Quick-access summary + wiring map |
| **MCP Server Config Guide** | Upstream: `github.com/github/github-mcp-server/docs/server-configuration.md` | Toolsets, read-only mode, lockdown, insiders |

### Critical: Token Usage for GitHub API Calls

```yaml
# ALWAYS use this token chain — never bare github.token for write operations
GH_TOKEN: ${{ secrets.CODEX_MASTER_KEY || secrets.CODEX_BACKUP_KEY || github.token }}
```

- `GITHUB_TOKEN` / `github.token` → installation token, **no OAuth scopes** → **403** on variables/secrets API
- `CODEX_MASTER_KEY` → `repo` + `workflow` + `actions:write` → full variable/secret CRUD
- MCP Server → **does NOT support** variable/secret CRUD — use REST API or `gh` CLI

### Handling GitHub URLs

Whenever the user provides a GitHub Action run URL (e.g., `https://github.com/.../actions/runs/...`) or a PR comment URL (`...#issuecomment-...`), you MUST proactively use the `github-mcp-server` tools (`get_job_logs`, `pull_request_read` with `get_comments`/`get_review_comments`, `issue_read` with `get_comments`) to fetch the exact error logs or review text. Do not hallucinate the feedback or failure reasons.

### Test Variables API

```bash
# Run live end-to-end test (requires CODEX_MASTER_KEY in env)
GH_TOKEN=$CODEX_MASTER_KEY python scripts/ci/test_variables_api.py

# Run via GitHub Actions (dispatches test-variables-api.yml)
gh workflow run test-variables-api.yml --repo Aries-Serpent/_codex_ --ref 0D_base_
```

## ⚙️ WEC Template Maintenance (MANDATORY)

**Effective:** 2026-06-26 onwards (applies to ALL Copilot Agent sessions)

### Before Making Any Code Changes

1. **Verify WEC Presence:**
   - PR must have `## 🔄 Workflow Execution Checklist` section
   - All REQUIRED workflows must be listed
   - If WEC is missing or malformed, post diagnostic and fix BEFORE proceeding

2. **Read Current WEC State:**
   - Extract WEC state from PR body at session START
   - Log state to session context comment (visible in actions)
   - Preserve this state throughout the session

3. **Understand Merge Target:**
   - For merges to `main`: All 5 REQUIRED workflows must be **[x] checked**
   - For merges to `0D_base_`: Same 5 REQUIRED workflows must be **[x] checked**
   - See: `.codex/WEC_CANONICAL_ITEMS.md` for full list

### During Session Work

- **Do NOT let `report_progress` calls strip the WEC**
- **Read current WEC state BEFORE every `report_progress` call**
- **Pass WEC block in `prDescription` parameter** (append to end)
- **If maintainer edits WEC mid-session, read it again** and preserve their selections
- **Post acknowledgment comment** if WEC was manually changed

### Pre-Commit Validation

```bash
# Before final commit, ALWAYS run:
python scripts/ci/session_wrapup_autofix.py --check --pr N

# Expected output: REQ-4 ✅, REQ-5 ✅, WEC valid ✅
```

**STOP if any check fails:**
- ❌ REQ-4 (AGENT_ACCOUNTABILITY_REPORT.md not updated): Run `--auto-update`
- ❌ REQ-5 (CHANGELOG.md not updated): Run `--auto-update`
- ❌ WEC invalid: Use `wec_enforcer.py --validate-body --pr N` to diagnose

### At Session End

1. Validate WEC is in final PR body
2. Ensure all selections are preserved
3. Document which workflows you selected/deselected and why
4. Post final session comment with WEC state + compliance status

### Key References

- **Full WEC Contract:** `.codex/WEC_SESSION_INVARIANT.md`
- **Workflow Definitions:** `.codex/WEC_CANONICAL_ITEMS.md`
- **PR Body Conflicts:** `docs/workflows/WEC_PR_BODY_CONFLICTS.md`
- **WEC Enforcer Tool:** `scripts/ci/wec_enforcer.py`
- **Session Wrapup Tool:** `scripts/ci/session_wrapup_autofix.py`

---

## Prohibited Actions

- Do **not** create or activate any GitHub Actions workflow files.
- Do **not** modify `.github/workflows/copilot-setup-steps.yml` or try to re-enable/fix commented-out steps within it unless explicitly instructed by a human.
- Keep automation artefacts confined to `.codex/`.
- Do **not** upgrade CCA version without explicit session review (violates `COPILOT_AGENT_CCA_VERSION_LOCK`).
- Do **not** strip the WEC section from PR body during `report_progress` calls.

## Documentation & Architecture Conventions

When generating or updating documentation related to architecture, domain ownership, or agent mapping:
1. **Assign specific ownership**: Always assign ownership to the exact ideal Copilot custom agent designed for that domain. As a fallback, use `@mbaetiong` or a secondary relevant custom agent.
2. **Use Mermaid**: Always format structural workflows, diagrams, and agent/workflow mappings using Mermaid.js (`mermaid` code blocks).

## Copilot Task Execution Protocol (CTEP)

When users activate CTEP mode using phrases like "Enable CTEP", "CTEP Mode: ON", or "Task mode: ON", follow the comprehensive task completion protocol:

### Activation Commands
- `Enable CTEP` / `CTEP Mode: ON` / `Task mode: ON` → Activate protocol
- `Disable CTEP` / `CTEP Mode: OFF` / `Exit Task mode` → Deactivate protocol

### Protocol Behavior (When Active)
1. **Complete ALL tasks** - Zero omissions allowed
2. **Maintain progress tracker** - Live status updates for each task
3. **Codebase-first approach** - Search existing utilities before creating new ones
4. **Document new utilities** - Include integration plans for any new code
5. **Verify completion** - Final check: `Completed = Total, Skipped = 0`

### Response Structure
```markdown
## 📊 Task Execution Progress
### Phase 1: [Name] - X% Complete
- [ ] Task 1.1: [Description] ⏳ PENDING
- [x] Task 1.2: [Description] ✅ COMPLETE

## 🔍 Codebase Integration Analysis
[Search results for existing utilities]

## ✅ Completion Summary
Total Tasks: X | Completed: X ✅ | Skipped: 0 ❌
CTEP Compliance: ✅ PASS
```

### Full Documentation
- [Copilot Task Execution Protocol](./docs/Copilot_Task_Execution_Protocol.md)
- [CTEP Usage Examples](./docs/CTEP_Usage_Examples.md)
- [CTEP Quick Reference](./docs/CTEP_Quick_Reference.md)

## Log Directory & Retention

This document collects the repository conventions, runtime configuration, testing commands, and operational constraints for contributors and automated agents (Codex automation) in the Aries-Serpent/_codex_ repository.

### Table of contents
- Repository overview
- Environment variables (table)
- Logging roles (table)
- Tooling, testing & checks
- CLI & tool usage
- Optional/third-party test dependencies and mocking guidance
- Prohibited actions & scope
- Log directory layout & retention
- Error handling & backward compatibility guidance
- Configuration management (Hydra)
- Next steps toward production readiness
- Troubleshooting checklist
- Contact / maintainers

### Repository overview
- Packaging: defined in pyproject.toml; install with `pip install -e .`
- Command-line tasks live in `src/codex/cli.py` and can be invoked with `python -m codex.cli <task>`.
- Base configuration files are stored under `configs/` and are Hydra-compatible.

### Environment variables

| Variable | Purpose | Default / Notes |
|---|---|---|
| CODEX_ENV_PYTHON_VERSION | Select Python version for environment setup | Used by environment provisioning tools |
| CODEX_ENV_NODE_VERSION | Select Node.js version for environment setup | Used by environment provisioning tools |
| CODEX_ENV_RUST_VERSION | Select Rust version for environment setup | Used by environment provisioning tools |
| CODEX_ENV_GO_VERSION | Select Go version for environment setup | Used by environment provisioning tools |
| CODEX_ENV_SWIFT_VERSION | Select Swift version for environment setup | Used by environment provisioning tools |
| CODEX_SESSION_ID | Identifier for a logical session; groups log events | Generate per session (UUID recommended) |
| CODEX_SESSION_LOG_DIR | Directory for session log files | `.codex/sessions` |
| CODEX_LOG_DB_PATH / CODEX_DB_PATH | Path to the SQLite DB used by logging tools | `.codex/session_logs.db` |
| CODEX_SQLITE_POOL | Enable per-session SQLite connection pooling | 0 (disabled). Set to 1 to enable |
| COPILOT_AGENT_CCA_VERSION_LOCK | **Lock CCA version to stable release** | `stable` (MANDATORY) |
| COPILOT_AGENT_DEDUPLICATION_ENABLED | **Enable payload deduplication** | `true` (MANDATORY) |
| COPILOT_AGENT_TURN_ISOLATION_ENABLED | **Enable turn-state isolation** | `true` (MANDATORY) |

### Logging roles

| Role | Intended use |
|---|---|
| system | System-generated events, orchestration, internal state changes |
| user | End-user messages or human agent actions |
| assistant | Generated assistant responses (Codex/agent) |
| tool | Events produced by external tools or integrations (e.g., git, mlflow) |

### Tooling, testing & checks

```bash
# Run pre-commit hooks for changed files
pre-commit run --files <changed_files>

# Run the test suite (nox runs pytest with coverage)
nox -s tests
```

#### Formatting & static checks
- Format Python code with Black.
- Lint with Ruff.
- Sort imports with isort (if configured).
- Run type checks with mypy when changing Python modules.

### CLI & tool usage
- `python -m codex.logging.session_logger` — record session events
- `python -m codex.logging.viewer` — view session logs
- `python -m codex.logging.query_logs` — search conversation transcripts
- `python -m codex.cli <task>` — run repository CLI tasks

When writing new CLI tasks:
- Follow existing patterns in `src/codex/cli.py`.
- Register argument parsing and Hydra-compatible configuration where applicable.
- Provide clear help strings and exit codes.

### Optional / third-party test dependencies and mocking guidance
Some tests require optional third-party packages (for example, `hydra-core`, `mlflow`). Adopt one of these approaches:
- Install optional test dependencies: `pip install -r requirements-tests-optional.txt`
- Prefer explicit mocks for services like mlflow or heavy integrations via `pytest-mock` or `monkeypatch`.
- Keep test module names unique to avoid import conflicts.

### Prohibited actions & scope
- Do NOT create or activate any GitHub Actions workflow files.
- Keep automation artifacts confined to the `.codex/` directory unless explicitly approved.
- Repository changes are limited to documentation and `.codex/*` outputs unless otherwise specified by maintainers.
- **Do NOT upgrade CCA version without explicit session review** — violates `COPILOT_AGENT_CCA_VERSION_LOCK`.

### Log directory layout & retention

```
./.codex/
  session_logs.db
  sessions/<SESSION_ID>.ndjson
```

Retention policy — retain NDJSON files and SQLite rows for 30 iterations:

```bash
# Purge session files older than 30 iterations (best-effort)
find ./.codex/sessions -type f -mtime +30 -print -delete || true

# Optionally vacuum the SQLite DB after purging rows (use with care)
# sqlite3 .codex/session_logs.db "VACUUM;"
```

### Error handling & backward compatibility guidance

#### General patterns
- Fail fast with clear, actionable error messages when a critical configuration is missing.
- Provide safe fallbacks for optional integrations. Prefer explicit runtime detection:

```python
try:
    import mlflow
    HAS_MLFLOW = True
except Exception:
    HAS_MLFLOW = False
    logger.warning("mlflow is not available; mlflow integration disabled.")
```

- Wrap calls to external tooling with retries and custom exceptions. Maintain idempotency where appropriate.

#### Backward compatibility
- Accept legacy keys/flags for at least one release cycle and emit a deprecation warning.
- Keep stable output formats (NDJSON, SQLite schema) backward compatible; version the schema when incompatible changes are required.

### Configuration management (Hydra)
- Base configuration files live in `configs/` and are Hydra-compatible.
- Document overrides and example commands:

```bash
python -m codex.cli train --config-name=my_config hydra.run.dir=./runs/my_run
```

### Next steps toward production readiness
1. **Stabilize the test suite** — mock optional deps, resolve duplicate test module names.
2. **Complete checkpoint resume** — extend `run_hf_trainer` to load optimizer/scheduler state.
3. **Consolidate configuration** — adopt Hydra consistently across training and CLI tools.
4. **Expand safety and documentation** — flesh out `docs/safety.md`, add architecture overview.
5. **Logging & observability** — add structured schemas, provide a schema migration helper.

### Troubleshooting checklist
- Tests failing due to missing optional deps: install them or mock them.
- Session logs not found: verify `CODEX_SESSION_LOG_DIR` and `CODEX_SESSION_ID`.
- CLI tasks failing with Hydra errors: ensure `configs/` contains the requested config-name.
- Database lock errors on SQLite: use `CODEX_SQLITE_POOL`, per-session DB files, or add retries.
- **CCA duplicate function call errors**: Verify `COPILOT_AGENT_CCA_VERSION_LOCK=stable`, `COPILOT_AGENT_DEDUPLICATION_ENABLED=true`, and `COPILOT_AGENT_TURN_ISOLATION_ENABLED=true` in `.codex/agent_context.json`. Confirm `turn_id` is passed to `MLStrategySelector.predict_strategy()` and `turn_state.end_turn()` is called after each loop.

### Contact / maintainers
- For repository-specific policy changes, open an issue in `Aries-Serpent/_codex_` and tag maintainers.
- For urgent security or data-leak concerns, follow the escalation path in `CONTRIBUTING`.
- **For CCA version lock or deduplication issues, escalate to the Copilot Cloud Agent team with full session logs and error context.**

<HighLevelDetails>
- A summary of what the repository does: This repository contains the Aries-Serpent _codex_ project. It focuses on automation, AI agent workflows, and maintaining rigorous code standards.
- High level repository information: Large codebase, written primarily in Python, Markdown, and Shell. Heavy use of GitHub Actions for CI/CD. Target runtimes include Python >=3.12 and Node.js 22+.
</HighLevelDetails>

<BuildInstructions>
- Format with **Black**, lint with **Ruff**, sort imports with **isort**.
- Ruff config selects only E,F,I; tests ignore E402 and F811.
- Before committing, always run:
  `pre-commit run --files <changed_files>`
- Run the test suite using nox:
  `nox -s tests`
</BuildInstructions>

<ProjectLayout>
- Command-line tasks live in `src/codex/cli.py`.
- Base configuration files are stored under `configs/` and are Hydra-compatible.
- Workflows are defined in `.github/workflows/`.
</ProjectLayout>
