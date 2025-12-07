# 🚀 MASTER KICKOFF PROMPT - Start Complete Transformation

> **THIS IS THE ENTRY POINT FOR ENTIRE 16-WEEK AUTONOMOUS TRANSFORMATION**
>
> Copy this entire prompt into GitHub Copilot Chat/Workspace to begin execution.

---

## 🎯 COPILOT: BEGIN AUTONOMOUS EXECUTION NOW

@workspace **EXECUTE COMPLETE MLOPS TRANSFORMATION**

You are about to autonomously transform the `_codex_` repository from **Level 2-3 maturity** to **Level 4 production-grade autonomy** over 16 weeks.

---

## Mission Parameters

**Repository:** Aries-Serpent/_codex_
**Current Directory:** `/home/runner/work/_codex_/_codex_/`
**Timeline:** 16 weeks (4 phases, 8 sprints, 45 tasks)
**Scope:** ALL audit findings
**Approach:** Fully autonomous with self-expansion, self-healing, self-validation

---

## What You Will Execute

### Comprehensive Coverage
- ✅ **45 prioritized gaps** from comprehensive audit
- ✅ **298 stubs/TODOs/FIXMEs** across codebase
- ✅ **18 capability domains** (checkpointing → security)
- ✅ **10 priority tasks** (T1-T10) with detailed implementations
- ✅ **4 phases** with parallel track coordination
- ✅ **6 execution tracks** running concurrently

### Target Improvements
- **Capability Scores:** All 18 domains from 0.61-0.84 → ≥0.90
- **Autonomy:** 38% → 95% (+57%)
- **Reproducibility:** 22% → 98% (+76%)
- **Security:** 60% → 98% (+38%)
- **Technical Debt:** 298 stubs → 0 (100% cleanup)
- **Test Coverage:** 0% → ≥70%
- **Maturity Level:** Level 2-3 → Level 4 (Production)

---

## Autonomous Capabilities You Have

**Self-Expansion:**
- Auto-detect missing prerequisites
- Generate sub-prompts on-the-fly
- Execute dependencies before main tasks
- Example: T1 needs pytest.ini → auto-generate config creation prompt → execute → continue

**Self-Healing:**
- 5-attempt error recovery per task
- Pattern-based diagnosis (ImportError, syntax, config issues)
- Automated fix strategies
- Example: pytest-cov missing → pip install pytest-cov → retry

**Self-Validation:**
- Continuous testing after each step
- Acceptance criteria verification
- Automated validation commands
- Example: After T1 → run `pytest --cov` → verify ≥70%

**Self-Adaptation:**
- Context-aware implementation
- Detects existing patterns (pyproject.toml vs pytest.ini)
- Extends rather than replaces
- Example: If pyproject.toml exists → add [tool.pytest] section instead of creating pytest.ini

**Human Escalation:**
- Only for truly blocking issues after 5 failed attempts
- Provide detailed diagnosis, attempted fixes, recommended action
- Continue with other tasks while blocked item awaits human review

---

## Execution Protocol

### Phase 1: Foundation (Weeks 1-4)

**Sprint 1 (Week 1-2):**
```
1. READ: .github/prompts/sprint_execution_plan/phase_1_foundation/_PHASE_OVERVIEW.md
2. EXECUTE: T1 (Coverage Gate) - CRITICAL PATH, NO DEPENDENCIES
   - File: phase_1_foundation/T1_coverage_gate_enforcement.md
   - Expected: 3-5 days, coverage ≥70% enforced
3. PARALLEL EXECUTE:
   - T5 (Prompt Sanitization)
     File: phase_1_foundation/T5_prompt_sanitization_default.md
     Expected: 1-2 days, inference endpoints secure
4. VALIDATE Sprint 1 Checkpoint:
   - pytest --cov=src --cov-fail-under=70
   - python cli/inference.py --prompt "test <script>alert()</script>"
   - Verify coverage ≥70%, prompt sanitization active
```

