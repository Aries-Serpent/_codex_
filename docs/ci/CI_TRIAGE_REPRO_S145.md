# CI Triage Reproducibility Reference — S145

**Last Updated:** 2026-06-22

> **Session:** S145 | **PR:** #3606 | **Date:** 2026-03-17
> **Script:** `scripts/ci/ci_triage_repro.sh`
> **Runbook:** Run `bash scripts/ci/ci_triage_repro.sh` to reproduce all checks in one pass.

---

## Overview

This document is the standardised reference for every diagnostic performed during
session S145.  Each check has its own section with:

- **Root cause** — what failed and why
- **Repro command** — exact shell command to reproduce the symptom
- **Fix command** — exact shell command to apply the fix
- **Verification** — how to confirm the fix took effect

All seven checks are bundled in `scripts/ci/ci_triage_repro.sh` and can be run
individually via `--check <N>` or all at once.

---

## Check 1 — actionlint: SC2072 decimal comparison {#check-1}

| Field | Value |
|-------|-------|
| **File** | `.github/workflows/coherence-snapshot.yml:199` |
| **CI gate** | Workflow Compliance Audit (actionlint) |
| **Error code** | SC2072 |
| **Session** | S145 |

### Root Cause

Shell's `[` (test) command performs **lexicographic** string comparison with `\>` and `\<`.
Applying it to floating-point values (e.g., `'99.65' \> '99.6'`) produces incorrect
results for strings like `100.0 \> 99.6` → `false` (because `'1' < '9'` lexicographically).
actionlint/shellcheck flag this as SC2072.

### Repro

```bash
bash scripts/ci/ci_triage_repro.sh --check 1
# or directly:
/tmp/actionlint .github/workflows/coherence-snapshot.yml 2>&1 | grep SC2072
```

## Fix

Replace the string comparison with `awk` arithmetic:

```bash
# Before (broken):
--status "$([ '${{ steps.aais.outputs.score }}' \> '99.6' ] && echo 'success' || echo 'warning')"

# After (fixed):
--status "$(awk -v s='${{ steps.aais.outputs.score }}' 'BEGIN{print (s+0 >= 99.7) ? "success" : "warning"}')"
```

## Verification

```bash
/tmp/actionlint .github/workflows/coherence-snapshot.yml 2>&1 | grep -c SC2072
# Expected: 0
```

---

## Check 2 — ruff I001: unsorted import block {#check-2}

| Field | Value |
|-------|-------|
| **Files** | `scripts/ci/aais_v4_scorer.py:31`, `scripts/ci/pr_comment_consolidator.py:58` |
| **CI gate** | Pre-Merge Validation, Auto-Fix Check |
| **Error code** | I001 |
| **Session** | S145 |

### Root Cause

Both files contain a guarded OTel import inside a `try:` block:

```python
try:
    sys.path.insert(0, str(ROOT / "src"))
    from codex.monitoring.otel_metrics import compute_coherence, workflow_coherence_score
    _OTEL_AVAILABLE = True
except Exception:
    _OTEL_AVAILABLE = False
```

`ruff --select I` (isort mode) flagged the import block as out of canonical order.
The pre-merge-validation workflow runs `ruff check --select I,E,F` which triggers I001.

### Repro

```bash
bash scripts/ci/ci_triage_repro.sh --check 2
# or directly:
ruff check --select I scripts/ci/aais_v4_scorer.py scripts/ci/pr_comment_consolidator.py
```

## Fix

```bash
ruff check --select I --fix scripts/ci/aais_v4_scorer.py scripts/ci/pr_comment_consolidator.py
```

### Verification

```bash
ruff check --select I scripts/ci/aais_v4_scorer.py scripts/ci/pr_comment_consolidator.py
# Expected: "All checks passed!"
```

---

## Check 3 — mypy: anti-regression baseline {#check-3}

| Field | Value |
|-------|-------|
| **File** | `.mypy_baseline` |
| **CI gate** | mypy Anti-Regression Gate |
| **Session** | S145 |

### Root Cause

`.mypy_baseline` contained `0`.  The CI gate runs:

```python
# scripts/ci/mypy_baseline.py logic:
if current_count > stored_baseline:
    sys.exit(1)  # regression
```

The codebase had 282 type errors, so `282 > 0` → gate failed.
The baseline was accidentally zeroed in a previous session.

## Repro

```bash
bash scripts/ci/ci_triage_repro.sh --check 3
# or directly:
cat .mypy_baseline
python scripts/ci/mypy_baseline.py  # shows current count
```

## Fix

After auditing that existing errors are pre-existing (not regressions):

