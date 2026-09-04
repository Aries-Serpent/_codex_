---
name: CI Failure Resolution Agent
description: Diagnose and resolve CI/CD pipeline failures using embedded fix patterns
  and self-healing loops
deprecated: true
superseded_by: ci-auto-healer-agent.md
id: ci-failure-resolution-agent
---

> ⚠️ **DEPRECATED** — This agent has been merged into [`ci-auto-healer-agent`](./ci-auto-healer-agent.md).
> All capabilities are available via the unified agent. See [agents/AGENT_CONSOLIDATION_MATRIX.md](../../agents/AGENT_CONSOLIDATION_MATRIX.md) for rationale.
> **Effective:** 2026-06-11 | **Policy:** `.codex/CODEBASE_AGENCY_POLICY.md` § CAD-Mandate

> ⚠️ **DEPRECATED** — This agent has been absorbed into **[CI Testing Agent v4.0](ci-testing-agent.md)**.
> All capabilities (log retrieval, pattern matching, self-healing loop, regression detection) are
> fully preserved in the unified agent. Use `ci-testing-agent` for all new invocations.

# CI Failure Resolution Agent

**Agent Name:** `ci-failure-resolution-agent`
**Version:** 1.1.0
**Created:** 2026-02-18
**Updated:** 2026-03-18 (S153/S154 — P-030 CHANGELOG check_7 pattern added; S172 — condensed to stub)
**Status:** DEPRECATED → see [`ci-testing-agent.md`](ci-testing-agent.md) (v4.1.0)

---

## 🎯 Agent Overview

This agent automated CI failure diagnosis, resolution, and verification for GitHub Actions workflows. All capabilities are now in `ci-testing-agent.md`.

### Core Capabilities (preserved in ci-testing-agent v4+)

1. **Log & Artifact Retrieval** — GitHub MCP tools: `get_job_logs`, `actions_list`, `actions_get`
2. **Failure Pattern Recognition** — import errors, protocol isinstance, timeout, assertion, mock
3. **Root Cause Analysis** — cluster failures, trace to source, correlate with `.codex/patterns/ci_failure_patterns.yaml`
4. **Automated Fix Implementation** — apply fixes in priority order P0→P1→P2
5. **Self-Validation** — `bash .codex/scripts/self_ci_validation.sh quick` before each commit
6. **Documentation** — `.codex/CI_FAILURE_TRACKING_LOG.md`, `.codex/CI_FAILURE_PATTERNS.md`

---

## 📋 Activation

> **New work should use `ci-testing-agent` instead.**

Legacy activation commands (still functional via ci-testing-agent):
- `@copilot Fix CI failures: [workflow_run_urls]`
- `@copilot fix-ci [pr_number]`
- `@copilot analyze-ci-failures [workflow_run_urls]`

---

## 🔄 Resolution Workflow (summary)

1. Parse workflow run URLs → extract run/job IDs
2. Download logs + artifacts (`get_job_logs`, GitHub API)
3. Analyze failure patterns (import, protocol, timeout, assertion, mock, pre-merge)
4. Diagnose root causes, prioritize P0→P2
5. Implement + self-validate each fix; commit separately
6. Push → monitor CI → loop on new failures
7. Update tracking log + memory

Full protocol: see `ci-testing-agent.md` §CI Failure Resolution.

---

## 📊 Pattern Categories

| Pattern | Priority | Detection |
|---------|----------|-----------|
| Import/Dependency | P0 | `ImportError`, `ModuleNotFoundError` |
| Protocol isinstance | P1 | `isinstance.*Protocol.*must be a type` |
| Timeout | P0 | execution > threshold |
| Assertion Failures | P2 | `AssertionError` grouped by module |
| Type/Attribute Errors | P1 | `TypeError`, `AttributeError` |
| Mock Issues | P2 | `MagicMock`, `spec=` problems |
| Pre-Merge Autofix | P1 | `auto-fixable issues detected` |
| CHANGELOG cross-PR (P-030) | P1 | `ci_triage_repro.sh check_7` (see §P-030 below) |

---

## 🔌 Integration Points

**GitHub MCP tools:**
- `github-mcp-server-actions_list`, `github-mcp-server-actions_get`
- `github-mcp-server-get_job_logs`
- `github-mcp-server-list_pull_requests`, `github-mcp-server-pull_request_read`

**Custom scripts:**
- `.codex/scripts/self_ci_validation.sh` — local CI simulation
- `scripts/ci/rvs_preflight.py` — mandatory codebase scan (see §Parallel Batch Scanning)

---

## 📞 Support & Escalation

- Escalate complex issues to: @mbaetiong
- Create issue with tag: `[CI-AGENT-HELP]`
- Include: Run ID, logs, attempted fixes

---

**Agent Status:** DEPRECATED (use `ci-testing-agent`)
**Last Updated:** 2026-03-21 S172 (condensed stub; P-030 pattern retained)
**Maintainer:** GitHub Copilot + Human Oversight (@mbaetiong)

---

## Pattern P-030: CHANGELOG cross-PR auto-generated bullet (check_7)

**ID:** changelog_check7_001
**Priority:** P1
**Detection:** `ci_triage_repro.sh` check_7 reports `FAIL: section='PR #X' references 'PR #Y'`
**Session introduced:** S152/S153 | **Fix in:** `session_wrapup_autofix.py`

### Description

`session_wrapup_autofix.py` was inserting auto-generated CHANGELOG bullets into the
first `### Fixed` section found in `[Unreleased]`, regardless of which PR owns that
section. When multiple PRs have entries in `[Unreleased]`, bullets from PR #Y ended up
inside a `### Fixed (... PR #X)` heading, violating `ci_triage_repro.sh` check_7.

### Detection

```bash
bash scripts/ci/ci_triage_repro.sh --check 7
# Output: FAIL: section='PR #X' references 'PR #Y'
```

### Fix Strategy

1. Identify bullets under wrong section header:
   ```bash
   grep -n "auto-generated.*PR #\|Auto-fix.*PR #" CHANGELOG.md
   ```
2. Move each misplaced bullet to its own `### Fixed (auto-update — PR #N)` section, OR remove it and let the next `session_wrapup_autofix.py` run re-insert correctly.
3. Structural fix (prevents recurrence): `session_wrapup_autofix.py` `fix_changelog()` now creates `### Fixed (auto-update — PR #N)` subsection per PR instead of inserting into first `### Fixed`.

### Automated Fix

The structural fix in `session_wrapup_autofix.py` (PR #3626 S153) prevents future occurrences:
```python
# Creates: ### Fixed (auto-update — PR #3626)
# Instead of inserting into the first ### Fixed (which may belong to another PR)
pr_section_heading = f"### Fixed (auto-update — PR #{pr_number})\n"
```

### Historical Fixes
- PR #3626 (S153, 2026-03-18): 6 cross-PR bullets removed; structural fix deployed — c20e833

---

## ⚡ Parallel Batch Scanning Protocol

> **Mandatory.** All codebase scans MUST use `scripts/ci/rvs_preflight.py`. Running `pytest tests/` directly is **prohibited**.

**Full protocol**: [BATCH_SCAN_PROTOCOL.md](archive/status-docs/BATCH_SCAN_PROTOCOL.md)
