# [Change Plan]: MSP Capability-Audit — File/Folder Tree and Scope
Roles: [Audit Orchestrator], [Capability Cartographer] Energy: 5

Note: This tree lists all files to create/update/refactor to close identified gaps:
- Missing required_patterns highlighting
- No component-level gap artifact
- Missing-detector gate
- Low-threshold hard fail + PR summary text
- Deterministic “(ZERO)” emphasis in matrix
- Remediation playbooks and validation scripts
- CI workflow with 90-day artifact retention and baseline bootstrap

Legend: [NEW] create | [UPDATE] modify | [REFACTOR] structural/logic change
```text
Repository-root
├─ .copilot-space/
│  └─ [UPDATE] workflow.yaml
├─ .github/
│  ├─ workflows/
│  │  └─ [NEW] capability-audit.yml
│  └─ docs/
│     └─ [NEW] Copilot_Audit_InstructionEnhancement.md
├─ scripts/
│  └─ space_traversal/
│     ├─ [UPDATE] audit_runner.py
│     ├─ [NEW] validators.py
│     └─ detectors/
│        └─ (no change; optional new detectors as needed)
├─ templates/
│  └─ audit/
│     └─ [UPDATE] capability_matrix.md.j2
├─ audit_artifacts/ (runtime outputs; not committed)
│  ├─ [UPDATE] gaps.json (extended schema)
│  ├─ [NEW] component_gaps.json
│  └─ capabilities_*.json (existing)
├─ reports/
│  └─ [UPDATE] capability_matrix_<ts>.md (rendered with missing_patterns and ZERO markers)
├─ docs/
│  ├─ remediation/
│  │  ├─ [NEW] README.md
│  │  ├─ [NEW] components.md
│  │  ├─ [NEW] detectors.md
│  │  └─ [NEW] policy.md
│  ├─ validation/
│  │  └─ [NEW] Gaps_Coverage_Checklist_And_Scripts.md
│  └─ changes/
│     ├─ [NEW] MSP_Capability_Audit_Changeplan_Tree.md (this file)
│     └─ [NEW] MSP_Capability_Audit_File_Map.md
├─ [UPDATE] space.mk
└─ [UPDATE] audit_run_manifest.json (runtime) — now includes missing_detectors in metadata
```text
Scope alignment with your selections:
- Baseline: artifact-based with first-run bootstrap
- Gating: hard-fail on low maturity AND generate PR summary text; fail on missing-detector
- Retention: 90 days; Thresholds: low=0.70, medium=0.85
- Remediation guidance: docs/remediation/* linked from matrix

*End of Tree*
