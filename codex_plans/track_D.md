# Codex Implementation Plan: Track D (Repo Audit Policy Integration)

This plan outlines tasks to integrate repository audit policies into the Codex workflow.

- **Policy-to-Capability Map**: Normalize the `repo_audit_policy_codex` into RA-1 to RA-5 guidelines (no fabrication, verified/inferred/planned labels, tool traceability, scope-constrained mutation, YAML/CI safety). Implement a mapping layer connecting these RA rules to the diff/refinement tracks A-F and to specific capabilities in the repository.

- **Local Gates & Scorecards**: Define a `GATE-*` taxonomy for tokenization, training, security, deployment, etc. Implement a local gate runner (`codex_audit.gates.run_gates`) that produces `artifacts/gate_results.json`. Create a scorecard renderer (`codex_audit.scorecard.render_scorecard`) that summarizes gate results into `artifacts/repo_audit_scorecard.md`. Wire gate execution into the workflow phases and offline gating.

- **Prompt and Error Wiring**: Extend error capture structures (`ErrorRecord`) to include RA policy references. Create repository status prompt templates (e.g., `prompts/repo_status_update_for_codex.md`) and scripts (`scripts/prepare_repo_status_prompt.py`) to generate ready-to-paste status updates for Codex after each audit cycle. Ensure prompts include RA links and gate results for transparency.

- **Tests and Documentation**: Add offline tests under `tests/repo_audit` verifying policy mapping, gate execution, scorecard generation, and prompt preparation. Update documentation to describe RA integration, gating, and audit procedures.

All tasks must execute offline with no network calls. Provide clear rollback instructions for each new module.
