# Semgrep Remediation Plan

> Generated: 2025-12-24T10:17:41.307005+00:00
> Total Alerts: 2

## Executive Summary

| Priority | Count | Target |
|----------|-------|--------|
| P0 (Critical) | 2 | Immediate |
| P1 (High) | 0 | This Sprint |
| P2 (Medium) | 0 | Backlog |
| P3 (Low) | 0 | Defer |

## Remediation Strategy

1. **Automated Codemods**: Apply existing codemods from `scripts/security/codemods/`
2. **Manual Review**: Address complex patterns requiring human judgment
3. **Suppress False Positives**: Document and suppress confirmed false positives
4. **Enable Baseline**: After remediation, enable baseline mode

## Pattern-Based Batches

### Pattern: `command_injection` (1 alerts)

**Priority Breakdown**: P0=1, P1=0
**Batches**: 1

| Batch | Alerts | P0 | P1 | Status |
|-------|--------|----|----|--------|
| 1 | 1 | 1 | 0 | ⏳ Pending |

### Pattern: `secrets` (1 alerts)

**Priority Breakdown**: P0=1, P1=0
**Batches**: 1

| Batch | Alerts | P0 | P1 | Status |
|-------|--------|----|----|--------|
| 1 | 1 | 1 | 0 | ⏳ Pending |

## Available Codemods

The following automated fixes are available in `scripts/security/codemods/`:

| Codemod | Pattern | Description |
|---------|---------|-------------|
| `fix_sql_injection.py` | SQL Injection | Converts to parameterized queries |
| `fix_subprocess.py` | Command Injection | Removes shell=True |
| `fix_subprocess_libcst.py` | Command Injection | LibCST-based AST transform |
| `fix_hardcoded_secrets.py` | Secrets | Moves to environment variables |

## Execution Commands

```bash
# Run all codemods
python scripts/security/run_codemods.py

# Run specific codemod
python scripts/security/codemods/fix_sql_injection.py

# Validate fixes
python scripts/security/validate_security.py
```

## Post-Remediation

After all alerts are resolved:

1. Update `.semgrep/semgrep.yml` with baseline configuration
2. Document any remaining suppressions in `.security-exceptions.md`
3. Enable baseline mode to catch only new alerts

---

*This plan is auto-generated. Update by re-running `generate_remediation_plan.py`*
