# MASTER_REMEDIATION_PLAN.md

- Generated: 2026-06-05T05:16:00Z
- Scope: Security Scanning Suite run `26992144518`

## Consolidated Findings

| Tool | Findings | Priority focus |
|---|---:|---|
| CodeQL Python | 107 | Sensitive logging/storage + uninitialized locals |
| Semgrep | 88 | Credential logging, pickle usage, dynamic URL handling |
| pip-audit | 2 | Unpatched transitive deserialization CVEs |
| SBOM | 338 components | Supply-chain drift and vulnerable component tracking |
| detect-secrets | 667 files flagged | True-positive triage and baseline hygiene | <!-- pragma: allowlist secret -->

## Phased Rollout (T+0 to T+30)

### T+0 (Immediate)
- Patch high-risk secret logging/storage findings in active runtime paths (`src/security/*`, token/credential handling scripts).
- Add guardrails against unsafe deserialization and dynamic URL misuse in production paths.
- Confirm no true plaintext credentials in active source files.

### T+1 to T+7 (Stabilization)
- Batch-fix medium issues (`py/log-injection`, semgrep subprocess/exec hotspots).
- Resolve CodeQL uninitialized-local-variable findings for high-churn modules first.
- Add/extend targeted tests for remediated modules.

### T+8 to T+30 (Hardening)
- Address low-severity correctness/quality findings in batches.
- Implement SBOM drift policy checks and dependency lifecycle tracking for unpatched CVEs.
- Complete full secret-baseline triage and reduce noisy false-positive buckets.

## Execution Backlog

- [ ] Execute code fixes for HIGH findings (CodeQL + Semgrep)
- [ ] Add tests for each remediated security hotspot
- [ ] Re-run `security-scanning-suite.yml` and compare deltas
- [ ] Remove pip-audit ignores once upstream patched versions are released
- [ ] Update `.codex/SECURITY_FINDINGS_LOG.md` with closure evidence

## Linked Detailed Plans

- `remediation_plan_codeql_python.md`
- `remediation_plan_pip_audit.md`
- `remediation_plan_semgrep.md`
- `remediation_plan_sbom.md`
- `remediation_plan_secrets.md`
