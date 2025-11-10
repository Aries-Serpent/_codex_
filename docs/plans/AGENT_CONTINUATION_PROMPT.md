# Agent Continuation Prompt: S-14, S-15, S-02 Implementation

> **Context**: This prompt enables an Agent to continue implementation from where the current PR left off.  
> **Generated**: 2025-11-06 11:31:00 | PR: Add S-17 deterministic docs pipeline with Agent-run infrastructure

---

## What's Done ✅

### S-17: Deterministic Docs Pipeline (COMPLETE)
**Commits**: 3a59994, ef0eed5, 5c8f464, 90adcff

**Infrastructure**:
- ✅ PR template with Agent-run checkboxes (`.github/pull_request_template.md`)
- ✅ Workflows: `docs.yml`, `space-audit.yml`, `draft-audit-pr.yml`
- ✅ Scripts: `docs_build.sh`, `probe_env.py`, `canonicalize_artifacts.py`, `run_selected_jobs.sh`
- ✅ Baseline management: `capture_baseline.sh`, `rotate_baselines.py`
- ✅ Nox session: `docs_build`
- ✅ Makefile targets: `docs-build`, `capture-baseline`, `rotate-baselines`
- ✅ Documentation: API docs guide, baseline policy, Agent validation

### S-vector: Vector Store Stubs (COMPLETE)
**Commit**: 90adcff

**Modules**:
- ✅ `codex_addons/vector_stores/__init__.py`
- ✅ `codex_addons/vector_stores/pgvector_stub.py`
- ✅ `codex_addons/vector_stores/weaviate_stub.py`
- ✅ `tests/test_vector_store_stub.py`
- ✅ `scripts/space_traversal/detectors/vector_store_detector.py`
- ✅ `docs/modeling/LoRA.md`

---

## What's Next 🚀

### S-14: Distributed Training (CPU-safe guards)
**Status**: Module exists (`training/accelerate_init_guard.py`), needs tests + docs

**Tasks Remaining**:
1. ✅ Module: `training/accelerate_init_guard.py` (EXISTS - validate it matches spec)
2. ⏳ Test: `tests/integration/test_distributed_init.py` (EXISTS - validate alignment)
3. ✅ Doc: `docs/training/distributed_troubleshooting.md` (EXISTS - validate content)

**Acceptance**:
- CPU path never raises in default/CI environments
- Structured `InitReport` diagnostics returned
- Environment gating via `ACCELERATE_TEST=1`
- Tests skip by default, run when env flag set

**Validation Command**:
```bash
# Should skip gracefully
python -c "from training.accelerate_init_guard import safe_accelerate_init; print(safe_accelerate_init())"

# Run tests (should skip without ACCELERATE_TEST)
pytest -q tests/integration/test_distributed_init.py
```

---

### S-15: Registry Stabilization (Deterministic ordering)
**Status**: Module exists (`codex_addons/registry.py`), needs name map + tests

**Tasks Remaining**:
1. ⏳ Module: `codex_addons/registry_names.py` (CREATE - canonical names + aliases)
2. ✅ Module: `codex_addons/registry.py` (EXISTS - validate deterministic list())
3. ⏳ Test: `tests/test_factory_registry.py` (EXISTS - validate alignment)
4. ✅ Doc: `docs/plugins/Plugin_API_Broader.md` (EXISTS - validate content)

**Spec for `registry_names.py`**:
```python
"""Canonical registry names and aliases."""
from typing import Dict

NAME_MAP: Dict[str, str] = {
    "model:base": "Base model adapters",
    "model:lora": "LoRA adapters",
    "data:loader": "Dataset loaders",
    "logging:mlflow": "MLflow logging",
    "metrics:core": "Core metric set",
}

ALIASES: Dict[str, str] = {
    "model_lora": "model:lora",
    "mlflow": "logging:mlflow",
    "metrics": "metrics:core",
}
```

**Acceptance**:
- `list()` returns stable, deterministic order
- Alias resolution: `"model_lora"` → `"model:lora"`
- Idempotent registration (re-register same object = no-op)

**Validation Command**:
```bash
pytest -q tests/test_factory_registry.py
```

---

### S-02: Optional BLEU/ROUGE Metrics (Gated by extras)
**Status**: Needs full implementation

**Tasks Remaining**:
1. ⏳ Module: `codex_ml/metrics/_optional_bleu_rouge.py` (CREATE)
2. ⏳ Test: `tests/metrics/test_bleu_rouge.py` (CREATE)
3. ⏳ Doc: `docs/metrics.md` (UPDATE or CREATE)
4. ✅ Requirements: `requirements-optional.txt` (EXISTS - verify nltk, rouge-score)

**Spec for `_optional_bleu_rouge.py`**:
```python
"""Optional BLEU/ROUGE metrics (gated by extras)."""
from typing import Dict

def _import_bleu_rouge():
    try:
        from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
        from rouge_score import rouge_scorer
        return sentence_bleu, SmoothingFunction, rouge_scorer
    except Exception:
        return None, None, None

def bleu(reference: str, hypothesis: str) -> float:
    from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
    chencherry = SmoothingFunction()
    return float(sentence_bleu(
        [reference.split()], 
        hypothesis.split(), 
        smoothing_function=chencherry.method1
    ))

def rouge_l(reference: str, hypothesis: str) -> float:
    from rouge_score import rouge_scorer
    scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
    return float(scorer.score(reference, hypothesis)['rougeL'].fmeasure)

def patch_registry(reg: Dict[str, object]) -> Dict[str, object]:
    sb, sm, rs = _import_bleu_rouge()
    if not (sb and rs):
        return reg
    reg.setdefault("bleu", bleu)
    reg.setdefault("rouge_l", rouge_l)
    return reg
```

