# Consolidated Security Residual Backlog

**Last Updated:** 2026-06-22

- Scope: cross-plan consolidation for `docs/security-open-findings-matrix.md`, `remediation_plan_codeql_python.md`, `remediation_plan_semgrep.md`, and `remediation_plan_secrets.md`
- Branch / HEAD sampled: `copilot/explore-codebase-and-create-implementation-plan` @ `f96e1ce6b77411e4a690ba4fb312c9fcc84bda9a`
- Purpose: keep one residual backlog so already-landed fixes are not reopened under multiple rule families.

## Validation performed in the current environment

| Check | Result | Notes |
|---|---|---|
| `python scripts/ci/rvs_preflight.py --group quick --preview` | PASS | No `quick` test files were discovered; preview still confirms the supported preflight path is clean. |
| `detect-secrets scan tests/safety/test_sanitizers_coverage.py tests/serving/test_inference_enhanced.py tests/test_token_verification.py .github/workflows/codeql-alert-fetcher.yml .github/workflows/security-scanning-suite.yml` | PASS | Returned `"results": {}` after the allowlist work already documented in `remediation_plan_secrets.md`. | <!-- pragma: allowlist secret -->
| `pip-audit -r requirements/lock.txt --desc on` | FAIL | Reported `torch 2.11.0` → `CVE-2025-3000` on the default lockfile surface. |
| `pip-audit -r requirements/lock-eval.txt --desc on` | FAIL | Reported `sqlitedict 2.1.0` → `CVE-2024-35515` on the opt-in eval lockfile surface. |
| CodeQL live alert query | BLOCKED | GitHub code-scanning API access returned `403 Resource not accessible by integration`. |
| Semgrep rerun | BLOCKED | `semgrep` CLI is not installed in the current environment. |
| Bandit rerun | BLOCKED | `bandit` CLI is not installed in the current environment; historical `artifacts/security/bandit.txt` remains the only local evidence. |
| Secret scanning API query | BLOCKED | GitHub secret-scanning API access returned `403 Resource not accessible by integration`. | <!-- pragma: allowlist secret -->

## Consolidated overlap rules

1. **Sanitized logging lane only once.**  
   CodeQL `py/clear-text-logging-sensitive-data`, Semgrep `python-logger-credential-disclosure`, and detect-secrets keyword false positives all touch the same logging surfaces. Reopen only if a fresh scan shows a real unsanitized runtime value, not because the same token/password wording appears under a second tool.

2. **Serialization / checkpoint lane only once.**  
   CodeQL storage findings, Semgrep `avoid-pickle`, checkpoint safety docs, and deserialization advisories such as `sqlitedict` all belong to the same trusted-boundary persistence story. The presence of `weights_only=True` and `RestrictedUnpickler` means the already-landed checkpoint fixes should not be reopened as separate Semgrep, secrets, and dependency issues.

3. **Dynamic URL / SSRF lane only once.**  
   Semgrep `dynamic-urllib-use-detected`, CodeQL proxy/logging follow-up, and the GitHub Discussions / MCP poster hardening all converge on outbound URL validation. Reopen only if a new path bypasses the current HTTPS/credential/host validation.

4. **Optional dependency isolation lane only once.**  
   Keep opt-in `eval`/`dataops` package vulnerabilities with the optional-extras lockfiles instead of reopening them against the default install when the vulnerable package is not part of the default surface.

5. **Branch-divergence docs are process hardening, not scan backlog.**  
   PR4393 follow-up docs describe CI churn mitigation and should not be treated as unresolved security findings.

## Residual backlog

| Priority | Residual item | Why it remains |
|---|---|---|
| P1 | Fresh CodeQL rerun for the partially fixed families, especially `py/uninitialized-local-variable` | The branch has implementation evidence but no fresh CodeQL proof in this session. |
| P1 | Fresh Semgrep rerun for sanitized logging, dynamic URL, and file-permission families | Current branch code shows the hardening patterns, but Semgrep was unavailable locally. |
| P1 | `torch 2.11.0` advisory on `requirements/lock.txt` | Newly reproduced by current-session `pip-audit`; this is the main default-install delta versus the historical plans. |
| P2 | `sqlitedict 2.1.0` advisory on `requirements/lock-eval.txt` | Still present, but isolated to the opt-in eval surface. |
| P2 | `.secrets.baseline` regeneration | Source-path false positives are already triaged; the baseline still needs a single cleanup pass to retire them. | <!-- pragma: allowlist secret -->
| P3 | Bandit low-severity hygiene rerun | Historical artifact still shows low-severity subprocess / broad-`except` findings, but Bandit was unavailable locally. |

## Non-reopen guidance

- Do **not** reopen the checkpoint safety lane unless a new unsafe deserialization entry point appears.
- Do **not** reopen exact-line secret false positives that are already covered by inline pragmas or baseline-only JSON/JSONL handling.
- Do **not** reopen branch-divergence or discussion-workflow docs as security defects unless a scanning tool reports a new actionable code path.
