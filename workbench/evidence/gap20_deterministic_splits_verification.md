# Gap 20 — Deterministic Data Splits Verification

## Scope
- Gap ID: 20
- Wave: 3
- Session mode: timeout-safe (<=55 minutes)
- Decision: complete Gap 20 based on existing implementation + targeted validation

## Implementation Evidence
- `/tmp/workspace/Aries-Serpent/_codex_/src/codex_ml/data/split.py`
  - `train_val_test_split(...)` uses seeded `random.Random(int(seed))`.
  - Writes manifest/checksum artifacts for reproducibility tracking.
- `/tmp/workspace/Aries-Serpent/_codex_/src/codex_ml/data/split_utils.py`
  - `deterministic_split(...)` with explicit seed/fraction validation.
  - `split_dataset(...)` deterministic JSONL split path.
- `/tmp/workspace/Aries-Serpent/_codex_/src/codex_ml/data/splits.py`
  - Stable hash-based split assignment (`stable_fold`, `assign_split`).

## Validation Evidence
- Queue lock check:
  - `python3` YAML validation script confirmed Wave 3/Wave 4 lock values and `special_flags.needs_verification`.
- Targeted tests for deterministic split behavior:
  - `python3 -m pytest tests/test_deterministic_split.py tests/data/test_split_dataset_deterministic.py -q`
  - Result: pass

## Notes
- Repository-wide `ruff check src/ tests/` currently reports pre-existing unrelated issues (import ordering/unused imports and one syntax error in untouched files). No new lint issues were introduced by this gap status/evidence update.

## Deferred >55 Minute Items (workflow/custom-agent route)
- Wave 3 long items: 17, 18, 21, 23
- Wave 4 queue: 32–45 (except explicitly bounded slices that can be completed within session budget)
