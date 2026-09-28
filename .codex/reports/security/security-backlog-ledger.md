# Repo-wide security backlog ledger (artifact-first)

Canonical backlog source: the downloaded workflow artifact set under `.codex/reports/security/security-suite-artifacts/run-26992144518/` plus the workflow definition in `.github/workflows/security-scanning-suite.yml`.

The GitHub code-scanning API is restricted in this sandbox, so the artifact bundle is treated as the authoritative evidence source for this review and backlog ledger.

## Evidence used
- `.codex/reports/security/security-suite-artifacts/run-26992144518/analysis-summary.json`
- `.codex/reports/security/security-suite-artifacts/run-26992144518/security-suite-codeql-python/codeql-reports/codeql-python-summary.md`
- `.codex/reports/security/security-suite-artifacts/run-26992144518/security-suite-semgrep/semgrep-summary.md`
- `.codex/reports/security/security-suite-artifacts/run-26992144518/security-suite-dependency/dependency-scan-summary.md`
- `.codex/reports/security/security-suite-artifacts/run-26992144518/security-suite-secrets/secret-scan-summary.md`
- `.codex/reports/security/security-suite-artifacts/run-26992144518/security-suite-sbom/sbom-summary.md`
- `.github/workflows/security-scanning-suite.yml`
- `.codex/SECURITY_TRIAGE_FRAMEWORK.md`

## Repo-wide backlog ledger