**Sprint 2 (Week 3-4):**
```
5. EXECUTE after T1 complete:
   - T9 (Security Scans in CI)
     File: phase_1_foundation/T7_T10_and_stub_cleanup.md → T9 section
     Expected: 2 days, bandit/pip-audit/detect-secrets in CI
6. PARALLEL EXECUTE:
   - T7 (Health Probes)
     File: phase_1_foundation/T7_T10_and_stub_cleanup.md → T7 section
     Expected: 2 days, /health and /ready endpoints
   - T8 (Prometheus Metrics)
     File: phase_1_foundation/T7_T10_and_stub_cleanup.md → T8 section
     Expected: 2 days, /metrics endpoint operational
7. ONGOING: P0 Stub Cleanup (15 items)
   - File: phase_1_foundation/T7_T10_and_stub_cleanup.md → Stub cleanup
   - Target: 15/15 P0 blocking stubs resolved
8. VALIDATE Sprint 2 Checkpoint:
   - curl http://localhost:8000/health
   - curl http://localhost:8000/metrics
   - gh workflow view security (if CI available)
   - Verify Phase 1 complete, ready for Phase 2
```

### Phase 2: Reproducibility (Weeks 5-8)

**Sprint 3 (Week 5-6):**
```
9. READ: .github/prompts/sprint_execution_plan/phase_2_reproducibility/_PHASE_OVERVIEW.md
10. EXECUTE:
    - T4 (Strict Resume RNG)
      File: phase_2_reproducibility/T4_strict_resume_rng.md
      Expected: 1-2 days, RNG sidecar enforced
11. EXECUTE:
    - Checkpoint Integrity (from T4 or separate)
      Add SHA256 validation, corruption detection
      Expected: 1 day
12. EXECUTE:
    - Deterministic Algorithms
      Enforce torch.use_deterministic_algorithms()
      Expected: 1 day
13. VALIDATE Sprint 3 Checkpoint:
    - pytest --strict-resume tests/test_rng_reproducibility.py
    - Verify bit-exact reproducibility
```

**Sprint 4 (Week 7-8):**
```
14. EXECUTE:
    - T6 (Dataset Hash Manifest)
      File: phase_2_reproducibility/T6_dataset_hash_manifest.md
      Expected: 2-3 days, dataset versioning operational
15. EXECUTE:
    - T10 (SBOM Generation)
      File: phase_1_foundation/T7_T10_and_stub_cleanup.md → T10 section
      Expected: 1 day, SBOM in releases
16. EXECUTE:
    - Config Drift Detection
      Hash configs, validate on resume
      Expected: 1 day
17. VALIDATE Sprint 4 Checkpoint:
    - python cli/train_codex.py --verify-dataset-manifest
    - ls dist/sbom.json
    - Verify Phase 2 complete, reproducibility ≥60%
```

### Phase 3: Autonomy (Weeks 9-12)

**Sprint 5 (Week 9-10):**
```
18. READ: .github/prompts/sprint_execution_plan/phase_3_autonomy/_PHASE_OVERVIEW.md
19. EXECUTE:
    - T2 (W&B Offline Default)
      File: phase_3_autonomy/T2_wandb_offline_default.md
      Expected: 0.5-1 day, WANDB_MODE=offline by default
20. EXECUTE:
    - T3 (EarlyStopping Integration)
      File: phase_3_autonomy/T3_earlystopping_integration.md
      Expected: 1-2 days, callback auto-injected
21. EXECUTE:
    - Drift Detection System (config/data/model)
      Expected: 3 days, 3 drift types operational
22. VALIDATE Sprint 5 Checkpoint:
    - python test_drift_detection.py
    - Verify drift alerts functional
```

