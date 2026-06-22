# Reasoning Pod: Dry-Run Deployment Guide

**Last Updated:** 2026-06-22

This guide defines the **dry-run** flow for a reasoning pod. All steps are **local-first** and **offline-friendly**.

## Objectives
- Validate manifests and resource expectations without contacting hosted services.
- Produce artifacts (MD + JSON) suitable for PR review and promotion gates.

## Control Surface (Knobs)
- **Curriculum phases**: `configs/training/reasoning/curricula/*`
- **Trace capture mode**: `trace_capture.mode ∈ {weights, activations}` (see `configs/training/reasoning/baseline.yaml`)
- **Evaluation presets**: `configs/evaluation/reasoning/*`
- **Deployment preset**: `configs/deploy/reasoning_pod.yaml`

> Formalism (signal tracking): let **R** be reasoning-readiness and **A** be artifact completeness.
> We model readiness heuristic as: **R = α·E + β·T + γ·D**, where E=evaluation pass ratio, T=trace coverage, D=deployment dry-run parity.
> Choose α,β,γ per your milestone; ensure **R ≥ R_min** before promotion.

## Dry-Run Steps
1) **Repo Map (Reasoning)**
   ```bash
   codex repo-map --reasoning > docs/status_updates/repo_map_reasoning.txt
   ```

2) **Status Report (Artifacts)**
   ```bash
   python tools/status_report.py \
     --emit-md docs/status_updates/status_report.md \
     --emit-json docs/status_updates/status_report.json
   ```

3) **Compose Deployment (Dry-Run)**
   ```bash
   python tools/selection_report.py --config configs/deploy/reasoning_pod.yaml \
     --dry-run \
     --emit-md docs/status_updates/deploy_dry_run.md \
     --emit-json docs/status_updates/deploy_dry_run.json
   ```

4) **Link in PR**
   Include the above artifacts in your promotion PR.

## Promotion Checklist (excerpt)
- [ ] Status report (MD+JSON) attached.
- [ ] Dry-run deploy artifacts (MD+JSON) attached.
- [ ] Trace capture mode documented (`weights` or `activations`).
- [ ] Evaluation preset recorded (e.g., `configs/evaluation/reasoning/base.yaml`).

## Notes
- This flow intentionally avoids CI and remote deployment to remain offline-first.
- For actual hosting, adapt these manifests to your environment (k8s, container runtime, etc.), preserving the artifact trail.
