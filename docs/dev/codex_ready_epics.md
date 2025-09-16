# Codex-Ready Epics & Minimal PR Plan

## Overview

This roadmap translates the near-term tokenization, training, and deterministic
splitting initiatives into Codex-ready epics. Each epic enumerates owners,
acceptance criteria, checklists, risks, tests, documentation deliverables, and
rollback guidance. An atomic PR plan accompanies every epic to encourage small,
reviewable diffs and early value delivery. All work should rely on local-only
validation; do **not** enable external or cost-incurring CI services.

---

## Epic 1 — Tokenization Pipeline

### Why

Establish a repeatable, configurable tokenizer workflow with CLI exposure,
training manifest management, and regression tests. The goal is to guarantee
consistent preprocessing, provenance, and cache integrity across development
environments.

### Owner(s)

- Owner: **ML Core**
- Co-owner: **DevEx**
- Reviewers: **QA**, **Security** (policy/glossary)
- Docs: **DX/Docs**

### Acceptance Criteria

1. Ship `configs/tokenization/base.yaml` with defaults covering dataset paths,
   cache directories, text normalizer options, vocabulary size, special tokens,
   and tokenizer training hyper-parameters.
2. The CLI exposes a `tokenizer` command group with `train`, `validate`,
   `encode`, and `decode` subcommands.
3. Tokenizer training validates dataset checksums before work begins and
   maintains a cache manifest recording dataset identifiers and checksums.
4. Round-trip tests ensure encode/decode symmetry, special-token behavior, and
   padding invariants.
5. Local quality gates (`pre-commit`, `nox -s tests`, coverage threshold)
   succeed.

### Checklist

- [ ] Create base YAML config under `configs/tokenization/base.yaml`.
- [ ] Wire the `tokenizer` command group into `src/codex_ml/cli/codex_cli.py`
      and forward to `tokenization/train_tokenizer.py`.
- [ ] Implement dataset checksum verification and manifest updates prior to
      training.
- [ ] Add `tests/tokenization/test_tokenizer.py` covering symmetry, padding, and
      special tokens, alongside manifest assertions.
- [ ] Document tokenizer usage, normalizer nuances, and caching in the README or
      dedicated guide.

### Tests

- `tests/tokenization/test_tokenizer.py`
  - Symmetry: `decode(encode(texts)) == texts` for ASCII, Unicode, and emoji
    payloads.
  - Special tokens exist (`[PAD]`, `[BOS]`, `[EOS]`) with correct indices.
  - Padding invariants: batched encode/decode respects target lengths.
  - Manifest assertions: file exists, contains dataset IDs and checksums, and
    updates when retraining.

### Documentation

- Provide a quickstart for tokenizer train/validate/encode/decode commands.
- Author `docs/examples/tokenization.md` describing config keys and cache
  layout.

### Risks

- Divergence between config defaults and CLI overrides.
- Non-deterministic upstream dataset ordering impacting manifests.
- Stale cache manifests caused by incomplete invalidation.

### Rollback Plan

- Preserve the prior tokenizer under `tokenization/legacy/` until parity is
  proven.
- Feature flag the new CLI entry point; revert by toggling the flag.

### Deliverables

- Base config file, CLI group wiring, manifest utilities, regression tests, and
  documentation.

### Atomic PR Plan

1. **PR-1: Config + CLI Skeleton**
   - Add `configs/tokenization/base.yaml`.
   - Register `tokenizer` group in `src/codex_ml/cli/codex_cli.py`.
   - Scaffold `tests/tokenization/test_tokenizer.py` (skipped initially).

2. **PR-2: Training & Manifest Validation**
   - Implement `tokenization/train_tokenizer.py` logic with checksum validation
     and manifest writes.
   - Introduce `tokenization/manifest.py` helpers.
   - Enable tests with round-trip and manifest coverage.

3. **PR-3: Docs & Polish**
   - Update README and add `docs/examples/tokenization.md`.
   - Adjust coverage thresholds or nox configuration if required.

---

## Epic 2 — Training Engine & CLI

### Why

Deliver a functional, single-GPU training entry point with sane defaults and
resumable checkpoints to unblock end-to-end smoke runs and improve developer
velocity.

### Owner(s)

- Owner: **ML Core**
- Co-owner: **Platform**
- Reviewers: **QA**, **DX/Docs**

### Acceptance Criteria

1. Provide `configs/training/base.yaml` specifying seed, optimizer/scheduler
   setup, learning rate, batch size, epoch count, and checkpoint cadence.
2. Extend `codex` CLI with `train` subcommand loading the config (Hydra or
   equivalent) and invoking `run_functional_training()`.
3. Support `--resume` via `utils.checkpointing`; smoke tests verify checkpoint
   artifacts and resume behavior.
4. Smoke test ensures 1–2 training steps on a toy dataset produce decreasing
   loss without NaNs.
5. Local gates (`pre-commit`, `nox -s tests`, coverage) pass.

### Checklist

- [ ] Implement `src/codex_ml/train.py` (or equivalent runner) with logging
      hooks.
