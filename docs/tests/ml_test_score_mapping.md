# ML Test Score Mapping for _codex_ Scaffolding Tests

This document maps tests to high-level ML Test Score categories
(e.g. data, model, infrastructure, regression, performance) and explains
how to use the **ML Test Score map + runner** to execute subsets of tests.

## Categories

- **data**: Dataset handling, determinism, splitting, preprocessing.
- **model**: Model construction and forward behavior; training loop basics;
  evaluation logic.
- **infrastructure**: Tooling, runners, config, logging, checkpointing,
  registries, and orchestration glue.
- **regression**: Tests that ensure previously fixed bugs remain fixed.
- **performance**: Tests that explicitly measure runtime or memory limits.

## Mapping (documentation view)

| Test module                                      | Category         | Notes                                      |
|--------------------------------------------------|------------------|--------------------------------------------|
| tests/tools/test_codex_gap_registry.py           | infrastructure   | Registry building & YAML serialization     |
| tests/tools/test_codex_yaml_gap_check.py         | infrastructure   | Coverage between registry and task YAML    |
| tests/tools/test_codex_task_sequence_runner.py   | infrastructure   | Task sequence orchestration & logging      |
| tests/tools/test_codex_hardship_and_capability_validators.py | infrastructure | Hardship/capability map validation    |
| tests/tools/test_codex_mltest_map_and_runner.py  | infrastructure   | ML test map + runner behavior              |
| tests/tools/test_codex_experiment_index.py       | infrastructure   | Experiment index builder                   |
| tests/codex_ml/test_tokenization_basic.py        | model            | Tokenization scaffolding determinism       |
| tests/codex_ml/test_model_factory.py             | model            | Model factory hidden size propagation      |
| tests/codex_ml/test_training_loop_smoke.py       | model            | Minimal training loop behavior             |
| tests/codex_ml/test_minimal_train_cli.py         | model            | End-to-end minimal training+eval path      |
| tests/codex_ml/test_eval_minimal_cli.py          | model            | Minimal evaluation CLI wiring              |
| tests/codex_ml/test_config_integration.py        | infrastructure   | Config/Hydra-like file presence & parsing  |
| tests/codex_ml/test_config_loader.py             | infrastructure   | Config loader merge behaviour              |
| tests/codex_ml/test_eval_smoke.py                | model            | Evaluation scaffolding correctness         |
| tests/codex_ml/test_logging_registry.py          | infrastructure   | Logger registration and retrieval          |
| tests/codex_ml/test_metrics_logger.py            | infrastructure   | NDJSON metric logging                      |
| tests/codex_ml/test_checkpoint_utils.py          | infrastructure   | Save/load roundtrip for checkpoint data    |
| tests/codex_ml/test_dataloader_determinism.py    | data             | Deterministic ordering based on seed       |
| tests/codex_ml/test_simple_dataset.py            | data             | SimpleDataset deterministic encoding       |
| tests/codex_ml/test_mlflow_wrapper_stub.py       | infrastructure   | Experiment tracking stub safety            |
| tests/codex_ml/test_registry_basic.py            | infrastructure   | Generic registry registration/get          |
| tests/codex_ml/test_cli_utils_run_context.py     | infrastructure   | Run context creation & manifest writing    |
| tests/codex_ml/test_codex_env_cli.py             | infrastructure   | Unified env CLI delegation                 |

The authoritative, machine-readable version lives in:

- `codex_ml_test_map.yaml`

## Using the ML Test Score runner

To run tests by category, use:

```bash
python tools/codex_mltest_runner.py --category data
python tools/codex_mltest_runner.py --category model
python tools/codex_mltest_runner.py --category infrastructure
```

You can specify multiple categories (merged test set):

```bash
python tools/codex_mltest_runner.py --category data --category model
```

If you omit --category, all categories are run according to the map:

```bash
python tools/codex_mltest_runner.py
```

To produce a small JSON summary of what was run and the pytest return code:

```bash
python tools/codex_mltest_runner.py \
  --category infrastructure \
  --json-summary codex_mltest_summary.json
```

This makes it easy to:
- Tie ML Test Score categories to local quality gates.
- Correlate gap registry entries with the types of tests exercising each area.
- Incrementally fill regression and performance as the project matures.
