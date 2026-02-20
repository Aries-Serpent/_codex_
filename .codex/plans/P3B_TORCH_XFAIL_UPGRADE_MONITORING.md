# Planset: P3b — PyTorch Upgrade Monitoring & _TORCH_PROFILER_XFAIL Lifecycle

**Status**: 🟢 MONITORING — Ongoing  
**Priority**: P3 — Enhancement  
**Created**: 2026-02-20

---

## Problem

PyTorch 2.x + Python 3.12 has a known bug where `isinstance()` with union types fails inside:
- `torch.utils.data.DataLoader.__next__` (profiler)
- `torch.nn.Module.to()` (device placement)

Affected tests are in `_TORCH_PROFILER_XFAIL` in `tests/conftest.py` (10 entries as of 2026-02-20).

**Upstream bug**: https://github.com/pytorch/pytorch/issues/118829

---

## Current State

```python
# tests/conftest.py — _TORCH_PROFILER_XFAIL (10 entries)
_TORCH_PROFILER_XFAIL = frozenset({
    "tests/data/test_datasets_module.py::test_build_dataloaders_with_split",
    "tests/unit/test_datasets_module.py::test_build_dataloaders",
    "tests/smoke/test_hf_trainer_hello.py::test_hf_trainer_on_tiny_hello_dataset",
    # 7 RAG initialization tests...
})
```

All marked `xfail(strict=False)` so CI passes but the failures are tracked.

---

## Monitoring Plan

### When PyTorch ≥2.7 is released

1. **Update `requirements.txt`** (or `pyproject.toml`):
   ```
   torch>=2.7.0
   ```

2. **Remove xfail entries** for tests that now pass:
   ```bash
   pytest tests/data/test_datasets_module.py::test_build_dataloaders_with_split -v
   # If PASSED (not XFAIL): remove from _TORCH_PROFILER_XFAIL
   ```

3. **Run full suite** to confirm no new failures:
   ```bash
   pytest tests/ -q --tb=short
   ```

4. **Update conftest.py** to remove resolved entries from `_TORCH_PROFILER_XFAIL`

### Adding New Entries

If a new test fails with:
```
RuntimeError: isinstance() arg 2 must be a type, a tuple of types, or a union
```

OR:
```
RuntimeError: Failed to move model to cpu: isinstance() arg 2 ...
```

**Action**: Add to `_TORCH_PROFILER_XFAIL` with `strict=False`:
```python
"tests/path/to/test.py::TestClass::test_method": None  # pattern already in conftest
```

---

## Version Tracking

| PyTorch Version | Python 3.12 isinstance bug | Action |
|----------------|---------------------------|--------|
| 2.0–2.5 | ❌ Present | xfail all affected tests |
| 2.6.x | ⚠️ Partial fix (upstream PR in progress) | Monitor |
| 2.7.0+ | Expected ✅ Fixed | Remove xfails, delete this monitoring plan |

---

## Automation: CI Check

Add a CI step to warn when `_TORCH_PROFILER_XFAIL` tests start passing (indicating PyTorch was upgraded and xfails can be removed):

```yaml
# In .github/workflows/ci.yml
- name: Check for resolved torch xfails
  run: |
    pytest tests/ -q --tb=no 2>&1 | grep "xpassed" | while read line; do
      echo "::warning::xpassed test detected: $line — consider removing from _TORCH_PROFILER_XFAIL"
    done
```

---

## Success Criterion

- `_TORCH_PROFILER_XFAIL` contains 0 entries (all tests pass natively)
- PyTorch version in `requirements.txt` ≥ 2.7.0
- This planset file deleted as obsolete
