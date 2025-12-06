# Sprint Execution Plan - GitHub Copilot Prompts

> **Generated:** 2025-12-06  
> **Purpose:** Explicit, tailored prompts for GitHub Copilot to complete all required and recommended aspects from the comprehensive codebase audit

## Overview

This directory contains explicit, actionable prompts for GitHub Copilot to execute all tasks identified in the comprehensive exhaustive codebase audit. Each prompt is designed to be:

- **Self-contained**: Complete context and requirements included
- **Explicit**: Clear acceptance criteria and validation steps
- **Testable**: Concrete verification commands provided
- **Incremental**: Can be executed independently or sequentially

## Audit Context

**Source Audit:**
- Files Analyzed: 7,152 (2,386 Python, 1,480 Markdown, 304 YAML)
- Capability Scores: 0.61-0.84 (average 0.76)
- Maturity Level: 2-3 (Managed to Defined)
- Target: Level 4 (Optimized - fully autonomous)

**Critical Gaps Identified:**
- Autonomy: 38% (need +62%)
- Reproducibility: 22% (need +78%)
- Security Coverage: ~60% (need +40%)
- TODOs/Stubs: 298 catalogued

## Execution Phases

### Phase 1: Foundation (Weeks 1-4)
**Focus:** Security, Monitoring, Basic Autonomy

- [T1: Coverage Gate Enforcement](./phase1_t1_coverage_gate.md) - P0
- [T5: Prompt Sanitization Default](./phase1_t5_prompt_sanitize.md) - P0
- [T9: Security Scans in CI](./phase1_t9_security_scans.md) - P0

**Target:** Security score 0.75+, automated scanning operational

### Phase 2: Reproducibility (Weeks 5-8)
**Focus:** Determinism, Testing, Supply Chain

- [T4: Strict Resume RNG](./phase2_t4_strict_resume.md) - P1
- [T6: Dataset Hash Manifest](./phase2_t6_dataset_hash.md) - P1

**Target:** Reproducibility 50%+, full determinism validated

### Phase 3: Autonomy (Weeks 9-12)
**Focus:** Drift Detection, Self-Healing

- [T2: W&B Offline Default](./phase3_t2_wandb_offline.md) - P1
- [T3: EarlyStopping Integration](./phase3_t3_earlystopping.md) - P1
- [T7: Health/Readiness Probes](./phase3_t7_health_probes.md) - P1

**Target:** Autonomy 60%+, health checks operational

### Phase 4: Excellence (Weeks 13-16)
**Focus:** Advanced Features, Optimization

- [T8: Prometheus Metrics](./phase4_t8_prometheus.md) - P2
- [T10: SBOM Generation](./phase4_t10_sbom.md) - P2

**Target:** Level 4 maturity, 90%+ scores across all capabilities

## Prompt Usage

### For Individual Tasks

```bash
# Copy the prompt content from the specific task file
# Example: T1 Coverage Gate
cat .github/prompts/sprint_execution_plan/phase1_t1_coverage_gate.md

# Paste into GitHub Copilot Chat or commit message
# Follow the validation steps in the prompt
```

### For Phased Execution

```bash
# Execute all Phase 1 tasks sequentially
for task in phase1_*.md; do
  echo "=== Executing: $task ==="
  # Process with GitHub Copilot
done
```

### For Automated Execution

```bash
# Use the master execution script
# See: master_execution_sequence.md
```

## Validation Framework

Each prompt includes:

1. **Pre-execution checklist** - Dependencies and prerequisites
2. **Implementation steps** - Explicit code changes required
3. **Validation commands** - Concrete tests to verify success
4. **Acceptance criteria** - Clear definition of done
5. **Rollback plan** - Recovery steps if issues arise

## Supporting Artifacts

All prompts reference the following audit artifacts:

- `audit_artifacts/capabilities_scored.json` - Component scores
- `audit_artifacts/gaps.json` - Low maturity segments
- `reports/_codex_task_sequences-20251206.md` - Task definitions
- `workbench/exhaustive_audit/gap_backlog_prioritized.md` - Prioritized gaps
- `workbench/exhaustive_audit/remediation_diffs.md` - Code fix examples

## Priority Matrix

| Task | Priority | Effort | Impact | Phase | Dependencies |
|------|----------|--------|--------|-------|--------------|
| T1   | P0       | Medium | High   | 1     | None         |
| T5   | P0       | Medium | High   | 1     | None         |
| T9   | P0       | Medium | High   | 1     | None         |
| T4   | P1       | Small  | High   | 2     | T1           |
| T6   | P1       | Medium | High   | 2     | T1           |
| T2   | P1       | Small  | Medium | 3     | T1           |
| T3   | P1       | Small  | Medium | 3     | T1, T2       |
| T7   | P1       | Medium | High   | 3     | T9           |
| T8   | P2       | Medium | Medium | 4     | T2, T7       |
| T10  | P2       | Medium | Medium | 4     | T9           |

## Effort Estimates

- **Small (S):** 1-2 days (8-16 hours)
- **Medium (M):** 3-5 days (24-40 hours)
- **Large (L):** 1-2 weeks (40-80 hours)

**Total Timeline:** 16 weeks  
**Total Effort:** 140-260 engineering days  
**Recommended Team:** 2-3 engineers

## Success Metrics

Track progress using:

```bash
# Check capability scores
python scripts/space_traversal/audit_runner.py run

# Compare to baseline
python scripts/space_traversal/audit_runner.py diff \
  --old audit_run_manifest.json \
  --new audit_run_manifest_new.json

# Verify specific capability
python scripts/space_traversal/audit_runner.py explain safety-security
```

## Contact & Support

For questions or issues:

1. Review audit artifacts in `audit_artifacts/`
2. Check detailed gaps in `workbench/exhaustive_audit/`
3. Consult operations runbook: `reports/_operations_runbook-20251206.md`
4. Reference capability explanations: `reports/_capability_explain_set-20251206.md`

## Related Documentation

- [Audit Complete Summary](../../../AUDIT_COMPLETE.md)
- [Executive Status Update](../../../reports/_codex_status_update-(2025-12-06).md)
- [Gap Backlog Prioritized](../../../workbench/exhaustive_audit/gap_backlog_prioritized.md)
- [Remediation Diffs](../../../workbench/exhaustive_audit/remediation_diffs.md)
- [Autonomy Checklist](../../../reports/_autonomy_checklist-20251206.md)

---

**Status:** Ready for execution  
**Version:** 1.0.0  
**Last Updated:** 2025-12-06  
**Next Review:** After Phase 1 completion
