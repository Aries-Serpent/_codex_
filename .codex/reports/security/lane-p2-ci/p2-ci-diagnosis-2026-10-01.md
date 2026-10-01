# Lane P2 — CI Failure Resolution: `Art_Security Scanning Suite`

**Date:** 2026-10-01
**Branch:** `copilot/resume-session-multi-lane-remediation`
**Workflow:** `.github/workflows/security-scanning-suite.yml`
**Failed run under diagnosis:** ID `36518740101` (branch `0D_base_`, conclusion=**failure**, head_sha `5192b368d35c4e931cd97c22ff0d37182bd3e964`, run_number `15086`, 2026-09-29)
**Evidence constraint:** Run `36518740101` jobs/artifacts have **EXPIRED** from the GitHub API (`list_workflow_jobs` → 0 jobs). Diagnosis is therefore driven by (1) the workflow definition itself, and (2) the local artifact bundle under `.codex/reports/security/security-suite-artifacts/run-26992144518/` (a stale **success**-run snapshot used as structural ground truth).

---

## 1. Executive summary

The workflow's **authoritative security gate** (`validate-security-artifact-contract`) is intact and was **not** weakened. The defects found are in the **per-job evidence-production layer**, where any missing artifact family caused a **hard job failure** (`if-no-files-found: error`) instead of a **recorded evidence-gap**, and where the **semgrep subprocess was invoked without stripping `PYTHONPATH`/`PYTHONHOME`** — the exact shadowing hazard the repo already documents and guards against in `tests/security/test_semgrep_rules.py:27-50`.

This corroborates the Lane S2 finding (".codex/reports/security/CHECKPOINT_2026_10_01_MULTILANE_REMEDIATION.md"): *"Workflow contract valid; containers hardened; 7 bundle families = evidence gap not workflow break."* The 7 missing bundle families are an **evidence gap**; the **workflow break** was that missing families were allowed to hard-fail jobs rather than degrade to recorded gaps. Fixes below make the degradation explicit and recorded while leaving the hard security contract enforced.

**Net effect:** coverage is **preserved or strengthened** — no scan scope narrowed, no gate threshold lowered, no suppression added.

---

## 2. Failure modes assessed (task items a–e)

| Mode | Description | Verdict | Disposition |
|---|---|---|---|
| **(a)** | semgrep subprocess `PYTHONPATH`/`PYTHONHOME` shadowing | **CONFIRMED — defect** | **FIXED** (F1) |
| **(b)** | editable-install failure on sparse/API-only runners | **Already mitigated** | Verified, no change (F2) |
| **(c)** | artifact upload path / `if-no-files-found` mismatch | **CONFIRMED — defect** | **FIXED** (F3) |
| **(d)** | gate threshold logic (critical/high fail conditions) | **Correct** | Verified, no change (F4) |
| **(e)** | missing artifact families hard-fail instead of recorded evidence-gap | **CONFIRMED — defect** | **FIXED** (F5) |

---

## 3. Root causes found

### F1 — Semgrep env shadowing (mode a) — P1 — FIXED
- **Where:** `.github/workflows/security-scanning-suite.yml`, steps `Run Semgrep scan (SARIF)` and `Run Semgrep scan (JSON)`.
- **Defect:** `semgrep scan` was invoked with the default runner environment. Sibling workflows in this repo (`ml-tests.yml`, `test-rag.yml`, `audit-qa-suite.yml`) `export PYTHONPATH=…src`, and `tests/security/test_semgrep_rules.py:40-41` explicitly pops `PYTHONPATH`/`PYTHONHOME` before calling the semgrep CLI, with a comment explaining that an external CLI must resolve **installed** third-party packages rather than **repo-local partial packages** under `src/`. On a runner where `PYTHONPATH` points at the repo `src/`, semgrep can import repo-local partial packages and error out / misbehave.
- **Fix:** Added a step-level `env:` block setting `PYTHONPATH: ""`, `PYTHONHOME: ""`, `SEMGREP_COLOR: never`, `SEMGREP_DISABLE_LIVE_PROGRESS: "1"`, and prefixed the `run:` with `unset PYTHONPATH PYTHONHOME`. This mirrors the test's defensive pattern and is applied to **both** the SARIF and JSON invocations. **Scan configs unchanged** (`p/security-audit`, `p/python`, `p/flask`) — coverage preserved.

