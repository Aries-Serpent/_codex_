# [Tasks]: Codex-Ready Remediation Sequences  
> Generated: 2025-12-06 04:45:00Z | Author: Comprehensive Audit System  
> 🧠 Roles: [Audit Orchestrator], [Capability Cartographer] ⚡ Energy: 5

## T1: Coverage Gate Enforcement
- Change: Add `--cov-fail-under=70` in `noxfile.py` tests session.
- Steps:
  - Edit tests session; ensure `pytest-cov` in dev requirements.
  - Run `nox -s tests`.
- Acceptance:
  - Coverage >= 70; no failures introduced.

## T2: W&B Offline Default
- Change: Set `WANDB_MODE=offline` by default in `sitecustomize.py`.
- Steps:
  - Add env default guard for `WANDB_MODE`.
  - Validate in `docs/logging/logging_guide.md`.
- Acceptance:
  - Env var default present; online mode requires explicit opt-in.

## T3: EarlyStopping Integration
- Change: Append `EarlyStoppingCallback(patience=3)` when eval dataset exists.
- Steps:
  - Modify HF trainer init; ensure no duplicate callback insertion.
  - Add unit test for early stop behavior.
- Acceptance:
  - Callback creation logged; early stop triggers when plateau.

## T4: Strict Resume RNG
- Change: Add `--strict-resume` in `cli/train_codex.py`.
- Steps:
  - Validate RNG sidecar presence; raise on missing.
  - Update docs and tests.
- Acceptance:
  - Resume without `.rng.json` fails with clear message.

## T5: Prompt Sanitize Default
- Change: Default `--sanitize` to True in inference CLI.
- Steps:
  - Wire policy hooks; expand sanitization rules.
  - Add tests; update SECURITY doc.
- Acceptance:
  - Injection tokens sanitized; safe behavior documented.

## T6: Dataset Hash Manifest
- Change: Compute SHA256 for `data/` files and embed in reproducibility manifest.
- Steps:
  - Implement hash pipeline under `codex_ml/utils/repro.py`.
  - Render manifest sidecar with training runs.
- Acceptance:
  - Deterministic reruns; dataset hashes logged.

## T7: Health/Readiness Probes
- Change: Add `/health` and `/ready` endpoints to all services.
- Steps:
  - Create health check module.
  - Wire into FastAPI/serve endpoints.
  - Add Docker health check configuration.
- Acceptance:
  - All services respond to health checks; K8s probes configurable.

## T8: Prometheus Metrics Export
- Change: Add Prometheus/OTel exporters for metrics.
- Steps:
  - Implement metrics exporters.
  - Add `/metrics` endpoint.
  - Wire training/serving metrics.
- Acceptance:
  - Prometheus can scrape metrics; dashboards functional.

## T9: Security Scans in CI
- Change: Wire bandit, pip-audit, detect-secrets into CI pipeline.
- Steps:
  - Add CI workflow steps.
  - Configure fail-fast on Critical/High findings.
  - Generate security reports.
- Acceptance:
  - CI fails on security vulnerabilities; reports published.

## T10: SBOM Generation
- Change: Generate SBOM for containers and Python environments.
- Steps:
  - Add `--sbom` to Docker builds.
  - Generate Python SBOM with tooling.
  - Store artifacts.
- Acceptance:
  - SBOM artifacts generated and stored with releases.

*End of Tasks*
