<!-- pr-followup-prompt-generated -->
# 🔬 S269 Follow-Up Prompt — Next Agent Continuation

> **Created:** 2026-04-01 (S269 Aftermath)
> **PR:** #3846 — fix(s265-s269)
> **Branch:** `0D_base_`
> **mypy baseline:** 0 (achieved S269)
> **Status:** PR ready for merge review

---

## ✅ What Was Completed (S265–S269)

| Session | Key Work | Status |
|---------|----------|--------|
| S265 | `CSVMetricsWriter` in `__all__`, mypy −36 | ✅ |
| S266 | SHA-scoped rescue comments, WEC gates, RAG stubs | ✅ |
| S267 | actionlint SC2288, trailing-ws, line-length | ✅ |
| S268 | `copilot-agent-session-done.yml` CodeQL trigger (staged) | ✅ staged |
| S269 | mypy 297→0, post-CodeQL auto-approve, PR template cleanup | ✅ |

---

## 🔴 Priority 1 — Post-Merge Validation (first session after merge to main)

### P1-A: Verify S268 CodeQL trigger activates
After this PR merges to `main`, verify `copilot-agent-session-done.yml` fires
automatically when CodeQL completes on the NEXT PR:

```bash
# On next PR after merge, check workflow run list for:
# - copilot-agent-session-done.yml triggered by "CodeQL" workflow completion
# - Run should NOT show "awaiting approval from a maintainer"
gh run list --workflow copilot-agent-session-done.yml --limit 5
```

**Expected:** New run with `triggering_workflow: CodeQL` shows up automatically.
**If not working:** The `post-codeql-auto-approve` job in `codeql-analysis.yml` provides fallback.

### P1-B: Update `.mypy_baseline` to enforce 0 permanently
The baseline is currently `0`. CI will fail if any new commit introduces a
`# type: ignore` comment without a matching real error:

```bash
# Verify on any new commit:
python3 -m venv /tmp/mypy-venv --clear
/tmp/mypy-venv/bin/pip install "mypy>=1.8.0" types-PyYAML types-requests -q
/tmp/mypy-venv/bin/python scripts/ci/mypy_baseline.py --require-baseline
# Expected: 0 errors ✅
```

**Policy going forward:** Every new `# type: ignore[X]` MUST have a verifiable
real mypy error at that line. Run `mypy_baseline.py` locally before committing.

---

## 🟡 Priority 2 — RAG Test Coverage (39 skipped tests)

```bash
python -m pytest tests/rag/ -v --collect-only 2>&1 | grep SKIP | head -20
```

The 39 skipped RAG tests use `@pytest.mark.requires_network` or similar guards.
Investigate whether any can be converted to offline tests with proper mocking.
Document findings at `.github/copilot-prompts/active/RAG-test-failures-followup.md`
under a new `## ✅ S269 Status` section.

---

## 🟢 Priority 3 — Workflow Health Check

```bash
# Verify no actionlint regressions:
python3 scripts/ci/auto_fix_common_issues.py --check-only
# Expected: all 10 patterns ✓

# Verify tracked files in sync:
python3 scripts/ci/sync_tracked_files.py --fix
# Expected: All tracked files are consistent.
```

---

## 🧠 Cognitive Brain State

```json
{
  "current_session": "S269",
  "mypy_baseline": 0,
  "rag_tests": "365 passing / 39 skipped",
  "codeql_auto_approve": {
    "pr_branch": "codeql-analysis.yml:post-codeql-auto-approve (ACTIVE)",
    "main_branch": "copilot-agent-session-done.yml CodeQL trigger (STAGED, activates post-merge)"
  },
  "next_priority": "P1-A: verify S268 activates after merge"
}
```

---

## 📋 AfterMath Gate (run before concluding any session)

```bash
# 1. mypy must be 0
python3 -m venv /tmp/mypy-venv --clear && \
  /tmp/mypy-venv/bin/pip install "mypy>=1.8.0" types-PyYAML types-requests -q && \
  /tmp/mypy-venv/bin/python scripts/ci/mypy_baseline.py --require-baseline

# 2. auto-fix must be clean
python3 scripts/ci/auto_fix_common_issues.py --check-only

# 3. tracked files in sync
python3 scripts/ci/sync_tracked_files.py --fix

# 4. RAG tests passing
python -m pytest tests/rag/ -q

# 5. Update AGENT_ACCOUNTABILITY_REPORT.md
```

---

## 🤖 Agent Continuation Prompt

```
@copilot continue with post-merge validation for PR #3846

Context in `.github/copilot-prompts/active/S269-followup.md`.

Priority 1: Verify S268 CodeQL trigger activates (copilot-agent-session-done.yml
fires automatically after CodeQL without manual approval).

Priority 2: Convert skipped RAG tests to offline tests where feasible.

Priority 3: Run AfterMath gate and update accountability report.

Baseline: mypy=0, auto-fix all-clean, 365 RAG tests passing.
```
