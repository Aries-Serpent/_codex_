# [Plan]: Training Loop Enhancements & Resume Logic Roadmap
> Generated: 2025-09-26 01:40:18 | Author: mbaetiong  
Roles: [Primary], [Secondary] ⚡ Energy: [5]

## Status Update
- P1.1 (Resume Logic) ✅
- P1.2 (Resume test) ✅
- P1.3 (Optimizer wiring) ✅
- P1.4 (Optimizer checkpoint save/load) ✅
- P1.5 (Scheduler minimal linear/step) ✅ (epoch-based; linear + step)
- P1.11 (Dataset real loader JSONL/CSV) ✅ (src/codex_ml/data/loaders.py)
- P1.13 (/infer masking tests) ✅
- P1.14 (/infer tokenizer roundtrip test) ✅

## Newly Completed (This Increment)
| Task | Implementation | Notes |
|------|---------------|-------|
| P1.5 Scheduler | Linear (custom) + Step (torch StepLR) | Stepped per epoch after optimizer loop |
| P1.11 Dataset loaders | load_jsonl / load_csv with SHA256 checksum | Returns (records, metadata) |
| P1.13 Masking tests | test_api_infer_masking.py | Covers all configured secret patterns + disable flag |
| P1.14 Tokenizer roundtrip | test_api_infer_tokenizer.py | Ensures echo / token path functional |

## Remaining Tasks
| Priority | Task | Status | Notes |
|----------|------|--------|-------|
| P1.6 | Gradient accumulation refinement | Partial | Works; refine once real forward integrated |
| P1.7 | AMP scaffold | Pending | GPU dependent |
| P1.8 | Deterministic seeds doc | Pending | docs/reproducibility.md |
| P1.9 | Extended metrics (epoch wall times, lr history) | Partial | Current LR returned; add history later |
| P1.10 | Evaluation hook skeleton | Pending | Callback design TBD |
| P1.12 | Data loader tests (extended scenarios) | Partial | Basic tests in place; add edge cases (empty lines, quoting) |
| P2.1 | Evaluate CLI | Pending | Requires evaluation hook |
| P2.2 | Evaluate tests | Pending | Dependent on CLI |
| P2.3 | MLflow toggle doc | Pending | |
| P3.1 | PR artifact validation script | Pending | |
| P3.2 | Retention policy utility | Pending | |
| P3.3 | Structured logging upgrade | Pending | |
| P4.1 | LoRA param selective optimizer | Pending | Narrow param set |
| P4.2 | Mixed precision perf test | Pending | |
| P5.1 | Advanced scheduler registry | Pending | Cosine, warmup linear |
| P5.2 | Plugin callback system | Pending | |
| P5.3 | Failure injection tests | Pending | Crash + resume integrity |

## Scheduler Details
| Type | Behavior | Config Keys | State Saved |
|------|----------|------------|-------------|
| linear | Linear decay: base_lr -> base_lr * final_lr_scale over epochs | final_lr_scale | last_epoch |
| step | Decay every step_size epochs by gamma | step_size, gamma | torch scheduler state_dict |

## Dataset Loader Details
| Format | Function | Record Type | Notes |
|--------|----------|-------------|-------|
| JSONL | load_jsonl | dict per line | Non-dict coerced to {"value": obj} |
| CSV | load_csv | dict rows | Uses csv.DictReader |

Metadata keys: path, format, num_records, checksum, size_bytes

## /infer Test Coverage
| Pattern | Example | Test Assertion |
|---------|---------|----------------|
| OpenAI key | sk-... | Masked "[SECRET]" |
| AWS AKIA | AKIAABCDEFGHIJKLMNOP | Masked |
| AWS ASIA | ASIAABCDEFGHIJKLMNOP | Masked |
| Google API | AIza... | Masked |
| GitHub PAT | ghp_... | Masked |
| Slack tokens | xoxb-, xoxp- | Masked |
| Disable flag | DISABLE_SECRET_FILTER=1 | Unmasked |

## Metrics Added / Updated
| Metric | Source |
|--------|--------|
| scheduler_type | training loop result |
| current_lrs | list of current LR(s) after final epoch |
| dataset_files_count | number of successfully loaded dataset files |
| dataset_total_records | cumulative records loaded |
| dataset_checksums | list of file checksums |

## Risks / Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Large CSV/JSONL memory load | High mem usage | Future: streaming loader |
| Non-atomic latest.json | Resume inconsistency | Plan atomic write P3 |
| Scheduler mismatch w/ future step-level logic | Subtle LR drift | Constrain to epoch-based until step-level schedule needed |
| Secret regex false positives | Masking benign substrings | Patterns kept prefix-scoped & length constrained |

## Next Recommendations
1. Implement P1.8 docs/reproducibility.md (seed, checkpoint, scheduler state).
2. Add callback/evaluation skeleton (P1.10) to enable Evaluate CLI.
3. Extend dataset tests: empty file, BOM, quoted CSV, malformed JSONL line handling (skip vs fail).
4. Introduce learning rate history metric (list per epoch) for debugging.

## Usage Snippet
```
python -m codex_ml.cli.train epochs=3 steps_per_epoch=5 grad_accum=2 \
  checkpoint.dir=artifacts/ckpts checkpoint.resume=true \
  scheduler.type=linear scheduler.final_lr_scale=0.2 \
  dataset.sources='[data/train.jsonl]'
```

## Validation Checklist (Current Increment)
| Check | Status |
|-------|--------|
| Scheduler linear decay applied | ✅ |
| Scheduler step decay applied | ✅ |
| Dataset loaders return checksum | ✅ |
| Secret masking patterns covered by tests | ✅ |
| Tokenizer fallback echo path validated | ✅ |

---
```