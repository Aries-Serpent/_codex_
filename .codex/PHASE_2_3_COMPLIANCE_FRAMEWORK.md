# Phase 2.3 Compliance Framework Design

**Version:** 1.0.0  
**Date:** 2026-06-21  
**Status:** Design Phase

---

## Executive Summary

The Phase 2.3 Compliance Framework establishes a unified, 6-requirement governance system that automatically validates PR eligibility, compliance, authorization, accountability reporting, changelog updates, and post-merge health. The framework is designed to be 100% accurate, explainable, and performant (<60 seconds per check).

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                   Unified Governance Gate                        │
│                (Master Orchestrator)                             │
│                                                                  │
│  unified_compliance_check.py                                    │
│  ├─ Run all 6 validators in parallel                            │
│  ├─ Aggregate results into compliance score                     │
│  ├─ Determine final decision (approve/warn/block)              │
│  └─ Log all decisions to audit trail                            │
└──────────────────────────────┬──────────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
   ┌────▼─────┐          ┌────▼─────┐          ┌────▼─────┐
   │ REQ-1/2/3│          │ REQ-4/5  │          │ REQ-6   │
   │Validators│          │Validators│          │Validator│
   │(Parallel)│          │(Sequential)        │(Async)  │
   └──────────┘          └──────────┘          └─────────┘
       │                      │                      │
       └──────────────────────┴──────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Result JSON       │
                    │  (pass/fail +      │
                    │   reasoning +      │
                    │   remediation)     │
                    └────────────────────┘
```

---

## Component Design

### 1. Base Validator Class

```python
class RequirementValidator:
    """Base class for all requirement validators."""

    def __init__(self, pr_number: str, repo: str = "Aries-Serpent/_codex_"):
        self.pr_number = pr_number
        self.repo = repo

    def validate(self) -> ComplianceResult:
        """Run the validation. Returns JSON-serializable result."""
        raise NotImplementedError

    @property
    def requirement_id(self) -> str:
        """REQ-1, REQ-2, etc."""
        raise NotImplementedError
```

### 2. ComplianceResult Structure

```python
@dataclass
class ComplianceResult:
    requirement_id: str        # "REQ-1", "REQ-2", etc.
    status: str               # "pass", "fail", "warn"
    score: float              # 0.0-1.0 (0=fail, 0.5=warn, 1.0=pass)
    reason: str               # Detailed explanation
    remediation: list[str]    # Actionable steps to fix
    metadata: dict            # Additional context
    elapsed_ms: float         # Performance tracking
```

### 3. Compliance Scoring Model

```
Overall Score = (REQ1 + REQ2 + REQ3 + REQ4 + REQ5 + REQ6) / 6 * 100

Status Mapping:
  90-100: APPROVE  (✅ pass)
  70-89:  WARN     (⚠️  pass with conditions)
  0-69:   BLOCK    (❌ fail, needs fix)

Per-Requirement Scoring:
  1.0 (pass)  = 100 points
  0.5 (warn)  = 50 points
  0.0 (fail)  = 0 points
```

### 4. Decision Matrix

```
REQ-1  REQ-2  REQ-3  REQ-4  REQ-5  REQ-6  |  Decision
────────────────────────────────────────────────────
  ✅     ✅     ✅     ✅     ✅     ✅    |  APPROVE
  ✅     ✅     ✅     ✅     ✅     ⚠️    |  WARN (post-merge issue)
  ✅     ✅     ✅     ✅     ⚠️     ✅    |  WARN (fix CHANGELOG)
  ✅     ✅     ✅     ⚠️     ✅     ✅    |  WARN (fix accountability)
  ✅     ✅     ⚠️     ✅     ✅     ✅    |  WARN (resolve approvals)
  ✅     ✅     ❌     ✅     ✅     ✅    |  BLOCK (authorization required)
  ✅     ❌     ✅     ✅     ✅     ✅    |  BLOCK (compliance issues)
  ✅     ❌     ❌     ❌     ❌     ❌    |  BLOCK (multiple failures)
  ❌     ✅     ✅     ✅     ✅     ✅    |  BLOCK (eligibility)
