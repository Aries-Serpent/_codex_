## Summary
Promotion readiness with offline-first artifacts and knobs.

## Readiness Checklist (attach links or paths)
- [ ] **Status Report (MD + JSON)**:
  - MD: `docs/status_updates/status_report.md`
  - JSON: `docs/status_updates/status_report.json`
- [ ] **Dry-Run Deploy (MD + JSON)**:
  - MD: `docs/status_updates/deploy_dry_run.md`
  - JSON: `docs/status_updates/deploy_dry_run.json`
- [ ] **Repo Map (Reasoning)**: `docs/status_updates/repo_map_reasoning.txt`
- [ ] **Trace Capture Mode**: `weights` or `activations` (record rationale)
- [ ] **Evaluation Preset**: e.g., `configs/evaluation/reasoning/base.yaml`
- [ ] Docs updated (`docs/README_ROOT.md`, `docs/deployment/reasoning_pod.md`)

## Notes for Reviewers
- This PR aligns the repo with a future “control surface” UI: curriculum phases,
  trace-capture mode, evaluation presets, and deployment presets are documented and togglable.
