# OFFLINE_TEST_COVERAGE_PLAN

Date: 2026-07-07
Source: lane4-tests (test-enhancement-agent)

## Objective

Raise deterministic offline test confidence for packaging profiles (`core`, `runtime`, `full`).

## Priority Matrix

| Area | core | runtime | full | Priority |
|---|---|---|---|---|
| Metadata/profile contract tests | ✅ | ✅ | ✅ | P0 |
| Offline install contract tests | ✅ | ✅ | ✅ | P0 |
| No-network enforcement tests | ✅ | ✅ | ✅ | P0 |
| Script syntax/flow tests | ✅ | ✅ | ✅ | P0 |
| Import contract +/-negative tests | ✅ | ✅ | ✅ | P1 |
| Upgrade/downgrade profile path tests | ⚪ | ✅ | ✅ | P2 |

## P0 Backlog

1. Add shell syntax checks for offline scripts.
2. Add profile offline install tests with explicit failure-path checks.
3. Add cross-file dependency consistency tests.
4. Add hard no-network assertions during offline validation.

## Execution

Use existing preflight pathway:
- `python scripts/ci/rvs_preflight.py --group quick --preview`
- `python scripts/ci/rvs_preflight.py --group quick --changed-only --workers 4`
- `python scripts/ci/rvs_preflight.py --group quick --workers 6 --batch-size 30`
