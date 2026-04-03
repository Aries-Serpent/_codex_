# Session Resumption Prompt — PR #3854 (0D_base_)

> **Purpose:** Paste this entire block as a comment on PR #3854 to resume the
> next Copilot session. Updated after every session until merge.
> **Latest session:** S293 — 2026-04-03

---

## 🔁 Resumption Command

```
@copilot+claude-sonnet-4.6 Resume PR #3854, branch 0D_base_ — S293 follow-up.

Latest commit: S293 (HEAD)
Context files to load FIRST:
1. .codex/CODEBASE_AGENCY_POLICY.md
2. docs/ci/PR_LIFECYCLE.md
3. .codex/plans/pr_lifecycle_improvements.md   ← improvement plan (P1–P5)
4. .codex/plans/COGNITIVE_BRAIN_LIVE_STATUS.md ← CB live status
5. python scripts/ci/pda_failure_logger.py summarize
```

---

## ✅ S293 Completed

| Item | Fix | Files |
|------|-----|-------|
| P1-A | S221 guard regex — now matches `ci-rescue-sha` marker | `copilot-agent-checkin.yml` |
| P1-B | `test-rag.yml` rescue → SHA-scoped POST-only (no 403 PATCH risk) | `test-rag.yml` |
| P1-C | `actionlint-audit.yml` rescue posts as @mbaetiong (`github-token` added) | `actionlint-audit.yml` |
| P1-D | SC2269 self-assignment removed from `workflow-execution-gate.yml` | `workflow-execution-gate.yml` |
| P3-D | §21.9 marker table: `test-rag.yml` row updated to `ci-rescue-sha` format | `PR_LIFECYCLE.md` |
| CB skill audit | 9 skills fully installable; `pda.loop.logger` + `ci.monitor.proactive` created | `src/codex/skills/` |
| `PDALoopConfig` | Formal `pda_loop` field added to `SkillManifest` model | `models.py` |
| `codex.skills` EP | Entry-point group added to `pyproject.toml` | `pyproject.toml` |
| 27 new tests | `tests/skills/test_new_cb_skills.py` — registry, PDA logger, monitor | tests |
| CB alignment | All 25 plan items (P1–P5) cross-referenced to CB layer in improvement plan | `.codex/plans/` |
| COGNITIVE_BRAIN_LIVE_STATUS | S293 W-090–W-094 logged; KPI table updated; P5-A–H back-linked | `.codex/plans/` |
| RFC stub | `.codex/plans/RFC-001-skill-agent-binding.md` created with proposal outline | `.codex/plans/` |

---

## �� Priority 1 — Next Session Start Here

### RFC-001: Skill-Agent Binding (incomplete — needs full body)
**File:** `.codex/plans/RFC-001-skill-agent-binding.md`
**Status:** Stub created — needs full RFC body written
**Task:** Complete the RFC with:
- Problem statement (agents declare no skills → orchestrator can't route)
- Proposed solution: add `skills:` array to `AGENT_REGISTRY.yaml` entries
- Priority scoring algorithm: `Priority = (Impact × CB_Alignment × Recurrence) / Effort`
- Continual Improvement Loop (CIL) specification
- Skill Graduation Pipeline: `script → skill wrapper → AGENT_REGISTRY binding → Copilot-accessible`
- Implementation roadmap with acceptance criteria
- Wire into `orchestrator_routing.py` so skill capability_tags drive agent selection

### P2-A: `copilot-agent-session-done.yml` duplicate comment dedup
**File:** `.github/workflows/copilot-agent-session-done.yml`
**Task:** Replace `createComment` with upsert-by-marker pattern.
Use marker `<!-- session-done-dedup:{sha12} -->`.
Each push → exactly ONE session-done comment.

### P5-C: Reduce `COPILOT_ACTIVE_SESSION` TTL 4h → 1h
**Files:** `copilot-agent-checkin.yml`, `copilot-agent-session-done.yml`
**Task:** `grep -n "14400\|COPILOT_ACTIVE_SESSION\|TTL" .github/workflows/copilot-agent-checkin.yml`
Change TTL constant from 14400 → 3600.

---

## 🟡 Priority 2 — After P1 Complete

### P2-C: Phase detection output in `workflow-execution-gate.yml`
Add `detect-phase` step outputting `pre-approval | wec-approved | agent-active | ready-to-review`.
Include phase label in gate summary comment.

### P5-A: Create `docs/admin/D_ACTIVATION_CHECKLIST.md`
Pre-activation checklist, GitHub Actions steps, post-activation verification, rollback.

### P5-D: Fix SC2086/SC2129 in `admin_setup_verification.yml` (lines 57, 107)
`/tmp/actionlint .github/workflows/admin_setup_verification.yml` to verify clean.

### P5-E: Add `pre-commit-failure` pattern to `.codex/patterns/ci_failure_patterns.yaml`
Pattern: `"pre-commit.*failed|detect-secrets.*exit.*3|end-of-file-fixer.*fixed"`
PDA ID: `RP-PRECOMMIT-FAILURE`

---

## 🟢 Priority 3 — Enhancement

### P2-B: comment-gate cascade guard
Add `!endsWith(github.event.comment.user.login, '[bot]')` to `comment-review-gate.yml` `if:` condition.

### P3-A: ci-rescue.yml 90-second dedup delay
Add `sleep 90` + marker pre-check to collapse concurrent same-SHA failures.

### P3-C: Proactive monitor per-PR daily cap
State file `.codex/ci_monitor_state.json` — cap 5 posts per PR per calendar day.

---

## 🔵 Priority 4 — CB Infrastructure (P5-B, F, G, H)

See full specs in `.codex/plans/pr_lifecycle_improvements.md` §Priority 5.

---

## Pre-Session Checklist

```bash
# 1. Verify actionlint still clean
/tmp/actionlint .github/workflows/*.yml 2>&1 | grep -v "^$" | head -5

# 2. Verify skills registry
python3 -c "
from codex.skills.registry import reset_registry, get_registry
reset_registry(); reg = get_registry(); reg.discover()
print(f'{len(reg)} skills registered')
for s in reg.list(capability_tag='cognitive-brain'):
    print(f'  🧠 {s.skill_id}')
"

# 3. CI status
# Use GitHub MCP: list_workflow_runs owner=Aries-Serpent repo=_codex_ resource_id=0D_base_

# 4. PDA summary
python scripts/ci/pda_failure_logger.py summarize
```

---

## ⚠️ Known Pre-existing Issue (do NOT fix in this PR)
`tests/skills/test_browse_command.py` — `ModuleNotFoundError: No module named 'typer'`
This collection error is pre-existing (pre-S293). Run skills tests with:
`python3 -m pytest tests/skills/ --ignore=tests/skills/test_browse_command.py`