**Acceptance**:
- Metrics skip gracefully when deps not installed
- When installed, `patch_registry()` adds `"bleu"` and `"rouge_l"`
- Tests use `@pytest.mark.skipif(not DEPS)` gate

**Validation Command**:
```bash
# Without optional deps (should skip)
pytest -q tests/metrics/test_bleu_rouge.py

# With optional deps
pip install -r requirements-optional.txt
pytest -q tests/metrics/test_bleu_rouge.py
```

---

### S-12: LoRA Minimal Tests (Environment-gated)
**Status**: Module + test exist, need validation

**Tasks Remaining**:
1. ✅ Module: `models/lora/_test_utils.py` (EXISTS - validate)
2. ✅ Test: `tests/modeling/test_lora_minimal.py` (EXISTS - validate)
3. ✅ Doc: `docs/modeling/LoRA.md` (CREATED in commit 90adcff)

**Acceptance**:
- Tests skip by default (require `RUN_LORA_TESTS=1`)
- `build_minimal_lora()` returns valid config structure
- No network or GPU required

**Validation Command**:
```bash
# Should skip
pytest -q tests/modeling/test_lora_minimal.py

# With env flag
RUN_LORA_TESTS=1 pytest -q tests/modeling/test_lora_minimal.py
```

---

## Agent Tasks Summary

### Priority 1: Validate Existing Modules
1. Check `training/accelerate_init_guard.py` matches S-14 spec
2. Check `codex_addons/registry.py` has deterministic `list()`
3. Check `models/lora/_test_utils.py` and test file
4. Check `tests/integration/test_distributed_init.py` alignment

### Priority 2: Create Missing Files
1. **S-15**: `codex_addons/registry_names.py` (NAME_MAP + ALIASES)
2. **S-02**: `codex_ml/metrics/_optional_bleu_rouge.py`
3. **S-02**: `tests/metrics/test_bleu_rouge.py`
4. **S-02**: Update or create `docs/metrics.md`

### Priority 3: Validation
1. Run: `pytest -q tests/integration/test_distributed_init.py`
2. Run: `pytest -q tests/test_factory_registry.py`
3. Run: `pytest -q tests/modeling/test_lora_minimal.py`
4. Run: `pytest -q tests/metrics/test_bleu_rouge.py`
5. Run: `pytest -q tests/test_vector_store_stub.py`

---

## Success Criteria

### All S-IDs Complete When:
- ✅ All Python files compile (`python -m py_compile <file>`)
- ✅ All tests pass or skip appropriately (env gates working)
- ✅ Documentation complete for each S-ID
- ✅ No hard dependencies on optional packages (graceful degradation)
- ✅ Determinism verified (registry list order, artifact SHAs)

### Final Commit Message Template:
```
Complete S-14, S-15, S-02 follow-on modules

- S-14: Distributed training CPU-safe guards with env gating
- S-15: Registry stabilization with canonical names and aliases
- S-02: Optional BLEU/ROUGE metrics (gated by extras)
- S-12: LoRA minimal tests validated
- All tests pass with appropriate environment gates
- Documentation complete for all modules
```

---

## Directory Structure Reference

```
.
├── codex_addons/
│   ├── registry.py              ✅ Exists (validate)
│   ├── registry_names.py        ⏳ CREATE (S-15)
│   └── vector_stores/           ✅ Complete
│       ├── __init__.py
│       ├── pgvector_stub.py
│       └── weaviate_stub.py
├── codex_ml/metrics/
│   └── _optional_bleu_rouge.py  ⏳ CREATE (S-02)
├── training/
│   └── accelerate_init_guard.py ✅ Exists (validate)
├── models/lora/
│   └── _test_utils.py           ✅ Exists (validate)
├── tests/
│   ├── integration/
│   │   └── test_distributed_init.py    ✅ Exists (validate)
│   ├── metrics/
│   │   └── test_bleu_rouge.py          ⏳ CREATE (S-02)
│   ├── modeling/
│   │   └── test_lora_minimal.py        ✅ Exists (validate)
│   ├── test_factory_registry.py        ✅ Exists (validate)
│   └── test_vector_store_stub.py       ✅ Complete
├── docs/
│   ├── training/
│   │   └── distributed_troubleshooting.md  ✅ Exists (validate)
│   ├── plugins/
│   │   └── Plugin_API_Broader.md           ✅ Exists (validate)
│   ├── modeling/
│   │   └── LoRA.md                         ✅ Complete
│   └── metrics.md                          ⏳ CREATE/UPDATE (S-02)
└── requirements-optional.txt               ✅ Exists (verify nltk, rouge-score)
```

---

## Notes for Agent

- **Preserve existing modules**: Check existing files before creating; update only if needed
- **Environment gating**: All heavy tests should skip by default (ACCELERATE_TEST, RUN_LORA_TESTS, etc.)
- **No breaking changes**: All additions should be additive-only
- **Determinism**: Registry list() must return stable sorted order
- **Documentation**: Each S-ID needs corresponding docs (guide/troubleshooting)
- **Testing**: All new code should have tests (with appropriate skip gates)

---

## Quick Start for Agent

```bash
# 1. Validate existing modules
python -c "from training.accelerate_init_guard import safe_accelerate_init; print(safe_accelerate_init())"
python -c "from codex_addons.registry import Registry; r=Registry(kind='test'); print(r.list())"

# 2. Create missing files (S-15, S-02)
# Use specs above

# 3. Run validation
pytest -q tests/integration/test_distributed_init.py
pytest -q tests/test_factory_registry.py
pytest -q tests/modeling/test_lora_minimal.py
pytest -q tests/test_vector_store_stub.py

# 4. Commit when all pass
git add .
git commit -m "Complete S-14, S-15, S-02 follow-on modules"
```

**Ready to proceed!** 🚀