**Sprint 6 (Week 11-12):**
```
23. EXECUTE:
    - Auto-Remediation Framework
      OOM → batch size reduction, checkpoint rollback on regression
      Expected: 4 days
24. EXECUTE:
    - Stub Cleanup Campaign
      File: STUB_RESOLUTION_AUTOMATION.md
      Target: 298 → <50 stubs remaining
      Expected: Ongoing, major push this sprint
25. VALIDATE Sprint 6 Checkpoint:
    - python train.py --enable-auto-remediation --inject-oom
    - grep -r "NotImplementedError\|TODO" src/ | wc -l
    - Verify <50 stubs, auto-remediation working
```

### Phase 4: Excellence (Weeks 13-16)

**Sprint 7 (Week 13-14):**
```
26. READ: .github/prompts/sprint_execution_plan/phase_4_excellence/_PHASE_OVERVIEW.md
27. EXECUTE:
    - Continuous Improvement Loop
      Ingest gap registry, auto-prioritize, auto-open tasks
      Expected: 3 days
28. EXECUTE:
    - Plugin Sandboxing
      Contract tests, sandboxed execution, auto-disable
      Expected: 2 days
29. EXECUTE:
    - Documentation Enhancement
      API docs (Sphinx/MkDocs), notebook validation, runbooks
      Expected: 4 days
30. VALIDATE Sprint 7 Checkpoint:
    - make docs
    - pytest --doctest-modules
    - Verify comprehensive documentation
```

**Sprint 8 (Week 15-16):**
```
31. EXECUTE:
    - Final Stub Cleanup
      Target: All remaining stubs → 0
      Expected: 2 days
32. EXECUTE:
    - Capability Batch Improvements
      File: CAPABILITY_BATCH_PROMPTS.md
      All 18 domains → ≥0.90
      Expected: 3 days
33. EXECUTE:
    - Final Audit & Validation
      Re-run audit, compare to baseline, verify all targets
      Expected: 2 days
34. VALIDATE Final Completion:
    - python scripts/space_traversal/audit_runner.py run
    - python scripts/compare_audits.py baseline.json current.json
    - nox -s final_validation
    - Verify ALL targets met, Level 4 achieved
```

---

## Parallel Execution Tracks

Execute these tracks concurrently when tasks don't have dependencies:

**Track A: Testing & Quality**
- T1 → Coverage infrastructure → Deterministic fixtures → Mutation testing

**Track B: Security & Compliance**
- T5 → T9 → T10 → AuthN/AuthZ → Security audit log

**Track C: Reproducibility**
- T4 → T6 → Checkpoint integrity → Deterministic algorithms → Config drift

**Track D: Observability & Ops**
- T7 → T8 → Alerting system → Dashboards → Chaos testing

**Track E: Autonomy & Self-Healing**
- T2 → T3 → Drift detection → Auto-remediation → Continuous improvement

**Track F: Technical Debt**
- P0 stubs (15) → P1 stubs (45) → P2 stubs (128) → P3 stubs (110) → 0

---

## Self-Healing Examples

**Example 1: Missing Dependency**
```
Task: T1 Coverage Gate
Step: Configure pytest with coverage
Error: ModuleNotFoundError: No module named 'pytest_cov'

Self-Diagnosis:
- Pattern: ImportError for pytest_cov
- Root Cause: pytest-cov not installed
- Confidence: 95%

Auto-Fix:
1. Run: pip install pytest-cov
2. Verify: python -c "import pytest_cov"
3. Retry: Configure pytest with coverage
4. Success: Coverage gate configured

Result: Task completed without human intervention
```

**Example 2: Config File Choice**
```
Task: T1 Coverage Gate
Step: Add pytest configuration

Context Detection:
- pyproject.toml exists: YES
- pytest.ini exists: NO

Self-Adaptation:
- Strategy: Use pyproject.toml (existing file)
- Add section: [tool.pytest.ini_options]
- Extend rather than create new file

Implementation:
- Edit pyproject.toml
- Add pytest config to existing structure
- Validate: pytest --version shows config loaded

Result: Context-aware implementation, no conflicts
```

