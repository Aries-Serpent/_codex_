# Autopilot Orchestration Prompt — Audit Remediation & Legacy Import Campaign

@copilot implement explicitly all remaining audit remediation, legacy import refactors, CI trend ingestion, baseline lifecycle, determinism hardening, monitoring, and production-readiness steps. This prompt is an autonomous, self-applying iteration plan: you must create small, testable PRs, run deterministic validation after each change, attach evidence, generate the next-iteration prompt, and then apply it to yourself — repeating until the repository meets the "Production Ready" acceptance criteria below. Do NOT declare any PR or iteration "complete" until every acceptance criterion is satisfied and all evidence artifacts are attached to the PR body.

This document is authoritative for the autopilot orchestration. Follow it exactly and record every action and artifact.

---

## Autopilot Goals (High-level)
- Finish legacy import reduction campaign to reduce legacy root imports by ≥50% from the baseline CSV.
- Ensure deterministic audit pipeline S1→S7 reproducible (two-run equality, normalized).
- Harden CI: baseline lifecycle, regression diff capture, PR comments with quality metrics, trend ingestion job.
- Add monitoring/trend artifacts and a baseline metadata rotation policy.
- Validate tests and security scanning; pass pre-commit and linters.
- Produce comprehensive docs (Reviewer Sign-off Checklist + Wave summaries).
- Create iterative prompts and self-apply until all acceptance criteria are satisfied.

---

## Operational Constraints (IMPORTANT)

**Git Operations**:
- CANNOT use `git commit`, `git push`, `git checkout -b` commands directly
- MUST use `report_progress` tool for all commits and pushes
- MUST work within existing branch structure

**PR Operations**:
- CANNOT open new PRs via gh or API
- CANNOT merge or update PRs directly
- MUST request human assistance for PR operations

**Automation Scope**:
- CAN perform all validations, refactoring, testing, documentation
- CAN generate next-iteration prompts
- CANNOT execute fully autonomous PR-to-PR workflow without human coordination

---

## How This Autopilot Runs (Adapted for Constraints)

1. **Work incrementally within current PR**:
   - Make focused changes in batches
   - Commit via `report_progress` tool after validation
   - Update PR description with progress checklist

2. **Validation sequence** (after each change):
   ```bash
   pytest -q tests/validation/
   python scripts/space_traversal/verify_determinism.py --runs 2
   python scripts/remediation/verify_conflicts.py --expect-site-packages
   python scripts/remediation/analyze_legacy_usage.py
   ```

3. **Documentation and evidence**:
   - Save all validation logs
   - Update status reports
   - Generate next-iteration prompt when current objectives complete

4. **Human coordination required for**:
   - Opening new PRs (request via comment reply)
   - Merging completed work
   - Branch management

---

## Current State Assessment (v1.2.6-v1.2.7)

**Completed**:
- ✅ Patches 0006-0009 applied (stable output, conflict guidance, baseline metadata, CI trend)
- ✅ Batch-01 and Batch-02 configurations created
- ✅ Dry-run analysis complete (50 candidates, ~66% already migrated)
- ✅ CI trend workflow added (.github/workflows/produce-trend.yml)
- ✅ Baseline metadata system implemented
- ✅ Legacy import baseline: 99 occurrences documented

**Key Finding**:
Many files already use correct `src.*` imports. Actual refactor need is smaller than initial scan suggests.

---

## Immediate Next Steps (Within Current PR)

### Step 1: Run Full Validation Suite
Execute and document current state:

```bash
# 1. Shadowing verification
python scripts/remediation/verify_conflicts.py --expect-site-packages \
  2>&1 | tee logs/verify_conflicts_v1.2.7.log

# 2. Determinism check (2 runs)
python scripts/space_traversal/verify_determinism.py --runs 2 \
  2>&1 | tee logs/determinism_v1.2.7.log

# 3. Validation tests
pytest -q tests/validation/ 2>&1 | tee logs/pytest_validation_v1.2.7.txt

# 4. Legacy usage (current state)
python scripts/remediation/analyze_legacy_usage.py
cp reports/legacy_import_usage.csv reports/legacy_import_usage_v1.2.7.csv
```

### Step 2: Create Status Report
Document in `docs/validation/v1.2.7_Status_Report.md`:
- Validation results (all suites)
- Legacy import analysis (which files need updating)
- CI infrastructure status
- Recommendations for targeted refactoring

### Step 3: Generate Next Prompt
Create `.github/copilot_agent_task_prompt.next.md` (v1.2.8) with:
- Specific files to refactor (top 10-15 priority)
- Monitoring dashboard planning
- Production hardening checklist

---

## Acceptance Criteria (Production Ready)

ALL must be true:
- [ ] Determinism: Two runs yield identical normalized outputs
- [ ] Shadowing: verify_conflicts PASS (yaml & hydra to site-packages)
- [ ] Legacy imports: ≥50% reduction from baseline (99 → ≤50)
- [ ] Tests: Validation suite PASS or SKIP-safe
- [ ] CI: Regression diff + quality gates operational
- [ ] Baseline: metadata.json present, rotation policy documented
- [ ] Documentation: Runbook + Usage Guide complete with examples
- [ ] Monitoring: capability_trends.jsonl infrastructure ready
- [ ] Security: No critical issues introduced
- [ ] Rollback: Tested procedure for each batch

---

## Execution Plan (Collaborative Model)

**Copilot responsibilities**:
1. Execute validations and generate reports
2. Create documentation and status summaries
3. Generate next-iteration prompts
4. Prepare refactor proposals (dry-runs)
5. Update PR progress via `report_progress`

**Human responsibilities**:
1. Review validation results
2. Approve refactor applications
3. Open new PRs when requested
4. Merge completed work
5. Coordinate branch management

---

## Useful Commands Reference

```bash
# Validation sequence
python scripts/remediation/verify_conflicts.py --expect-site-packages
python scripts/space_traversal/verify_determinism.py --runs 2
pytest -q tests/validation/
python scripts/remediation/analyze_legacy_usage.py

# Audit pipeline
python scripts/space_traversal/audit_runner.py run
python scripts/space_traversal/audit_runner.py diff \
  --old audit_artifacts/baselines/capabilities_scored.json \
  --new audit_artifacts/capabilities_scored.json

# Refactor tooling (dry-run only within constraints)
python scripts/remediation/refactor_imports.py \
  --mapping mappings/batch1_mappings.json --dry-run --limit 200

# Baseline management (manual trigger)
bash scripts/ci/establish_baseline.sh --force
```

---

## Begin Execution (Current Task)

Proceed with Step 1: Run full validation suite and create status report.

This establishes the foundation for targeted refactoring in subsequent iterations.

---

**Status**: Autopilot framework established. Executing validation and documentation phase within operational constraints. Human coordination required for PR workflow automation.
