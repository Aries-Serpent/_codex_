# Guide: Audit Integrity Chain (v1.2)
> Generated: 2024-11-02 15:08:30 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Audit Lead], [Secondary: Release Auditor] ⚡ Energy: 5

Artifacts
| File | Description |
|---|---|
| audit_artifacts/context_index.json | Enumerated file listing |
| audit_artifacts/facets.json | Domain clustering of files |
| audit_artifacts/capabilities_raw.json | Autodiscovery candidates |
| audit_artifacts/capabilities_scored.json | Scored capability matrix |
| audit_artifacts/gaps.json | Low maturity items and rationale |
| audit_run_manifest.json | Integrity root with hashes |

Procedure
1) Run: python scripts/audit/build_integrity_chain.py
2) Record SHA256 hashes and timestamps in report section 2.8
3) Upload artifacts in CI
4) Verify by re-hashing locally; discrepancies trigger investigation