```

---

## Requirement Validators

### REQ-1: PR Eligibility Validator

**Validates:**
- Branch name pattern (feat/, fix/, docs/, test/, chore/, refactor/)
- PR title descriptive (not auto-generated)
- PR description quality (minimum 50 chars)
- Reviewer assignment

**CLI:**
```bash
python scripts/ci/validators/req1_eligibility_validator.py --pr 3575
```

**Output:**
```json
{
  "requirement_id": "REQ-1",
  "status": "pass",
  "score": 1.0,
  "reason": "PR eligibility requirements met: branch 'feat/compliance-framework', descriptive title, detailed description, reviewer assigned",
  "remediation": [],
  "metadata": {
    "branch": "feat/compliance-framework",
    "title_quality": "high",
    "description_chars": 450,
    "reviewer_assigned": true
  },
  "elapsed_ms": 120
}
```

### REQ-2: Compliance Validator

**Validates:**
- Documentation updated (CHANGELOG, docs/)
- Tests updated (tests/)
- Code quality (ruff, mypy)
- Security (CodeQL, bandit, pip-audit)
- Coverage maintained

**CLI:**
```bash
python scripts/ci/validators/req2_compliance_validator.py --pr 3575
```

### REQ-3: Merge Authorization Validator

**Validates:**
- Not a draft PR
- Blocking comments resolved
- Required approvals obtained
- Status checks passing
- No merge conflicts

**CLI:**
```bash
python scripts/ci/validators/req3_merge_validator.py --pr 3575
```

### REQ-4: Accountability Validator

**Validates:**
- AGENT_ACCOUNTABILITY_REPORT.md updated in latest commit
- Entry includes required sections
- Timestamp recorded

**CLI:**
```bash
python scripts/ci/validators/req4_accountability_validator.py --pr 3575 --sha abc1234
```

### REQ-5: CHANGELOG Validator

**Validates:**
- CHANGELOG.md updated in latest commit
- Entry in [Unreleased] section
- Follows changelog format

**CLI:**
```bash
python scripts/ci/validators/req5_changelog_validator.py --pr 3575 --sha abc1234
```

### REQ-6: Post-Merge Validator

**Validates:**
- Workflows passed after merge
- No new failures introduced
- Coverage maintained
- No regressions

**CLI:**
```bash
python scripts/ci/validators/req6_postmerge_validator.py --pr 3575 --merged-sha abc1234
```

---

## Master Orchestrator

**File:** `scripts/ci/unified_compliance_check.py`

**Functionality:**
- Run all 6 validators in parallel (REQ-1/2/3) + sequential (REQ-4/5) + async (REQ-6)
- Aggregate results
- Determine final decision
- Generate compliance report
- Update audit trail

**CLI:**
```bash
# Run all validators
python scripts/ci/unified_compliance_check.py --pr 3575

# With custom options
python scripts/ci/unified_compliance_check.py --pr 3575 --strict --json-output report.json

# Dry run
python scripts/ci/unified_compliance_check.py --pr 3575 --dry-run
```

**Output:**
```json
{
  "compliance_report": {
    "pr_number": "3575",
    "overall_score": 95.0,
    "status": "APPROVE",
    "generated_at": "2026-06-21T23:34:02Z",
    "validators": [
      { "requirement_id": "REQ-1", "status": "pass", "score": 1.0, ... },
      { "requirement_id": "REQ-2", "status": "pass", "score": 1.0, ... },
      { "requirement_id": "REQ-3", "status": "pass", "score": 1.0, ... },
      { "requirement_id": "REQ-4", "status": "pass", "score": 1.0, ... },
      { "requirement_id": "REQ-5", "status": "pass", "score": 1.0, ... },
      { "requirement_id": "REQ-6", "status": "warn", "score": 0.5, ... }
    ],
    "decision": "APPROVE",
    "next_steps": ["Monitor post-merge workflows"]
  }
}
```

---

## Compliance Dashboard

**Location:** `.codex/compliance/`

**Tracked Metrics:**
- Compliance score per PR (0-100)
- Violations by requirement
- Trends over time
- Override audit trail

**Daily Report:** `.codex/compliance/daily-report-YYYY-MM-DD.json`

**Monthly Report:** `.codex/compliance/monthly-report-YYYY-MM.json`

---

## Pre-Merge Blocker Integration

**Workflow:** `.github/workflows/unified-governance-check.yml`

**Trigger:** On PR push

**Jobs:**
1. Run unified compliance check
2. Determine status (pass/warn/block)
3. Post comment with results
4. Block merge if status is "block"
5. Allow override only by @mbaetiong with documented reason

**Override Audit Trail:** `.codex/compliance/overrides.log`

---

## Performance Targets

- REQ-1/2/3 validators: <10 seconds each (run in parallel)
- REQ-4/5 validators: <5 seconds each
- REQ-6 validator: <20 seconds (async)
- Total orchestrator time: <60 seconds

---

## Error Handling & Resilience

- All validators must handle missing data gracefully
- Network errors are retried with exponential backoff
- Timeouts result in "warn" status, not "fail"
- All errors logged with full context for debugging

---

## Testing Strategy

**Unit Tests:** `tests/unit/test_compliance_validators.py`
- 100% coverage of all validators
- Mock GitHub API responses
- Test all pass/fail/warn scenarios
- Verify JSON output format
- Performance benchmarks

**Integration Tests:** Real PR validation
- Test on recent merged PRs
- Verify no false positives
- Compare with manual review

---

## Migration Path

1. Implement all 6 validators
2. Add unified orchestrator
3. Run in "warning mode" on existing PRs (log but don't block)
4. Validate against recent PRs
5. Enable "strict mode" on new PRs
6. Gradually roll out to all PRs over 2 weeks
