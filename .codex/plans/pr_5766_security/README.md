# PR #5766 Security Remediation Planset

**Status:** Planned; no remediation or alert disposition is authorized by this planset alone.  
**Target:** PR #5766, `0D_base_` → `main`  
**Created:** 2026-11-15  
**Purpose:** Give a Copilot Cloud Agent an evidence-bound, end-to-end sequence for triaging the reported Trivy, CodeQL, Semgrep OSS, and Strict No-Deferral findings.

## Start here

1. Read this file and the four linked plans before changing source, dependencies, or workflow configuration.
2. Refresh PR #5766's head/base SHA and the exact check-run IDs. The snapshot below is historical; if the head differs, re-collect evidence and do not treat these results as proof for the new head.
3. Use current authorized GitHub check/SARIF/artifact access. The code-scanning-alert listing returned HTTP 403 to the prior inspection; do not infer that alerts are resolved or work around the denial with a token, shell API call, or write operation.
4. Work only on actionable findings verified against the current PR head. If a change is warranted, use the repository's authorized PR flow: a scoped `copilot/session-*` sub-PR to `0D_base_`, or direct work on the promotion PR only when that operation is explicitly authorized. Preserve reviews, checks, approval gates, and existing dirty work.
5. Re-run applicable checks on the final candidate SHA and update findings only with run-bound evidence.

## Evidence snapshot (2026-11-15; PR head `f6d4223cb94b255d1c6082deae761ce246255cfe`)

| Surface | Latest observed evidence on this SHA | Interpretation and limitation |
|---|---|---|
| Trivy / Security Scanning Suite | Run [43669524391](https://github.com/Aries-Serpent/_codex_/actions/runs/43669524391) completed successfully. Trivy matrix jobs for `.config/Dockerfile`, `docker/Dockerfile.cpu`, and `docker/Dockerfile.gpu` all succeeded. | A passing job does not prove that the GHAS code-scanning configuration warning or the supplied 14 alert records were cleared. Alert inventory access was denied. |
| CodeQL GA gate | Run [43669524413](https://github.com/Aries-Serpent/_codex_/actions/runs/43669524413) completed successfully; its log records gate status PASS, critical/high/medium counts 0, and dry-run false. | This is the repository CodeQL gate's result, not independent proof that every code-scanning configuration or alert in the supplied report is resolved. |
| Semgrep OSS | Run [43669524190](https://github.com/Aries-Serpent/_codex_/actions/runs/43669524190) completed successfully; the parser summary records zero critical, high, and informational findings. | Confirms that run's scan and policy summary only. Confirm its SHA and artifacts again after any changes. |
| Strict No-Deferral | Run [43669790036](https://github.com/Aries-Serpent/_codex_/actions/runs/43669790036) completed successfully on the same SHA. | The user's phrase “on: pull_request 2” is ambiguous. Resolve what “2” denotes before proposing any gate change. |

The user-supplied Trivy report described three missing GHAS configurations for `.github/workflows/container-scan.yml` (one for each Dockerfile) and 14 findings: **2 critical, 5 high, 7 medium**. The report listed:

- `chromadb` 1.5.9: CVE-2026-45829 (critical), CVE-2026-45833 (critical), CVE-2026-45830 (high), CVE-2026-45831 (high); no fixed version shown.
- `mcp` 1.29.0: CVE-2026-59951 (the annotation heading says High while its detail says Medium; detail lists 1.30.0 or 2.2.0 as fixed), plus CVE-2026-116684, CVE-2026-116685, and CVE-2026-116686 (reported medium; the report lists 1.30.0 or 2.2.0 as fixed).
- `sqlitedict` 2.1.0: CVE-2024-35515 (high), no fixed version shown.
- `oauthlib` 4.0.0: CVE-2026-49272 (high), reported fix 4.0.1.
- `diskcache` 5.6.3: CVE-2025-69872 (medium), no fixed version shown.
- `opentelemetry-api` 1.37.0 and 1.45.1: CVE-2026-114603 and CVE-2026-126360 (medium); the report lists 1.45.1 and 1.45.2 as respective fixes, with CVE-2026-126360 also reported against 1.45.1.

Treat that list as **user-provided evidence to revalidate**, not a current alert inventory. Existing `uv.lock` entries confirm some listed versions, but transitive reachability, enabled extras, fixed releases, and exact alert state require fresh evidence. In particular, `pyproject.toml` constrains one `opentelemetry-api` dependency below 1.38.0; understand that compatibility constraint before upgrading it.

## Plan order and handoffs

1. **Evidence refresh** — establish the exact PR head/base, check conclusions, scanner artifacts and alert inventory. If GitHub still denies alert access, report the exact denial and request an authorized security maintainer to provide the current inventory; proceed only with read-only checks that remain available.
2. **Trivy remediation** — execute [01 — Trivy and dependency advisories](01_trivy_and_dependency_advisories.md). Separate versioned fixes from advisories with no verified fix and from the GHAS configuration mismatch.
3. **Independent source scans** — execute [02 — CodeQL](02_codeql_alerts_and_coverage.md) and [03 — Semgrep OSS](03_semgrep_oss.md). Their latest gates passed, so do not make speculative scanner or source changes to manufacture work.
4. **Gate verification** — execute [04 — Strict No-Deferral](04_strict_no_deferral_gate.md). Keep this gate unchanged unless a current, reproducible finding identifies a defect in the gate itself.
5. **Final evidence** — bind every test, scan, alert disposition, and review to the same final SHA. Report unresolved findings with owner, mitigation, and the next authorized decision. A passing gate, numeric score, or plan completion is not merge clearance.

## Global execution constraints

- Do not lower severity thresholds, remove scan scope, disable workflows, bypass checks, or add broad suppressions to obtain a pass.
- Do not dismiss or close alerts without current finding-level evidence and the authorized security owner/reason.
- Do not change dependency versions based only on package-name matches. Verify current vendor/advisory details, dependency paths, runtime extras, and compatibility first.
- Keep independent, reviewable fixes small; update relevant tests/docs and run existing project checks.
- Do not dispatch or approve workflows, mutate PRs, merge, or deploy unless separately authorized.
- Preserve the pre-existing dirty `.codex/session_startup_packet.json` worktree edit; do not publish timestamp-only churn.