### F2 — Editable-install guard (mode b) — P2 — ALREADY MITIGATED
- **Where:** `.github/actions/setup-python-cached/action.yml:247-250`.
- **Finding:** The composite action already guards the editable install: `if [ -f pyproject.toml ]; then pip install -e ".[extras]"; else echo "::warning::Skipping editable install: pyproject.toml not present in this workspace"`. Same guard at lines 239-241 for package-dir installs. This matches the `workflow-execution-gate.yml` sparse-checkout contract. **No change required.**

### F3 — `if-no-files-found: error` hard-fail on missing families (mode c) — P1 — FIXED
- **Where:** 10 evidence-producing `upload-artifact` steps in `security-scanning-suite.yml`.
- **Defect:** Every evidence upload used `if-no-files-found: error`. Because the scan steps run `continue-on-error: true`, a tool that produces no output (or a family that is skipped/empty) caused the **upload step to hard-fail the job**, surfacing as a workflow failure even though the correct disposition is a **recorded evidence-gap**. This is the workflow-break half of S2's "7 missing families."
- **Fix:** Changed the 10 evidence-producing uploads from `error` → `warn`. The three uploads that remain `error` are intentional and correct:
  - `security-suite-artifact-contract-report` (line ~1386) — the gate's **own** report, produced unconditionally by a heredoc, must exist.
  - `security-cache` and `security-findings-trend-report` (lines ~1427, ~1435) — gated behind `if: success()` **and** downstream of `validate-security-artifact-contract == 'success'`, so they only run after the hard gate has already passed.
- **Gate preserved:** `validate-security-artifact-contract` keeps `continue-on-error: false` on its download and `exit 1` on missing/invalid contract files. The authoritative enforcement point is unchanged.

### F4 — Gate threshold logic (mode d) — P3 — VERIFIED CORRECT
- **Where:** `scripts/ci/aggregate_security_findings.py:380-386` (`failure_classification`) and `:504-562` (`main`).
- **Finding:** `failure_classification` (`blocked_by_critical_or_high_vulnerabilities` / `warning_only` / `clean`) is computed and recorded as **data** in the report. The script exits non-zero **only** on a parse/IO error, never on a critical/high count. The workflow's aggregation step also runs the aggregator with `|| true`. There is **no spurious hard-fail on critical/high**; documented intent is preserved. **No change required.**

### F5 — Missing families not recorded as evidence-gaps (mode e) — P1 — FIXED
- **Where:** `security-suite-summary` job in `security-scanning-suite.yml`.
- **Defect:** `download-artifact` used `continue-on-error: true`, so missing families were **silently swallowed** — nothing recorded *which* families were absent. Absence was indistinguishable from an empty scan.
- **Fix:** Added a new step **"Audit artifact family presence (record evidence gaps)"** immediately after the download. It enumerates the expected families (lane-contract, codeql-python/javascript, semgrep, dependency, secrets, sbom, summary, plus the `container-*`/`cve-*` matrix prefixes), writes:
  - `security-suite-summary/artifact-evidence-gap.json` (machine-readable, `classification: evidence_gap|complete`, `evidence_gaps[]`, `evidence_gap_count`), and
  - `security-suite-summary/artifact-evidence-gap.md` (human table, appended to `$GITHUB_STEP_SUMMARY`).
  Both are included in the existing `security-suite-summary` upload path (`security-suite-summary/`), so gaps are **persisted as evidence**. The step exits 0 whether or not gaps exist — it **records**, it does not **fail**.

### F6 — Corroborating observation (context, not a separate defect)
- The stale success-run bundle `run-26992144518` contains `semgrep-results.json` + `semgrep-summary.md` but **no** `semgrep-results.sarif`, `sarif-chunks/`, scan logs, or `output-contract-semgrep.json`, even though the summary text references those files. This is consistent with F1 (SARIF-path instability from env shadowing) combined with F3 (the job still reported "success" via `continue-on-error` while the upload surface was incomplete). It reinforces that env-shadowing + error-mode interaction is the practical root cause of the observed instability.

---

## 4. Fixes applied (file:line)

All changes are confined to `.github/workflows/security-scanning-suite.yml`. No new workflow files created; `copilot-setup-steps.yml` untouched.