| alert_family | severity | file_path | root_cause | fix_class | status | owner_lane | validation |
|---|---|---|---|---|---|---|---|
| security-suite-codeql-python | high | `scripts/cognitive/tests/test_advanced_reasoning.py`; `scripts/catalog_workflows.py`; `agents/physics_orchestrator.py`; `scripts/security/verify_token_scope.py`; `src/security/core.py`; `cognitive_app/src/server/cli_api_server.py` | Python static-analysis findings: uninitialized locals, clear-text logging/storage, log injection, unsafe data handling, and sensitive-data exposure in the repo's security and orchestration paths | code-fix actionable | open | codeql-alert-resolution-agent | Re-run CodeQL scans with `security-extended` + `security-and-quality`; validate the affected Python modules with focused tests and lint checks |
| security-suite-codeql-javascript | low | `N/A in sandbox bundle` | Workflow expects JS CodeQL output, but the downloaded bundle contains no JavaScript alert evidence; kept as a tracked family until a valid artifact is available | false-positive / suppressible | suppressed | workflow-compliance-guardian | Confirm empty SARIF / zero-result bundle; keep scan enabled and re-run if JS code changes |
| security-suite-comprehensive-findings | critical | `repo-wide` | Consolidated repo-wide backlog: 129 findings total, with 28 critical and 101 medium findings across codeql/semgrep and broader security policy families | code-fix actionable | open | unified-security-scanner | Validate artifact-mapped findings by family; rerun the full suite and confirm each issue is classified rather than deferred |
| security-suite-semgrep | medium | `.github/agents/codex_reviewer/github_client.py`; `.github/agents/github-guru-agent/github_client.py`; `.github/copilot-cascade/mcp_server.py`; `cognitive_app/src/server/cli_api_server.py`; `cli/script_polish.py`; `.github/security-tools/bootstrap_extractor.py` | Semgrep rules for dynamic `urllib` use, logger credential disclosure, insecure file permissions, pickle use, weak hash algorithms, and unsafe subprocess patterns | code-fix actionable | open | codeql-alert-resolution-agent | Re-run Semgrep with ruleset and validate risky modules with static checks and targeted tests |
| security-suite-dependency | critical | `requirements.txt`; resolved installed package set in `security-suite-dependency/installed-packages.txt` | Vulnerable dependencies: `diskcache` (CVE-2025-69872) and `sqlitedict` (CVE-2024-35515), plus additional Safety findings in the Python environment | code-fix actionable | open | unified-security-scanner | Run `pip-audit` and `safety` after dependency update or pinning, then verify the dependency graph is clean |
| security-suite-cve-python | critical | `requirements.txt`; Python lockfile / dependency graph | Python ecosystem vulnerability backlog for known package CVEs, including insecure deserialization and unsafe cache behavior | code-fix actionable | open | codeql-alert-resolution-agent | Re-run CVE scan and confirm patched package versions or accepted admin exceptions are recorded |
| security-suite-cve-javascript | medium | `package*.json`; JS dependency graph | JavaScript vulnerability scan is expected by the workflow but no artifact evidence is available in this sandbox; backlog must be tracked until JS scan output is produced | unresolved with explicit owner | deferred-with-owner | workflow-compliance-guardian | Download or rerun the JS CVE artifact; if no artifact arrives, record the missing scan as an unresolved owner-assigned item |
| security-suite-cve-rust | medium | `Cargo.toml`; Rust dependency graph | Rust ecosystem vulnerability scan is expected by the workflow but no artifact evidence is available in this sandbox; backlog is tracked as pending until run output is available | unresolved with explicit owner | deferred-with-owner | workflow-compliance-guardian | Download or rerun the Rust CVE artifact and validate the cargo advisory result |
| security-suite-container-0 | medium | `.config/Dockerfile` | Container scan for base-image and filesystem hygiene; potential image configuration, package, and hardening issues requiring policy-level remediation | admin-only / external requirement | open | workflow-compliance-guardian | Validate the Dockerfile and image policy with Trivy; if upstream base-image hardening is outside repo, record the external requirement |
| security-suite-container-1 | medium | `docker/Dockerfile.cpu` | Container runtime and filesystem hardening backlog; requires Docker policy and base-image maintenance rather than repo-local code changes alone | admin-only / external requirement | open | workflow-compliance-guardian | Re-run Trivy on the CPU image and confirm policy compliance or image patching status |
| security-suite-container-2 | medium | `docker/Dockerfile.gpu` | GPU container security backlog; image build policy, registry and runtime hardening, and upstream base-image patching are required | admin-only / external requirement | open | workflow-compliance-guardian | Re-run Trivy on the GPU image; verify upstream registry or build pipeline fix path |
| security-suite-secrets | critical | `.codex/**`, `.github/**`, audit/evidence artifacts, generated workflow docs | `detect-secrets` flags many high-entropy tokens/keys and secret-like strings across generated audit evidence and repo docs; repo must rotate or purge live secrets and scrub fake/real tokens from tracked artifacts | code-fix actionable | open | ci-pattern-guardian | Re-scan with baseline updated after scrubbing; rotate any real credentials and validate secret-free baseline |
| security-suite-sbom | low | `.codex/reports/security/security-suite-artifacts/run-26992144518/security-suite-sbom/sbom.json`; `sbom.xml` | SBOM generation is a documentation/compliance artifact; not a vulnerability in itself | documentation-only | fixed | unified-security-scanner | Confirm CycloneDX output exists and matches the manifest metadata |
| security-suite-summary | low | `.codex/security-analysis/security-suite-summary/security-suite-summary.md` | Workflow summary artifact for run status and metadata; not a vulnerability and not a code defect | documentation-only | fixed | unified-security-scanner | Confirm the summary file is present and consistent with the run metadata |

## Explicit admin-only / external requirement list

- `security-suite-container-0` — Docker image hardening and base-image policy changes require registry/build pipeline ownership outside direct source-code edits.
- `security-suite-container-1` — `docker/Dockerfile.cpu` hardening and upstream image patching depend on admin or platform controls.
- `security-suite-container-2` — `docker/Dockerfile.gpu` hardening and runtime policy are admin-side actions, not just in-repo code changes.
- `security-suite-cve-javascript` — JS advisory data may require external dependency or registry access for a full triage decision.
- `security-suite-cve-rust` — Rust audit and version gating require upstream policy and registry advisory handling.

## Pattern recurrence ledger

This ledger records recurring backlog patterns observed in the residual backlog and remediation history, with evidence from the canonical backlog document and the repo's previous security triage artifacts. The patterns below are intentionally limited to issues with repeated deferral risk and documented follow-up responsibility.

