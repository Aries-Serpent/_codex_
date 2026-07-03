# 🎯 PHASE 8.3 — REMEDIATION PRIORITY & SEQUENCING

**Workstream:** 8.3.2 — Remediation Priority & Sequencing
**Track Lead:** cross-platform-filename-validator (Track 8.3)
**Authority:** @mbaetiong (D-tier autonomy)
**Decision Gate:** GO CONTINUE (all gates approved)
**Date Generated:** 2026-07-03T02:00Z
**Input:** PHASE_8_3_COMPATIBILITY_MATRIX.md

---

## EXECUTIVE SUMMARY

This document defines the **exact sequence** in which the 11 identified platform compatibility issues
should be remediated to minimize risk, maximize parallelism, and respect cross-track dependencies.

**Key Insight:** The critical path is **B1 (case collisions) → H1 (.gitattributes) → H2/H3/H4 (symlinks/paths)**.
These three issues block Windows/macOS support. The remaining issues (M1/M2/M3/L1/L2) are independent and
can proceed in parallel or be deferred to later phases.

---

## REMEDIATION PHASES

### PHASE 1: BLOCKING (B1) — Case-Collision De-Duplication

**Gate:** Blocks Windows/macOS checkout. **Must complete before 8.2 doc moves.**

**Issues:** B1

**Sequence:**

| Step | Task | Owner | Effort | Duration | Dependency |
|------|------|-------|--------|----------|------------|
| 1.1 | Audit inbound references to colliding files (grep all 28 files + `docs/`, `.codex/`, `reports/` for links) | Track 8.3 | 2h | 1–2 days | None |
| 1.2 | Decide canonical casing per group (recommend **lowercase** for consistency: `index.md`, `ci.md`) | @mbaetiong | 0.5h | <1 day | 1.1 |
| 1.3 | Merge conflicting content (if files differ; most are duplicates by case only) | Track 8.3 | 3h | 1–2 days | 1.2 |
| 1.4 | Git-remove non-canonical files (`git rm --cached docs/ARCHITECTURE.md docs/Architecture.md`) | Track 8.3 | 1h | <1 day | 1.3 |
| 1.5 | Update all inbound references (mkdocs nav, links in other docs, README) | Track 8.3 | 4–6h | 2–3 days | 1.4 |
| 1.6 | Verify links (dead-link check, mkdocs build test) | Track 8.3 | 1h | <1 day | 1.5 |
| 1.7 | Commit & push (branch `copilot/deploy-phase-8-agents`) | Track 8.3 | 0.5h | <1 day | 1.6 |

**Total Phase 1 Effort:** 11–13h (2–4 days, 1 person)

**Cross-Track Gate:** **PHASE 1 MUST COMPLETE before Track 8.2 bulk doc moves** to avoid merge churn.
Contact 8.2 PM: "Case collisions resolved; docs finalized at canonical paths. You may proceed with
directory restructuring."

**Risk Mitigation:**
- **Risk:** Broken links if references incomplete → **Mitigation:** Use reference-graph tool (if available)
  or multi-pass grep + manual verification
- **Risk:** Lost content if files differ → **Mitigation:** Audit content before deletion; commit merge
  step separately

**Rollback:** If issues arise, revert commit; branches remain separate until next attempt.

---

### PHASE 2: HIGH-PRIORITY (H1, H2, H3, H4) — Platform-Breaking Fixes

**Gate:** Blocks Windows/macOS execution. **Can run in parallel; no inter-dependencies.**

**Issues:** H1 (gitattributes), H2 (symlinks), H3 (hardcoded paths), H4 (tool paths)

**Sequence (4 Parallel Tracks):**

#### H1 Track: Root `.gitattributes`

| Step | Task | Owner | Effort | Duration | Notes |
|------|------|-------|--------|----------|-------|
| 2.1.1 | Copy `.config/.gitattributes` to root `.gitattributes` | Track 8.3 | 0.25h | <1 day | Verify content matches |
| 2.1.2 | Test attribute activation: `git check-attr text eol -- scripts/run_updates.sh` | Track 8.3 | 0.5h | <1 day | Should report `text: auto eol: lf` |
| 2.1.3 | One-time renormalize: `git add --renormalize .` or similar | Track 8.3 | 1h | <1 day | **CAUTION:** Large diff; may require `--force` |
| 2.1.4 | Commit & push | Track 8.3 | 0.5h | <1 day | Test on Windows runner post-commit |

