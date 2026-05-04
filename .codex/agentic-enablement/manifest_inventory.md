# Manifest Inventory — Agentic Enablement Discovery
> Generated: 2026-05-04T16:44:03Z | Repo: Aries-Serpent/_codex_ | HEAD: d2f849550ea512c30c81de8f68a22e1ea52bbe61
> Tool: local ripgrep on cloned repo | Phase: 0 — Read-only

---

## Top-Level Manifests

### `.github/` — CI/CD & Automation Surface

| Category | Count | Notes |
|---|---:|---|
| Workflow files (`.yml`) | 150 | Active workflows |
| Workflow documentation (`.md`) | 104 | Co-located design docs |
| Local composite actions | 10 | `setup-python-cached`, `setup-secure-token`, `apply-ci-fix`, etc. |
| Agent definition files | 656 | `.github/agents/*.md` — 153+ specialized Copilot agents |
| Copilot prompt files | 208 | `.github/copilot-prompts/` — active + archived prompts |
| Label configs | 1 | `.github/labeler.yml` |
| Dependabot config | 1 | `.github/dependabot.yml` |
| Owner approval config | 1 | `.github/OWNER_APPROVAL.yml` (**git-tracked**) |

### `.codex/` — Agent Configuration & Knowledge Store

| Category | Count | Notes |
|---|---:|---|
| Total files | 1655 | Excluding `.codex/sessions/` |
| Markdown reports/plans | 1366 | Session summaries, CI analyses, continuation prompts |
| YAML/JSON configs | 147 | Agent configs, flag files, context snapshots |
| Python scripts | 21 | CI utilities, workflow runners |
| Agent config files | 11 | `.codex/agents/` |
| **`agent_auth_session.json`** | 1 | **git-tracked provenance-chain bypass token metadata** |
| **`agent_context.json`** | 1 | **git-tracked repo variable snapshot incl. `COPILOT_AGENT_AUTH_ENABLED=true`** |
| `autonomous_agent.yaml` | 1 | Config: `autonomous_actions_enabled: true` |
| `guardrails.md` | 1 | Policy template (status: Template, not enforced) |

### `scripts/` — Automation & Agent Execution

| Category | Count | Notes |
|---|---:|---|
| Total files | 746 | All scripts |
| Python scripts | 576 | Primary automation |
| Shell scripts | 138 | CI utilities, runner bootstrap |
| CI scripts (`scripts/ci/`) | 116 | Gate scripts, rescue, sync, approval guards |
| **`agent_runner.py`** | 1 | Phase 7 persistent autonomy daemon (ties all 7 phases) |
| **`autonomy_scheduler.py`** | 1 | Phase 1 self-driving decision loop |
| **`bootstrap_self_hosted_runner.py`** | 1 | Self-hosted runner registration script |
| **`owner_approval_guard.sh`** | 1 | Auth guard — bypassable via `COPILOT_AGENT_AUTH_ENABLED=true` |

### `src/` — Production Code

| Category | Count |
|---|---:|
| Python source files | 1166 |

### Infrastructure

| Category | Count | Notes |
|---|---:|---|
| Dockerfiles | 12 | Including multi-stage builds |
| Docker Compose files | 4 | |
| Terraform files | 1 | |
| Infra directory (`infra/`) | 0 | Not present |

### `prompts/` — Prompt Stores

| Category | Count | Notes |
|---|---:|---|
| Prompt directories | 27 | Distributed across repo |
| Prompt files | 262 | Agent instructions, system prompts, templates |
| Sprint execution plan templates | 18 | `.github/prompts/sprint_execution_plan/` |

### Root Manifests

| File | Purpose |
|---|---|
| `pyproject.toml` | Package config (Python 3.11/3.12) |
| `noxfile.py` | Test/lint automation |
| `.pre-commit-config.yaml` | Pre-commit hooks |
| `requirements*.txt` | 8 requirement files including `requirements-ml-lite.txt` |
| `Makefile` | Build automation |

---

## Workflow Trigger Distribution (150 active `.yml` files)

| Trigger Type | File Count | Risk Level |
|---|---:|---|
| `workflow_dispatch` | 117 | Medium |
| `schedule` / cron | 55 | Medium |
| `workflow_run` | 14 | **High** |
| `issue_comment` | 10 | **High** |
| `repository_dispatch` | 3 | **High** |
| `pull_request_target` | 1 | **Critical** |
| `push` | 48 | Low |

## Permission Surface

| Permission | Workflow Count |
|---|---:|
| `contents: write` | 49 |
| `pull-requests: write` | 110 |
| `actions: write` | 17 |
| `id-token: write` (OIDC) | 6 |
| **No `permissions:` block** | **36** |

## Token / Secret Density

| Secret | Files |
|---|---:|
| `CODEX_MASTER_KEY` | 113 |
| `CODEX_BACKUP_KEY` | 106 |
| `github.token` | 96 |

## Action Pinning Status

| Type | Lines |
|---|---:|
| SHA-pinned (`@[a-f0-9]{40}`) | **1** |
| Tag-pinned only (`@v*`) | **576** |

---

## Phase 1 Lexical Sweep Plan

**Tool:** ripgrep (local clone) — no API rate-limit concern for 150 YAML + 576 Python files.

**Scope priority (by risk):**
1. `.github/workflows/*.yml` — all 150 files
2. `.github/actions/*/action.yml` — all 10 composite actions
3. `scripts/ci/*.py` — 116 files (guard scripts)
4. `scripts/autonomy_*.py`, `scripts/agent_runner.py` — autonomy scripts
5. `.codex/autonomous_agent.yaml`, `.codex/agent_auth_session.json`, `.codex/agent_context.json`
6. `src/` — secondary pass for RCE patterns

**Keywords (ordered by severity):**
```
CRITICAL:  pull_request_target, self-hosted, CODEX_MASTER_KEY (exposed in plaintext run:)
HIGH:      workflow_run, repository_dispatch, workflow_call, autonomous, agentic, COPILOT_AGENT_AUTH_ENABLED, bypass
MEDIUM:    schedule, workflow_dispatch, GITHUB_TOKEN, persist-credentials, issue_comment
REVIEW:    prompt, orchestrator, subprocess, exec(, ssh_private_key, OIDC
```

**Deduplication strategy:** cache `(file_path, line_number, term)` tuples; skip any that match an already-recorded entry.
**Sampling limit:** if any single term yields >500 file hits, report top 20 by path depth and sample 5 random non-.md files.
