# 🔧 Hardened CI Automation System — Implementation Guide

**Last Updated:** 2026-06-23T00:11:55Z

## Overview

This document describes the hardened CI automation system for detecting, diagnosing, and healing recurring CI failures in the Aries-Serpent/_codex_ repository.

The system comprises three interconnected components:

1. **CI Auto-Fix Orchestrator** — Pattern detection engine with structured reporting
2. **CI Pattern Healer** — Automated workflow for coordinated healing
3. **Enhanced CI Triage** — Improved diagnostics and Copilot agent prompts

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│         GitHub Actions Workflows (Triggers)                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  • secrets-baseline-enforcer.yml    (on: push/PR)          │
│  • workflow-link-validation.yml      (on: push/PR/sched)   │
│  • batch-ci-triage.yml               (on: schedule 1h)     │
│  • ci-pattern-healer.yml             (on: workflow_run/sch)│
│                                                              │
└───────────────┬───────────────────────────────────────────┘
                │
                ▼
    ┌──────────────────────────────────┐
    │  CI Auto-Fix Orchestrator        │
    │  .github/scripts/                │
    │  ci-autofix-orchestrator.py      │
    ├──────────────────────────────────┤
    │ • Pattern detection (9 patterns)  │
    │ • Issue classification           │
    │ • Fix coordination               │
    │ • JSON diagnostics output        │
    └───────────┬──────────────────────┘
                │
                ▼
    ┌──────────────────────────────────┐
    │  Healing Pipeline                │
    ├──────────────────────────────────┤
    │ • Detect-secrets pragmas         │
    │ • PyYAML dependency injection    │
    │ • YAML indentation fixes         │
    │ • Coverage threshold standardize │
    │ • Unused import cleanup (ruff)   │
    └──────────────────────────────────┘
```

---

## Components

### 1. CI Auto-Fix Orchestrator

**File:** `.github/scripts/ci-autofix-orchestrator.py`

Central orchestrator for automated CI failure healing. Detects 9 distinct failure patterns and coordinates fixes.

#### Supported Patterns

| Pattern | Name | Severity | Auto-Fixable | Workflow |
|---------|------|----------|--------------|----------|
| 1 | Unused Imports | error | ✅ Yes | ruff F401 |
| 2 | Unused Variables | warning | ❌ No (detect-only) | Manual |
| 3 | YAML Indentation | error | ❌ No (detect-only) | Manual |
| 4 | Coverage Threshold | warning | ✅ Yes | Standardize to 70% |
| 5 | Tokenizer Fallback | warning | ❌ No (detect-only) | Context-specific |
| 6 | Test Assertions | warning | ❌ No (detect-only) | Context-specific |
| 7 | Redundant Imports | warning | ❌ No (detect-only) | Manual review |
| 8 | CodeQL Suppression | error | ✅ Yes | lgtm → codeql |
| 9 | PyYAML Dependency | error | ✅ Yes | pip install pyyaml |

#### Usage

```bash
# Check for issues (no changes)
python .github/scripts/ci-autofix-orchestrator.py --check-only

# Generate JSON diagnostic report
python .github/scripts/ci-autofix-orchestrator.py --check-only --json-output .codex/diagnostic.json

# Apply all auto-fixable issues
python .github/scripts/ci-autofix-orchestrator.py

