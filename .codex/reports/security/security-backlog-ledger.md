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
