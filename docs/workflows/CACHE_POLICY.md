# Cache Policy — 4-Layer Hierarchy

> **Owner:** `cache-management-agent` (canonical) — supporting `workflow-optimization-agent`.
> **Status:** Specification (Phase 5; YAML rollout in Phase 5b).
> **Branch authored:** `copilot/analyze-test-coverage-and-documentation`
> **ADA citation:** [../../.codex/CODEBASE_AGENCY_POLICY.md](../../.codex/CODEBASE_AGENCY_POLICY.md)

## Why

User directive: *"we must improve workflow functions where we do not want to continue scans on files that have been retouched by more recent commits… save on bandwidth and leverage cache"* (recorded in repository memory `workflow optimization`). The current estate includes 285 workflow files under `.github/workflows/` (active workflows plus dispatch-only stubs) and can run duplicate scans on superseded SHAs, wasting CI minutes and Actions cache quota.

## The four layers

| Layer | Scope | Cache key | Expected retention* | Owner agent |
|---|---|---|---:|---|
| **L1: Toolchain** | Python interpreters, ruff, mypy, pre-commit binaries, actionlint | `runner.os + py-version + pyproject.toml hash` | 30 d | `cache-management-agent` |
| **L2: Dependencies** | pip/uv site-packages, npm `node_modules`, Cargo `target/` (rlib only) | `runner.os + requirements*.txt + uv.lock + package-lock.json + Cargo.lock` hash | 14 d | `cache-management-agent` |
| **L3: Tool-state** | `.mypy_cache/`, `.ruff_cache/`, `.pytest_cache/`, `.hypothesis/` | `runner.os + branch + paths-changed-since-base` | 7 d | `cache-management-agent` |
| **L4: Data/models** | DVC remote, HuggingFace model cache, datasets | `dvc.lock` hash + `models/manifest.json` hash | 30 d | `cache-management-agent` + DVC |

*GitHub Actions cache eviction is GitHub-managed (typically inactivity-based). Values above are target retention windows, not guaranteed TTLs.*

## Skip-rescan policy

Every scanning workflow (lint, security, coverage, doc-link-check, markdown-link-check, mypy) **must**:

1. Declare `concurrency` with `group: ${{ github.workflow }}-${{ github.ref }}` and `cancel-in-progress: true` for PR events.
2. Use a paths-filter step (e.g. `dorny/paths-filter@v3` or `tj-actions/changed-files@v45`) to short-circuit when the changed file set contains zero files in the workflow's scope.
3. On `push` to a superseded SHA (same ref, newer SHA exists): cancel via the concurrency group — no manual diff needed.
4. Never key caches on `${{ github.sha }}` directly; always on lockfile hashes plus a workflow-version segment (`v1`, `v2`, …) bumped only when the workflow's input contract changes.

## Workflow Execution Gate (single entry point)

To cut duplicate fan-out, a single front-gate workflow (`workflow-execution-gate.yml`, already present) must:

1. Resolve the changed-files set once (cached as an artifact).
2. Pre-check `workflow-compliance-guardian` (concurrency + timeout rules) and `ci-pattern-guardian` (forbid known anti-patterns).
3. Emit per-workflow `should-run: true|false` outputs; downstream workflows read this output instead of re-computing.

## Verification

- `actionlint` after each workflow YAML edit.
- A scheduled `cache-management-agent` job audits hit/miss rates weekly and reports to `docs/workflows/MONITORING_LOG.md`.

## Phase 5b rollout sequence (deferred to follow-up PR)

1. Add `concurrency` + `cancel-in-progress` to the 70+ workflows that lack it.
2. Add `paths-filter` to lint/security/doc/coverage workflows.
3. Migrate cache keys to lockfile-hash + version segment.
4. Wire downstream workflows to read `workflow-execution-gate.yml` outputs.
5. Bump cache-key version segment when contract changes (no purge needed; old keys are evicted by GitHub cache policy over time).

This file is the contract; the YAML diff lands in Phase 5b under `workflow-management-agent`.
