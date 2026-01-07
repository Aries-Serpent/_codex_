# Guide: Copilot Instruction Enhancements (v1.2)
> Generated: Previous Cycle-11-02 15:05:03 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Instruction Curator], [Secondary: Workflow Orchestrator] ⚡ Energy: 5

Purpose
- Align Copilot interactions with repository-specific practices for status v1.2.
- Standardize prompts, outputs, and validation coupling for repeatable automation.

Prompt Patterns (use verbatim or adapt minimally)
- Generate Status JSON skeleton:
  - "Create a v1.2 status report JSON for branch 0D_base_ with metadata.git_context and metadata.environment populated; leave snapshot/patches/automation empty."
- Validate hydra configs:
  - "Run: python tools/validate_configs.py --root configs/training --schema configs/schemas/training.schema.yaml"
- Validate a data+schema pair:
  - "Run: python tools/schema_validate.py --data <path> --schema <path>"
- Build audit chain:
  - "Run: python scripts/audit/build_integrity_chain.py and attach audit_run_manifest.json as an artifact"

Output Conventions
- Files first, no chat prose
- Markdown files:
  - Header line: "# [Type]: [Topic]"
  - Metadata line: "> Generated: [UTC ISO] | Author: [login]"
  - Roles/Energy line: "🧠 Roles: [Primary, Secondary] ⚡ Energy: [1–5]"
- Tables for checklists, matrices, and coverage

Automation Hooks Table
| Action | Entry Point | Artifact(s) | Success Criteria |
|---|---|---|---|
| Status skeleton | tools/status_report.py | reports/daily/YYYY-MM-DD.json | File created with template_version v1.2 |
| Status schema test | tests/status/test_example_report_schema.py | Test log | Passes validation |
| Config validation | tools/validate_configs.py | CLI output | No FAIL lines |
| Ad-hoc schema | tools/schema_validate.py | PASS/FAIL | Exit code 0 |
| Audit chain | scripts/audit/build_integrity_chain.py | audit_run_manifest.json | Manifest written |

DoD for Copilot-led PRs
- Status example JSON validates in CI
- Configs validated or explicitly skipped with rationale
- Security gates run and artifacts uploaded
- References to CAP-/FIND-/PATCH-/REPRO- IDs are consistent