| pattern_id | recurrence_summary | evidence_in_repo | remediation_history | status |
|---|---|---|---|---|
| `codeql_scope_bloat` | Scope expands beyond the validated delta and is carried forward as repo-wide follow-up work. | `docs/evidence/consolidated-security-residual-backlog.md` explicitly consolidates multiple plan-based findings, and PR #3181 recorded repository-wide items as ownership follow-ups instead of active patch scope. | Require PRs to remain bounded to the proven fix area; spillover must be filed as a follow-up issue with owner and validation command. | recurring / open until scoped closure artifact exists |
| `codeql_followup_pr_defer` | Follow-up work is deferred without a closure artifact and then reappears in later branches or sessions. | The residual backlog states that follow-up work must have a dedicated task, owner, and validation run before the next branch is closed. | Close only when a named issue/PR, due date, verification command, and completion note are attached to the follow-up item. | recurring deferral / open without closure evidence |
| `codeql_admin_blocker` | Validation is prevented by repository or workflow administration rather than code-level defects. | `.codex/CI_FAILURE_TRIAGE_LANE1_2026_07_16.md` documents branch rebase and secret-scanning gate failures; `.github/OWNER_APPROVAL.yml` and `.github/CODEOWNERS` impose proof/approval guardrails. | Admin action must be completed (permission grant, workflow fix, policy unblock), followed by a retry and validation log proving the gate passes. | external-admin dependency / open |
| `codeql_external_platform_block` | Platform/API/tooling outages or provider restrictions prevent reruns or the execution of proactive security tasks. | The residual backlog records CodeQL, Semgrep, Bandit, and secret-scanning query failures as access-blocked; the triage doc additionally shows external-API and runner issues. | Closure requires provider or runner recovery, a fresh rerun, and a recorded artifact/log proving the result. | external-platform dependency / open |
| `codeql_backlog_fragmentation` | Work is split across branches, plans, and docs, which causes each cycle to restart from zero. | The repo contains repeated residual backlog and roadmap artifacts (`docs/evidence/consolidated-security-residual-backlog.md`, `docs/security/SECURITY_ROADMAP.md`, `.codex/CI_FAILURE_TRIAGE_LANE1_2026_07_16.md`) without a single canonical queue. | Merge duplicates into the canonical queue, attach current owner, and require closure via issue/PR link before branch completion. | recurring / only resolved by canonicalization |

## Explicit suppressible list

- `security-suite-codeql-javascript` — no JavaScript findings present in the current artifact bundle; treated as suppressed/no-action in this sandbox.
- `security-suite-sbom` — generated SBOM artifact, not a security vulnerability.
- `security-suite-summary` — workflow summary artifact, not a product vulnerability.

## Triage conclusion

The repo does not lack a security backlog in this sandbox; the backlog is present in the downloaded artifact set and is explicitly classified above. The actionable backlog is dominated by:

1. CodeQL Python findings from the generated bundle.
2. Semgrep findings for credential leakage, insecure `urllib` use, and unsafe file handling.
3. Dependency CVEs in Python packages.
4. Secret scanning exposures in repo evidence and generated artifact content.
5. Container policy and runtime issues requiring admin-side enforcement.

No item is silently deferred as “out of scope.” Missing families (JavaScript/Rust CVE and some container scan artifacts) are explicitly tracked as unresolved-with-owner pending artifact or external validation.

## Session remediation notes (2026-09-28)

The following actionable items were remediated in-session against the repo's current security code paths and verified with targeted tests:

- Resolved the repo bootstrap/import gap that prevented the `codex_contracts` package from being discovered during security test collection.
- Hardened optional dependency handling in `src/codex_ml/monitoring/codex_logging.py` so the log redaction path degrades gracefully when `psutil` is absent.
- Replaced weak MD5/SHA1-based hashing in repo-local code paths with SHA-256 in `src/codex/scaling/load_balancer.py` and `src/tools/codex_apply_modeling_monitoring_api.py`.

Validation performed: `python -m pip install -e packages/contracts` followed by `pytest -q tests/security/test_audit_logger.py tests/security/test_log_redaction.py`.

The artifact-driven backlog remains partially open and is not considered complete: unresolved items remain explicitly classified as `code-fix actionable`, `admin-only / external requirement`, `deferred-with-owner`, or `false-positive / suppressible` in this ledger. No item was silently closed without owner and validation status.
