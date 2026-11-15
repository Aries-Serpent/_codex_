# 01 — Trivy and Dependency Advisory Remediation

**Objective:** Resolve or explicitly disposition the Trivy-reported dependency findings and explain the three missing GHAS configuration entries without weakening scan coverage.

## 1. Establish current evidence

1. Record PR #5766 head SHA, base SHA, and the latest run attempt for the Trivy check.
2. Obtain the current Trivy SARIF, dependency audit/SBOM artifacts, and GitHub code-scanning alert records through authorized read access. Verify each artifact's run ID, attempt, SHA, scanner and configuration identity.
3. If alert access is denied, stop short of claiming any alert is fixed or closed. Record the denial and request a security maintainer to provide the current alert export; do not attempt alternate credential/API access.
4. Reconcile the current records with the supplied 14-alert list in the parent README. Mark findings as current, resolved, superseded, duplicate, or unverified only when the evidence supports that state.

## 2. Resolve the GHAS configuration warning

1. Compare `.github/workflows/container-scan.yml` and relevant GHAS code-scanning configuration on the current PR head and `main`.
2. Identify why the three configurations named in the report are unmatched:
   - `trivy-scan/dockerfile:.config/Dockerfile`
   - `trivy-scan/dockerfile:docker/Dockerfile.cpu`
   - `trivy-scan/dockerfile:docker/Dockerfile.gpu`
3. Determine whether this is a missing workflow/configuration identity, a renamed matrix job, a branch-baseline mismatch, or an artifact/configuration upload issue. Use the actual GHAS diagnostic and workflow provenance, not assumptions from a green Actions job.
4. Propose the smallest compatibility correction that preserves scans of all three Dockerfiles and SARIF upload. If the required change is in GitHub-side configuration or needs an administrator, record the owner and request that decision rather than attempting a settings mutation.
5. Acceptance: the next authorized PR-head analysis recognizes the intended configuration identities, emits valid SARIF for each applicable Dockerfile, and no longer reports the three configurations as missing. A successful `container-scan.yml` run alone is insufficient.

## 3. Triage dependency findings

For each current alert, establish the exact installed version, dependency chain, affected extra/environment, whether the vulnerable code is reachable in that environment, the vendor advisory's current status, and a supported fixed version. Do not copy the report's “Fixed Version” field without verification.

### Critical/high first

1. **ChromaDB** — validate the four supplied CVEs against current vendor advisories and affected/fixed ranges. The lockfile and `pyproject.toml` include ChromaDB 1.5.9; determine which optional extras and product paths install/use it. Since no fixed version was shown, do not invent a version. If a fix exists, update the narrowest dependency constraint and regenerate only the necessary lock changes. Otherwise prepare a mitigation and evidence-based owner decision; do not suppress the alerts.
2. **MCP** — verify all four supplied CVEs and actual `mcp` lock version. The supplied CVE-2026-59951 annotation heading says High while its detail says Medium; resolve the discrepancy from current advisory and scanner records. The supplied report lists 1.30.0 or 2.2.0 as fixed for all four CVEs; verify that range remains valid, select the smallest compatible supported release, and test clients/transports, auth audience validation, redirect handling and schema-resolution limits. Do not assume one version change clears an alert until a new scan confirms it.
3. **OAuthlib** — verify CVE-2026-49272 and whether 4.0.1 is still the minimum safe supported release. Update `oauthlib` through the direct/transitive dependency that owns it and run OAuth/authentication tests.
4. **Sqlitedict** — verify current affected range and whether a fixed release now exists. Inspect the dependency chain and runtime reachability. If no fix exists, preserve the finding as unresolved pending a security-owner decision; do not silently accept it based on the older `security-remediation-planset.md`.

### Medium and duplicate/version-specific findings

5. **Diskcache** — recheck CVE-2025-69872 and available fixes. Inspect whether it is confined to development/DVC tooling or installed in product/runtime extras. Remove it only if the owning dependency no longer needs it and lock resolution proves it is unused; otherwise request an explicit risk disposition.
6. **OpenTelemetry API** — independently verify CVE-2026-114603 and CVE-2026-126360 against each installed version in `uv.lock`. Resolve the duplicate CVE-2026-126360 records as version-specific findings, not as one automatically cleared alert. Before changing the existing `<1.38.0` constraint in `pyproject.toml`, locate the code/API compatibility reason, test impacted integrations, and coordinate a separate compatible dependency boundary if needed.

## 4. Implement a bounded dependency batch

1. Group only compatible updates whose tests and owning extras can be validated together. Avoid repository-wide dependency upgrades or a broad lockfile refresh.
2. Update the declaring constraints and regenerate `uv.lock` using the repository's supported `uv` workflow. Review all lockfile changes and confirm unrelated packages/checksums did not churn.
3. Run lock consistency checks, focused tests for each affected feature, and the existing relevant CI dependency/security scans. Include installation tests for the affected extras and runtime configurations.
4. Run Ruff/format/type checks for changed source and `git diff --check`. Run the repository's secret scan before committing.
5. Submit each bounded code/dependency batch through the authorized review path. Do not alter GHAS findings or workflow settings as part of a dependency commit.

## Completion criteria

- Each supplied Trivy alert has a current, SHA-bound finding record and a verified state.
- All fixable critical/high findings are fixed and rescanned; no-fix findings have documented mitigation, named security owner, and explicit pending decision. Nothing is silently dismissed.
- The three workflow configurations are recognized, or the exact external administrator action and owner are recorded.
- Focused product tests and dependency/security checks pass on the same candidate SHA; remaining medium findings are transparently reported.
