# [How-to]: Run the Deterministic Audit on 0D_base_
> Generated: 2025-10-10 01:27:43 UTC | Author: mbaetiong
Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5

Purpose
- Produce canonical, hash-stamped maturity artifacts (S1–S7) for branch 0D_base_.

Prereqs
- Python 3.10+ environment; install pyyaml and jinja2 for rendering:
  - pip install pyyaml jinja2

Commands
- Full pipeline (S1–S7)
  - python scripts/space_traversal/audit_runner.py run
- Fast path (S1, S3, S4, S6)
  - make space-audit-fast
- Explain a capability’s score
  - python scripts/space_traversal/audit_runner.py explain checkpointing
- Diff two runs
  - python scripts/space_traversal/audit_runner.py diff --old <old.json|md> --new <new.json|md>

Outputs (deterministic)
- audit_artifacts/context_index.json (S1)
- audit_artifacts/facets.json (S2)
- audit_artifacts/capabilities_raw.json (S3)
- audit_artifacts/capabilities_scored.json (S4)
- audit_artifacts/gaps.json (S5)
- reports/capability_matrix_<timestamp>.md (S6)
- audit_run_manifest.json (S7)

Determinism guard
- Run twice unchanged; expect identical repo_root_sha and identical capabilities_scored.json (ignoring timestamp fields). On mismatch, audit detectors for ordering or file filters.

Quality gates (optional)
- Configure low threshold and regression delta in .copilot-space/workflow.yaml.
- Use “diff” exit codes to fail builds on score regression if enabled.

Notes
- The pipeline is offline-first; no network calls are made.
- Template_hash is embedded in the matrix for tamper detection.

*End of Runbook*
