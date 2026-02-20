# Remaining Test Failures - Follow-up Required

## Status After Initial Fix Round

**Fixed:** 15/25 tests (60%)
**Remaining:** 10 tests requiring deeper investigation

---

## Remaining Failures (Priority Order)

### 1. PyTorch Checkpoint Test (High Priority)
**Test:** `tests/test_checkpoint_metadata.py::test_checkpoint_records_git_and_env`

**Error:**
```
CheckpointLoadError: failed to save checkpoint via pickle: issubclass() arg 2 must be a class, a tuple of classes, or a union
```

**Root Cause:** PyTorch 2.x + Python 3.12 compatibility issue in `torch.save()` when using pickle protocol

**Suggested Fix:**
- Update `src/codex_ml/utils/checkpointing.py` to handle PyTorch 2.x serialization
- Add guards for PyTorch version and Python version
- Consider using `torch.save(..., _use_new_zipfile_serialization=True)` or downgrade pickle protocol

**Files to check:**
- `src/codex_ml/utils/checkpointing.py` (save_checkpoint function)

---

### 2. Performance Benchmark Test (High Priority)
**Test:** `tests/test_performance_benchmark.py::test_benchmark_data_loading`

**Error:**
```
RuntimeError: profiler::_record_function_exit() Expected a value of type '__torch__.torch.classes.profiler._RecordFunction'
```

**Root Cause:** PyTorch profiler API incompatibility with Python 3.12

**Suggested Fix:**
- Add `@pytest.mark.skipif` for PyTorch < 2.1 or Python 3.12
- Or mock the profiler in test environment
- Or use alternative profiling approach

**Files to check:**
- `tests/test_performance_benchmark.py`
- Consider using `@pytest.mark.skipif(sys.version_info >= (3, 12), reason="PyTorch profiler issue on Py3.12")`

---

### 3. PEFT/LoRA Model Tests (Medium Priority)
**Tests:**
- `tests/test_modeling_module.py::test_load_model_requires_peft_when_lora_enabled`
- `tests/test_modeling_module.py::test_load_model_with_lora`

**Errors:**
```
ValueError: Target modules {'v_proj', 'q_proj'} not found in the base model
AssertionError: PeftModelForCausalLM(...) == 'wrapped'
```

**Root Cause:** Mock model doesn't have expected projection layers for LoRA, assertion expects string but gets model object

**Suggested Fix:**
- Update mock model to include dummy `q_proj`, `v_proj` layers
- Fix assertion to check isinstance(model, PeftModel) or check model type name
- Or skip tests if peft not properly installed

**Files to check:**
- `tests/test_modeling_module.py`
- Mock model definition

---

### 4. CLI Tests (Medium Priority)
**Tests:**
- `tests/tokenization/test_cli_inspect_export.py::test_cli_inspect_export`
- `tests/test_run_eval_cli.py::test_run_eval_cli`

**Errors:**
```
subprocess.CalledProcessError: Command [...] returned non-zero exit status 1
```

**Root Cause:** CLI subprocess calls failing (need to check stderr for actual error)

**Suggested Fix:**
- Run CLI commands manually to see actual error
- Likely missing dependencies or import errors
- Check subprocess stderr output in test

**Investigation needed:**
```bash
python -m tokenization.cli inspect <path>
python -m codex_ml.eval.run_eval --model sshleifer/tiny-gpt2 --data <path>
```

---

### 5. HuggingFace Dataset Test (Low Priority)
**Test:** `tests/data/test_hf_factory_compat.py::test_hf_dataset_factory`

**Error:**
```
OSError: abcdef0 is not a valid git identifier for 'hf-internal-testing/llama-tokenizer'
```

**Root Cause:** Test uses fake revision "abcdef0" that doesn't exist

**Suggested Fix:**
- Use a real revision hash or tag
- Or mock the HF API call
- Or skip if network unavailable

---

## Summary

**Critical Path:**
1. Fix checkpoint test (PyTorch serialization)
2. Fix or skip performance benchmark (PyTorch profiler)
3. Fix PEFT/LoRA tests (mock model updates)

**Lower Priority:**
4. Investigate CLI test failures
5. Fix HF dataset test with valid revision

**Estimated Effort:** 2-4 hours for remaining tests

**Recommendation:** Create follow-up PR for remaining 10 tests after this PR merges the 15 fixes
