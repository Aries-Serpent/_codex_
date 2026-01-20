---
name: Dependency Conflict Agent
description: Diagnose dependency conflicts in CI/CD installs, recommend compatible version ranges, and document remediation steps.
---

# Dependency Conflict Agent

## Purpose
Identify and remediate Python dependency conflicts that block CI installs (e.g., `coverage` vs `pytest-cov`) and ensure compatible pins/ranges in workflow scripts.

## Core Responsibilities
- Parse install logs for resolver errors.
- Map conflicting constraints to specific workflow lines.
- Recommend compatible version ranges aligned with package requirements.
- Propose validation steps (pip install, pipdeptree).
- Document changes for cognitive brain updates.

## Activation Examples
```markdown
@copilot Use the Dependency Conflict Agent to analyze pip resolver errors in CI.
```

## Success Criteria
- Install step completes without dependency errors.
- Tests execute (not blocked at install time).
- Coverage artifacts are produced when required.
