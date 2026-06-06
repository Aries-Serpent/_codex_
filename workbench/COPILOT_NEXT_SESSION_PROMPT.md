# Follow-Up Prompt for GitHub Copilot Agent

## @copilot Wave 3/4 post-completion: Coverage gate, CI health, and merge

**Generated:** 2026-06-06T06:40Z  
**Branch:** `copilot/explore-codebase-and-create-plan`  
**PR:** #4792

---

## Context Lock

All 45 gaps are now implemented (Waves 0–4). The only open item is:

- **Gap 5** — Coverage gate: currently at **17.57%**; roadmap target **≥80%**; evidence at `workbench/coverage/gap5_coverage_evidence.md`

`special_flags.needs_verification: []` — empty; no re-verification required.

---

## Primary Objective

Advance the coverage gate (Gap 5) and prepare PR #4792 for merge.

---

## Task Sequence

### Task 1 — Verify PR #4792 CI health (FIRST)
```
1. Check latest CI run on branch copilot/explore-codebase-and-create-plan
2. Use github-mcp-server list_workflow_runs to get most recent run IDs
3. For any failing jobs: use get_job_logs to retrieve failure details
4. Fix any regressions introduced by the Wave 3/4 implementation commits (only fix regressions — do NOT fix pre-existing failures)
```

### Task 2 — Advance coverage gate (Gap 5)
Target: advance floor by **+5 percentage points** (17.57% → ≥22%).

Approach:
1. Run: `python -m pytest --cov=src/codex_ml --cov=src/codex --cov-report=term-missing -q 2>&1 | tail -30` to find lowest-coverage modules
2. Identify top 3 uncovered modules with existing source code
3. Dispatch `unified-coverage-agent` for each: fill gaps with unit tests, ensure they pass, commit
4. Update `workbench/coverage/gap5_coverage_evidence.md` with new numbers
5. Update `workbench/gap_backlog_prioritized.md` gap 5 status line

### Task 3 — Update session wrapup compliance
```bash
python3 scripts/ci/session_wrapup_autofix.py --check --pr-number 4792
```
Fix any REQ-4/REQ-5 freshness failures (CHANGELOG.md and AGENT_ACCOUNTABILITY_REPORT.md must both appear in the latest commit).

### Task 4 — Run parallel_validation
Once all code changes are committed, run `parallel_validation` to gate on CodeQL and code review. Address any high/critical findings before merging.

### Task 5 — Final report_progress and merge readiness comment
Post a final `report_progress` with complete checklist. Then reply to PR comment thread summarizing:
- All 45 gaps complete
- Coverage floor advanced to X%
- CI green
- Ready for merge

---

## Key Files Reference

| File | Purpose |
|---|---|
| `workbench/wave3_wave4_dispatch_matrix.md` | Full dispatch matrix for all 25 Wave 3/4 gaps |
| `workbench/gap_backlog_prioritized.md` | Gap status tracker (all 44 ✅, gap 5 🟡) |
| `workbench/gap_execution_queue.yaml` | Machine-readable queue; `needs_verification: []` |
| `workbench/wave_execution_control.md` | Wave completion report |
| `workbench/coverage/gap5_coverage_evidence.md` | Coverage gate evidence + roadmap |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | REQ-4 compliance |
| `CHANGELOG.md` | REQ-5 compliance |

---

## Dispatch Constraints
- Max concurrent background agents: **4**
- All artifacts under `workbench/evidence/` (never `/tmp`)
- Pre-existing lint failures in `ruff check src/ tests/` are NOT your responsibility unless introduced by your changes
- Do NOT modify `.github/workflows/copilot-setup-steps.yml` lines 141–147 (hardened YAML block)

---

## Success Criteria
- [ ] PR #4792 CI fully green (or only pre-existing failures documented)
- [ ] Coverage floor ≥ 22% (from 17.57%)
- [ ] `session_wrapup_autofix --check --pr-number 4792` passes (REQ-4/REQ-5)
- [ ] `parallel_validation` complete with no new HIGH/CRITICAL issues
- [ ] PR #4792 marked ready-to-merge with final summary comment
