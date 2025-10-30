# Deployment Dry-Run — codex-reasoning-pod

## Overview
- Kind: ReasoningPod
- Version: 0
- Image: local/offline/codex:latest
- Config: `configs/deploy/reasoning_pod.yaml`

## Resources
- cpu: 2
- memory: 8Gi

## Reasoning Knobs
- Trace capture mode: weights
- Evaluation preset: configs/evaluation/reasoning/base.yaml
- Curriculum template: configs/training/reasoning/baseline.yaml

## Artifact Targets
- Markdown: docs/status_updates/deploy_dry_run.md
- JSON: docs/status_updates/deploy_dry_run.json

## Notes
- This config is safe to commit; it does not perform deployment or network I/O.
- Use Python local tools to generate review artifacts for promotion gates.
