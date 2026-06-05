# Gap 11 — Automated Dependency Vulnerability Scanning in CI

**Status**: ✅ Complete  
**Priority**: P1 High  
**Completed**: 2026-06-10  

---

## What Was Done

### Workflow File Modified

**File**: `.github/workflows/scheduled-dependency-audit.yml`

The pre-existing `Scheduled Dependency Audit & SBOM` workflow already handled Docker-based SBOM generation with Syft/Grype and wheel-manifest drift detection, but had **no direct pip-audit or safety scanning** of requirements files. This gap was closed by:

1. **Adding a `pull_request` trigger** scoped to requirements-related paths so every PR that touches dependencies is scanned automatically.
2. **Adding a new `dependency-audit` job** (`pip-audit + safety`) that runs independently of Docker infrastructure.
3. **Extending the `summary` job** (`needs`) to include `dependency-audit` so the weekly audit summary reflects the new job's outcome.

---

## Triggers

| Trigger | Condition |
|---------|-----------|
| `pull_request` | Path filter: `requirements*.txt`, `requirements/**`, `pyproject.toml` |
| `schedule` | Weekly, every Monday at 00:00 UTC (`cron: '0 0 * * 1'`) |
| `workflow_dispatch` | Manual — any time via GitHub Actions UI |

---

## What the Scan Does

### pip-audit
- Scans `requirements.txt` and `requirements-dev.txt` against the PyPA Advisory Database.
- Outputs JSON report → `workbench/security/ci_pip_audit.json`
- Outputs CycloneDX JSON report → `workbench/security/ci_pip_audit_cyclonedx.json`
- **Fail policy**: If any `CRITICAL` or `HIGH` CVE is found in plain-text output, the step exits non-zero and the job fails with `::error::pip-audit found HIGH or CRITICAL CVEs`.

### safety
- Scans `requirements.txt` against the Safety DB advisory list.
- Outputs JSON report → `workbench/security/ci_safety_check.json`
- **Warn policy**: `CRITICAL`/`HIGH` findings emit a `::warning::` annotation pointing to the JSON report; the job does **not** fail hard (allows CI to continue while the issue is tracked).

---

## Artifact Retention

| Artifact Name | Contents | Retention |
|---------------|----------|-----------|
| `dependency-audit-<run_id>` | `ci_pip_audit.json`, `ci_pip_audit_cyclonedx.json`, `ci_safety_check.json` | **30 days** |

Artifacts are uploaded with `actions/upload-artifact@v4` and are always uploaded (`if: always()`) even when a scan step fails, so evidence is preserved for triage.

---

## Gap Dependency

This gap depends on **Gap 1** (pip-audit baseline) which established:
- `workbench/security/pip_audit_results.json` — baseline scan results
- `workbench/security/pip_audit_summary.md` — human-readable summary

The CI workflow now runs pip-audit continuously so the baseline is kept fresh on every qualifying PR and weekly schedule.

---

## Verification

```bash
# Validate YAML is parseable
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/scheduled-dependency-audit.yml'))" && echo "YAML valid"

# Confirm pip-audit job exists
grep -A 3 'dependency-audit:' .github/workflows/scheduled-dependency-audit.yml

# Confirm pull_request trigger exists
grep -A 5 'pull_request:' .github/workflows/scheduled-dependency-audit.yml
```