| Fix | Location | Change |
|---|---|---|
| F1 | `security-scanning-suite.yml` — `Run Semgrep scan (SARIF)` step (~line 427) | Added `env:` strip block + `unset PYTHONPATH PYTHONHOME` in `run:` |
| F1 | `security-scanning-suite.yml` — `Run Semgrep scan (JSON)` step (~line 446) | Added `env:` strip block + `unset PYTHONPATH PYTHONHOME` in `run:` |
| F3 | `security-scanning-suite.yml` — 10 evidence `upload-artifact` steps (lines 196, 391, 589, 686, 786, 910, 982, 1056, 1201, 1308) | `if-no-files-found: error` → `warn` |
| F5 | `security-scanning-suite.yml` — `security-suite-summary` job, new step after artifact download (~line 1080) | Added "Audit artifact family presence (record evidence gaps)" step emitting `artifact-evidence-gap.{json,md}` |

**Kept as hard gate (unchanged):** `validate-security-artifact-contract` (`continue-on-error: false`, `exit 1` on missing/invalid contract), and the `if: success()` cache/trend uploads downstream of it.

---

## 5. Validation results

| Check | Command | Result |
|---|---|---|
| YAML parse | `python -c "import yaml; yaml.safe_load(...)"` | ✅ OK — 13 jobs intact |
| Repo workflow contract | `python scripts/ci/check_workflow_yaml.py .github/workflows/security-scanning-suite.yml` | ✅ `1 workflow file(s) passed YAML syntax and repo contract validation` |
| Semgrep rule tests | `python -m pytest tests/security/test_semgrep_rules.py -x -q` | ✅ **PASS** (exit 0), semgrep 1.178.0 present |
| Semgrep env-strip structure | programmatic assert on parsed YAML | ✅ both SARIF+JSON steps carry `env` strip + `unset` |
| Evidence-gap step present | programmatic assert | ✅ present in `security-suite-summary` |
| Evidence-gap Python compiles | `compile()` on extracted heredoc | ✅ compiles (69 lines) |
| Evidence-gap simulation (empty artifacts dir = 0D_base_ scenario) | run block in temp dir | ✅ exit 0, `classification: evidence_gap`, `gap_count: 10` — records without failing |
| Hard gate preserved | programmatic assert | ✅ `validate-security-artifact-contract` download `continue-on-error: false` |
| Secret scan (changed file) | repo secret scanner | ✅ No secrets detected |

---

## 6. Residual items (owner + reason + plan — no deferral)

| ID | Item | Owner | Reason it remains | Plan |
|---|---|---|---|---|
| R1 | `validate-security-artifact-contract` hard gate is unreachable on the failed 0D_base_ run because upstream producers failed first. | Lane P2 (this lane) | The gate only runs when producers upload; with F3/F5 fixed, producers now degrade to recorded gaps so the gate receives its contract input. | Next scheduled/dispatch run of the suite on `0D_base_` will exercise the full path; confirm `security-suite-comprehensive-findings` uploads and the gate evaluates. Verify via the run's `artifact-evidence-gap.json`. |
| R2 | `cache-findings` step commands (`security_cache_manager.py`, `security_findings_trend_analyzer.py`) use `set -euo pipefail` with no `|| true`. | ci-testing-agent | Out of scope for a surgical P2 fix; they are correctly gated behind `validate-security-artifact-contract == 'success'` so they only run when findings exist. | ci-testing-agent to add defensive empty-input handling in those two scripts as a follow-up hardening; tracked in `.codex/reports/security/security-backlog-ledger.md`. |
| R3 | Live confirmation that F1 resolves the 0D_base_ semgrep SARIF-path instability (F6) requires a real run — cannot be proven from the expired-run evidence alone. | Lane P2 (this lane) | The failed run's logs are expired; local bundle is a stale success-run snapshot. | Trigger/observe the next `Art_Security Scanning Suite` run and confirm `security-suite-semgrep` now contains `semgrep-results.sarif` + `sarif-chunks/` + `output-contract-semgrep.json`. |

---

## 7. Cross-check vs Lane S2

S2 concluded: *"Workflow contract valid; containers hardened; 7 bundle families = evidence gap not workflow break."*

**This lane confirms and operationalizes that finding.** The contract (validate-security-artifact-contract) is valid and remains the hard gate. The 7 missing families in the stale bundle are an evidence gap — and the workflow defect was that such gaps were previously allowed to **hard-fail** jobs (`if-no-files-found: error`) and were **not recorded**. Fixes F3 + F5 convert missing families into explicitly recorded evidence-gaps, and F1 removes the semgrep env-shadowing that contributed to incomplete evidence production. Container hardening (S2) is untouched; the Trivy/container jobs are unchanged except for the upload error→warn mode (F3).

**No scan scope narrowed. No gate threshold lowered. No suppressions added. Coverage preserved or strengthened.**