**H1 Subtotal:** 2.25h (1 day, can start immediately after 1.7)

**H1 Risk:** Low — gitattributes is passive; rollback is simple (revert commit).

---

#### H2 Track: Symlink Conversion

| Step | Task | Owner | Effort | Duration | Notes |
|------|------|-------|--------|----------|-------|
| 2.2.1 | Triage 2 critical code symlinks (audit targets + decide real-file vs import-shim strategy) | Track 8.3 | 1h | <1 day | Test imports after conversion |
| 2.2.2 | Convert critical symlinks to real files (or implement import shim) | Track 8.3 | 2h | 1–2 days | Run test suite after conversion |
| 2.2.3 | Evaluate Hydra config symlinks (4 `configs/*` dirs); replicate or consolidate if needed | Track 8.3 | 1.5h | 1 day | Integration test with Hydra |
| 2.2.4 | Add `.venv_ci/`, `venv_test/` to `.gitignore`; git-remove tracked symlinks | Track 8.3 | 0.5h | <1 day | Run `git rm --cached` |
| 2.2.5 | Commit & push | Track 8.3 | 0.5h | <1 day | Verify cleanup via `git ls-files -s` (no mode 120000) |

**H2 Subtotal:** 5.5h (2–3 days)

**H2 Risk:** Medium — must test code imports; Hydra integration testing required.

---

#### H3 Track: Hardcoded Repo-Root Paths (44 files)

| Step | Task | Owner | Effort | Duration | Notes |
|------|------|-------|--------|----------|-------|
| 2.3.1 | Create centralized `repo_root()` resolver in `src/codex/utils/path_utils.py` | Track 8.3 | 1h | <1 day | Test with `git rev-parse --show-toplevel` fallback |
| 2.3.2 | Identify all 44 files via grep: `grep -r "/home/runner/work/_codex_/_codex_"` | Track 8.3 | 0.5h | <1 day | Automate regex for replacement |
| 2.3.3 | Replace hardcoded paths with `repo_root()` calls (batch edit) | Track 8.3 | 2h | 1–2 days | Use regex+sed or manual in critical files |
| 2.3.4 | Test each module (import + execution) after replacement | Track 8.3 | 3h | 2–3 days | Run test suite; manual spot-checks for CI helpers |
| 2.3.5 | Commit & push | Track 8.3 | 0.5h | <1 day | Verify CI pipeline success |

**H3 Subtotal:** 7h (3–4 days)

**H3 Risk:** Medium — must verify each module's imports and CI helpers; test-driven approach recommended.

---

#### H4 Track: Linux Tool-Path Assumptions (8 files)

| Step | Task | Owner | Effort | Duration | Notes |
|------|------|-------|--------|----------|-------|
| 2.4.1 | Identify all Linux tool paths: `grep -r "/opt/hostedtoolcache\|/usr/bin\|/usr/local"` | Track 8.3 | 0.5h | <1 day | Focus on `.py` files; ignore comments |
| 2.4.2 | Replace hardcoded paths with `shutil.which()` or platform guards | Track 8.3 | 1.5h | 1 day | Add `if sys.platform == "win32"` guards where needed |
| 2.4.3 | Document WSL/Git-Bash requirement for CI helpers | Track 8.3 | 0.5h | <1 day | Add docstring + inline comment |
| 2.4.4 | Test on CI (GitHub Actions runner) | Track 8.3 | 1h | 1–2 days | Verify CodeQL and other CI tools still work |
| 2.4.5 | Commit & push | Track 8.3 | 0.5h | <1 day | CI pipeline sign-off |

**H4 Subtotal:** 4h (2 days)

**H4 Risk:** Medium (CI-scoped) — low local risk; CI runner verification critical.

---

**PHASE 2 TOTAL:** 18.75h (2–4 days, 4 parallel tracks)

