# Dynamic CI Coverage Threshold Management

**Implementation Guide for `Aries-Serpent/_codex_` Repository**

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture & Decision Flow](#architecture--decision-flow)
3. [File Structure](#file-structure)
4. [Error Scenarios & Debugging](#error-scenarios--debugging)
5. [Troubleshooting Checklist](#troubleshooting-checklist)

---

## Overview

This implementation provides **dynamic coverage threshold enforcement** for the repository:

- ✅ **Maintains quality**: Enforces minimum 70% coverage floor
- 📈 **Optimizes gradually**: Auto-lowers threshold to highest achievable (70-100%)
- 🤖 **Self-healing**: Creates PR when threshold needs adjustment
- 🔍 **Observable**: Extensive debug logs at every decision point
- 🚨 **Actionable failures**: Clear error messages with resolution steps

### Key Behaviors

| Coverage Range | Action | Result |
|---|---|---|
| ≥ Current threshold (e.g., 96%) | ✅ Pass | CI succeeds, no changes |
| 70-95% (below threshold) | 🔄 Auto-adjust | Create PR to lower threshold, job succeeds |
| < 70% | ❌ Fail | CI fails with actionable error message |
| 0% or parse error | ❌ Fail | CI fails, coverage.xml debug output shown |

---

## Architecture & Decision Flow

```text
┌─────────────────────────────────────────────────────────────────┐
│                    CI Workflow Execution                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. Setup Environment (Python 3.11, deps, nox)                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. Run Coverage (nox -s coverage → artifacts/coverage.xml)     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. Debug: Print coverage.xml (first 500 lines)                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. Parse Coverage (ci_parse_coverage.py → XX.XX%)              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────┴─────────┐
                    │   Parse Success?   │
                    └─────────┬─────────┘
                         NO   │   YES
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
            ┌───────────────┐   ┌──────────────────┐
            │ coverage=0    │   │ coverage=XX.XX   │
            │ EXIT 1 (FAIL) │   │ Continue...      │
            └───────────────┘   └──────────────────┘
                                        │
                                        ▼
                          ┌─────────────────────────┐
                          │ Read threshold file     │
                          │ Default: 96             │
                          └─────────────────────────┘
                                        │
                                        ▼
                          ┌─────────────────────────┐
                          │ Coverage < 70?          │
                          └─────────────────────────┘
                                   │
                              YES  │  NO
                    ┌──────────────┴──────────────┐
                    ▼                             ▼
        ┌──────────────────────┐      ┌──────────────────────┐
        │ ERROR: Below floor   │      │ Coverage ≥ threshold?│
        │ EXIT 1 (FAIL)        │      └──────────────────────┘
        └──────────────────────┘                 │
                                            YES  │  NO
                                  ┌──────────────┴──────────────┐
                                  ▼                             ▼
                      ┌──────────────────┐      ┌──────────────────────┐
                      │ OK: Pass CI      │      │ Create branch        │
                      │ EXIT 0 (SUCCESS) │      │ Update threshold.txt │
                      └──────────────────┘      │ Commit & Push        │
                                                │ Open PR              │
                                                │ EXIT 0 (SUCCESS)     │
                                                └──────────────────────┘
```text

---

## File Structure

```text
Aries-Serpent/_codex_/
├── .github/
│   ├── coverage_threshold.txt          # Current threshold (96)
│   ├── docs/
│   │   └── CI_Coverage_Implementation.md  # This file
│   ├── scripts/
│   │   └── ci_parse_coverage.py        # XML parser (70-100% variant)
│   └── workflows/
│       └── ci.yml                      # Main CI workflow
├── artifacts/
│   └── coverage.xml                    # Generated by pytest-cov
└── ...
```text

### Parser Script Exit Codes

The `ci_parse_coverage.py` script uses the following exit codes:

| Code | Meaning |
|---|---|
| 0 | Success, coverage printed to stdout |
| 2 | Missing argument |
| 3 | File not found |
| 4 | XML parse error |
| 5 | ValueError (couldn't determine coverage) |
| 6 | Non-finite value |
| 8 | Unexpected error |

---

## Error Scenarios & Debugging

### Scenario 1: Coverage XML Not Generated

**Symptoms**:
```text
No coverage.xml at artifacts/coverage.xml
ERROR: coverage xml missing
coverage=0
ERROR: Coverage could not be parsed or is 0. Failing CI.
```text

**Root Cause**: Test command didn't generate XML or wrote to wrong path.

**Debug Steps**:
1. Check "Run coverage session" step output
2. Verify `nox -s coverage` or `pytest` command ran
3. Look for coverage configuration in `pyproject.toml` or `.coveragerc`

**Resolution**:
```bash
# Option A: Update noxfile.py coverage session
@nox.session
def coverage(session):
    session.install("-e", ".[dev]")
    session.run(
        "pytest",
        "--cov=src/codex",
        "--cov-report=xml:artifacts/coverage.xml",
        "--cov-report=term",
    )

# Option B: Update COVERAGE_XML_PATH in workflow
env:
  COVERAGE_XML_PATH: coverage.xml  # If nox writes to root
```text

---

### Scenario 2: XML Parse Failure

**Symptoms**:
```text
===== coverage.xml contents =====
<html><body>404 Not Found</body></html>
================================
ERROR: failed to parse coverage xml as XML: syntax error: line 1, column 0
coverage=0
```text

**Root Cause**: Wrong file generated or corrupt XML.

**Debug Steps**:
1. Review printed XML in "Show coverage.xml" step
2. Check if file is HTML error page
3. Verify coverage tool is installed

**Resolution**:
```bash
# Ensure pytest-cov is installed
pip install pytest pytest-cov coverage

# Test locally
pytest --cov=src/codex --cov-report=xml:artifacts/coverage.xml
cat artifacts/coverage.xml  # Verify structure
```text

---

### Scenario 3: Coverage Below 70%

**Symptoms**:
```text
DEBUG: computed coverage = 45.67
DEBUG: current target threshold = 96
DEBUG: rounded coverage=46 threshold=96
ERROR: Coverage (45.67%) is below minimum allowed 70%.
To fix: run tests locally, inspect artifacts/coverage.xml, add tests or adjust exclusions.
```text

**Root Cause**: Insufficient test coverage.

**Debug Steps**:
1. Download `coverage.xml` artifact from GitHub Actions
2. Run `coverage html` locally to see uncovered lines
3. Check `.coveragerc` for exclusions

**Resolution**:
```bash
# Generate HTML report locally
nox -s coverage
coverage html
open htmlcov/index.html  # Review coverage gaps

# Add tests for uncovered modules
# OR add justified exclusions to pyproject.toml:
[tool.coverage.run]
omit = [
    "*/tests/*",
    "*/migrations/*",
    "*/__init__.py",
]
```text

---

### Scenario 4: Coverage Between 70-95% (Auto-Adjust)

**Symptoms**:
```text
DEBUG: computed coverage = 87.23
DEBUG: current target threshold = 96
DEBUG: rounded coverage=87 threshold=96
INFO: Coverage (87.23%) is lower than threshold (96) but >=70.
INFO: Will update .github/coverage_threshold.txt -> 87 and open a PR.
git checkout -b auto/adjust-coverage-to-87-1699901234
git commit -m "ci: lower coverage threshold to 87% (auto-generated by CI)"
git push --set-upstream origin auto/adjust-coverage-to-87-1699901234
```text

**Expected Behavior**: PR created automatically.

**Debug Steps**:
1. Verify PR appears in repository
2. Check PR title: `chore(ci): lower coverage threshold to 87% (auto)`
3. Review PR diff (should only change `.github/coverage_threshold.txt`)

**Action Required**: Review and merge PR to accept new threshold.

---

### Scenario 5: Git Push Permission Denied

**Symptoms**:
```text
git push --set-upstream origin auto/adjust-coverage-to-87-1699901234
remote: Permission to Aries-Serpent/_codex_.git denied to github-actions[bot].
fatal: unable to access 'https://github.com/Aries-Serpent/_codex_.git/': The requested URL returned error: 403
```text

**Root Cause**: GitHub Actions doesn't have write permission.

**Resolution**:
1. Verify workflow has `permissions: contents: write`
2. Check repository Settings → Actions → General → Workflow permissions
3. Ensure "Read and write permissions" is selected
4. If using branch protection, allow `github-actions[bot]` to bypass

---

## Troubleshooting Checklist

| Issue | Check | Fix |
|---|---|---|
| ❌ No coverage.xml | Verify nox/pytest command | Update coverage session config |
| ❌ Parse error | Inspect printed XML | Fix coverage tool installation |
| ❌ Coverage 0% | Check test execution | Ensure tests run successfully |
| ❌ Coverage < 70% | Review coverage HTML | Add tests or exclusions |
| ✅ Coverage 70-95% | Verify PR created | Review and merge PR |
| ✅ Coverage ≥ 96% | Check CI passes | No action needed |
| ❌ Git push denied | Check permissions | Enable write access in repo settings |
| ⚠️ Duplicate PR | Normal behavior | peter-evans action handles it |

---

**Maintained by**: mbaetiong  
**Last Updated**: 2024-11-12  
**Related Files**: 
- `.github/workflows/ci.yml`
- `.github/scripts/ci_parse_coverage.py`
- `.github/coverage_threshold.txt`