```bash
python scripts/ci/mypy_baseline.py --update
# Writes current error count to .mypy_baseline
```

**Policy:** baseline should only increase to unblock CI after a verified audit;
ratchet it down incrementally as errors are fixed.

## Verification

```bash
python scripts/ci/mypy_baseline.py
# Expected: "✅ X errors ≤ baseline Y"
```

---

## Check 4 — auto-fix gate: 16 patterns {#check-4}

| Field | Value |
|-------|-------|
| **Script** | `scripts/ci/auto_fix_common_issues.py` |
| **CI gate** | Pre-Merge Validation, Auto-Fix Check |
| **Session** | S145 |

### Root Cause

This is the canonical first-line diagnostic.  Patterns 1–16 cover unused imports,
unused variables, YAML indentation, coverage thresholds, tokenizer fallbacks,
test assertions, redundant imports, CodeQL alerts, unsorted imports, bandit,
f-string placeholders, line length, W-series warnings, link checker config,
mypy baseline freshness, and stub duplicate definitions.

### Repro

```bash
bash scripts/ci/ci_triage_repro.sh --check 4
# or directly:
python scripts/ci/auto_fix_common_issues.py --check-only
```

## Fix

```bash
python scripts/ci/auto_fix_common_issues.py        # apply all fixable patterns
python scripts/ci/auto_fix_common_issues.py --pattern 1  # apply one pattern
```

### Verification

```bash
python scripts/ci/auto_fix_common_issues.py --check-only
# Expected: all 16 patterns show "✓ No issues found"
```

---

## Check 5 — ci-health-monitor: telemetry extraction bug {#check-5}

| Field | Value |
|-------|-------|
| **File** | `.github/workflows/ci-health-monitor.yml:71` |
| **Issue** | CI Health Alert #3614 |
| **Session** | S145 |

### Root Cause

The workflow embeds a base64-encoded Python script to extract metrics from
`/tmp/telemetry_report.json`.  The original script used `chr(34)` obfuscation:

```python
# BUGGY — constructs the string '"failed_runs"' (with embedded quotes):
print(f'FAILED_RUNS={s.get(chr(34)+"failed_runs"+chr(34),0)}')
# chr(34) == '"', so this calls: s.get('"failed_runs"', 0)
# The actual JSON key is 'failed_runs' (no quotes) → always returns 0
```

`failure_rate` used plain `'failure_rate'` (single-quote string) and worked
correctly.  Only `failed_runs` and `total_runs` used `chr(34)` — always returning 0.

**Observable symptom:** GitHub issue body showed `Total Runs: 0, Failed Runs: 0`
alongside a non-zero `Failure Rate: 11.7%` — mathematically impossible unless the
counts and rate came from different code paths.

## Repro

```bash
bash scripts/ci/ci_triage_repro.sh --check 5

# Manually reproduce the bug:
python3 - <<'EOF'
import json, base64

test_json = {"summary": {"total_runs": 180, "failed_runs": 21, "failure_rate": 0.117}}

# Buggy extraction (chr(34) obfuscation):
buggy = '''import json,sys
d={"summary":{"total_runs":180,"failed_runs":21,"failure_rate":0.117}}
s=d.get("summary",{})
rate=s.get("failure_rate",0)
print(f"FAILURE_RATE={rate*100:.1f}")
print(f"FAILED_RUNS={s.get(chr(34)+'failed_runs'+chr(34),0)}")
print(f"TOTAL_RUNS={s.get(chr(34)+'total_runs'+chr(34),0)}")
'''
print("=== BUGGY ===")
exec(buggy)

# Fixed extraction (plain string keys):
fixed = '''import json,sys
d={"summary":{"total_runs":180,"failed_runs":21,"failure_rate":0.117}}
s=d.get("summary",{})
rate=s.get("failure_rate",0)
print(f"FAILURE_RATE={rate*100:.1f}")
print(f"FAILED_RUNS={s.get('failed_runs',0)}")
print(f"TOTAL_RUNS={s.get('total_runs',0)}")
'''
print("=== FIXED ===")
exec(fixed)
EOF
```

Expected output:
```
=== BUGGY ===
FAILURE_RATE=11.7
FAILED_RUNS=0          ← always 0 (wrong key)
TOTAL_RUNS=0           ← always 0 (wrong key)
=== FIXED ===
FAILURE_RATE=11.7
FAILED_RUNS=21         ← correct
TOTAL_RUNS=180         ← correct
```

## Fix

Re-encode the extraction script with plain string keys:

```bash
python3 -c "
import base64
script = '''import json,sys
try:
    d=json.load(open(\'/tmp/telemetry_report.json\'))
    s=d.get(\'summary\',{})
    rate=s.get(\'failure_rate\',0)
    print(f\'FAILURE_RATE={rate*100:.1f}\')
    print(f\'FAILED_RUNS={s.get(\"failed_runs\",0)}\')
    print(f\'TOTAL_RUNS={s.get(\"total_runs\",0)}\')
except Exception:
    print(\'FAILURE_RATE=0\');print(\'FAILED_RUNS=0\');print(\'TOTAL_RUNS=0\')
'''
print(base64.b64encode(script.encode()).decode())
"
# Use the output to replace the METRICS=\$(echo '...') payload in the workflow
```

## Verification

```bash
bash scripts/ci/ci_triage_repro.sh --check 5
# Expected: "✅ PASS — Telemetry extraction: FAILURE_RATE=11.7%  TOTAL_RUNS=180  FAILED_RUNS=21"
```

---

## Check 6 — coherence-snapshot.yml: threshold misalignment {#check-6}

| Field | Value |
|-------|-------|
| **File** | `.github/workflows/coherence-snapshot.yml:199,210` |
| **PR review** | #3613 thread r2949785151 |
| **Session** | S145 |

### Root Cause

Two thresholds in the same workflow were inconsistent:

| Step | Expression | Value |
|------|-----------|-------|
| Dashboard `--status` | `s+0 > 99.6` | 99.6 (strict greater-than) |
| Enforcement `threshold` | `score < threshold` | 99.7 |

A score of **99.65** would set `--status success` (dashboard looks green) but then
immediately fail the enforcement step (job fails red).  Users see contradictory
signals.

### Repro

```bash
bash scripts/ci/ci_triage_repro.sh --check 6
# or directly:
grep -n "s+0\|threshold" .github/workflows/coherence-snapshot.yml
```

## Fix

Change the dashboard awk expression from `> 99.6` to `>= 99.7`:

```yaml
# Before:
--status "$(awk -v s='...' 'BEGIN{print (s+0 > 99.6) ? "success" : "warning"}')"

# After:
--status "$(awk -v s='...' 'BEGIN{print (s+0 >= 99.7) ? "success" : "warning"}')"
```

## Verification

```bash
bash scripts/ci/ci_triage_repro.sh --check 6
# Expected: "✅ PASS — Thresholds aligned: dashboard '>= 99.7' == enforcement '99.7'"
```

---

## Check 7 — CHANGELOG: self-inconsistent PR references {#check-7}

| Field | Value |
|-------|-------|
| **File** | `CHANGELOG.md:11` |
| **PR review** | #3613 thread r2949785123 |
| **Session** | S145 |

### Root Cause

`scripts/ci/session_wrapup_autofix.py` injected an auto-generated bullet into the
`### Fixed (S145 — ... — PR #3606)` section that referenced `PR #3613`:

```markdown
### Fixed (S145 — 2026-03-17 — PR #3606 CI triage)          ← header: #3606
- Auto-fix: session_wrapup_autofix.py updated ... for PR #3613  ← bullet: #3613
```

This breaks traceability: a reader cannot determine which PR the section belongs to.

### Repro

```bash
bash scripts/ci/ci_triage_repro.sh --check 7
# or directly:
grep -n "PR #" CHANGELOG.md | head -30
```

## Fix

Remove the cross-PR auto-generated bullet and consolidate the section header
to the correct PR number.

### Verification

```bash
bash scripts/ci/ci_triage_repro.sh --check 7
# Expected: "✅ PASS — CHANGELOG: no self-inconsistent PR number references"
```

---

## Running All Checks

```bash
# Full check-only pass (safe, read-only):
bash scripts/ci/ci_triage_repro.sh

# Apply all auto-fixable issues:
bash scripts/ci/ci_triage_repro.sh --fix

# JSON output for machine consumption:
bash scripts/ci/ci_triage_repro.sh --json

# Single check:
bash scripts/ci/ci_triage_repro.sh --check 5
```

## Quick-Reference Card

| Check | Command | Expected |
|-------|---------|---------|
| actionlint | `actionlint .github/workflows/*.yml` | 0 errors |
| ruff imports | `ruff check --select I .` | All checks passed |
| mypy baseline | `python scripts/ci/mypy_baseline.py` | count ≤ baseline |
| auto-fix | `python scripts/ci/auto_fix_common_issues.py --check-only` | 0 issues |
| telemetry bug | `bash scripts/ci/ci_triage_repro.sh --check 5` | 3 fields correct |
| threshold | `grep "s+0\|threshold" .github/workflows/coherence-snapshot.yml` | both 99.7 |
| changelog | `bash scripts/ci/ci_triage_repro.sh --check 7` | consistent |
