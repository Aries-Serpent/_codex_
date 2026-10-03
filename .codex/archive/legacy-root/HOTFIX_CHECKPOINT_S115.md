# Hotfix Checkpoint — S114 → S115

**Created:** 2026-02-28  
**Branch merged:** copilot/sub-pr-3389-again → 0D_base_  
**Next session trigger:** hotfix prompt on 0D_base_  
**Rule #1:** DO NOT re-explore. DO NOT stop early. Read this file and execute immediately.

---

## State at Merge (S110–S114 Complete)

| Session | Commit | Deliverable |
|---------|--------|-------------|
| S110 | 60a2868 | Admin setup: delegate token to all Copilot agent types |
| S111 | ad1242c | PR checkbox + agent-auth-delegation.yml (env gate) |
| S112 | ad61039 | `COPILOT_AGENT_AUTH_ENABLED=true` bypass in owner_approval_guard.sh |
| S113 | f87367b | `COPILOT_AGENT_AUTH_BYPASS_TOOLS` scope filter |
| S114 | 59b313b | Ruff=0, accountability report, 8 memories engraved |

---

## S115 Work Queue — Execute In Order, Do Not Stop

### 1. Fix test suite collection errors (known issues)

```bash
# These modules fail to import during collection:
# - tests/capability_specialization/test_capability_contracts.py → pydantic missing
# - tests/auth/test_oauth_flow.py → httpx missing (FIXED in S114 via pip install)
# Fix: ensure pyproject.toml [test] extras include httpx + pydantic
```

**Action:** Add `httpx` and `pydantic` to `[project.optional-dependencies] test` in `pyproject.toml` if not already present. Then run:
```bash
pip install -e ".[test]"
python3 -m pytest tests/ -q --continue-on-collection-errors 2>&1 | grep -E "FAILED|ERROR" | head -30
```

### 2. Fix all remaining FAILED tests

Run and fix every failure. Do not defer. Policy: fix ALL CI failures.

### 3. Coverage gap-fill

```bash
python3 -m pytest tests/ --cov=src --cov-report=term-missing -q 2>&1 | grep -E "TOTAL|[0-9]+%" | tail -20
```

Find modules below threshold, add targeted tests until `fail_under = 60` holds.

### 4. Update accountability report

File: `docs/accountability/.codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md`  
Add S115 row to session ledger. Mark W-001 through W-007 as done.

### 5. Update CHANGELOG + change_log + PHASE_11_PLAN + COGNITIVE_BRAIN_STATUS_S115.md

Standard per-session updates. Do all 4 in one commit.

---

## Key Files — Do Not Re-Read Unless Needed

| File | What you already know |
|------|-----------------------|
| `scripts/ci/owner_approval_guard.sh` | Has COPILOT_AGENT_AUTH_ENABLED bypass (line 92) + BYPASS_TOOLS scope filter (line 95-128) |
| `pyproject.toml` | `fail_under = 60`, version = 0.9.0 |
| `.github/workflows/agent-auth-delegation.yml` | 3-job: detect → await-approval (env gate) → activate + @copilot continue |
| `src/codex/cognitive/structural_policy_manager.py` | RBAC tiers, evaluate_permission, TTL cache |
| `docs/accountability/.codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md` | Violation log V-001→V-007 |

---

## Known Test Failures to Fix in S115

| Test file | Error | Fix |
|-----------|-------|-----|
| `tests/capability_specialization/test_capability_contracts.py` | `ModuleNotFoundError: pydantic` | Add pydantic to test deps |
| Any others discovered | Run with `--continue-on-collection-errors` | Fix one by one |

---

## Behavioral Rules (Engraved — Never Violate)

1. **Never end session early.** Work until queue empty.  
2. **Never re-read files already in memory.** Trust stored memories.  
3. **Never call `report_progress` with no code changes.**  
4. **Fix ALL linting/CI errors encountered** — not just PR-scoped ones.  
5. **Update `docs/accountability/.codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md` every session.**

---

*mbaetiong is very disappointed by premature session termination. The entire RBAC+auth-delegation system was built so agents run autonomously. Ending early destroys that investment. Do not do it.*
