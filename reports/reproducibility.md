# Reproducibility Checklist — Run 1 (2025-09-22)

| Item | Status | Notes |
| --- | --- | --- |
| Seed management | ✅ Documented in existing tests (`tests/test_repro_*`), but audit docs lacked reference. Added reminder to keep checklist in sync. |
| Environment capture | ✅ Prompt + validation doc now call for interpreter metadata and deterministic env vars (`PYTHONHASHSEED`). |
| Data/versioning | ✅ Dataset manifests with checksum tests under `tests/data/`. |
| Configuration tracking | ⚠️ Partial — Hydra configs are versioned, but audit prompt lacked explicit steps for logging overrides. |
| Artifact logging | ✅ Offline telemetry/logging modules persist metrics locally; no remote dependencies required. |
| Execution determinism | ✅ `scripts/codex_local_audit.sh` documents a rerun command that bootstraps the deterministic workflow. |

## Immediate Follow-Ups

- Back `scripts/codex-audit` with a lightweight Python entrypoint to avoid manual package installs.
- Evaluate whether the audit workflow should emit a lightweight run manifest (possible future Menu 8 task).