**Parallelization:** H1, H2, H3, H4 are **independent**. Start all 4 simultaneously after Phase 1.

**Cross-Track Gate:** Coordinate H4 timing with Track 8.4 (CI/CD hardening) if 8.4 also refactors CI
helpers; otherwise, proceed independently.

**Risk Mitigation:**
- **Risk:** Test suite failures → **Mitigation:** Run full suite after each step; pin + revert on failure
- **Risk:** CI runner issues → **Mitigation:** Test on Windows + macOS runners post-commit
- **Risk:** Import breakage (H3) → **Mitigation:** Spot-check critical imports before batch commit

---

### PHASE 3: MEDIUM-PRIORITY (M1, M2, M3) — Portability Improvements

**Gate:** Improves Windows/macOS experience but **not a blocker** (WSL/Git-Bash mitigates).

**Issues:** M1 (`/tmp/` paths), M2 (bash-only scripts), M3 (Linux-specific commands)

**Sequence (3 Parallel Tracks):**

#### M1 Track: `/tmp/` Path Replacement (93 files)

| Step | Task | Owner | Effort | Duration | Notes |
|------|------|-------|--------|----------|-------|
| 3.1.1 | Grep all `/tmp/` hardcodes: `grep -r "/tmp/"` | Track 8.3 | 0.5h | <1 day | Focus on `.py` files only |
| 3.1.2 | Replace with `tempfile.gettempdir()` (batch regex) | Track 8.3 | 1.5h | 1 day | Use `tempfile.NamedTemporaryFile()` where applicable |
| 3.1.3 | Audit for `/tmp/` path assumptions (symlinks, permissions) | Track 8.3 | 1h | 1 day | Ensure no hardcoded `/tmp/path` assumptions |
| 3.1.4 | Test on Windows + macOS (temp dir logic) | Track 8.3 | 1.5h | 1–2 days | Run suite; verify temp cleanup |
| 3.1.5 | Commit & push | Track 8.3 | 0.5h | <1 day | Low-risk commit |

**M1 Subtotal:** 5h (2–3 days)

**M1 Risk:** Low — `tempfile` module is robust.

---

#### M2 Track: Bash-Only Scripts (Triage; Defer Porting)

| Step | Task | Owner | Effort | Duration | Notes |
|------|------|-------|--------|----------|-------|
| 3.2.1 | Triage 216 scripts: categorize by criticality (setup/test/ci vs. utils) | Track 8.3 | 1.5h | 1 day | Identify high-traffic scripts (~47) for potential porting |
| 3.2.2 | Document WSL/Git-Bash requirement in README + script headers | Track 8.3 | 1h | 1 day | Add shebang comments; update setup docs |
| 3.2.3 | (DEFER) Port high-traffic scripts (47) to Python in future phase | Track 8.3 (future) | **defer** | — | Out of scope for 8.3.2; add to roadmap |

**M2 Subtotal (8.3.2):** 2.5h (1 day) — triage + docs only; porting deferred.

**M2 Risk:** Low — documentation is non-breaking.

---

#### M3 Track: Linux-Specific Commands (Guards + Documentation)

| Step | Task | Owner | Effort | Duration | Notes |
|------|------|-------|--------|----------|-------|
| 3.3.1 | Grep Linux commands: `apt`, `sudo`, `systemctl`, `sed -i`, etc. in 33 scripts | Track 8.3 | 0.5h | <1 day | Quantify impact |
| 3.3.2 | Add platform guards (e.g., `if command -v apt-get`) to critical ~10 scripts | Track 8.3 | 1.5h | 1–2 days | Graceful fail-soft on missing tools |
| 3.3.3 | Document WSL/Git-Bash requirement + tool assumptions | Track 8.3 | 0.5h | <1 day | Update script headers + docs |
| 3.3.4 | (OPTIONAL) Normalize `sed -i` to Python for ~10 files | Track 8.3 | **defer** | — | Low priority; WSL has `sed` |
| 3.3.5 | Commit & push | Track 8.3 | 0.5h | <1 day | Low-risk commit |

**M3 Subtotal (8.3.2):** 3.5h (1–2 days) — guards + docs; full porting deferred.

