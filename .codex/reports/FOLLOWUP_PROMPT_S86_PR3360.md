# Follow-Up Prompt S86 → S87

**PR:** #3360 (`copilot/sub-pr-3248-again` → `0D_base_`)
**Session:** S86 → S87 handoff
**Date:** 2026-02-24
**Latest commit:** `86ce05b`
**Branch:** `copilot/sub-pr-3248-again`

---

## S86 Completion Summary

| Task | Status | Commit |
|------|--------|--------|
| Art_Validation Fast Validation — trailing whitespace in PR-3360-followup.md | ✅ Fixed | 86ce05b |
| Pre-Flight CI Validation — composite action plugin pin awareness | ✅ Fixed | 86ce05b |
| Resilient Suite slow — Decision.name field + evaluator→evaluation_fn | ✅ Fixed | 86ce05b |
| Resilient Suite slow — test_training_resume HFModelUnavailableError skip | ✅ Fixed | 86ce05b |
| Cognitive brain S86 status | ✅ Done | 86ce05b |
| Follow-up prompt S87 | ✅ This file | 86ce05b |

---

## S87 Priority Queue

### 🔴 P0 — CI Verification (MANDATORY FIRST STEP)

```bash
# Per AI Codebase Agency Policy: NEVER declare CI green without checking ALL workflows
# Use GitHub MCP list_workflow_runs for branch copilot/sub-pr-3248-again
# Check EVERY workflow:
# - Art_Validation Pipeline / Fast Validation
# - Resilient Validation Suite / validation (quick)
# - Resilient Validation Suite / validation (slow)
# - Resilient Validation Suite / validation (integration)
# - Pre-Flight CI Validation
# - Pre-Merge Validation
# - Art_Rust-Python Hybrid Swarm CI/CD / Code Coverage
# - Art_"CodeQL"
```

Fix ALL failures before proceeding.

### 🔴 P1 — Merge Gate

Once CI is green on `86ce05b` (or latest):
1. Merge `copilot/sub-pr-3248-again` → `0D_base_`
2. Verify `0D_base_` CI is green after merge
3. Begin S89 HOTFIX prep (per plan: S89 merges regardless of green status)

### 🟡 P2 — Proactive Test Audit

Run locally to find any remaining failures before CI does:
```bash
# Quick suite
python -m pytest tests/ -m "not slow and not integration" --timeout=60 --maxfail=5 -q 2>&1 | tail -30

# Slow suite
python -m pytest tests/ -m "slow" --timeout=600 --maxfail=5 -q 2>&1 | tail -30
```

### 🟡 P3 — Recon Scout RS-ARCH-001/002

```bash
# Duplicate function detection
grep -rn "^def \|^    def " src/ --include="*.py" | awk -F: '{print $NF}' | sort | uniq -d | head -20

# __init__.py gap scan
find src/ -type d | while read d; do [ ! -f "$d/__init__.py" ] && echo "MISSING: $d/__init__.py"; done
```

### 🟢 P4 — Agent Ecosystem 53 → 70+

Update `.github/agents/AGENT_REGISTRY.yaml`:
- Current: 36 registered agents (v1.2.0)
- Target: 70+ ecosystem map
- Scan `.github/agents/` for all `.md` files not yet in REGISTRY

### 🟢 P5 — Coverage Roadmap Phase 23–26

Target: 90% overall. Gap analysis from latest CI coverage report.

---

## Key Patterns for S87 Agent

| Pattern | Trigger | Fix |
|---------|---------|-----|
| P-029 | JSON/MD missing `\n`; YAML trailing blank | `end-of-file-fixer` |
| P-030 | Plugin pin check missing composite action | Extend search to `.github/actions/*/action.yml` |
| P-031 | `Decision(evaluator=func)` | `Decision(name=id, evaluation_fn=func)` |
| P-032 | `HFModelUnavailableError` in test | `try/except: pytest.skip(...)` |

---

## Critical Reminders

- ✅ NEVER declare CI green without querying `list_workflow_runs` for ALL workflow names
- ✅ Run `pre-commit run trailing-whitespace end-of-file-fixer` on all generated files
- ✅ Check dataclass `__init__` signatures before constructing with keyword arguments
- ✅ Tests that call HuggingFace model download must guard with `HFModelUnavailableError` skip
- ✅ When workflows use composite actions, CI checks must scan composite action files too

---

**Generated:** 2026-02-24T19:45:00Z
**Next session:** S87
