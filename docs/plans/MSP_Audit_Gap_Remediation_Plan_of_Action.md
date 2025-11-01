# MSP Audit Gap Remediation — Plan of Action
Roles: [Audit Orchestrator], [Capability Cartographer] Energy: 5

## Objectives
- Surface missing required patterns directly in scored artifacts and reports.
- Enforce low-maturity and missing-detector gates across local + CI workflows.
- Provide remediation playbooks and validation scripts for follow-through teams.

## Approved Implementation Snapshot
| Pillar | Status | Evidence |
|--------|--------|----------|
| Policy Gates | ✅ Enabled via `.copilot-space/workflow.yaml` and `audit_runner validate` | See docs/remediation/policy.md |
| Reporting | ✅ Matrix shows missing patterns and ZERO markers | templates/audit/capability_matrix.md.j2 |
| Remediation Enablement | ✅ Docs available under `docs/remediation/` | docs/remediation/README.md |
| Validation | ✅ Checklist and scripts published | docs/validation/Gaps_Coverage_Checklist_And_Scripts.md |
| CI Automation | ✅ Workflow `capability-audit.yml` bootstrapped | .github/workflows/capability-audit.yml |

## Follow-up Links
- Component gaps artifact: `audit_artifacts/component_gaps.json`
- Manifest snapshot (with thresholds + missing_detectors): `audit_run_manifest.json`
- Copilot instructions for audit context: `.github/docs/Copilot_Audit_InstructionEnhancement.md`

## Next Review
Re-evaluate thresholds and regression delta after two full audit cycles or if detector inventory changes materially.
