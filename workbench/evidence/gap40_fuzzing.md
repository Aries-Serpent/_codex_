# Gap 40 — Fuzz Testing Suite: Evidence

**Status:** ✅ Implemented  
**Date:** 2025-06-06  
**Implemented by:** Copilot coding agent  

---

## Summary

A Hypothesis-based fuzz testing suite was created under `tests/fuzz/` targeting
three critical code-path categories:

| File | Target module(s) | `@given` tests |
|------|-----------------|---------------|
| `tests/fuzz/test_fuzz_tokenizer.py` | `codex_ml.data.utils`, `codex_ml.data.split_utils`, `codex_ml.data.jsonl_loader` | 8 |
| `tests/fuzz/test_fuzz_configs.py` | `codex_ml.config_schema.TrainConfig`, `codex_ml.config_schema.LoraConfig` | 7 |
| `tests/fuzz/test_fuzz_api.py` | `codex.api.rag_api` Pydantic request/response models | 8 |
| **Total** | | **23** |

---

## Test Run Output

```
================================================= test session starts ==================================================
platform linux -- Python 3.12.3, pytest-9.0.3, pluggy-1.6.0
rootdir: /tmp/workspace/Aries-Serpent/_codex_
configfile: pytest.ini
plugins: asyncio-1.4.0, anyio-4.3.0, hypothesis-6.155.2
asyncio: mode=Mode.AUTO

collecting ... collected 23 items

tests/fuzz/test_fuzz_api.py ........                                          [ 34%]
tests/fuzz/test_fuzz_configs.py .......                                       [ 65%]
tests/fuzz/test_fuzz_tokenizer.py ........                                    [100%]

============================================ 23 passed, 1 warning in 3.17s ============================================
```

---

## Done Criteria Verification

| Criterion | Status |
|-----------|--------|
| `tests/fuzz/` directory with ≥3 fuzz test files | ✅ 4 files (`__init__.py` + 3 test files) |
| ≥15 total `@given` tests, all passing | ✅ 23 `@given` tests, 23/23 pass |
| Evidence file at `workbench/evidence/gap40_fuzzing.md` | ✅ This file |
| `workbench/gap_backlog_prioritized.md` gap 40 → `✅ Implemented` | ✅ Updated |

---

## Coverage Details

### `test_fuzz_tokenizer.py` (8 tests)

| Test | Behaviour Verified |
|------|--------------------|
| `test_fuzz_deterministic_split_ids_partition` | train+eval always partitions the original list (no lost/duplicate IDs) |
| `test_fuzz_deterministic_split_ids_reproducible` | same inputs yield identical splits (determinism) |
| `test_fuzz_deterministic_split_ids_invalid_fraction` | fraction ≤0 or ≥1 raises `ValueError` |
| `test_fuzz_assign_split_map_values` | all split labels are "train" or "eval"; all IDs present |
| `test_fuzz_normalise_ratios_invalid_sum` | wrong-length ratio list raises `ValueError` |
| `test_fuzz_ensure_split_seed_positive_int` | provided seed is returned unchanged as `int` |
| `test_fuzz_normalise_text_string_returns_list` | string input always yields a list of strings |
| `test_fuzz_extract_texts_from_line_never_raises` | arbitrary lines (incl. null bytes, broken UTF-8) never raise |

### `test_fuzz_configs.py` (7 tests)

| Test | Behaviour Verified |
|------|--------------------|
| `test_fuzz_train_config_valid_construction` | valid numeric/string combos accepted |
| `test_fuzz_train_config_boundary_numerics` | non-positive numerics raise `ValidationError` |
| `test_fuzz_train_config_extra_fields_forbidden` | extra fields rejected (`extra="forbid"`) |
| `test_fuzz_train_config_dtype_and_eval_split` | `eval_split` enforced in [0,1] |
| `test_fuzz_lora_config_construction` | positive-int ranks accepted; non-positive rejected |
| `test_fuzz_lora_config_invalid_dropout` | dropout outside [0,1] raises `ValidationError` |
| `test_fuzz_lora_config_target_modules` | `None`/list accepted; other types rejected cleanly |

### `test_fuzz_api.py` (8 tests)

| Test | Behaviour Verified |
|------|--------------------|
| `test_fuzz_query_request_valid` | valid query/index/top_k/score accepted; fields round-trip |
| `test_fuzz_query_request_invalid_inputs` | empty query, bad top_k, out-of-range score raise |
| `test_fuzz_build_index_request_valid` | valid file lists and numeric params accepted |
| `test_fuzz_build_index_request_invalid_numerics` | out-of-range chunk_size / negative overlap raise |
| `test_fuzz_delete_index_request_valid` | arbitrary index names and tenant IDs accepted |
| `test_fuzz_merge_indices_request_valid` | ≥2 source indices accepted |
| `test_fuzz_merge_indices_request_too_few_sources` | 0 or 1 source indices raise |
| `test_fuzz_health_response_construction` | arbitrary string fields for all response keys accepted |

---

## Implementation Notes

- Uses **hypothesis** `@given` decorator pattern throughout (no atheris native compilation required).
- Each file has `pytest.importorskip("hypothesis")` at top — skips gracefully when hypothesis is absent.
- `@settings(suppress_health_check=[HealthCheck.too_slow])` applied where strategies involve heavy
  Pydantic models to silence hypothesis health-check warnings.
- `deadline=None` used throughout to avoid flakiness on slow CI runners.