# Dry run (show what would change)
python .github/scripts/ci-autofix-orchestrator.py --dry-run
```

#### JSON Output Format

```json
{
  "timestamp": "2026-06-23T00:11:55.900Z",
  "status": "failed",
  "total_issues": 10,
  "auto_fixable": 5,
  "manual_review": 5,
  "issues": [
    {
      "pattern": 1,
      "pattern_name": "Unused Imports",
      "issue_type": "unused_imports",
      "severity": "error",
      "file": "tests/test_example.py",
      "line": 10,
      "message": "Import 'Mock' is unused",
      "auto_fix_available": true,
      "suggested_fix": "ruff check --fix . --select=F401"
    }
  ],
  "fixes_applied": 3,
  "next_steps": [
    "Run: ruff check --fix . --select=F401",
    "Review coverage thresholds in workflows"
  ]
}
```

### 2. CI Pattern Healer Workflow

**File:** `.github/workflows/ci-pattern-healer.yml`

Automated workflow for coordinated healing of CI failure patterns.

#### Triggers

- **workflow_run:** On failure of major CI workflows
- **schedule:** Twice daily (6 AM, 6 PM UTC)
- **workflow_dispatch:** Manual trigger with options

#### Jobs

1. **detect-failures** — Runs orchestrator in check-only mode
2. **heal-patterns** — Applies fixes if issues detected
3. **post-heal-validation** — Validates results and generates summary

#### Features

- ✅ Automatic pattern detection
- ✅ Coordinated fix application
- ✅ JSON diagnostic artifacts
- ✅ Git commit with [skip ci] tag
- ✅ Dry-run mode for testing

### 3. Enhanced CI Triage Workflow

**File:** `.github/workflows/batch-ci-triage.yml`

Improved triage with better Copilot agent prompts and structured output.

#### Enhancements

**Improved Copilot Prompt:**
```
@copilot Fix the failing CI workflow "Workflow Name" (run #12345).

**Workflow Context:**
- Workflow file: .github/workflows/...
- Branch: main
- Commit: abc123def456
- Run URL: https://...
- Associated PR: #5000

**Failure Details:**
- Failed jobs: job-1, job-2
- Failing steps: step 1; step 2; step 3

**Analysis Instructions:**
1. Examine the workflow file and job logs
2. Identify root cause (dependency, environment, configuration)
3. Check if this pattern matches known CI failure patterns (see #5041)
4. Apply fix and validate with local test if possible
5. If auto-fixable: commit with [skip ci] and reference this issue
6. If manual: create actionable remediation steps

**Note:** This failure may be part of a recurring pattern. Check the CI Failure Triage Report (#5041) for similar issues.
```

**Structured JSON Report:**
- Failures grouped by pattern
- Auto-fixable vs. manual review counts
- Recommendations (immediate, short-term, long-term)
- Artifact storage for agent access

#### Output Artifacts

- `ci-triage-report.md` — Markdown report with Copilot prompts
- `ci-triage-report.json` — Structured data for agent consumption

---

## Integration Points

### Secrets Baseline Enforcer

**File:** `.github/workflows/secrets-baseline-enforcer.yml`

Enhanced auto-fix pattern to include documentation files:

```bash
# Auto-fixes pragmas for:
# • tests/** and src/**/tests/**
# • examples/** and fixtures/**
# • .codex/** markdown docs
# • docs/accountability/** (auto-generated reports)
# • docs/reference/** (reference documentation)
```

### Workflow Link Validation

**File:** `.github/workflows/workflow-link-validation.yml`

Fixed PyYAML dependency issue:

```yaml
steps:
  - name: Set up Python
    uses: actions/setup-python@v6
  
  - name: Install PyYAML (required by setup-python-cached)
    run: pip install pyyaml --quiet
  
  - name: Set up cached Python environment
    uses: ./.github/actions/setup-python-cached
```

---

## Failure Patterns Reference

### Pattern 1: Unused Imports (ruff F401)

**Root Cause:** Unused import statement in Python code

**Detection:** `ruff check . --select=F401`

**Fix:** `ruff check --fix . --select=F401`

**Example:**
```python
import os  # ← unused
from typing import Dict

x = Dict[str, str]
```

### Pattern 4: Coverage Threshold

**Root Cause:** Inconsistent coverage thresholds across workflows

**Detection:** grep for `--cov-fail-under`

**Fix:** Standardize all to 70%

### Pattern 8: CodeQL Suppressions

**Root Cause:** Using deprecated LGTM format instead of CodeQL format

**Detection:** grep for `# lgtm`

**Fix:** Replace with `# codeql[py/...]`

**Example:**
```python
# ❌ Old format
result = eval(user_input)  # lgtm[py/eval-injection]

# ✅ New format
result = eval(user_input)  # codeql[py/unsafe-code]
```

### Pattern 9: PyYAML Dependency

**Root Cause:** Using `setup-python-cached` action without pre-installing PyYAML

**Detection:** Check if PyYAML is installed before action usage

**Fix:** Add `pip install pyyaml --quiet` before action

---

## Operationalization

### Daily Operations

1. **Automated Detection:** `ci-pattern-healer` runs 2x daily
2. **Auto-Healing:** Patterns 1, 4, 8, 9 are auto-fixed
3. **CI Triage:** Updated hourly with improved diagnostics
4. **Artifact Storage:** Reports available for manual review

### When Failures Occur

1. Workflow fails → `batch-ci-triage` captures details
2. CI triage issue updated with structured Copilot prompt
3. `ci-pattern-healer` detects if issue matches known pattern
4. Auto-fix applied if eligible, or manual review recommended
5. JSON diagnostic report available for agent consumption

### Monitoring

Check `.codex/ci-patterns-*.json` artifacts in workflow runs:

```bash
# List latest diagnostic reports
gh run list --workflow ci-pattern-healer.yml --limit 10 --json artifacts

# Download latest
gh run download <RUN_ID> -n ci-patterns-detected-<RUN_ID>
jq '.' .codex/ci-patterns-detected.json
```

---

## Known Limitations

| Pattern | Why Not Auto-Fixed | Mitigation |
|---------|-------------------|-----------|
| 2 | Context-dependent | Manual analysis required |
| 3 | Complex grammar | Use yamllint + manual fix |
| 5, 6, 7 | Semantic analysis needed | Expert review required |

---

## Escalation Path

### For Recurring Failures

1. Check if pattern matches one of 9 known patterns
2. If auto-fixable: Trigger `ci-pattern-healer` manually
3. If not: Create issue referencing #5041 (CI Failure Triage Report)
4. @mention `@copilot` with structured context

### For New Patterns

1. Document in `.codex/new-ci-patterns.md`
2. Add detection logic to orchestrator (Pattern 10+)
3. Implement fix logic if auto-fixable
4. Update this documentation

---

## Performance Notes

- **Detection:** ~30 seconds (orchestrator)
- **Healing:** ~5-10 minutes (orchestrator + git operations)
- **API Calls:** ~50 per triage run (rate-limited)
- **Storage:** ~1MB per diagnostic artifact (30-day retention)

---

## Related Issues & Documents

- **#5041** — CI Failure Triage Report (pattern catalog)
- **.codex/CODEBASE_AGENCY_POLICY.md** — Automation policy
- **.codex/PHASE_9_COORDINATION_DASHBOARD.md** — Phase 9 roadmap
- **docs/reference/GITHUB_VARIABLES_SECRETS_REFERENCE.md** — API tokens

---

## Future Enhancements

- [ ] Pattern 2-3 auto-fix (unused variables, YAML indentation)
- [ ] Machine learning-based pattern classifier
- [ ] Cross-repository pattern sharing
- [ ] Custom agent delegation to specialized healers
- [ ] Pattern confidence scoring

---

**Maintained by:** CI Automation Team
**Last Review:** 2026-06-23T00:11:55Z
