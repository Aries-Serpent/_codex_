# Copilot Continuation System - Complete Guide

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Quick Start](#quick-start)
4. [Usage Patterns](#usage-patterns)
5. [Template Reference](#template-reference)
6. [Advanced Features](#advanced-features)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)
9. [Examples](#examples)
10. [FAQ](#faq)

---

## Overview

The Copilot Continuation System provides persistent, version-controlled storage for multi-phase PR implementations, ensuring zero context loss across Copilot Agent sessions.

### Key Capabilities

- **Persistent Storage**: All prompts in git (never /tmp)
- **Auto-Generation**: Prompts created automatically on PR open
- **Smart Analysis**: Intelligent task categorization based on PR content
- **Multi-Session**: Seamless continuation across agent restarts
- **Multi-Phase**: Support for complex, phased implementations
- **Self-Healing**: Copilot updates prompts with progress

### Benefits

| Benefit | Description | Impact |
|---------|-------------|--------|
| Zero Context Loss | All work persists in git | No re-work needed |
| Automated Generation | No manual prompt writing | Saves time & effort |
| Intelligent Defaults | Smart task suggestions | Better task planning |
| Version Control | Full git history | Complete traceability |
| Standardization | Consistent format | Easier collaboration |
| Self-Documentation | Prompts explain work | Better handoff |

---

## Architecture

### Directory Structure

```
.github/
├── pull_request_template.md          # Enhanced PR template (v1.4.0)
├── copilot-prompts/
│   ├── README.md                      # System documentation
│   ├── templates/                     # Reusable templates
│   │   ├── pr-continuation.md         # Standard PR follow-up
│   │   ├── multi-phase-implementation.md  # Multi-phase projects
│   │   ├── ci-fix-continuation.md     # CI/CD fixes
│   │   └── consolidation.md           # Workflow consolidation
│   ├── active/                        # Current PR prompts
│   │   └── PR-{number}-followup.md    # Active prompts
│   └── archived/                      # Completed prompts
│       └── PR-{number}-{date}.md      # Historical archive
└── workflows/
    └── pr-followup-generator.yml      # Auto-generation workflow

scripts/
└── generate_pr_followup.py            # Generator script

docs/
└── workflows/
    └── COPILOT_CONTINUATION_GUIDE.md  # This file
```

### Component Interaction

```
PR Opened/Updated
     ↓
GitHub Actions Workflow
     ↓
Analyze PR Content
     ↓
Select Template
     ↓
Generate Prompt (Python)
     ↓
Extract Git Metadata
     ↓
Populate Template
     ↓
Commit Prompt to Git
     ↓
Post PR Comment (optional)
     ↓
User Comments "@copilot continue"
     ↓
Copilot Loads Prompt
     ↓
Executes Tasks
     ↓
Updates Prompt
     ↓
Posts Status Comment
```

---

## Quick Start

### For Developers

**Opening a PR**:
1. Create branch and make changes
2. Open PR (prompt auto-generated)
3. Review PR description for continuation link
4. Check for auto-generated comment with prompt details

**Continuing Work**:
```
@copilot continue with next phase tasks
```

### For Copilot Agent

**On PR Open**:
1. Workflow auto-generates prompt
2. Prompt link appears in PR description
3. Comment may be posted with summary

**On `@copilot continue`**:
1. Load prompt from `.github/copilot-prompts/active/PR-{number}-followup.md`
2. Execute Priority 1 tasks with validation
3. Update prompt with completed tasks (✅)
4. Post status comment
5. Generate new prompt if work remains

---

## Usage Patterns

### Pattern 1: Single-Phase PR

**Scenario**: Simple bug fix or feature

```bash
# Auto-generated on PR open
# File: .github/copilot-prompts/active/PR-2650-followup.md

# Continue work
@copilot continue
```

**Workflow**:
1. PR opened → prompt generated
2. Comment `@copilot continue`
3. Copilot executes all tasks
4. Marks complete, closes PR

### Pattern 2: Multi-Phase Implementation

**Scenario**: Large feature across 3+ phases

```bash
# Generate phase 1 prompt
python3 scripts/generate_pr_followup.py 2650 \
  --template multi-phase-implementation \
  --phase 1 \
  --total-phases 5 \
  --phase-name "Infrastructure Setup"

# After phase 1 complete, generate phase 2
python3 scripts/generate_pr_followup.py 2650 \
  --phase 2 \
  --phase-name "Core Implementation"
```

**Workflow**:
1. Open PR for phase 1
2. Complete phase 1 tasks
3. Generate phase 2 prompt
4. Comment `@copilot continue with Phase 2 tasks`
5. Repeat for each phase

### Pattern 3: CI/CD Fix Sprint

**Scenario**: Multiple failing workflows

```bash
# Auto-selects ci-fix template if CI failing
# File: .github/copilot-prompts/active/PR-2651-followup.md

# Continue with fixes
@copilot continue with CI fixes
```

**Workflow**:
1. PR opened with failing CI
2. Workflow detects failures
3. Generates ci-fix prompt
4. Prompt includes failure analysis
5. Copilot executes fixes iteratively

---

## Template Reference

### Standard PR Continuation

**File**: `pr-continuation.md`

**Sections**:
- Previous Session Summary
- Next Phase Objectives (P1/P2/P3)
- Implementation Steps
- Execution Checklist
- Mandatory Self-Review (5 passes)
- Expected Outcomes
- References

**Best For**: Standard PRs, feature implementations, bug fixes

### Multi-Phase Implementation

**File**: `multi-phase-implementation.md`

**Sections**:
- Phase Overview Table
- Current Phase Details
- Phase Transition Criteria
- Phase Schedule
- Dependencies & Blockers

**Best For**: Large projects, multi-PR features, refactors

### CI Fix Continuation

**File**: `ci-fix-continuation.md`

**Sections**:
- Failing Workflows List
- Failure Analysis (per workflow)
- Fix Implementation (step-by-step)
- Validation Commands
- Monitoring Instructions

**Best For**: CI failures, test issues, linting errors

---

## Advanced Features

### Custom Template Variables

Add custom variables to generator:

```bash
python3 scripts/generate_pr_followup.py 2650 \
  --immediate "Custom task 1" \
  --criteria "Custom criterion"
```

Variables available in template as `{variable}`.

### JSON Output Mode

Get metadata as JSON:

```bash
python3 scripts/generate_pr_followup.py 2650 --json-output
```

Output:
```json
{
  "pr_number": "2650",
  "branch": "feature-branch",
  "commit_sha": "abc123",
  "output_file": ".github/copilot-prompts/active/PR-2650-followup.md",
  "template": "pr-continuation"
}
```

### Manual Workflow Trigger

Trigger prompt generation manually:

```bash
gh workflow run pr-followup-generator.yml \
  -f pr_number=2650
```

---

## Troubleshooting

### Prompt Not Generated

**Symptoms**: No prompt file after PR open

**Diagnosis**:
```bash
# Check workflow runs
gh run list --workflow=pr-followup-generator.yml --limit 5

# View latest run logs
gh run view {run_id} --log
```

**Solutions**:
- Check workflow permissions
- Verify Python script has no errors
- Manually trigger workflow
- Generate prompt locally and commit

### Copilot Not Reading Prompt

**Symptoms**: `@copilot continue` doesn't execute tasks

**Diagnosis**:
```bash
# Verify prompt exists
ls -la .github/copilot-prompts/active/

# Check prompt committed
git log -- .github/copilot-prompts/active/

# Verify link in PR description
gh pr view {PR_NUMBER} --json body
```

**Solutions**:
- Ensure file committed and pushed
- Check comment format (exact: `@copilot continue`)
- Verify prompt file readable
- Try commenting with full prompt text

### Template Variables Not Replaced

**Symptoms**: Prompt has `{variable}` placeholders

**Diagnosis**:
```bash
# Check generator output
python3 scripts/generate_pr_followup.py 2650 --json-output

# Verify template file
cat .github/copilot-prompts/templates/pr-continuation.md
```

**Solutions**:
- Ensure generator script has latest version
- Check template file for typos
- Verify environment variables set
- Regenerate prompt with explicit values

---

## Best Practices

### 1. Prompt Quality

✅ **DO**:
- Be explicit with file paths, commands, expected outputs
- Include validation steps for every task
- Document failure resolution plans
- Link to all relevant resources

❌ **DON'T**:
- Leave tasks vague or ambiguous
- Skip validation commands
- Omit failure scenarios
- Assume context is obvious

### 2. Task Prioritization

**Priority 1 (P1)**: MUST complete in next session
- Blocking issues
- CI failures
- Critical bugs
- Security vulnerabilities

**Priority 2 (P2)**: Should complete soon
- Validation tasks
- Test additions
- Documentation updates
- Code review fixes

**Priority 3 (P3)**: Nice to have
- Performance optimizations
- Future enhancements
- Technical debt reduction
- Additional test coverage

### 3. Self-Review Protocol

MANDATORY 5 passes before concluding:

1. **Code Quality**: Syntax, linting, types, readability
2. **Testing**: Coverage, edge cases, integration
3. **Documentation**: Comments, docs, changelog
4. **Security**: Secrets, validation, vulnerabilities
5. **Integration**: Compatibility, dependencies, CI

### 4. Prompt Maintenance

- Update after every session
- Mark completed tasks with ✅
- Document blockers/issues
- Add new tasks as discovered
- Commit frequently

### 5. Archival

After PR merge:
```bash
# Move to archive with date
mv .github/copilot-prompts/active/PR-2650-followup.md \
   .github/copilot-prompts/archived/PR-2650-$(date +%Y%m%d).md
```

---

## Examples

### Example 1: Simple Bug Fix

```markdown
Priority 1:
- [ ] Fix null pointer exception in auth.py line 45
- [ ] Add unit test for edge case

Priority 2:
- [ ] Verify all tests pass
- [ ] Update CHANGELOG.md
```

### Example 2: Multi-Phase Refactor

```bash
# Phase 1: Database migration
python3 scripts/generate_pr_followup.py 2701 \
  --template multi-phase-implementation \
  --phase 1 \
  --total-phases 4 \
  --phase-name "Database Schema Migration"
```

### Example 3: CI Failure Sprint

```markdown
Failed Workflows:
- test-suite.yml (3 jobs failing)
- lint.yml (2 errors)
- security-scan.yml (1 vulnerability)

Priority 1:
- [ ] Fix import order error in module_a.py
- [ ] Resolve linting issues (2 files)
- [ ] Update dependency to patch CVE-2025-1234
```

---

## FAQ

**Q: Do I need to manually create prompts?**
A: No. Prompts are auto-generated on PR open. Manual creation is optional.

**Q: Can I customize the generated prompt?**
A: Yes. Edit the file in `.github/copilot-prompts/active/` and commit.

**Q: What if I want to use a different template?**
A: Trigger workflow manually with template parameter, or generate locally.

**Q: How do I handle multi-PR dependencies?**
A: Link PRs in prompt "Depends On" section. Block dependent PRs until complete.

**Q: Can I archive old prompts?**
A: Yes. Move to `archived/` directory after PR merge.

**Q: What if Copilot doesn't follow the prompt?**
A: Verify prompt is committed, link is correct, comment format is exact.

**Q: How do I track progress across multiple sessions?**
A: Check session history in prompt file. Each session logs duration, tasks, status.

**Q: Can I use this for non-PR work?**
A: Yes. Generate prompts locally for any task. Commit to `docs/prompts/`.

---

## Support & Resources

**Documentation**:
- PR Template: `.github/pull_request_template.md`
- System README: `.github/copilot-prompts/README.md`
- This Guide: `docs/workflows/COPILOT_CONTINUATION_GUIDE.md`

**Scripts**:
- Generator: `scripts/generate_pr_followup.py`
- Test Suite: `scripts/test_continuation_system.sh`

**Workflows**:
- Auto-Generation: `.github/workflows/pr-followup-generator.yml`

**Templates**:
- All Templates: `.github/copilot-prompts/templates/`

**Examples**:
- Active Prompts: `.github/copilot-prompts/active/`
- Archived Prompts: `.github/copilot-prompts/archived/`

---

**Version**: 2.0.0  
**Last Updated**: 2025-12-29  
**Maintainer**: Copilot Agent Automation System