- [ ] Add CLI glue for `codex train --config ... [--resume]`.
- [ ] Seed RNGs at run start for determinism.
- [ ] Emit artifacts: checkpoints, config snapshot, NDJSON metrics.
- [ ] Provide smoke test ensuring loss decrease and resume validation.

### Tests

- `tests/training/test_training_loop.py`
  - Train 1–2 steps and assert `loss_t2 < loss_t1` with no NaNs.
  - Confirm checkpoint creation and resume restores optimizer/state.
  - Validate config snapshot saved alongside artifacts.

### Documentation

- Draft `docs/training/quickstart.md` with copy-pasteable commands.
- Document resume semantics, artifact locations, and example overrides.

### Risks

- CUDA/cuDNN incompatibilities or missing dependencies.
- Data loading nondeterminism without explicit seeding.

### Rollback Plan

- Keep entry point behind `--experimental-train`; fallback to legacy scripts if
  issues arise.

### Deliverables

- Training config, CLI wiring, runner implementation, checkpoint utilities,
  smoke tests, and documentation.

### Atomic PR Plan

1. **PR-1: Config + Runner Skeleton**
   - Add `configs/training/base.yaml`.
   - Introduce `src/codex_ml/train.py` skeleton with `run_functional_training`.
   - Scaffold `tests/training/test_training_loop.py` (skipped initially).

2. **PR-2: CLI + Checkpointing + Smoke Test**
   - Wire CLI `train` command in `codex_cli.py` with `--config` and `--resume`.
   - Add `src/codex_ml/utils/checkpointing.py` utilities.
   - Enable and expand smoke tests for loss decrease and resume.

3. **PR-3: Metrics & Docs**
   - Emit NDJSON metrics and config snapshots.
   - Publish `docs/training/quickstart.md` and update `noxfile.py` if coverage or
     packaging hooks change.

---

## Epic 3 — Deterministic Data Splitting & Manifests

### Why

Guarantee reproducible experiments through seeded data partitions and manifest
provenance capturing dataset IDs, checksums, and split membership.

### Owner(s)

- Owner: **Data/ML**
- Co-owner: **Platform**
- Reviewers: **QA**, **Security** (provenance), **DX/Docs**

### Acceptance Criteria

1. Provide `src/codex_ml/data/split.py` with seeded, stable train/val/test split
   helpers.
2. Produce JSON manifests recording dataset IDs, file checksums, split
   membership, and the seed used for partitioning.
3. Tests confirm identical splits when seeds match and divergence when seeds
   differ, while preserving size invariants.
4. CLI (e.g., `prepare-data`) accepts `--seed`, writes manifests, and logs
   checksums in run artifacts.

### Checklist

- [ ] Implement checksum utilities (`hash_dataset_id`, `checksum_file`).
- [ ] Implement `seeded_split(items, ratios, seed)` with stable ordering.
- [ ] Write manifest JSON containing seed, dataset IDs, checksums, and split
      allocation.
- [ ] Provide a `prepare-data` command generating manifests and caches.
- [ ] Add tests verifying determinism and manifest schema validity.

### Tests

- `tests/data/test_splits.py`
  - Identical splits across runs with same seed.
  - Different seeds produce distinct partitions while keeping union/size
    invariants.
  - Manifest schema includes seed, dataset IDs, checksums, and split membership.

### Documentation

- Draft `docs/data/deterministic_splits.md` with examples and schema reference;
  link from README.

### Risks

- Platform-specific file ordering differences impacting determinism.
- Large datasets slowing checksum computation.

### Rollback Plan

- Feature flag deterministic mode; fallback to non-deterministic splits if
  issues surface.

### Deliverables

- Split helper utilities, checksum helpers, manifest writer, CLI integration,
  tests, and docs.

### Atomic PR Plan

1. **PR-1: Utilities + Split Helper**
   - Add `src/codex_ml/data/split.py` and supporting checksum utilities.
   - Scaffold `tests/data/test_splits.py` (skipped initially).

2. **PR-2: Manifest + CLI Integration**
   - Implement manifest writer and integrate `prepare-data --seed` CLI.
   - Enable deterministic split tests and add manifest assertions.

3. **PR-3: Docs & Performance Safeguards**
   - Document deterministic splits and schema.
   - Optimize checksum utilities (e.g., chunked hashing) as needed.

---

## Quality Gates (Local-Only)

- `pre-commit run --files <changed_files>`
- `nox -s tests`
- Coverage threshold ≥ **80%** for touched files
- No external network calls; logs and manifests remain local

## Changelog (Running)

- `feat(tokenization): add base config, CLI group, manifest & tests`
- `feat(train): add training runner, CLI, checkpointing, smoke test`
- `feat(data): deterministic split helper, checksums, manifest + CLI`
- `docs: add quickstarts & deterministic split schema`

## Open Questions

1. Preferred hashing algorithm for large corpora (xxh3 vs SHA-256) balancing
   speed and auditability?
2. Minimum acceptable coverage threshold for smoke-heavy phases?
3. Should tokenizer, training, and data manifests share a unified run ID format
   (e.g., ULID)?
