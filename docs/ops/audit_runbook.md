# Ops: Audit Runbook (v1.2)
> Generated: 2025-11-02 15:42:47 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Audit Lead], [Secondary: CI Maintainer] ⚡ Energy: 5

Purpose
- End-to-end steps to produce and verify audit integrity artifacts referenced in Status 2.8.

Steps
| Step | Command | Output | Notes |
|---|---|---|---|
| Context Index | python scripts/audit/gen_context_index.py | audit_artifacts/context_index.json | File listing with sha256 |
| Facets | python scripts/audit/gen_facets.py | audit_artifacts/facets.json | Domain groupings |
| Capability Discovery | python tools/capability_autodiscover.py | audit_artifacts/capabilities_raw.json | Evidence-based suggestions |
| Capability Scoring | python tools/capability_score.py | audit_artifacts/capabilities_scored.json | Normalized weights |
| Gaps Analysis | python tools/gaps_analyze.py | audit_artifacts/gaps.json | Low-maturity/high-risk flags |
| Integrity Chain | python scripts/audit/build_integrity_chain.py | audit_run_manifest.json | Root manifest with hashes |
| Verify | bash scripts/audit/verify_integrity_chain.sh | exit 0 on success | Re-hash and compare |

Reporting
- Record SHA256 and timestamps in Status section 2.8 (Audit Integrity Chain).
- Attach manifest and artifacts as workflow artifacts for traceability.
