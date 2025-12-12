# Codex Status Update (2025-11-28)

## Summary
- Added `codex config-sweep` CLI to emit Hydra-ready sweep configs with reproducibility metadata (seed grids, dataset version/hash, locked overrides).
- Surfaced explicit MLflow toggles (`--mlflow/--no-mlflow`, tracking URI, run/experiment overrides) on training/resume CLIs and documented usage.
- Integrated self-correction helpers: structured error logging with retention guards, JSON logging/NVML opt-outs, and an analyzer utility for `.codex/logs`.
- Expanded quickstart and tracking docs with resume manifest, metrics writer, and plugin registration workflows; enforced pytest coverage threshold.

## Capability Table
| Capability | Status | Notes / Evidence | Remaining Gaps & Risks |
| --- | --- | --- | --- |
| Tokenization | Fully Implemented | `pad_sequences` helper with validation and tests (`tests/test_tokenization.py`); legacy adapters preserved. | None known. |
| ChatGPT Codex Modeling | Implemented | LoRA/quantization validation and env fallbacks in `src/codex_ml/models/factory.py`; defaults safe. | Further coverage for additional model builders could be added. |
| Training Engine | Implemented | HF trainer exposes `--metrics-writer`, `--sys-metrics`; checkpoint manifest/top-k in `training/checkpoint_manager.py`. | Monitor manifest schema stability across versions. |
| Configuration Management | Implemented | Hydra/OmegaConf configs in `configs/`/`hydra/`; dataclasses in `training/config.py`; `codex config-sweep` emits sweep YAML with seeds/version/hash metadata. | Ensure generated sweep templates stay aligned with evolving configs. |
| Evaluation & Metrics | Partially Implemented | Metrics writers (NDJSON/CSV) selectable; registry hooks exist; quickstart notes added. | Custom metric hook docs still limited; MLflow summary export optional. |
| Logging & Monitoring | Partially Implemented | JSON/system metrics flag available; evidence under `.codex/`. | NVML/GPU metrics depend on optional deps; logging format inconsistent across older modules. |
| Checkpointing & Resume | Implemented | Top-k best checkpoints, best symlinks, manifest emission; resume CLI exercised by tests. | Ensure manifest/backward compatibility when configs change. |
| Data Handling | Implemented | Dataset hashing/caching helpers in `training/datasets.py`; deterministic seeds in configs. | Large dataset hashing may be slow; document caching strategy. |
| Security & Safety | Implemented | Pre-commit includes detect-secrets, bandit, pip-compile; SECURITY.md present. | Developers must manage detect-secrets baselines manually. |
| Internal CI/Test | Implemented | Pytest markers in `pytest.ini`; nox sessions for tests/eval/hygiene in `noxfile.py`; targeted unit tests added. | Coverage thresholds not enforced globally; heavy suites may be skipped locally. |
| Deployment | Implemented | Packaging via `pyproject.toml`/`setup.cfg`; Dockerfiles present. | No automated release pipeline documented. |
| Documentation & Examples | Implemented | README and docs refreshed; quickstart now covers sweeps, manifests, metrics writers, and plugins. | Keep examples in sync with CLI evolution. |
| Experiment Tracking | Implemented | MLflow hooks in `training/functional_training.py`; offline W&B shim; CLI toggles for MLflow enablement and tracking URI/run metadata. | Remote MLflow usage still depends on optional dependency availability. |
| Extensibility | Implemented | Plugin entrypoints defined in `pyproject.toml` (tokenizers/models/metrics/plugins); registries in `src/codex_ml/registry`. | Developer guide for plugin authoring could be richer. |

## Risks & Mitigations
- **Sweep template drift**: Generated YAML may fall out of sync with future config schema; mitigate by regenerating sweeps when configs change.
- **Optional MLflow deps**: Tracking flags require `mlflow`; mitigate by guarding with `--no-mlflow` in air-gapped environments.
- **Detect-secrets baseline**: Hook may flag false positives until baseline created; mitigate by generating baseline per team policy.
- **Logging variability**: Older modules may emit unstructured logs; prefer new JSON helpers when extending.

## Next Steps
1. Expand custom metrics hook documentation and examples to move Evaluation & Metrics to fully implemented.
2. Standardize JSON logging across legacy modules and document optional NVML/GPU monitoring guards.
3. Add regression tests for MLflow summary export and plugin discovery paths to keep coverage green under the new threshold.

