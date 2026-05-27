# Reproducibility Checklist — Run 1 (2025-09-22)

| Item | Status | Notes |
| --- | --- | --- |
| Seed management | ✅ Documented in existing tests (`tests/test_repro_*`), but audit docs lacked reference. Added reminder to keep checklist in sync. |
| Environment capture | ✅ Prompt + validation doc now call for interpreter metadata and deterministic env vars (`PYTHONHASHSEED`). |
| Data/versioning | ✅ Dataset manifests with checksum tests under `tests/data/`. |
| Configuration tracking | ✅ Hydra configs are versioned; override logging enabled via `hydra.run.dir` and `hydra.sweep.dir` with `${now:%Y-%m-%d_%H-%M-%S}` timestamped output dirs. All overrides are captured in `.hydra/overrides.yaml` and `.hydra/config.yaml` at experiment runtime. Audit prompt updated to require override log verification. |
| Artifact logging | ✅ Offline telemetry/logging modules persist metrics locally; no remote dependencies required. |
| Execution determinism | ✅ `scripts/codex_local_audit.sh` documents a rerun command that bootstraps the deterministic workflow. |

## Immediate Follow-Ups

- Back `scripts/codex-audit` with a lightweight Python entrypoint to avoid manual package installs.
- Evaluate whether the audit workflow should emit a lightweight run manifest (possible future Menu 8 task).
