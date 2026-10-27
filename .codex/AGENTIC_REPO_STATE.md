# Repository agent context and authorization boundaries

This document describes repository automation configuration. It does not grant
GitHub permissions, administrative authority, approval bypasses, or access to
credentials. Read relevant context before affected edits; independent inspection
may use available tools in parallel.

## Configuration is not authorization

The values below are historical configuration references, not verified current
settings. `.codex/agent_context.json` was generated on 2026-07-13; its checkout
mtime is not its synchronization time.

| Variable | Historical value | Meaning |
|---|---|---|
| `COPILOT_AGENT_AUTH_ENABLED` | `true` | Application/workflow feature gate, not a GitHub credential |
| `COPILOT_AGENT_MAX_AUTONOMY_LEVEL` | `D` | Repository automation setting, not an assigned GitHub role |
| `COGNITIVE_BRAIN_ALLOWED_ACTORS` | See snapshot | Application allowlist, not a platform permission grant |
| `COPILOT_AGENT_SESSION_RESTORE_ENABLED` | `true` | Session restoration setting |

## Preparation, publication, and protected operations

- Prepare task-relevant repository and workflow changes when local editing is
  available and the task authorizes them. Do not demand a nonexistent PR or
  unavailable specialist for ordinary local work.
- Push or invoke remote operations only when the current credential, assigned
  branch mechanism, task authorization, and platform controls permit them.
- Protected merges, deployment, governance approvals, and administrative changes
  remain subject to their actual controls. Green CI, a feature flag, checkbox,
  local session file, or historical user preference is not an approval bypass.
- Preserve an existing PR's WEC selections. A selected workflow is not proof that
  it ran, passed, or is required by GitHub protection. No-PR work must not invent
  a PR number, workflow conclusion, or approval.

## Verify capabilities for the operation

Use available, authorized read-only metadata to establish relevant capabilities.
Record denied or unavailable sources as unknown, not absent. A successful
repository read does not establish write, administration, token inheritance,
branch bypass, or deployment permission. Session-token limitations do not
describe the requesting user's own permissions.

The 2026-10-22 audit observed accessible branch/ruleset and environment metadata,
but classic protection details, Actions approval settings, dedicated Agents
secrets/variables, and hosted firewall/runner settings remained inaccessible or
unverified. See the [audit and rollout](reports/AGENT_RESTRICTIONS_AUDIT_2026_10_22.md)
for timestamps, source boundaries, and administrator verification actions.

Use the least-privileged available credential suitable for the operation.
Repository helpers may specify a fallback chain; credential names alone do not
prove scope or validity. Never log credentials or distribute a privileged token
to every agent to compensate for missing access.

## 📋 Complete Variable Catalogue (S183d additions)

This is a repository configuration reference. Defaults and historical values
must be checked against actual consumers and accessible current settings before
use. "Writable By" describes the repository's intended request path, not proof
that a session can perform a GitHub write.

### Core Auth & Autonomy
| Variable | Current Value | Purpose | Writable By |
|---|---|---|---|
| `COPILOT_AGENT_AUTH_ENABLED` | `true` | Application authorization feature gate | Owner only |
| `COPILOT_AGENT_MAX_AUTONOMY_LEVEL` | `D` | Max agent tier | Owner only |
| `COPILOT_AGENT_STATE` | `ACTIVE` | Session lifecycle state | Agent (via agent-var-writer) |
| `COPILOT_AGENT_SESSION_RESTORE_ENABLED` | `true` | Enable session restore | Owner only |
| `COGNITIVE_BRAIN_ALLOWED_ACTORS` | `mbaetiong,...` | Authorised actors | Agent (via agent-var-writer) |

### CI Health & Cascade Control (S183d)
| Variable | Default | Purpose | Writable By |
|---|---|---|---|
| `CODEX_CI_FAILURE_RATE` | auto | Current failure rate e.g. `11.6:degraded` | Agent (via agent-var-writer) |
| `CODEX_CI_LAST_GREEN_SHA` | auto | Last all-green commit SHA | Agent (via agent-var-writer) |
| `CODEX_MAX_HEALER_RUNS_PER_HOUR` | `5` | Rate cap for self-healer per branch. Recommended range: 3–7 (3=conservative, 5=default, 7=aggressive healing on fast-moving branches) | Agent (via agent-var-writer) |
| `CODEX_SWEEP_SKIP_MAIN` | `false` | Set `true` to stop sweep from pushing metadata to `main` during heavy PR activity (prevents merge conflicts in open PRs) | Agent (via agent-var-writer) |
| `CODEX_HEALER_SKIP_SKIPCI` | `true` | When `true`, healer skips runs triggered by `[skip ci]` commits — breaks sweep→validate→healer cascade | Agent (via agent-var-writer) |