**Example 3: Test Failure Recovery**
```
Task: T4 Strict Resume RNG
Step: Test RNG determinism
Error: AssertionError: RNG not deterministic

Self-Diagnosis:
- Attempt 1: Check torch.manual_seed called
- Attempt 2: Check numpy.random.seed called  
- Attempt 3: Check CUDA seeding
- Root Cause: torch.backends.cudnn.deterministic not set
- Confidence: 85%

Auto-Fix:
1. Add: torch.backends.cudnn.deterministic = True
2. Add: torch.backends.cudnn.benchmark = False
3. Retry: Test RNG determinism
4. Success: Tests pass

Result: Fixed after 3 diagnostic iterations
```

---

## Progress Reporting

**Update progress weekly:**

```yaml
week_1:
  phase: 1
  sprint: 1
  completed: [T1]
  in_progress: [T5]
  blocked: []
  stubs_resolved: 5/298
  capability_scores:
    ci_test: 0.35 → 0.60 (+0.25)

week_2:
  phase: 1
  sprint: 1
  completed: [T1, T5]
  in_progress: [T7, T8]
  blocked: []
  stubs_resolved: 10/298

# ... continue weekly updates
```

**Report blocking issues immediately:**
```
⚠️ BLOCKING ISSUE

Task: T4 Strict Resume RNG
Issue: RNG sidecar implementation requires torch>=1.8, but torch==1.7.1 installed
Attempts: 5 (all failed)
Diagnosis: Version incompatibility
Recommended Action: Upgrade torch to ≥1.8 OR implement fallback for older versions
Escalation: HUMAN_REVIEW_NEEDED

Other tasks continuing: T5, T7, T8 (not blocked)
```

---

## Validation Checkpoints

**After each sprint (every 2 weeks):**
```bash
# Run validation suite
pytest --cov=src --cov-fail-under=70
nox -s tests
python scripts/space_traversal/audit_runner.py run

# Compare progress
python scripts/compare_audits.py audit_baseline.json audit_current.json

# Generate report
python generate_progress_report.py --sprint N
```

**Final validation (Week 16):**
```bash
# Complete audit
python scripts/space_traversal/audit_runner.py run

# Verify all targets
python verify_targets.py --baseline audit_baseline.json --current audit_current.json

# Expected output:
# ✅ All capability scores ≥0.90
# ✅ Autonomy ≥95%
# ✅ Reproducibility ≥98%
# ✅ Security ≥98%
# ✅ Stubs: 0/298 remaining
# ✅ Level 4 maturity achieved

# Final validation
nox -s final_validation
make docs
pytest --doctest-modules

# SUCCESS: Transformation complete
```

---

## Master Orchestration Reference

**Primary Orchestrator:**
```
File: .github/prompts/sprint_execution_plan/MASTER_ORCHESTRATOR.md
Purpose: Complete 16-week autonomous execution protocol
Contains: Dependency graphs, parallel coordination, self-healing protocol
```

**Phase Overviews:**
```
phase_1_foundation/_PHASE_OVERVIEW.md (Weeks 1-4)
phase_2_reproducibility/_PHASE_OVERVIEW.md (Weeks 5-8)
phase_3_autonomy/_PHASE_OVERVIEW.md (Weeks 9-12)
phase_4_excellence/_PHASE_OVERVIEW.md (Weeks 13-16)
```

**Task Prompts:**
```
T1: phase_1_foundation/T1_coverage_gate_enforcement.md
T2: phase_3_autonomy/T2_wandb_offline_default.md
T3: phase_3_autonomy/T3_earlystopping_integration.md
T4: phase_2_reproducibility/T4_strict_resume_rng.md
T5: phase_1_foundation/T5_prompt_sanitization_default.md
T6: phase_2_reproducibility/T6_dataset_hash_manifest.md
T7-T10: phase_1_foundation/T7_T10_and_stub_cleanup.md
```

