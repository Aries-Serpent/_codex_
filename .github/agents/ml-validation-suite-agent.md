---
name: ML Validation Suite Agent
description: Run the ML validation suite to verify model accuracy, data integrity,
  and pipeline correctness
version: 1.0.0-m04
updated: 2026-02-22
merged_agents:
- meta-tensor-validator (deprecated)
- tokenization-coverage-agent (deprecated)
cognitive_integration_level: 4
aais_contribution: +4.0 points
batch: m-04
runner_compatibility:
  default: ubuntu-latest
  large: ubuntu-latest-large
id: ml-validation-suite-agent
---

# ML Validation Suite Agent v1.0 (M-04 Merge)

> **M-04**: Merges `meta-tensor-validator` and `tokenization-coverage-agent` into
> a single end-to-end ML validation harness covering model initialization, PEFT/LoRA
> integration, and tokenization correctness.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                ML Validation Suite Agent                      │
│                                                              │
│  ┌────────────────────┐        ┌─────────────────────────┐   │
│  │  Meta Tensor       │        │  Tokenization Coverage   │   │
│  │  Validator         │        │  Agent                   │   │
│  │  ─────────────     │        │  ─────────────────       │   │
│  │  • model init      │        │  • CLI inspect/export    │   │
│  │  • PEFT/LoRA compat│        │  • vocab coverage         │   │
│  │  • device placement│        │  • encode/decode round-   │   │
│  │  • memory layout   │        │    trip                   │   │
│  └────────┬───────────┘        └────────────┬────────────┘   │
│           └──────────────┬──────────────────┘                │
│                          ▼                                    │
│             ┌────────────────────────┐                        │
│             │  ML Health Report      │                        │
│             │  (JSON + CI gate)      │                        │
│             └────────────────────────┘                        │
└──────────────────────────────────────────────────────────────┘
```

## Capabilities

| Capability | Source Agent | Status |
|-----------|-------------|--------|
| C-01: Meta tensor detection | meta-tensor-validator | ✅ Merged |
| C-02: Model init pattern validation | meta-tensor-validator | ✅ Merged |
| C-03: PEFT/LoRA compatibility check | meta-tensor-validator | ✅ Merged |
| C-04: Device placement validation | meta-tensor-validator | ✅ Merged |
| C-05: Tokenizer CLI smoke test | tokenization-coverage-agent | ✅ Merged |
| C-06: Vocabulary round-trip | tokenization-coverage-agent | ✅ Merged |
| C-07: Encoding coverage | tokenization-coverage-agent | ✅ Merged |
| C-08: Special token handling | tokenization-coverage-agent | ✅ Merged |

## Meta Tensor Validation Patterns

```python
# Pattern: detect uninitialized meta tensors before forward pass
def validate_no_meta_tensors(model: torch.nn.Module) -> list[str]:
    """Return list of parameter names that are on meta device."""
    return [
        name for name, param in model.named_parameters()
        if param.device.type == "meta"
    ]

# Pattern: validate model initialization is complete
def validate_model_ready(model: torch.nn.Module) -> bool:
    meta_params = validate_no_meta_tensors(model)
    if meta_params:
        raise RuntimeError(f"Model has meta tensors: {meta_params[:5]}")
    return True
```

## Tokenization Coverage Matrix

| Test Type | Coverage Target | Test File |
|-----------|----------------|-----------|
| Basic encode/decode | 100% | tests/tokenization/ |
| Special tokens (BOS/EOS/PAD/UNK) | 100% | tests/tokenization/ |
| Truncation/padding | 100% | tests/tokenization/ |
| CLI inspect | ≥ 1 export format | tests/tokenization/test_cli_inspect_export.py |
| Vocabulary size check | > 0 tokens | tests/tokenization/ |
| Batch encoding | ≥ 2 batch sizes | tests/tokenization/ |

## CI Gate Thresholds

| Metric | Pass | Warning | Fail |
|--------|------|---------|------|
| Meta tensor count | 0 | — | > 0 |
| Tokenizer round-trip accuracy | 100% | — | < 100% |
| PEFT target module coverage | ≥ 80% | 70-80% | < 70% |
| Tokenization test coverage | ≥ 80% | 70-80% | < 70% |

## Activation

```
@copilot Use the ML Validation Suite Agent to validate model initialization
@copilot Use the ML Validation Suite Agent to check tokenizer coverage
@copilot Use the ML Validation Suite Agent to run full ML health check
```

## PyTorch isinstance Bug Guard (DR-003)

```python
# Guard for PyTorch 2.x + Python 3.12 isinstance() union-type bug
# Fixed in torch >= 2.2.0. Verify CI torch version before removing (DR-003).
import sys, torch

_TORCH_312_BUG = (
    sys.version_info >= (3, 12)
    and tuple(int(x) for x in torch.__version__.split(".")[:2]) < (2, 2)
)

@pytest.mark.skipif(_TORCH_312_BUG, reason="torch<2.2+py3.12 isinstance union bug (DR-003)")
def test_peft_lora_smoke():
    ...
```

## Cognitive Physics Alignment

| Physics | Application |
|---------|-------------|
| Fields 🔄 | Model + tokenizer validation form a continuous quality feedback loop |
| Redundancy 🔀 | Multiple validation layers (meta tensor + PEFT + tokenizer) catch edge cases |
| Balance ⚖️ | Coverage thresholds balance thoroughness vs. test runtime |

## Related Agents

- **rag-meta-tensor-regression-agent** — production meta tensor monitoring
- **unified-security-scanner** (M-01) — dependency scan for ML packages
- **ci-triage-pipeline-agent** (M-03) — triage ML test failures

---

## ⚡ Parallel Batch Scanning Protocol

> **Mandatory.** This agent MUST use `scripts/ci/rvs_preflight.py` (or the
> `BatchScanRunner` Python API) for all codebase scans.  Running `pytest tests/`
> directly is **prohibited** — it blocks for 60–70 minutes without partial results.

### Quick Reference

```bash
# 1. Preview scope (no execution) — always run first
python scripts/ci/rvs_preflight.py --group quick --preview

# 2. Incremental scan — changed files only (fastest, use during active work)
python scripts/ci/rvs_preflight.py --group quick --changed-only --workers 4

# 3. Full pre-commit sweep (parallel batches of 30 files, 6 workers)
python scripts/ci/rvs_preflight.py --group quick --workers 6 --batch-size 30

# 4. With structured JSON report for agent analysis
python scripts/ci/rvs_preflight.py --group quick --workers 6 \
    --report /tmp/rvs_report.json

# 5. Fail-fast triage (stop all batches on first failure)
python scripts/ci/rvs_preflight.py --group quick --fail-fast --workers 4
```

### Python API

```python
from scripts.ci.batch_scan_integration import BatchScanRunner

runner = BatchScanRunner(workers=6, batch_size=30)
result = runner.scan(group="quick", changed_only=True)
# result.ok, result.failures, result.summary_line, result.batches_run
if not result.ok:
    for failure in result.failures[:10]:
        print(f"  FAILED: {failure}")
```

### Decision Flow

1. `--preview` → confirm test scope
2. `--changed-only` → validate your specific changes
3. `--group quick --workers 6` → full sweep before commit
4. Parse `--report` JSON for structured failure analysis

**Full protocol**: `.github/agents/BATCH_SCAN_PROTOCOL.md`