**M3 Risk:** Low — guards fail gracefully.

---

**PHASE 3 TOTAL:** 11h (2–4 days, 3 parallel tracks)

**Parallelization:** M1, M2, M3 are **independent**. Run in parallel; start after Phase 1 completes,
optionally overlapping with Phase 2.

**Cross-Track Gate:** No external dependencies; Track 8.4 may inherit M3 guards.

**Risk Mitigation:**
- **Risk:** Over-scoping (porting all scripts) → **Mitigation:** Triage + defer; Phase 8.3.2 focuses on
  documentation and critical guards only
- **Risk:** False positives in grep → **Mitigation:** Manual review of each matched file

---

### PHASE 4: LOW-PRIORITY (L1, L2) — Hygiene Cleanup

**Gate:** Non-blocking; recommended for repository cleanliness.

**Issues:** L1 (`.editorconfig` relocation), L2 (virtualenv untracking)

**Sequence (2 Independent Tasks):**

#### L1 Task: `.editorconfig` Relocation

| Step | Task | Owner | Effort | Duration |
|------|------|-------|--------|----------|
| 4.1.1 | Copy `.config/.editorconfig` to root `.editorconfig` | Track 8.3 | 0.25h | <1 day |
| 4.1.2 | Commit & push | Track 8.3 | 0.25h | <1 day |

**L1 Subtotal:** 0.5h (<1 day)

---

#### L2 Task: Virtualenv Untracking

| Step | Task | Owner | Effort | Duration |
|------|------|-------|--------|----------|
| 4.2.1 | Add `.venv_ci/` and `venv_test/` to `.gitignore` | Track 8.3 | 0.25h | <1 day |
| 4.2.2 | Run `git rm --cached .venv_ci .venv_test` (if tracked) | Track 8.3 | 0.25h | <1 day |
| 4.2.3 | Commit & push | Track 8.3 | 0.25h | <1 day |

**L2 Subtotal:** 0.75h (<1 day)

---

**PHASE 4 TOTAL:** 1.25h (<1 day, can run in parallel with earlier phases)

---

## OVERALL REMEDIATION TIMELINE

### Sequential Critical Path

```
PHASE 1: B1 De-Collision  [████████████] 11–13h  (2–4 days)
         ↓ (gate 8.2)
PHASE 2: H1/H2/H3/H4      [████████████████████] 18.75h (2–4 days, parallel)
         ↓ (test + verify)
PHASE 3: M1/M2/M3         [███████████████] 11h     (2–4 days, parallel)
         ↓
PHASE 4: L1/L2            [█] 1.25h                (<1 day)
```

**Critical Path Duration:** 2–4 weeks (assuming 8–10 hours/day, 1 person)
**With Parallelization:** Overlapping tracks can reduce to 2–3 weeks

**Milestone Gates:**
- **End of Phase 1:** B1 resolved; 8.2 unblocked for doc moves
- **End of Phase 2:** Windows/macOS checkout viable; all HIGH issues resolved
- **End of Phase 3:** Full portability documentation in place; WSL/Git-Bash story clear
- **End of Phase 4:** Repository hygiene complete

---

## RISK MITIGATION & ROLLBACK STRATEGY

### Phase 1 (B1) Rollback

**Risk:** Broken references after deletion.
**Mitigation:**
1. Use reference-graph tool (if available) to audit all inbound links before deletion
2. Commit in this order: (1) merge step, (2) deletion step, (3) reference update
3. Each sub-commit is independently revertible

**Rollback Procedure:**
```bash
git revert <commit-hash>  # Revert reference updates
git revert <commit-hash>  # Revert deletions
git revert <commit-hash>  # Revert merge if needed
```

### Phase 2 (H1–H4) Rollback

**Risk:** Import failures (H3), symlink issues (H2), CI tool unavailability (H4), CRLF corruption (H1).

**Mitigation:**
1. **H1 (gitattributes):** Large renormalization diff; use `--force-add` on CI if needed; test on
   Windows runner first
2. **H2 (symlinks):** Test code imports on Linux/macOS before pushing; run full test suite
3. **H3 (hardcoded paths):** Spot-check critical imports; test on CI
4. **H4 (tool paths):** Run on GitHub Actions runner before general commit

