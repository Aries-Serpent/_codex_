# Branch `copilot/explore-codebase-implementation-plan` — What's Next

**Session:** S1270 (Coverage + AsyncSSH CVE + Collection Blockers) | **Date:** 2026-05-28
**Branch:** `copilot/explore-codebase-implementation-plan`
**Status:** ✅ COLLECTION BLOCKERS FIXED · 🔄 FULL TEST RUN IN PROGRESS

---

## 📋 Session Summary

**Completed in this session:**

| Task | Status | Notes |
|------|--------|-------|
| AsyncSSH CVE-2025 triage | ✅ DONE | `uv.lock` already at 2.23.0 (patched); PR #4637 cherry-picked |
| `requirements/lock.txt` asyncssh update | ✅ DONE | Updated 2.22.0 → 2.23.0 to match `uv.lock` |
| Collection blocker 1: `_mlf` missing | ✅ FIXED | Added `_mlf` attr to `src/codex_ml/tracking/mlflow_utils.py` |
| Collection blocker 2: `ALLOWED_TASKS` import | ✅ FIXED | Wrapped `_load_click_cli()` in try/except in `src/codex/cli/__init__.py` |
| `.github/workflows/copilot-setup-steps.yml` | ✅ PROTECTED | User applied direct fix (`3fc3f7c` → `1186f05`); lines 141–148 hardened |
| Codebase intent-files clarification | ✅ DONE | `.codex/pending_ops/variable_set_*.json` = variable-set intent files (21 files) |

**Commits:**
- `15a3409` — Fix collection blockers: add `_mlf` to tracking/mlflow_utils, guard `_load_click_cli()`, update asyncssh lock
- `1186f05` — Fix indentation in session preload step (user-applied)

---

## 🔐 Security: AsyncSSH CVE-2025 (#263)

**Status: ✅ RESOLVED in `uv.lock`**

- **Vulnerability**: Path traversal via `%u` in `AuthorizedKeysFile` (asyncssh ≤ 2.22.0)
- **Fix**: asyncssh 2.23.0
- **Active resolver** (`uv.lock`): **already at 2.23.0** ✅
- **Transitive chain**: `dvc 3.67.1` → `scmrepo 3.6.2` → `asyncssh`
- **Secondary lock** (`requirements/lock.txt`): Updated 2.22.0 → 2.23.0 in this session
- **Dependabot PR**: #4637 cherry-picked on this branch

---

## 📊 Coverage Status

**Prior baseline (pre-collection-fix):**
- Total: **17.57%** — from import-only (run was interrupted at collection phase)
- 0 tests actually ran (2 collection errors blocked full execution)

**Current run (in progress):**
- Collection blockers fixed ✅
- Tests running (3%+ at session time)
- Full results pending

**Low-coverage priority targets:**
- `src/security/` — raised to 90.72% in prior session ✅
- `src/training/` — ~8–25% (target: 50%+)
- `src/services/` — ~10–35% (target: 50%+)
- `src/agents/` — ~0% (most require torch)
- `training/` top-level — ~8–25%

---

## 🎯 Remaining Blockers & Next Steps

### Immediate (next session)

1. **Record final coverage** from current `nox -s tests` run (running at session end)
2. **Run `parallel_validation`** for PR title: `Continue coverage improvements for MSP Gateway, ITA, training, and security tests`
3. **Review any new failing tests** from the completed nox run

### Phase B Continuation (coverage improvement)

4. **MSP Gateway services tests** — `tests/services/msp_gateway/` has `__init__.py` markers; verify collection
5. **ITA (Intent/Training/Agents) coverage** — delegate to `unified-coverage-agent` if regression confirmed
6. **Training module coverage** — `src/training/` currently ~8–25%

### Phase C (codebase health)

7. **Continue VALIDATION_AUDIT_PHASE_PLAN_2026-05-27.md Phase Sets A–D**
8. **WebSocket real-time metrics** — 50% complete (streaming integration pending)
9. **CI/CD cache optimization** — Add caching to 15+ Python workflows

---

## 🚨 Protected Files

> **DO NOT MODIFY** `.github/workflows/copilot-setup-steps.yml` lines 141–148 without explicit owner approval.
> Post-PR #4616 revert hardening. Current HEAD: `1186f05`. The `run: |` block-scalar at line 143 is required.

---

## 📎 Reference

- AsyncSSH CVE detail: https://github.com/Aries-Serpent/_codex_/security/code-scanning/263
- Dependabot PR: https://github.com/Aries-Serpent/_codex_/pull/4637
- Previous whats_next: `docs/roadmap/PR4547_whats_next.md`
- Session validation plan: `.codex/VALIDATION_AUDIT_PHASE_PLAN_2026-05-27.md`
