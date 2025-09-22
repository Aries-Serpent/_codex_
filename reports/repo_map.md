# Repo Map — 2025-09-22

## Top-Level Layout

| Path | Purpose | Notes |
| --- | --- | --- |
| `src/` | Primary Python packages (`codex`, `codex_ml`, utilities) | Rich training, evaluation, registry, and tooling modules. |
| `tests/` | Extensive offline regression suite | Covers tokenizers, trainers, logging, telemetry, and CLI pathways. |
| `tools/` | Automation, maintenance, and safety scripts | Includes patch runners, offline audits, packaging, and CI guards. |
| `configs/` | Hydra-compatible configuration bundles | Supports training/eval presets and offline catalogue defaults. |
| `requirements*/` | Dependency pins for runtime, dev, and optional toolchains | Multiple lock files for pip/uv driven workflows. |
| `docs/` & `documentation/` | Guides, runbooks, onboarding materials | Mix of structured guides, prompts, and experiment notes. |
| `services/` | Operational scaffolding (e.g., ITA service) | Contains service-level READMEs and docker assets. |
| `monitoring/`, `ops/`, `analysis/` | Observability, operations, and analytical artefacts | Provide dashboards, ops runbooks, and derived study notes. |
| `artifacts/`, `.codex/`, `logs/` | Generated status outputs and historical archives | Large backlog of status updates with inconsistent fence formatting. |
| `Makefile`, `codex.mk`, `noxfile.py` | Entry points for local automation | Orchestrate tasks like `nox -s tests`, packaging, and gating. |
| `Dockerfile`, `deploy/`, `docker-compose.yml` | Containerization and deployment recipes | Offline-friendly base images and compose stacks. |
| `notebooks/`, `examples/`, `experiments/` | Exploratory assets | Prototype notebooks and scenario walkthroughs. |

## High-Signal Mapping Notes

- Historical `.codex/` archives predate current fence discipline; exclude them from new audits to avoid noise.
- Multiple automation entry points in `tools/` overlap (e.g., `audit_runner.py`, `offline_repo_auditor.py`); consolidate usage guidance in future runs.
- Tests already exercise most ML capabilities; prioritise syncing new reports with existing fixtures to stay aligned with regressions.

## Quick Wins Identified

1. Stand up a curated `reports/` tree for ongoing audits (this run).
2. Refresh `AUDIT_PROMPT.md` to reflect current offline workflow expectations.
3. Wire a Markdown fence gate into `pre-commit` to stop regression of the new discipline.