**Rollback Procedure:**
```bash
git revert <commit-hash>
# If renormalization (H1) causes issues, reset to pre-H1 state and retry with --rebase-mergebase
```

### Phase 3 (M1–M3) Rollback

**Risk:** Low — these are independent and use well-tested utilities.

**Rollback Procedure:**
```bash
git revert <commit-hash>
```

---

## RESOURCE ALLOCATION

| Phase | Effort | Owner | Duration | Status |
|-------|--------|-------|----------|--------|
| 1 | 11–13h | Track 8.3 | 2–4 days | Ready |
| 2 | 18.75h | Track 8.3 (4 parallel) | 2–4 days | Ready |
| 3 | 11h | Track 8.3 (3 parallel) | 2–4 days | Ready |
| 4 | 1.25h | Track 8.3 | <1 day | Ready |
| **TOTAL** | **42h** | Track 8.3 | **2–4 weeks** | Ready |

**Capacity:** 1 full-time engineer (Track 8.3) for 4 weeks, or 2 engineers for 2 weeks.

---

## SUCCESS CRITERIA

### Windows Checkout Validation (Post-Remediation)

```bash
# On Windows NTFS (case-insensitive filesystem):
git clone https://github.com/Aries-Serpent/_codex_ --branch copilot/deploy-phase-8-agents
cd _codex_

# Verify no case-collision dirty files:
git status  # Should report: "On branch ... nothing to commit, working tree clean"

# Verify gitattributes active:
git check-attr text eol -- scripts/run_updates.sh  # Should report: text: auto, eol: lf

# Verify symlinks handled (no .txt files for symlinks):
git ls-files -s | grep 120000  # Should return nothing (0 symlinks)

# Verify paths resolve:
python -c "from src.codex.utils.path_utils import repo_root; print(repo_root())"
# Should print: C:\Users\...\work\_codex_\_codex_ (or Windows path equivalent)

# Test shell script shebang:
bash scripts/run_updates.sh --help  # Should work under Git-Bash; no "bad interpreter" error
```

### macOS Checkout Validation (Post-Remediation)

```bash
# On macOS APFS (case-insensitive, case-preserving filesystem):
git clone https://github.com/Aries-Serpent/_codex_ --branch copilot/deploy-phase-8-agents
cd _codex_

# Same checks as Windows above
```

### Linux Validation (Control / Smoke Test)

```bash
# On Linux (case-sensitive filesystem):
git clone https://github.com/Aries-Serpent/_codex_ --branch copilot/deploy-phase-8-agents
cd _codex_

# Same checks as Windows/macOS
```

---

## TRACKING & COMMUNICATION

### Phase 1 (B1)

- **Slack:** `#phase-8-track-8-3` — Daily standup with 8.2 PM
- **Tracking:** GitHub Issues / Jira board for each step
- **Gate:** Notify @mbaetiong when ready to proceed to Phase 2

### Phase 2 (H1–H4)

- **Tracking:** 4 parallel GitHub Issues (one per track)
- **Gate:** Verify Windows + macOS checkout + CI success before proceeding to Phase 3

### Phase 3 (M1–M3)

- **Tracking:** 3 parallel GitHub Issues
- **Gate:** Document requirements in README before Phase 4

### Phase 4 (L1–L2)

- **Gate:** Simple commit; no external dependencies

---

## DECISION AUTHORITY

| Phase | Approval Authority | Escalation |
|-------|-------------------|------------|
| 1 | @mbaetiong (D-tier autonomy) | If Phase 1 duration > 5 days: escalate to 8.2 PM |
| 2 | Track 8.3 (autonomous) | If any test suite failure: escalate to @mbaetiong |
| 3 | Track 8.3 (autonomous) | If WSL/Git-Bash impact unexpected: escalate |
| 4 | Track 8.3 (autonomous) | None |

---

**Planning Status:** ✅ COMPLETE
**Next Deliverable:** 8.3.3 Critical Fixes (executable task list)
**Timestamp:** 2026-07-03T02:00Z
**Authority:** cross-platform-filename-validator (Track 8.3)
