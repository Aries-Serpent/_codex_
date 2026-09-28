# Consolidated Security Residual Backlog
**Last Updated:** 2026-07-11
**Version:** v0.2.0

**Last Updated: 2026-06-22

- Scope: cross-plan consolidation for `docs/security-open-findings-matrix.md`, `remediation_plan_codeql_python.md`, `remediation_plan_semgrep.md`, and `remediation_plan_secrets.md`
- Branch / HEAD sampled: `copilot/explore-codebase-and-create-implementation-plan` @ `f96e1ce6b77411e4a690ba4fb312c9fcc84bda9a`
- Purpose: keep one residual backlog so already-landed fixes are not reopened under multiple rule families.

## Validation performed in the current environment

| Check | Result | Notes |
|---|---|---|
| `python scripts/ci/rvs_preflight.py --group quick --preview` | PASS | No `quick` test files were discovered; preview still confirms the supported preflight path is clean. |
| `detect-secrets scan tests/safety/test_sanitizers_coverage.py tests/serving/test_inference_enhanced.py tests/test_token_verification.py .github/workflows/codeql-alert-fetcher.yml .github/workflows/security-scanning-suite.yml` | PASS | Returned `"results": {}` after the allowlist work already documented in `remediation_plan_secrets.md`. | <!-- pragma: allowlist secret -->
| `pip-audit -r requirements/lock.txt --desc on` | FAIL | Reported `torch 2.11.0` `CVE-2025-3000` on the default lockfile surface. |
| `pip-audit -r requirements/lock-eval.txt --desc on` | FAIL | Reported `sqlitedict 2.1.0` `CVE-2024-35515` on the opt-in eval lockfile surface. |
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

## Canonical next-cycle queue

This repository has repeated the same backlog families across multiple branches and sessions. The following queue is the canonical "do not restart from zero" list for the next cycle. Each family is tracked as a recurring work item with a designated owner and a closure path before it is considered complete.

| Family ID | Recurring pattern | Evidence seen in repo | Closure path | Owner |
|---|---|---|---|---|
| `codeql_scope_bloat` | Scope expands beyond what is proven, validated, or required for a single change set. | `docs/evidence/consolidated-security-residual-backlog.md` consolidates multiple plan-based findings; PR #3181 explicitly says repository-wide issues were recorded as follow-up ownership items instead of being merged into the active patch. | Close only when a PR or patch is narrowed to a bounded scope, any spillover is filed as a follow-up task with owner, and the validation gate passes on the scoped delta. | `@Aries-Serpent/owners` |
| `codeql_followup_pr_defer` | Follow-up work is deferred without a closure artifact, then reappears in the next branch/session. | PR #3181 validation note requires a dedicated follow-up task, owner, and validation run before merge of the follow-up change. The residual backlog doc itself is explicitly a consolidation against repeated re-openings. | Require a named follow-up issue/PR, due date, verification command, and closure note before closure. Deferrals without a reference are escalated as open recurring items. | `@Aries-Serpent/owners` |
| `codeql_admin_blocker` | Repository or workflow administration prevents validation (permissions, access, gating, or requirement mismatches). | Branch rebase and secret-scanning gate failures are treated as systemic environment failures in `.codex/CI_FAILURE_TRIAGE_LANE1_2026_07_16.md`; the repo also has admin/approval guardrails in `.github/OWNER_APPROVAL.yml` and `.github/CODEOWNERS`. | Close only after the admin action is taken (permission grant, workflow fix, policy unblocking), with a retry and a validation log proving the gate can pass. | `@Aries-Serpent/ops-team` |
| `codeql_external_platform_block` | Platform/API/tooling outage or provider restriction blocks code verification or follow-up work. | `docs/evidence/consolidated-security-residual-backlog.md` records CodeQL, Semgrep, Bandit, and secret-scanning query failures as blocked by environment access. `.codex/CI_FAILURE_TRIAGE_LANE1_2026_07_16.md` also shows a large workflow cascade with external-API/runner symptoms. | Close only when the provider or runner issue is resolved, a fresh scan or rerun is executed, and the result is recorded with the run or API evidence. | `@Aries-Serpent/ops-team` |
| `codeql_backlog_fragmentation` | Work is split across branches, plans, and docs, causing the next cycle to start from zero. | The repo contains multiple residual backlog and roadmap artifacts (`docs/evidence/consolidated-security-residual-backlog.md`, `docs/security/SECURITY_ROADMAP.md`, `.codex/CI_FAILURE_TRIAGE_LANE1_2026_07_16.md`, and branch-specific follow-up plans) without a single canonical queue. | Merge all duplicates into this canonical queue, attach the current owner, and link the closure PR/issue before the branch is considered complete. | `@Aries-Serpent/owners` + `@Aries-Serpent/docs-team` |

### Escalation policy for recurring deferrals

- If a family appears in more than one branch, session artifact, or PR narrative in the same cycle, it is marked as `recurring-deferral` and must have an owner.
- Any deferral without a closure artifact (issue/PR link, owner, proof command, and completion note) is considered open until the next cycle reconciliation.
- The canonical queue is the only source of truth for next-cycle carryover; plan docs, branch notes, and session summaries are supporting evidence only.
- Closure requires all four elements: owner, evidence, verification, and a linked follow-up path.

## Non-reopen guidance

- Do **not** reopen the checkpoint safety lane unless a new unsafe deserialization entry point appears.
- Do **not** reopen exact-line secret false positives that are already covered by inline pragmas or baseline-only JSON/JSONL handling.
- Do **not** reopen branch-divergence or discussion-workflow docs as security defects unless a scanning tool reports a new actionable code path.
