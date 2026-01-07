# Ops: Promotion Checklist (0D_base_ → main)
> Generated: 2024-11-11 07:55:43 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Release Manager], [Secondary: Auditor] ⚡ Energy: 5/5  
⚛️ Physics: Path🛤️ [Ring → Verify → Promote] Fields🔄 [nox, artifacts] Patterns👁️ [Determinism, Offline] Redundancy🔀 [Hash chain] Balance⚖️ [Safety vs. velocity]

## Preconditions
- nox -s tests lint typecheck docs_build validate-configs security
- Evaluate with `codex-eval run` and produce NDJSON + JSON summary.
- Audit traversal updated; artifacts committed:
  - audit_artifacts/capabilities_raw.json
  - audit_artifacts/capabilities_scored.json
  - audit_artifacts/context_index.json
  - audit_run_manifest.json
  - artifacts/security_report.json

## Scope & Risk
- Additive changes; offline-first maintained.
- Training/evaluation/registry wired; best‑k pruning implemented atomically.

## Post-Merge Tasks
- Generate daily report; link artifacts.
- Schedule coverage push (96–99%) per Copilot prompt.

— End —