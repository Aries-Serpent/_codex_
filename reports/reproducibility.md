# Reproducibility Checklist — Run 1 (2025-09-22)

| Item | Status | Notes |
| --- | --- | --- |
| Seed management | ✅ Documented in existing tests (`tests/test_repro_*`), but audit docs lacked reference. Added reminder to keep checklist in sync. |
| Environment capture | ⚠️ Partial — `requirements-dev.txt` and lock files exist, yet audit prompt did not instruct contributors to record interpreter info. |
| Data/versioning | ✅ Dataset manifests with checksum tests under `tests/data/`. |
| Configuration tracking | ⚠️ Partial — Hydra configs are versioned, but audit prompt lacked explicit steps for logging overrides. |
| Artifact logging | ✅ Offline telemetry/logging modules persist metrics locally; no remote dependencies required. |
| Execution determinism | ⚠️ Pending — There are regression tests, but the new audit workflow still needs a documented “rerun command” template. |

## Immediate Follow-Ups

- Add explicit instructions in the refreshed `AUDIT_PROMPT.md` for capturing environment metadata and Hydra override snapshots.
- Evaluate whether the audit workflow should emit a lightweight run manifest (possible future Menu 8 task).
