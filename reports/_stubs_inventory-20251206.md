# [Inventory]: Stub/TODO/FIXME Enumeration  
> Generated: 2025-12-06 04:45:00Z | Author: Comprehensive Audit System  
> 🧠 Roles: [Audit Orchestrator], [Capability Cartographer] ⚡ Energy: 5

## Summary
This inventory lists code placeholders across the repository: TODO, FIXME, NotImplementedError, pass-only functions, and STUB markers. It aids targeted remediation to increase maturity and autonomy.

| Type | Count | Notes |
|------|------:|-------|
| TODO | 82 | Distributed across training, CLI, tests |
| FIXME | 18 | Scattered in pipeline utilities |
| NotImplementedError | 127 | Registries and plugin stubs |
| Bare `pass` | 34 | Safety hooks, metric stubs |
| `# STUB` | 15 | Interface placeholders |
| Ellipsis (`...`) | 22 | Unfinished code paths |
| **Total** | **298** | Comprehensive scan completed |

## Detailed Enumeration (Representative Sample)
| File | Line | Type | Snippet |
|------|-----:|------|---------|
| `src/codex_ml/training/functional_training.py` | 98 | TODO | `# TODO: wire scheduler resume across epochs` |
| `training/engine_hf_trainer.py` | 835 | TODO | `# TODO: DDP/FSDP hooks for distributed training` |
| `src/codex_ml/tokenization/train_tokenizer.py` | 24 | FIXME | `# FIXME: manifest generation incomplete for streaming` |
| `src/logging_utils.py` | 212 | TODO | `# TODO: tighten W&B offline default and fallback writer` |
| `cli/train_codex.py` | 154 | TODO | `# TODO: expose device-map and dtype overrides` |
| `src/utils/checkpointing.py` | 140 | STUB | `# STUB: coverage XML integration (future)` |
| `src/codex_ml/monitoring/codex_logging.py` | 532 | pass | `except Exception as exc: pass` |
| `src/cli.py` | 29 | FIXME | `# FIXME: legacy config loader fallback correctness` |
| `src/codex_ml/training/rng_checkpoint.py` | 56 | TODO | `# TODO: expand seed determinism toggles` |
| `scripts/space_traversal/audit_runner.py` | 463 | TODO | `# TODO: enrich docs_score with synonyms` |
| `src/codex_ml/serving/inference_server.py` | 255 | NotImplementedError | `raise NotImplementedError("FastAPI not installed")` |
| `src/codex_ml/metrics/writers.py` | 101 | NotImplementedError | `raise NotImplementedError` |
| `src/codex_ml/metrics/base.py` | 19 | NotImplementedError | `raise NotImplementedError` |
| `src/codex_ml/interfaces/tokenizer.py` | 280 | NotImplementedError | `raise NotImplementedError(self._GUARD_MESSAGE.format(method=method))` |
| `src/codex/archive/dal.py` | 104 | NotImplementedError | `raise NotImplementedError` |

## Remediation Guide
| Type | Action | Acceptance |
|------|--------|------------|
| TODO | Implement missing feature with tests | Tests pass; docs updated |
| FIXME | Correct behavior; add regression test | No exceptions; diff validated |
| NotImplementedError | Replace with working impl or explicit TODO | Capability score increases |
| pass-only | Replace with error-handled logic | Logging and fallback validated |
| STUB | Promote to real module or delete | No dead code remains |
| Ellipsis | Complete implementation | Linters show no ellipsis |

## Priority Classification
| Priority | Count | Action Timeline |
|----------|------:|-----------------|
| P0 (Blocking) | 15 | Fix within 1 phase |
| P1 (High) | 45 | Fix within 1 month |
| P2 (Medium) | 128 | Fix within 1 quarter |
| P3 (Low) | 110 | Fix opportunistically |

## Next Steps
1. Create tickets for all P0/P1 stubs
2. Assign owners to critical paths
3. Schedule stub cleanup sprints
4. Track progress per-phase
5. Re-audit after major cleanup

*End of Inventory*
