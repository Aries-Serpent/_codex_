# Minimal _codex_ Run (Scaffolding)

This example describes a minimal local run using the scaffolding modules:

## 1. Prepare the gap registry (optional but recommended)

1. Ensure you have a recent status audit, e.g.:

   - `_codex_status_update-YYYY-MM-DD.md`

2. Generate or refresh the gap registry:

   ```bash
   python tools/codex_gap_registry.py \
     --audit _codex_status_update-YYYY-MM-DD.md \
     --out codex_gap_registry.yaml
   ```

3. Optionally run the Search & Mapping phase via the task sequence runner:

```bash
./run_codex_task_sequence.sh codex_task_sequence.yaml _codex_status_update-YYYY-MM-DD.md
```

This will produce:
- `codex_gap_registry.yaml`
- `codex_yaml_gap_report.md`
- `codex_gap_trends.md`
- `codex_change_log.md`
- `codex_error_questions.md`

## 2. Run the minimal training + evaluation path

The minimal end-to-end path uses only in-repo scaffolding:
- `codex_ml.config.load.load_config`
- `codex_ml.data.simple_dataset.SimpleDataset`
- `codex_ml.tokenization.base.tokenize_example`
- `codex_ml.training.loop.train_one_step`
- `codex_ml.eval.evaluator.evaluate_constant`
- `codex_ml.tracking.mlflow_wrapper.log_metric`
- `codex_ml.cli.minimal_train.run_minimal`

You can exercise it in two ways:

### As a script

```bash
python -m codex_ml.cli.minimal_train
```

This prints:
- `loss_before`
- `loss_after`
- `score`

### From the Python REPL

```python
from codex_ml.cli.minimal_train import run_minimal

result = run_minimal()
print(result.loss_before, result.loss_after, result.score)
```

## 3. Run tests

To validate the scaffolding, run:

```bash
pytest tests/tools -q
pytest tests/codex_ml -q
```

As the project evolves, this minimal path can be extended to:
- Use real models and optimizers.
- Integrate richer config and Hydra-like overrides.
- Connect to a proper experiment tracking backend in offline mode.
