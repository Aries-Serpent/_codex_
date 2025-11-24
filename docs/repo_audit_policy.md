# Repo Audit Policy Integration (Track D)

This repository ships an offline-first audit workflow that maps the `repo_audit_policy_codex` requirements to concrete gates and prompts.

## RA Policy (RA-1 to RA-5)
- **RA-1**: No fabrication — all statements must be grounded in repository evidence.
- **RA-2**: Label clarity — responses must specify verified, inferred, or planned content.
- **RA-3**: Tool traceability — include the command or tool that produced each artifact.
- **RA-4**: Scope-constrained mutation — only touch in-scope files with reversible steps.
- **RA-5**: YAML/CI safety — infrastructure edits stay deterministic and offline.

Policy mapping is generated with `codex_audit.policy.write_policy_mapping`, which writes `artifacts/ra_policy_map.json` with capability and track coverage.

## Local Gates & Scorecards
- **Gate runner**: `codex_audit.gates.run_gates` evaluates local-only gates (tokenization, training, security, deployment, docs, offline posture) and stores results in `artifacts/gate_results.json`.
- **Scorecard**: `codex_audit.scorecard.render_scorecard` renders `artifacts/repo_audit_scorecard.md` and threads RA references into the summary.
- All gates execute offline; no network calls are issued.

## Prompt and Error Wiring
- **Error records**: `codex_audit.errors.ErrorRecord` now carries `ra_references` so failures cite the relevant RA policies. Records are stored in JSON and Markdown under `audit_artifacts/error_captures/`.
- **Status prompt**: `prompts/repo_status_update_for_codex.md` is filled by `scripts/prepare_repo_status_prompt.py`, producing `artifacts/repo_status_update_prompt.txt` that includes RA links, gate results, and a scorecard pointer.

## Workflow Hooks
- The audit orchestrator (`tools/codex_audit_orchestrator.py`) now:
  - Emits the RA policy map and gate results during phase 2.
  - Generates the scorecard and Codex-ready status prompt during phase 6.
- All steps remain offline and reversible; artifacts live under `artifacts/` or `audit_artifacts/` for traceability.