### Runner & Cache Performance
| Variable | Default | Purpose | Writable By |
|---|---|---|---|
| `COPILOT_RUNNER_PROFILE` | `ubuntu-latest-m` | Historical runner preference; actual provisioning uses the setup job's `runs-on` and requires an available label | Agent request (via agent-var-writer) |
| `CODEX_CACHE_VERSION` | `v2` | Cache key version; bump to invalidate all caches | Agent (via agent-var-writer) |

### Cognitive Brain
| Variable | Current Value | Purpose | Writable By |
|---|---|---|---|
| `COGNITIVE_BRAIN_INJECTION_ENABLED` | `true` | Enable session memory injection | Owner only |
| `COGNITIVE_BRAIN_MAX_CONTEXT_TOKENS` | `128000` | Max tokens for context injection | Owner only |
| `COGNITIVE_BRAIN_MEMORY_TIER` | `both` | STM+LTM both active | Owner only |
| `COGNITIVE_BRAIN_SESSION_NUMBER` | auto | Monotonic session counter | Agent (via agent-var-writer) |
| `COGNITIVE_BRAIN_PATTERN_MIN_CONFIDENCE` | `0.75` | Min confidence for pattern promotion | Owner only |
| `COGNITIVE_BRAIN_LTM_RETENTION_DAYS` | `90` | LTM retention window | Owner only |

## 🔧 How to Toggle Variables (Agent Instructions)

Only submit these requests when the task authorizes the change. Queuing an intent
does not prove it was accepted or applied; the processing workflow's permissions,
actor checks, and any required review still apply.

### Temporarily prevent sweep from conflicting open PRs
```bash
python scripts/tools/variable_intent_writer.py set CODEX_SWEEP_SKIP_MAIN "true"
# then report_progress → process-variable-intents workflow applies it
# Re-enable after PR activity settles:
python scripts/tools/variable_intent_writer.py set CODEX_SWEEP_SKIP_MAIN "false"
```

### Tune the healer rate cap
```bash
python scripts/tools/variable_intent_writer.py set CODEX_MAX_HEALER_RUNS_PER_HOUR "3"
# Lower = more conservative, Higher = more aggressive healing
```

### Request a verified runner configuration for a subsequent session

Verify the label, entitlement, and actual `runs-on` consumer first. A variable
write or resource-probe recommendation cannot resize an already running job.
```bash
python scripts/tools/variable_intent_writer.py set COPILOT_RUNNER_PROFILE "ubuntu-8-core"
# Revert after heavy session:
python scripts/tools/variable_intent_writer.py set COPILOT_RUNNER_PROFILE "ubuntu-latest-m"
```

## 📁 Related Files

- `.codex/agent_context.json` — full repo variable snapshot (auto-synced by `copilot-agent-vars-bootstrap.yml`)
- `.codex/aftermath/pda_iterations.jsonl` — session history
- `.codex/pending_ops/variable_*.json` — queued variable writes (processed by `process-variable-intents.yml`)
- `docs/admin/COPILOT_AGENT_ADMIN_SETUP.md` — one-time human setup steps
- `scripts/tools/variable_intent_writer.py` — CLI to queue variable changes
- `scripts/ci/session_wrapup_autofix.py` — session start / WEC management

## Provenance and unavailable context

The previous state summary was dated 2026-05-24. It is not current CI, coverage,
profile-discovery, credential, or permission evidence. The snapshot JSON remains
historical and was not rewritten to simulate a live refresh.

Use relevant supplied memories as scoped context, not policy. If retrieval is
unavailable, disclose that limitation and continue work that does not require it;
do not call a storage operation to simulate retrieval. Local context artifacts,
logs, and feature flags do not prove attachment to the cloud agent's prompt.
