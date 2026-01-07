# Semgrep Suppression Register

> Last Updated: 2025-12-17
> Maintained by: @mbaetiong

## Overview

This document tracks all intentionally suppressed Semgrep alerts in the `Aries-Serpent/_codex_` repository. Each suppression must be documented with a clear rationale and undergo periodic review.

## Suppression Policy

1. **Documentation Required**: Every suppression must be documented in this register
2. **Rationale Required**: Clear explanation of why the alert is a false positive
3. **Approval Required**: Security team review for high/critical severity suppressions
4. **Review Cycle**: All suppressions reviewed every 6 months

## Active Suppressions

| Rule ID | File | Line | Severity | Reason | Approved By | Approved Date | Review Date |
|---------|------|------|----------|--------|-------------|---------------|-------------|
| python.lang.security.audit.eval-used | src/agents/sandbox_executor.py | 142 | High | Eval used in sandboxed agent executor with AST validation | @mbaetiong | 2025-12-17 | 2025-06-17 |
| python.lang.security.audit.exec-used | src/agents/code_runner.py | 89 | High | Exec in isolated subprocess with resource limits | @mbaetiong | 2025-12-17 | 2025-06-17 |

## Path Exclusions

| Path Pattern | Reason | Approved By | Approved Date |
|--------------|--------|-------------|---------------|
| tests/** | Test files contain intentional vulnerable patterns for testing | @mbaetiong | 2025-12-17 |
| examples/** | Example code demonstrates patterns without production context | @mbaetiong | 2025-12-17 |
| docs/code-samples/** | Documentation samples are not production code | @mbaetiong | 2025-12-17 |

## Review History

### 2025-12-17 - Initial Suppression Setup
- Created suppression register
- Documented path exclusions
- Added eval/exec suppressions for agent sandbox

## How to Add a Suppression

1. **Create inline suppression** in code:
   ```python
   # nosemgrep: rule-id
   # SECURITY REVIEW: Explanation of why this is safe
   # Reviewed by: @username on YYYY-MM-DD
   code_here()
   ```

2. **Document in this register** with:
   - Rule ID
   - File and line number
   - Severity
   - Detailed rationale
   - Approver and date
   - Next review date (6 months out)

3. **Get approval** from security team for high/critical severity

## Suppression Removal Process

1. Review suppression rationale
2. Determine if original justification still applies
3. If no longer valid, remove suppression and fix the issue
4. Update this register
