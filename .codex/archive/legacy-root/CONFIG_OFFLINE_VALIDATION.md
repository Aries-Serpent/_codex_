# CONFIG_OFFLINE_VALIDATION

Date: 2026-07-07
Source: lane2-packaging (packaging-validation-agent)

## Executive Score

Overall external packaging readiness: **NO-GO (4.5/10)** until lock/profile and offline flow issues are fixed.

**Clarification:** campaign artifact delivery can be complete while release readiness remains NO-GO; this document tracks distribution gate status, not report-generation progress.

## Key Configuration Findings

| Area | Status | Notes |
|---|---|---|
| PEP 621 metadata | Mostly ready | project metadata present and structured |
| `core/runtime/full` profile model | Drifted | profile definitions exist but lock/extras alignment is inconsistent |
| Reproducibility | Partial | `uv.lock` is strong; exported requirements are `--no-hashes` |
| Offline bootstrap | Partial | offline flow exists but includes potentially online tool-upgrade step |
| Runtime profile weight claims | Drift risk | documented lightweight profile conflicts with heavy transitive ML stack |

## P0 Actions

1. Re-lock to align `uv.lock` with current profile definitions.
2. Produce release-grade hash-verified dependency manifests.
3. Harden offline bootstrap to avoid unconditional network-sensitive upgrades.

## P1 Actions

4. Fix unresolved script/entrypoint target mismatches.
5. Reconcile runtime size claims with actual dependency footprint.
6. Align OS support messaging with lock marker realities.
