# Agent Brief: Stage 2 - Promotion Validation & Coverage Gate

**Target Agent:** unified-coverage-agent  
**Priority:** HIGH (gates Stage 3 promotion merge)  
**Authority:** @mbaetiong (Autonomous GO CONTINUE)  
**Timeline:** 1.5-2 hours after Stage 1 completion  
**Status:** READY FOR DISPATCH

---

## Mission

Validate coverage gate ≥70% and prepare promotion readiness report for 0D_base_ → main merge (172 commits).

---

## Conditional Execution Paths

### Path A: Collection Errors <50 (FULL MEASUREMENT)
Execute complete coverage validation:

**1. Run Full Test Collection:**
```bash
cd /home/runner/work/_codex_/_codex_
pytest --collect-only 2>&1 | tail -5
# Verify: Interrupted count < 50 or 0 (no errors)
```

**2. Execute Full Coverage Measurement:**
```bash
pytest tests/ --cov=src --cov-config=.coveragerc --cov-report=term-missing --cov-report=html
# Capture: % coverage per module
```

**3. Validate Thresholds:**
- Overall: ≥70% (required for promotion)
- TIER-1 modules (src/services, src/mcp, src/tools, src/codex_utils, src/utils, src/security): ≥60% minimum
- TIER-2 modules: ≥50% minimum

**4. Execute CodeQL Security Gate:**
- Run existing CodeQL workflow or `codeql database analyze`
- Verify: HIGH severity findings ≤1

**5. Verify All 142 Workflows Passing:**
- Check: GitHub Actions run status on 0D_base_
- Verify: All PR checks GREEN

**6. Generate Promotion Validation Report:**
Save to `.codex/PHASE_6_WAVE_1_STAGE2_VALIDATION_REPORT.md` with:
- Coverage metrics by module (table format)
- CodeQL findings summary
- Workflow status summary
- Decision: PASS (proceed to Stage 3) / FAIL (escalate)

### Path B: Collection Errors 50-100 (PARTIAL MEASUREMENT)
Run tests on subset of cleanly-collecting modules (~80-100 test files):

**1. Identify Clean Test Modules:**
```bash
pytest tests/ --collect-only 2>&1 | grep -v ERROR | grep "collected" | head -1
# Run only modules with <5 errors
```

**2. Measure Coverage on Clean Subset:**
```bash
pytest tests/unit tests/integration tests/security tests/monitoring \
  --cov=src --cov-config=.coveragerc --cov-report=term-missing
```

**3. Report Interim Validation:**
- Document which test modules cannot collect
- Report coverage from passing subset
- Flag: "Full measurement blocked by collection errors in X test files"
- Recommendation: Proceed on partial validation OR delay promotion

**4. Escalate to @mbaetiong:**
Present interim metrics + decision options

### Path C: Collection Errors >100 (BLOCKED)
Gate remains BLOCKED:
- Report detailed error analysis (top 10 patterns)
- Estimate time to resolve
- Escalate to @mbaetiong for decision

---

## Success Criteria

- ✅ Coverage measurement completed (full or partial)
- ✅ Coverage ≥70% confirmed OR documented blocker
- ✅ CodeQL security gate passing
- ✅ All 142 workflows passing on 0D_base_
- ✅ Promotion validation report generated and committed

---

## Escalation

If coverage <70% or CodeQL alerts >1:
1. Document interim metrics in report
2. Report to @mbaetiong with:
   - Current coverage % by module
   - Identified gaps
   - Recommendation: proceed on interim / delay for full fixes
3. Await decision

---

## Output Artifacts

**Committed to Repository:**
- `.codex/PHASE_6_WAVE_1_STAGE2_VALIDATION_REPORT.md` (detailed metrics)
- Update `.codex/PHASE_6_WAVE_1_EXECUTION_TRACKING.md` (status)
- Update `docs/accountability/.codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md` (session tracking)

---

## Dependencies

- Stage 1 completion (collection errors fixed or diagnosed)
- All Phase 3-5 work already on 0D_base_
- Phase 6 Wave 1 core documentation available in `.codex/`

---

**Authority:** @mbaetiong - all steps pre-approved  
**Mode:** Autonomous GO CONTINUE - proceed at all decision points  
**Dispatch Status:** AWAITING STAGE 1 COMPLETION SIGNAL
