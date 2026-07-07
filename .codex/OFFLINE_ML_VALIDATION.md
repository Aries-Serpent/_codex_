# OFFLINE_ML_VALIDATION

Date: 2026-07-07
Source: lane4-ml (ml-validation-suite-agent)

## Readiness Summary

| Profile | Install Readiness | Validation Readiness | Status |
|---|---|---|---|
| core | Good | Core/offline checks align | ✅ Ready |
| runtime | Partial | ML checks exist but profile-gated offline matrix missing | ⚠️ Partial |
| full | Partial | Broad surface, no dedicated offline CI profile gate | ⚠️ Partial/High-risk |

## Gaps

1. No profile-specific offline CI matrix (`core/runtime/full`).
2. Offline bootstrap path not fully profile-aware in one-step flow.
3. Optional/skip-heavy paths reduce confidence for runtime/full in baseline runs.

## Recommended Test Matrix

- Offline install for each profile via wheelhouse (`--no-index`).
- Profile-specific import smoke tests.
- Meta-tensor safety checks (no `meta` params after load).
- Tokenization roundtrip checks.
- Batch preflight using existing `scripts/ci/rvs_preflight.py` workflows.

## Go/No-Go

- GO core: offline install + core imports + bootstrap checks pass.
- GO runtime/full: core criteria + model/meta/tokenization checks pass.
- NO-GO: any offline resolver/network dependency or meta-tensor regression.
