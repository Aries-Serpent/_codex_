<!--
PR Template — Archive & Hygiene Policy
This template guides PR authors to provide the evidence and governance signals enforced by CI.
-->

## Summary
Describe what is being archived/modified and why. Link to ADR and any related issues.

## ADR
- [ ] ADR added and linked: `docs/arch/adr-YYYYMMDD-<slug>.md`

## Evidence
- [ ] Evidence lines appended to `.codex/evidence/archive_ops.jsonl` (append-only)
  - Each new JSON line includes: `id`, `path`, `sha256`, `removed_by`, `when`, `adr`, `reason`, `provenance`
- [ ] Tombstone stubs added that reference the above `id` and digest(s)
- [ ] Provenance attestation(s) attached and referenced (SLSA/in-toto): `attestations/<id>.intoto.jsonl`

## SBOM / Reverse Dependency
- [ ] SBOM check executed: `scripts/sbom/check.sh`
  - Outputs under `.codex/sbom/` (e.g., `sbom.cdx.json`, `pip-audit.json`, `npm-ls.json`)
  - Notable consumers/risks:

## CHANGELOG
- [ ] Updated `CHANGELOG.md` (Deprecated/Removed sections)

## CODEOWNERS & Reviews
- [ ] CODEOWNERS auto-requested (see PR Reviewers panel)
- [ ] Required approvals present

## Commits
- [ ] Conventional Commits used (e.g., `deprecate:`, `refactor:`)
- [ ] `BREAKING CHANGE:` trailer provided **if** there are API removals

## Risk & Mitigation
- Impact summary:
- Migration plan / deprecation window:
- Rollout / fallback:

## Testing
- [ ] Unit/integration tests updated or removed where applicable
- How to verify:

## Notes
- Planner/summary artifacts (if generated): `.codex/reports/plan-*.json`, `.codex/reports/summary-*.json`
- Any exceptions/rescues tracked with owners:

---

### Checklist (CI mirrors)
- [ ] Evidence JSON lines valid (CI enforces append-only & required keys)
- [ ] SBOM check script executed (non-blocking unless `STRICT_SBOM=1`)
- [ ] CHANGELOG updated (warning if omitted)
- [ ] CODEOWNERS file present (branch protection enforces approvals)

<!-- End of template -->
