---
id: session-wrapup-autofix-agent
name: Session Wrap-Up Auto-Fix Agent
description: Auto-heal cognitive-preflight governance failures by updating the accountability
  report and changelog after a session, then commit the minimal documentation fix
  without triggering CI loops.
version: 1.0.0
status: active
maturity: production
tools:
- bash
- python
- git
---

# Session Wrap-Up Auto-Fix Agent

**Version:** 1.0.0
**Status:** ✅ Active
**Type:** GitHub Copilot Custom Agent
**Scope:** CI/CD compliance, self-healing, cognitive preflight

---

## 🎯 Purpose

The **Session Wrap-Up Auto-Fix Agent** is a specialized GitHub Copilot custom agent
that automatically resolves the most frequent Cognitive Pre-flight gate failures:

- **REQ-4**: `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` not updated in last commit
- **REQ-5**: `CHANGELOG.md` not updated in last commit

It is triggered when **Agent Token Delegation** is enabled (`COPILOT_AGENT_AUTH_ENABLED`)
and the `cognitive-preflight` job detects that either file was not touched.

---

## 🚀 Activation

### Automatic Activation (primary)
The agent is invoked automatically by `agent-auth-delegation.yml` when:
1. `COPILOT_AGENT_AUTH_ENABLED` checkbox is checked in the PR description
2. The `cognitive-preflight` job's REQ-4 or REQ-5 check fails

### Manual Activation
```bash
@copilot Use the session-wrapup-autofix-agent to fix accountability report and CHANGELOG
```

Or directly:
```bash
python scripts/ci/session_wrapup_autofix.py \
    --pr-number <PR_NUMBER> \
    --fix-all \
    --sha $(git rev-parse --short HEAD)
```

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     Agent Token Delegation Workflow               │
│                     (.github/workflows/agent-auth-delegation.yml) │
│                                                                   │
│  cognitive-preflight job                                          │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  REQ-1: Post mandatory checklist to PR ✅                    │ │
│  │  REQ-2: Parse CI failure patterns ✅                         │ │
│  │  REQ-3: Verify .gitignore allows agent_auth_session.json ✅  │ │
│  │  REQ-4: accountability_check (outcome: failure/success)      │ │
│  │  REQ-5: changelog_check (outcome: failure/success)           │ │
│  │                           │                                  │ │
│  │             ┌─────────────▼───────────────┐                  │ │
│  │             │  autofix_docs step           │                  │ │
│  │             │  (if REQ-4 OR REQ-5 failed) │                  │ │
│  │             │                              │                  │ │
│  │             │  1. session_wrapup_autofix   │                  │ │
│  │             │     .py --fix-accountability │                  │ │
│  │             │         --fix-changelog      │                  │ │
│  │             │                              │                  │ │
│  │             │  2. git add + commit [skip]  │                  │ │
│  │             │  3. git push (CODEX_MASTER)  │                  │ │
│  │             └─────────────────────────────┘                  │ │
│  │  REQ-6: Timebox acknowledgment ✅                             │ │
│  │  REQ-7: Commit count warning ✅                               │ │
│  │  REQ-8: Memory system soft gate ✅                            │ │
│  │  REQ-9: 5-pass self-review ✅                                 │ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Components

### Core Script
**File:** `scripts/ci/session_wrapup_autofix.py`

| Feature | Description |
|---------|-------------|
| Idempotent | Never creates duplicate entries |
| Offline | No network calls; reads local files only |
| Audit trail | All auto-entries tagged `[auto-generated]` |
| Dry-run | `--dry-run` shows changes without writing |
| Detection | `--check` mode returns exit code for CI use |

### Workflow Integration
**File:** `.github/workflows/agent-auth-delegation.yml`
**Step:** `autofix_docs` (runs when REQ-4 or REQ-5 fails)

| Property | Value |
|----------|-------|
| Trigger | `steps.accountability_check.outcome == 'failure' OR steps.changelog_check.outcome == 'failure'` |
| Token | `CODEX_MASTER_KEY` → `CODEX_BACKUP_KEY` → `github.token` |
| Commit message | `fix(docs): auto-update accountability report + CHANGELOG [cognitive-preflight][skip ci]` |
| Branch resolution | `gh pr view` API fallback for merge-ref events |
| Loop prevention | `[skip ci]` in commit message |

---

## 📋 Capabilities

| Capability | Description |
|------------|-------------|
| **REQ-4 auto-fix** | Appends dated session summary to `AGENT_ACCOUNTABILITY_REPORT.md` |
| **REQ-5 auto-fix** | Ensures `CHANGELOG.md` has `## [Unreleased]` with current session entry |
| **Duplicate detection** | Checks for existing auto-entry for the same PR number before writing |
| **Branch resolution** | Resolves PR branch name via `gh pr view` when event context is insufficient |
| **Self-healing commit** | Commits and pushes without triggering infinite CI loop (`[skip ci]`) |
| **Dry-run mode** | Previews changes without modifying files |
| **Check mode** | Reports compliance status for external callers |

---

## ✅ Codebase Alignment Verification

| Check | File | Status |
|-------|------|--------|
| Script exists | `scripts/ci/session_wrapup_autofix.py` | ✅ |
| Workflow step exists | `agent-auth-delegation.yml:autofix_docs` | ✅ |
| Python 3.12 compatible | All f-strings, type hints use >=3.12 syntax | ✅ |
| No network calls | Only `subprocess.run(["git", ...])` and file I/O | ✅ |
| CODEX_MASTER_KEY used | `env: GH_TOKEN: ${{ secrets.CODEX_MASTER_KEY || ... }}` | ✅ |
| `.gitignore` safe | Only writes tracked files (`.md`) | ✅ |
| Idempotent | `_report_already_has_auto_entry()` + `_changelog_has_unreleased()` checks | ✅ |
| `[skip ci]` commit | Prevents infinite workflow loop | ✅ |
| Policy compliant | No deferral language in auto-generated entries | ✅ |

---

## 🔗 Policy References

| Document | Relevance |
|----------|-----------|
| `.codex/CODEBASE_AGENCY_POLICY.md` | Master policy (§8 Self-Review, §10 Documentation) |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | Target file for REQ-4 |
| `.codex/patterns/ci_failure_patterns.yaml` | Pattern #20: `accountability_report_not_updated` |
| `.github/workflows/agent-auth-delegation.yml` | Host workflow |

---

## 🧪 Testing

```bash
# Check compliance status
python scripts/ci/session_wrapup_autofix.py --check

# Dry-run: see what would be written
python scripts/ci/session_wrapup_autofix.py --pr-number 3575 --dry-run --fix-all

# Apply fixes (writes files, does NOT commit)
python scripts/ci/session_wrapup_autofix.py --pr-number 3575 --fix-all

# Full test with known PR
python scripts/ci/session_wrapup_autofix.py \
    --pr-number 3575 \
    --sha $(git rev-parse --short HEAD) \
    --run-url "https://github.com/Aries-Serpent/_codex_/actions/runs/23079141876" \
    --fix-all --dry-run
```

---

## 🔄 Integration with Other Agents

| Agent | Relationship |
|-------|-------------|
| `ci-auto-healer-agent` | Sibling — handles other CI failure patterns |
| `cognitive-brain-manager` | Downstream — reads `COGNITIVE_BRAIN_STATUS_PR*.md` |
| `qa-walkthrough-agent` | Validates this agent's output in QA passes |
| `unified-governance-gate` | Enforces that auto-fix commits include `[auto-generated]` tag |

---

_Last updated: 2026-03-14T03:20Z | PR #3575 | session-wrapup-autofix-agent v1.0.0_