**Batch Processing:**
```
CAPABILITY_BATCH_PROMPTS.md (All 18 domains)
STUB_RESOLUTION_AUTOMATION.md (All 298 stubs)
```

**Quick Reference:**
```
QUICK_START.md (Immediate execution guide)
TEMPLATE.md (Prompt format v2.0.0)
README.md (Framework overview)
```

---

## Success Criteria

**You will know you're done when:**

1. ✅ All 45 gaps resolved
2. ✅ All 298 stubs cleaned up
3. ✅ All 18 capability domains ≥0.90
4. ✅ Autonomy ≥95%
5. ✅ Reproducibility ≥98%
6. ✅ Security ≥98%
7. ✅ Test coverage ≥70%
8. ✅ All tests passing
9. ✅ Documentation complete
10. ✅ Final audit confirms Level 4 maturity

---

## Your Autonomous Authority

**You have full authority to:**
- Execute all 45 tasks autonomously
- Generate sub-prompts for missing prerequisites
- Install dependencies (pip, apt, npm)
- Modify any files in the repository
- Create new files and directories
- Run tests and validation
- Commit changes (via report_progress tool if available)
- Adapt implementation based on discovered context
- Retry failed steps up to 5 times with different approaches

**You must escalate only when:**
- 5 attempts failed and no auto-fix strategy available
- External resource required (API keys, credentials)
- Architectural decision needed
- Breaking change requires approval
- Completely blocked with no alternative path

---

## 🚀 BEGIN EXECUTION NOW

```
@workspace START TRANSFORMATION

Primary Orchestrator:
File: .github/prompts/sprint_execution_plan/MASTER_ORCHESTRATOR.md

Execution Mode: FULLY AUTONOMOUS
Timeline: 16 weeks
Target: Level 4 MLOps maturity
Approach: Self-expanding, self-healing, self-validating

BEGIN WITH:
1. Read MASTER_ORCHESTRATOR.md fully
2. Read Phase 1 overview
3. Start T1 (Coverage Gate) - CRITICAL PATH
4. Report progress weekly
5. Escalate only blocking issues

Authorization: FULL AUTONOMOUS EXECUTION GRANTED
Supervision: Minimal (human reviews checkpoints only)
Intervention: Only when you request it

GO! 🚀
```

---

## Quick Commands Reference

**Start Full Transformation:**
```
@workspace Execute MASTER_ORCHESTRATOR.md
```

**Start Single Phase:**
```
@workspace Execute Phase 1 Foundation
File: phase_1_foundation/_PHASE_OVERVIEW.md
```

**Start Single Task:**
```
@workspace Implement T1 Coverage Gate
File: phase_1_foundation/T1_coverage_gate_enforcement.md
```

**Check Progress:**
```
@workspace Report current progress
Check: completed tasks, blocked tasks, sprint status
```

**Resume After Interruption:**
```
@workspace Resume transformation
Load progress from MASTER_ORCHESTRATOR.md
Continue from last completed task
```

---

## 🎯 FINAL INSTRUCTION

**Copilot:** You are now authorized to execute the complete 16-week autonomous transformation of the _codex_ repository. Read MASTER_ORCHESTRATOR.md, execute all phases systematically, self-expand for prerequisites, self-heal on failures, self-validate continuously, and escalate only truly blocking issues.

**Timeline:** 16 weeks starting NOW
**Supervision:** Minimal (weekly progress reviews)
**Authority:** Full autonomous execution
**Target:** Level 4 production-grade autonomy

**BEGIN TRANSFORMATION IMMEDIATELY.** 🚀

---

*This kickoff prompt is your complete authorization and instruction set. Copy this entire prompt into GitHub Copilot Chat/Workspace to begin the transformation. All supporting prompts, automation scripts, and frameworks are in place. You have everything you need to succeed.*

**LET'S BUILD THE FUTURE OF AUTONOMOUS ML! 🤖✨**
