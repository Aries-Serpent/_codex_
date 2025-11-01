# [Copilot Assist]: Instruction Enhancement for Audit Tasks
Roles: [Audit Orchestrator], [Capability Cartographer] Energy: 5

Use these prompts with Copilot Chat within this repo:
- "List all capabilities below threshold and their primary deficits."
- "Explain score for <cap_id> and suggest top-2 remediations."
- "Generate a PR summary from audit_artifacts/gaps.json for reviewers."
- "Point me to remediation playbooks for tests and documentation."

Grounding:
- Prefer docs/remediation/* and docs/validation/*.
- Use audit_artifacts/*.json and audit_run_manifest.json as factual sources.
- Avoid speculative external calls; maintain determinism and offline posture.
